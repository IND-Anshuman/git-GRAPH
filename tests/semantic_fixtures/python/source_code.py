import fastapi
from langgraph import StateGraph

class OrderCoordinator:
    """Coordinates order creation with FastAPI and LangGraph."""
    
    def __init__(self, service):
        self.service = service
        
    def create_order(self, order_id: str):
        password = "test"
        return self.service.save(order_id)

class OrderService:
    def save(self, order_id: str):
        return True
