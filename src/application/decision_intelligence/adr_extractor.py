import os
import re

class ADRExtractor:
    def extract_adrs(self, repository_path: str) -> list[str]:
        adr_paths = []
        for root, _, files in os.walk(repository_path):
            if "node_modules" in root or ".git" in root or "venv" in root:
                continue
            for file in files:
                if "adr" in file.lower() and file.endswith(".md"):
                    adr_paths.append(os.path.join(root, file))
        return adr_paths
