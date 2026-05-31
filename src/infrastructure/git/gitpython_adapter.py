"""GitPython adapter for repository cloning."""

import os
from git import Repo, exc
from src.application.ports.git_port import IGitAdapter
from src.domain.exceptions import DomainException

class GitPythonAdapter(IGitAdapter):
    """Implementation of IGitAdapter using GitPython."""
    
    def clone_repository(self, url: str, branch: str, target_dir: str) -> str:
        """Clones a git repository.
        
        Args:
            url: Git repository URL
            branch: Branch to clone
            target_dir: Where to clone the repo
            
        Returns:
            The absolute path to the cloned repository
            
        Raises:
            DomainException: If cloning fails
        """
        try:
            repo = Repo.clone_from(url, target_dir, branch=branch, depth=1)
            return os.path.abspath(repo.working_dir)
        except exc.GitCommandError as e:
            raise DomainException(f"Failed to clone repository: {str(e)}") from e
        except Exception as e:
            raise DomainException(f"Unexpected error during clone: {str(e)}") from e
            
    def get_current_commit_hash(self, repo_path: str) -> str:
        """Gets the current commit hash of a repository.
        
        Args:
            repo_path: Local path to the repository
            
        Returns:
            The SHA-1 commit hash
            
        Raises:
            DomainException: If getting commit fails
        """
        try:
            repo = Repo(repo_path)
            return repo.head.commit.hexsha
        except exc.InvalidGitRepositoryError as e:
            raise DomainException(f"Not a valid git repository: {repo_path}") from e
        except Exception as e:
            raise DomainException(f"Failed to get commit hash: {str(e)}") from e
