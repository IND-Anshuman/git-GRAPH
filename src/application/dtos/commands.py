from pydantic import BaseModel, HttpUrl

class IngestRepositoryCommand(BaseModel):
    url: str | HttpUrl
    branch: str = "main"
    name: str | None = None
