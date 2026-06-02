"""Git history commit walker."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator, List, Optional
import os
from git import Repo

from src.domain.entities.commit import Commit
from src.domain.value_objects.repository_id import RepositoryId

@dataclass(frozen=True)
class GitFileChange:
    """Represents a file-level change in a git commit."""
    path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    old_path: Optional[str] = None

class CommitWalker:
    """Traverses Git repository history and identifies commits and changed files."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = repo_path

    def walk_history(
        self,
        repository_id: RepositoryId,
        branch: str,
        start_commit_hash: Optional[str] = None
    ) -> List[tuple[Commit, List[GitFileChange]]]:
        """Walks the commit history from oldest to newest, starting after start_commit_hash if provided.
        
        Returns a list of tuples containing the Commit entity and its list of GitFileChanges.
        """
        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        repo = Repo(self.repo_path)
        
        # 1. Determine commit range
        if start_commit_hash:
            # Check if start_commit_hash exists in the repo
            try:
                repo.commit(start_commit_hash)
                # Walk commits from start_commit_hash..branch (newest to oldest)
                commit_objs = list(repo.iter_commits(f"{start_commit_hash}..{branch}"))
            except Exception:
                # If start commit is invalid/not found, fall back to full history walk
                commit_objs = list(repo.iter_commits(branch))
        else:
            commit_objs = list(repo.iter_commits(branch))

        # Reverse to process from oldest to newest (root to HEAD)
        commit_objs.reverse()

        result = []
        for c in commit_objs:
            # Convert timezone
            tz = timezone(c.author_tz_offset) if c.author_tz_offset else timezone.utc
            authored_dt = datetime.fromtimestamp(c.authored_date, tz)
            
            commit_entity = Commit(
                hash=c.hexsha,
                repository_id=repository_id,
                author=c.author.name or "Unknown",
                email=c.author.email or "unknown@example.com",
                timestamp=authored_dt,
                message=c.message or "",
                parent_hashes=[p.hexsha for p in c.parents]
            )

            # Get file changes
            file_changes = []
            if not c.parents:
                # Root commit: all blobs in the tree are 'added'
                for entry in c.tree.traverse():
                    if entry.type == 'blob':
                        file_changes.append(
                            GitFileChange(path=entry.path, change_type="added")
                        )
            else:
                # Diff against the first parent (which is standard for branch ancestry)
                parent = c.parents[0]
                diffs = parent.diff(c)
                for diff in diffs:
                    ctype = diff.change_type
                    # Map git change types to simple strings
                    if ctype == "A":
                        file_changes.append(GitFileChange(path=diff.b_path, change_type="added"))
                    elif ctype == "D":
                        file_changes.append(GitFileChange(path=diff.a_path, change_type="deleted"))
                    elif ctype == "R":
                        file_changes.append(
                            GitFileChange(
                                path=diff.b_path,
                                change_type="renamed",
                                old_path=diff.a_path
                            )
                        )
                    else:
                        # M (modified), T (type changed), etc.
                        file_changes.append(GitFileChange(path=diff.b_path, change_type="modified"))

            result.append((commit_entity, file_changes))

        return result
