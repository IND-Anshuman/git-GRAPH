from fastapi import Query

class PaginationParams:
    def __init__(
        self,
        offset: int = Query(0, ge=0, description="The number of items to skip"),
        limit: int = Query(50, ge=1, le=200, description="The number of items to return")
    ):
        self.offset = offset
        self.limit = limit
