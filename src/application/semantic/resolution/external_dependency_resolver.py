"""External Dependency Resolver for identifying third-party frameworks/packages/services."""

from typing import List, Dict, Any, Optional
from src.application.semantic.resolution.global_semantic_graph import GlobalSemanticGraph

class ExternalDependencyResolver:
    """Detects and registers external package, framework, API and model dependencies."""

    def __init__(self, global_graph: GlobalSemanticGraph):
        self.global_graph = global_graph
        # Standard classification of known external modules
        self.package_mappings = {
            "fastapi": ("EXTERNAL_FRAMEWORK", "FastAPI"),
            "flask": ("EXTERNAL_FRAMEWORK", "Flask"),
            "django": ("EXTERNAL_FRAMEWORK", "Django"),
            "redis": ("EXTERNAL_SERVICE", "Redis"),
            "postgres": ("EXTERNAL_SERVICE", "Postgres"),
            "postgresql": ("EXTERNAL_SERVICE", "Postgres"),
            "stripe": ("EXTERNAL_API", "Stripe"),
            "openai": ("EXTERNAL_MODEL", "OpenAI"),
            "anthropic": ("EXTERNAL_MODEL", "Anthropic"),
            "langchain": ("EXTERNAL_FRAMEWORK", "LangChain"),
            "llamaindex": ("EXTERNAL_FRAMEWORK", "LlamaIndex"),
            "celery": ("EXTERNAL_SERVICE", "Celery"),
            "nats": ("EXTERNAL_SERVICE", "NATS"),
            "kafka": ("EXTERNAL_SERVICE", "Kafka"),
            "sqs": ("EXTERNAL_SERVICE", "AWS SQS"),
            "boto3": ("EXTERNAL_SDK", "AWS SDK"),
            "google.cloud.pubsub": ("EXTERNAL_SERVICE", "GCP PubSub"),
            "azure.servicebus": ("EXTERNAL_SERVICE", "Azure Service Bus"),
        }

    def resolve_external_imports(self, file_path: str, imports: List[Dict[str, Any]]) -> None:
        """Processes import statements to detect external package usages and registers them in the global graph."""
        for imp in imports:
            module_name = imp.get("module_name")
            if not module_name:
                continue
            base_module = module_name.split(".")[0].lower()
            
            # Check mappings
            if base_module in self.package_mappings:
                dep_type, name = self.package_mappings[base_module]
                self.global_graph.add_external_dependency(name, dep_type, {"imported_module": module_name})
            else:
                # Default to EXTERNAL_PACKAGE
                # Skip relative paths or local modules
                if not module_name.startswith(".") and "/" not in module_name and "\\" not in module_name:
                    # check if it is defined as a file in the repository
                    is_local = False
                    for qname in self.global_graph.symbols:
                        if qname.startswith(module_name):
                            is_local = True
                            break
                    if not is_local:
                        self.global_graph.add_external_dependency(module_name, "EXTERNAL_PACKAGE")
