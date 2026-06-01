from pydantic import BaseModel, HttpUrl

class CreateRepositoryRequest(BaseModel):
    url: HttpUrl
    branch: str = "main"
    name: str | None = None
