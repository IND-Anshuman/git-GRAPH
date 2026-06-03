from pydantic import BaseModel, HttpUrl

class CreateRepositoryRequest(BaseModel):
    url: HttpUrl
    branch: str = "main"
    name: str | None = None

class ExecuteRepairRequest(BaseModel):
    issue_ids: list[str]
    operator: str = "system"
