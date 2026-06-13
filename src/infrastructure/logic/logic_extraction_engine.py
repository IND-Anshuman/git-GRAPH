"""Engine that matches AST features against behavior patterns to extract logic signatures."""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from src.application.ports.ast_feature_port import ASTFeatures, ExtractedFeature
from src.domain.entities.behavior_explanation import BehaviorExplanation, RuleVerdict
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_version import LogicVersion
from src.domain.enums.evidence_type import EvidenceType
from src.domain.enums.language import SupportedLanguage
from src.domain.exceptions import LogicExtractionException
from src.domain.services.logic_identity_service import LogicIdentityService
from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.logic.ast_feature_extractor import (
    TreeSitterASTFeatureExtractor,
)
from src.infrastructure.logic.logic_fingerprint_engine import (
    LogicFingerprintEngine,
)
from src.infrastructure.logic.pattern_registry import PatternRegistry


class LogicExtractionEngine:
    """Orchestrates logic extraction from CodeEntities by matching AST features against patterns."""

    def __init__(
        self,
        extractor: TreeSitterASTFeatureExtractor,
        fingerprinter: LogicFingerprintEngine,
        registry: PatternRegistry,
    ) -> None:
        self._extractor = extractor
        self._fingerprinter = fingerprinter
        self._registry = registry

    def extract_logic(
        self,
        entity: CodeEntity,
        parsed_tree: Any,
        source_code: str,
        commit_hash: str,
    ) -> List[
        Tuple[
            LogicSignature,
            LogicVersion,
            List[LogicEvidence],
            BehaviorExplanation,
        ]
    ]:
        """
        Extract behavioral logic from a CodeEntity at a given commit.

        Args:
            entity: The CodeEntity being analyzed.
            parsed_tree: The tree-sitter parse tree of the containing source file.
            source_code: The raw content of the containing source file.
            commit_hash: The current commit hash.

        Returns:
            A list of tuples (Signature, Version, EvidenceList, Explanation) for
            each matched pattern.
        """
        try:
            # 1. Extract AST Features for the entity's line range
            features = self._extractor.extract_features(
                parsed_tree,
                source_code,
                entity.location.start_line,
                entity.location.end_line,
            )

            # 2. Compute logic fingerprint
            fingerprint = self._fingerprinter.compute_fingerprint(features)

            # 3. Retrieve candidate patterns based on index keys
            # Combine all feature symbols to query candidates
            index_keys = []
            for c in features.calls:
                index_keys.append(c.symbol)
            for imp in features.imports:
                index_keys.append(imp.symbol)
            for dec in features.decorators:
                index_keys.append(dec.symbol)
            for comp in features.comparisons:
                index_keys.append(comp.symbol)
            for sub in features.subscripts:
                index_keys.append(sub.symbol)
                raw_text = sub.metadata.get("raw", "") if sub.metadata else ""
                if "cache" in raw_text.lower():
                    index_keys.append("struct:dict_lookup")
                if "session" in raw_text.lower():
                    index_keys.append("subscript:session")

            candidates = self._registry.get_candidate_patterns(index_keys)
            print(f"  [ExtractionEngine] Entity: {entity.qualified_name}")
            print(f"  [ExtractionEngine] Features: calls={len(features.calls)}, imports={len(features.imports)}")
            print(f"  [ExtractionEngine] Index keys: {index_keys}")
            print(f"  [ExtractionEngine] Candidates found: {[p.pattern_id for p in candidates]}")

            results = []

            # 4. Evaluate each candidate pattern
            for pattern in candidates:
                match_result = self._evaluate_pattern(entity, features, pattern)
                if not match_result:
                    print(f"  [ExtractionEngine] Pattern {pattern.pattern_id} evaluation returned None (negative indicator or filter).")
                    continue

                verdicts, confidence_breakdown, evidence_list = match_result
                print(f"  [ExtractionEngine] Pattern {pattern.pattern_id} evaluated: overall_confidence={confidence_breakdown.overall_confidence}")

                # Check if it meets a minimum threshold
                if confidence_breakdown.overall_confidence < 0.30:
                    continue

                # 5. Build domain entities
                # Logic Signature
                sig_id = LogicIdentityService.generate_logic_signature_id(
                    repository_id=entity.repository_id,
                    entity_seid=entity.seid,
                    language=entity.language.name,
                    canonical_name=pattern.pattern_id,
                )

                signature = LogicSignature(
                    id=sig_id,
                    repository_id=entity.repository_id,
                    canonical_name=pattern.pattern_id,
                    language=entity.language,
                    ontology_node_id=pattern.ontology_node_id,
                    description=pattern.name,
                    created_at=datetime.utcnow(),
                    metadata={"pattern_version": pattern.pattern_version},
                )

                # Logic Version
                version_id = uuid.uuid4()
                version = LogicVersion(
                    id=version_id,
                    logic_signature_id=sig_id,
                    code_entity_seid=entity.seid,
                    commit_hash=commit_hash,
                    version_ordinal=1,  # Will be adjusted by application service during timeline linking
                    fingerprint=fingerprint,
                    overall_confidence=confidence_breakdown.overall_confidence,
                    confidence_breakdown=confidence_breakdown,
                    is_primary=True,
                    metadata={"source_file": entity.location.file_path},
                    created_at=datetime.utcnow(),
                )

                # Update evidence logic_version_ids
                for ev in evidence_list:
                    ev.logic_version_id = version_id

                # Behavior Explanation
                explanation = BehaviorExplanation(
                    id=uuid.uuid4(),
                    logic_version_id=version_id,
                    behavior_name=pattern.name,
                    ontology_path=pattern.ontology_node_id,
                    overall_confidence=confidence_breakdown.overall_confidence,
                    confidence_breakdown=confidence_breakdown,
                    matched_pattern_ids=[pattern.pattern_id],
                    evidence_summary=f"Matched behavioral pattern '{pattern.name}' with {len(evidence_list)} evidence points.",
                    rule_verdicts=verdicts,
                    is_stale=False,
                    generated_at=datetime.utcnow(),
                    metadata={},
                )

                results.append((signature, version, evidence_list, explanation))

            return results

        except Exception as e:
            raise LogicExtractionException(
                f"Failed logic extraction for entity {entity.qualified_name}: {e}"
            ) from e

    def _evaluate_pattern(
        self, entity: CodeEntity, features: ASTFeatures, pattern: BehaviorPattern
    ) -> (
        Tuple[List[RuleVerdict], ConfidenceBreakdown, List[LogicEvidence]] | None
    ):
        """Evaluate a BehaviorPattern against ASTFeatures. Returns None if negative indicators are hit."""
        rules = pattern.rules
        verdicts: List[RuleVerdict] = []
        evidence_list: List[LogicEvidence] = []

        # Check negative indicators first (fail-fast)
        neg_indicators = rules.get("negative_indicators", [])
        for neg in neg_indicators:
            neg_sym = neg.get("symbol")
            if not neg_sym:
                continue
            # If any call, import, or string contains the negative indicator symbol
            call_hit = any(neg_sym in c.symbol for c in features.calls)
            imp_hit = any(neg_sym in i.symbol for i in features.imports)
            str_hit = any(neg_sym in s.metadata.get("raw", "") for s in features.strings if s.metadata)
            if call_hit or imp_hit or str_hit:
                # Disqualify this pattern entirely
                return None

        # Track category scores for ConfidenceBreakdown
        ast_score = 0.0
        dep_score = 0.0
        data_flow_score = 0.0
        pattern_score = 0.0
        struct_score = 0.0

        ast_rules = rules.get("ast_features", [])
        ast_passed = 0
        ast_count = len(ast_rules)

        for i, r in enumerate(ast_rules):
            m_type = r.get("match_type")
            desc = r.get("description", f"AST rule {i}")
            passed = False
            ev_id = None

            if m_type == "call":
                target_func = r.get("target_function")
                target_func_pat = r.get("target_function_pattern")
                target_method = r.get("target_method")
                target_method_pat = r.get("target_method_pattern")
                target_mod = r.get("target_module")
                target_mod_pat = r.get("target_module_pattern")
                target_class_pat = r.get("target_class_pattern")

                # Match call
                for call in features.calls:
                    func_part = call.symbol.split(":")[-1] if ":" in call.symbol else call.symbol
                    
                    # 1. Match function/method name
                    func_matched = False
                    has_func_rule = any([target_func, target_func_pat, target_method, target_method_pat])
                    if not has_func_rule:
                        func_matched = True
                    else:
                        if target_func and (target_func == func_part or target_func in func_part):
                            func_matched = True
                        elif target_func_pat and re.search(target_func_pat, func_part, re.IGNORECASE):
                            func_matched = True
                        elif target_method and (target_method == func_part or target_method in func_part):
                            func_matched = True
                        elif target_method_pat and re.search(target_method_pat, func_part, re.IGNORECASE):
                            func_matched = True

                    # 2. Match module
                    mod_matched = True
                    if target_mod:
                        mod_matched = any(target_mod in imp.symbol for imp in features.imports)
                    elif target_mod_pat:
                        mod_matched = any(re.search(target_mod_pat, imp.symbol, re.IGNORECASE) for imp in features.imports)

                    # 3. Match class (e.g. cursor / connection)
                    class_matched = True
                    if target_class_pat:
                        if "." in func_part:
                            class_part = func_part.split(".")[0]
                            class_matched = bool(re.search(target_class_pat, class_part, re.IGNORECASE))
                        else:
                            class_matched = False

                    if func_matched and mod_matched and class_matched:
                        passed = True
                        ev = LogicEvidence(
                            id=uuid.uuid4(),
                            logic_version_id=uuid.UUID(int=0),  # Placeholder, filled later
                            evidence_type=EvidenceType.AST_CALL,
                            file_path=entity.location.file_path,
                            start_line=call.line_number,
                            end_line=call.line_number,
                            ast_node_type="Call",
                            matched_symbol=call.symbol,
                            matched_rule_id=f"{pattern.pattern_id}_call_{i}",
                            confidence_contribution=0.30,
                        )
                        evidence_list.append(ev)
                        ev_id = ev.id
                        break

            elif m_type == "import":
                target_mod = r.get("target_module")
                target_mod_pat = r.get("target_module_pattern")
                for imp in features.imports:
                    imp_module = imp.symbol.split(":")[-1] if ":" in imp.symbol else imp.symbol
                    import_matched = False
                    if target_mod and target_mod in imp_module:
                        import_matched = True
                    elif target_mod_pat and re.search(target_mod_pat, imp_module, re.IGNORECASE):
                        import_matched = True

                    if import_matched:
                        passed = True
                        ev = LogicEvidence(
                            id=uuid.uuid4(),
                            logic_version_id=uuid.UUID(int=0),
                            evidence_type=EvidenceType.AST_IMPORT,
                            file_path=entity.location.file_path,
                            start_line=imp.line_number,
                            end_line=imp.line_number,
                            ast_node_type="Import",
                            matched_symbol=imp.symbol,
                            matched_rule_id=f"{pattern.pattern_id}_import_{i}",
                            confidence_contribution=0.10,
                        )
                        evidence_list.append(ev)
                        ev_id = ev.id
                        break

            elif m_type == "decorator":
                target_pat = r.get("target_function_pattern")
                target_method_pat = r.get("target_method_pattern")
                target_obj_pat = r.get("target_object_pattern")

                for dec in features.decorators:
                    dec_name = dec.symbol.split(":")[-1] if ":" in dec.symbol else dec.symbol
                    
                    matched_dec = False
                    has_dec_rule = any([target_pat, target_method_pat, target_obj_pat])
                    if not has_dec_rule:
                        matched_dec = True
                    else:
                        if target_pat and (target_pat == dec_name or re.search(target_pat, dec_name, re.IGNORECASE)):
                            matched_dec = True
                        
                        method_matched = True
                        obj_matched = True
                        if target_method_pat or target_obj_pat:
                            if "." in dec_name:
                                obj_part, method_part = dec_name.split(".", 1)
                                if target_method_pat:
                                    method_matched = bool(re.search(target_method_pat, method_part, re.IGNORECASE))
                                if target_obj_pat:
                                    obj_matched = bool(re.search(target_obj_pat, obj_part, re.IGNORECASE))
                            else:
                                if target_method_pat:
                                    method_matched = bool(re.search(target_method_pat, dec_name, re.IGNORECASE))
                                if target_obj_pat:
                                    obj_matched = False
                        
                        if method_matched and obj_matched:
                            matched_dec = True

                    if matched_dec:
                        passed = True
                        ev = LogicEvidence(
                            id=uuid.uuid4(),
                            logic_version_id=uuid.UUID(int=0),
                            evidence_type=EvidenceType.STRUCTURAL,
                            file_path=entity.location.file_path,
                            start_line=dec.line_number,
                            end_line=dec.line_number,
                            ast_node_type="Decorator",
                            matched_symbol=dec.symbol,
                            matched_rule_id=f"{pattern.pattern_id}_dec_{i}",
                            confidence_contribution=0.15,
                        )
                        evidence_list.append(ev)
                        ev_id = ev.id
                        break

            elif m_type == "comparison":
                target_op = r.get("operator_pattern")
                for comp in features.comparisons:
                    op_part = comp.symbol.split(":")[-1] if ":" in comp.symbol else comp.symbol
                    if target_op and re.search(target_op, op_part, re.IGNORECASE):
                        passed = True
                        ev = LogicEvidence(
                            id=uuid.uuid4(),
                            logic_version_id=uuid.UUID(int=0),
                            evidence_type=EvidenceType.DATA_FLOW,
                            file_path=entity.location.file_path,
                            start_line=comp.line_number,
                            end_line=comp.line_number,
                            ast_node_type="Comparison",
                            matched_symbol=comp.symbol,
                            matched_rule_id=f"{pattern.pattern_id}_comp_{i}",
                            confidence_contribution=0.10,
                        )
                        evidence_list.append(ev)
                        ev_id = ev.id
                        break

            elif m_type == "subscript":
                target_key = r.get("key_pattern")
                for sub in features.subscripts:
                    raw_text = sub.metadata.get("raw", "") if sub.metadata else ""
                    if not target_key or re.search(target_key, raw_text, re.IGNORECASE):
                        passed = True
                        ev = LogicEvidence(
                            id=uuid.uuid4(),
                            logic_version_id=uuid.UUID(int=0),
                            evidence_type=EvidenceType.STRUCTURAL,
                            file_path=entity.location.file_path,
                            start_line=sub.line_number,
                            end_line=sub.line_number,
                            ast_node_type="Subscript",
                            matched_symbol=sub.symbol,
                            matched_rule_id=f"{pattern.pattern_id}_sub_{i}",
                            confidence_contribution=0.10,
                        )
                        evidence_list.append(ev)
                        ev_id = ev.id
                        break

            if passed:
                ast_passed += 1

            verdicts.append(
                RuleVerdict(
                    rule_id=f"ast_{i}",
                    rule_description=desc,
                    passed=passed,
                    contribution=0.20 if passed else 0.0,
                    evidence_ref=ev_id,
                )
            )

        if ast_count > 0:
            ast_score = ast_passed / ast_count
            struct_score = ast_score  # decorators and structure
            dep_score = (
                ast_score  # calls and imports map to dependency score as well
            )

        # Evaluate data flow rules
        df_rules = rules.get("data_flow", [])
        df_passed = 0
        df_count = len(df_rules)

        for i, r in enumerate(df_rules):
            src_pat = r.get("source_param_pattern")
            sink_call = r.get("sink_call")
            passed = False
            ev_id = None

            for flow in features.data_flows:
                source_matches = re.search(
                    src_pat, flow["source"], re.IGNORECASE
                )
                sink_matches = sink_call in flow["sink"]

                if source_matches and sink_matches:
                    passed = True
                    ev = LogicEvidence(
                        id=uuid.uuid4(),
                        logic_version_id=uuid.UUID(int=0),
                        evidence_type=EvidenceType.DATA_FLOW,
                        file_path=entity.location.file_path,
                        start_line=flow["line"],
                        end_line=flow["line"],
                        ast_node_type="Call",
                        matched_symbol=flow["sink"],
                        matched_rule_id=f"{pattern.pattern_id}_df_{i}",
                        data_flow_path=flow["path"],
                        confidence_contribution=0.40,
                    )
                    evidence_list.append(ev)
                    ev_id = ev.id
                    break

            if passed:
                df_passed += 1

            verdicts.append(
                RuleVerdict(
                    rule_id=f"df_{i}",
                    rule_description=f"Data flow from param matching '{src_pat}' to call '{sink_call}'",
                    passed=passed,
                    contribution=0.30 if passed else 0.0,
                    evidence_ref=ev_id,
                )
            )

        if df_count > 0:
            data_flow_score = df_passed / df_count

        # Evaluate string literals
        sl_rules = rules.get("string_literals", [])
        sl_passed = 0
        sl_count = len(sl_rules)

        for i, r in enumerate(sl_rules):
            pat = r.get("pattern")
            desc = r.get("description", f"String literal matching '{pat}'")
            passed = False
            ev_id = None
            for s in features.strings:
                raw_text = s.metadata.get("raw", "") if s.metadata else ""
                if re.search(pat, raw_text, re.IGNORECASE):
                    passed = True
                    ev = LogicEvidence(
                        id=uuid.uuid4(),
                        logic_version_id=uuid.UUID(int=0),
                        evidence_type=EvidenceType.STRUCTURAL,
                        file_path=entity.location.file_path,
                        start_line=s.line_number,
                        end_line=s.line_number,
                        ast_node_type="String",
                        matched_symbol=s.symbol,
                        matched_rule_id=f"{pattern.pattern_id}_sl_{i}",
                        confidence_contribution=0.05,
                    )
                    evidence_list.append(ev)
                    ev_id = ev.id
                    break

            if passed:
                sl_passed += 1

            verdicts.append(
                RuleVerdict(
                    rule_id=f"sl_{i}",
                    rule_description=desc,
                    passed=passed,
                    contribution=0.10 if passed else 0.0,
                    evidence_ref=ev_id,
                )
            )

        # Fail pattern entirely if string literals are required but not all matched
        if sl_count > 0 and sl_passed < sl_count:
            return None

        if sl_count > 0:
            sl_score = sl_passed / sl_count
            if ast_count > 0:
                struct_score = (ast_score + sl_score) / 2
            else:
                struct_score = sl_score

        # Evaluate required parameters
        rp_rules = rules.get("required_params", [])
        rp_passed = 0
        rp_count = len(rp_rules)

        # Extract parameter names from entity signature
        # We can extract from metadata or do regex on source text
        # If parameters are empty, we check if they are in data flow sources
        params = list({flow["source"] for flow in features.data_flows})

        for i, r in enumerate(rp_rules):
            name_pat = r.get("name_pattern")
            passed = False
            for p in params:
                if re.search(name_pat, p, re.IGNORECASE):
                    passed = True
                    break

            if passed:
                rp_passed += 1

            verdicts.append(
                RuleVerdict(
                    rule_id=f"rp_{i}",
                    rule_description=f"Parameter name matching pattern '{name_pat}' required",
                    passed=passed,
                    contribution=0.10 if passed else 0.0,
                )
            )

        # Compute general pattern score based on passed verdicts fraction
        total_rules = len(verdicts)
        passed_rules = sum(1 for v in verdicts if v.passed)
        pattern_score = passed_rules / total_rules if total_rules > 0 else 0.0

        # Build ConfidenceBreakdown
        breakdown = ConfidenceBreakdown.compute(
            ast=ast_score,
            dependency=dep_score,
            data_flow=data_flow_score,
            pattern=pattern_score,
            structural=struct_score,
            evidence_count=len(evidence_list),
        )

        return verdicts, breakdown, evidence_list
