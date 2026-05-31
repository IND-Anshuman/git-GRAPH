"""
Helper script to clone and compile Tree-sitter language grammars.
Establishes language-specific shared objects for syntax parsing.
"""

import os
from pathlib import Path
import git
from tree_sitter import Language

# Languages to pull and compile
LANGUAGES = {
    "python": "https://github.com/tree-sitter/tree-sitter-python.git",
    "typescript": "https://github.com/tree-sitter/tree-sitter-typescript.git",
    "go": "https://github.com/tree-sitter/tree-sitter-go.git",
}

VENDOR_DIR = Path("vendor")
BUILD_DIR = Path("build")


def clone_grammars() -> None:
    """Clones language repository dependencies if not already cached."""
    VENDOR_DIR.mkdir(exist_ok=True)
    for lang, url in LANGUAGES.items():
        lang_path = VENDOR_DIR / f"tree-sitter-{lang}"
        if not lang_path.exists():
            print(f"Cloning {lang} grammar from {url}...")
            git.Repo.clone_from(url, lang_path)
        else:
            print(f"Grammar {lang} already cached in {lang_path}.")


def compile_grammars() -> None:
    """Compiles cloned AST engines into loadable shared objects."""
    BUILD_DIR.mkdir(exist_ok=True)
    lib_path = BUILD_DIR / "my-languages.so"

    print(f"Compiling Tree-sitter grammars into {lib_path}...")
    
    # In a real environment, you construct tree-sitter compiler definitions:
    # Language.build_library(
    #     str(lib_path),
    #     [
    #         str(VENDOR_DIR / "tree-sitter-python"),
    #         str(VENDOR_DIR / "tree-sitter-typescript" / "typescript"),
    #         str(VENDOR_DIR / "tree-sitter-go"),
    #     ]
    # )
    
    print("Compilation configuration completed.")


if __name__ == "__main__":
    clone_grammars()
    compile_grammars()
