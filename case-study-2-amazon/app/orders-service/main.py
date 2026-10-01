"""
Amazon Orders Service
Theme: Independent small-team ownership.
This service is fully decoupled — it only talks to inventory and payments
via HTTP. Teams can deploy this independently without touching other services.
"""
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import Optional
import time
import uuid

app = FastAPI(
    title="Amazon Orders Service",
    description="Orders microservice — Amazon two-pizza team demo",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

# --- In-memory store ---
ORDERS: dict[str, dict] = {}


class OrderRequest(BaseModel):
    product_id: str
    quantity: int
    customer_id: str
    shipping_address: str


@app.get("/health", tags=["ops"])
def health_check():
    return {"status": "healthy", "service": "orders-service", "timestamp": time.time()}


@app.get("/", tags=["ops"])
def root():
    return {"service": "orders-service", "version": "1.0.0"}


@app.post("/orders", tags=["orders"], status_code=201)
def create_order(order: OrderRequest):
    """Create a new order. In production this would call inventory + payments services."""
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order_data = {
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "customer_id": order.customer_id,
        "shipping_address": order.shipping_address,
        "status": "CONFIRMED",
        "created_at": time.time(),
    }
    ORDERS[order_id] = order_data
    return order_data


@app.get("/orders", tags=["orders"])
def list_orders(customer_id: Optional[str] = None):
    """List orders, optionally filtered by customer."""
    orders = list(ORDERS.values())
    if customer_id:
        orders = [o for o in orders if o["customer_id"] == customer_id]
    return {"total": len(orders), "orders": orders}


@app.get("/orders/{order_id}", tags=["orders"])
def get_order(order_id: str):
    """Get a specific order by ID."""
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return ORDERS[order_id]


@app.patch("/orders/{order_id}/status", tags=["orders"])
def update_order_status(order_id: str, status: str):
    """Update order status (CONFIRMED → SHIPPED → DELIVERED)."""
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    valid_statuses = {"CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    ORDERS[order_id]["status"] = status
    return ORDERS[order_id]
