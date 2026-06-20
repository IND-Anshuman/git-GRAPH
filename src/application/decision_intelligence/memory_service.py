from .repository_memory import RepositoryMemory
from .repository_event import RepositoryEvent, RepositoryEventType

class MemoryService:
    def build_memory(self, events: list[RepositoryEvent]) -> RepositoryMemory:
        if not events:
            return RepositoryMemory(repository_id="unknown")
            
        repository_id = events[0].repository_id
        memory = RepositoryMemory(repository_id=repository_id, events=events)
        
        for event in events:
            if event.event_type == RepositoryEventType.DEPENDENCY_INTRODUCED:
                memory.technology_introductions.append(event.commit_hash)
            elif event.event_type == RepositoryEventType.SERVICE_CREATED:
                memory.service_creations.append(event.commit_hash)
            elif event.event_type in (RepositoryEventType.CAPABILITY_CREATED, RepositoryEventType.CAPABILITY_SPLIT):
                memory.capability_changes.append(event.commit_hash)
            elif event.event_type == RepositoryEventType.ARCHITECTURE_CHANGED:
                memory.architecture_changes.append(event.commit_hash)
            elif event.event_type == RepositoryEventType.OWNERSHIP_CHANGED:
                memory.ownership_changes.append(event.commit_hash)
                
        return memory
