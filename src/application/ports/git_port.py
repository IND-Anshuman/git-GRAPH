from abc import ABC, abstractmethod

class IGitAdapter(ABC):
    @abstractmethod
    def clone_repository(self, url: str, branch: str, target_dir: str) -> str:
        """Clones a git repository and returns the local path."""
        pass

    @abstractmethod
    def get_current_commit_hash(self, repo_path: str) -> str:
        """Returns the current commit hash for the repository at the given path."""
        pass

    @abstractmethod
    def checkout_commit(self, repo_path: str, commit_hash: str) -> None:
        """Checks out a specific commit hash in the repository."""
        pass
