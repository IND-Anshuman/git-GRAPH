from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class SymbolNode:
    symbol_id: str
    canonical_name: str
    scope_id: str
    aliases: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class SymbolReference:
    source_symbol: str
    target_symbol: str
    reference_type: str

@dataclass
class SymbolGraph:
    nodes: List[SymbolNode] = field(default_factory=list)
    references: List[SymbolReference] = field(default_factory=list)
