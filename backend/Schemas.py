from pydantic import BaseModel

class QueryRequest(BaseModel):
    user_query: str  # This will validate that `user_query` is a string

class QueryResponse(BaseModel):
    response: str  # This will define the structure of the response
