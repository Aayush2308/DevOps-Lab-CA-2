"""
Amazon Inventory Service
Independently deployable — tracks stock levels per product.
Demonstrates: a team can release inventory features without
touching orders or payments (two-pizza team principle).
"""
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import time

app = FastAPI(
    title="Amazon Inventory Service",
    description="Inventory microservice — Amazon two-pizza team demo",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

# --- In-memory inventory ---
INVENTORY: dict[str, dict] = {
    "P001": {"product_id": "P001", "name": "Echo Dot", "stock": 500, "reserved": 0, "warehouse": "US-WEST"},
    "P002": {"product_id": "P002", "name": "Kindle Paperwhite", "stock": 250, "reserved": 10, "warehouse": "US-EAST"},
    "P003": {"product_id": "P003", "name": "Fire TV Stick", "stock": 800, "reserved": 50, "warehouse": "EU-WEST"},
    "P004": {"product_id": "P004", "name": "Ring Doorbell", "stock": 120, "reserved": 5, "warehouse": "US-WEST"},
}


class ReserveRequest(BaseModel):
    quantity: int
    order_id: str


@app.get("/health", tags=["ops"])
def health_check():
    return {"status": "healthy", "service": "inventory-service", "timestamp": time.time()}


@app.get("/", tags=["ops"])
def root():
    return {"service": "inventory-service", "version": "1.0.0"}


@app.get("/inventory", tags=["inventory"])
def list_inventory():
    """List all products with stock levels."""
    items = list(INVENTORY.values())
    return {
        "total_products": len(items),
        "items": [
            {**item, "available": item["stock"] - item["reserved"]}
            for item in items
        ],
    }


@app.get("/inventory/{product_id}", tags=["inventory"])
def get_product_stock(product_id: str):
    """Get stock level for a specific product."""
    if product_id not in INVENTORY:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    item = INVENTORY[product_id]
    return {**item, "available": item["stock"] - item["reserved"]}


@app.put("/inventory/{product_id}/reserve", tags=["inventory"])
def reserve_stock(product_id: str, req: ReserveRequest):
    """Reserve stock for an order. Returns 409 if insufficient stock."""
    if product_id not in INVENTORY:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    item = INVENTORY[product_id]
    available = item["stock"] - item["reserved"]
    if req.quantity > available:
        raise HTTPException(
            status_code=409,
            detail=f"Insufficient stock. Requested: {req.quantity}, Available: {available}",
        )
    INVENTORY[product_id]["reserved"] += req.quantity
    return {
        "product_id": product_id,
        "order_id": req.order_id,
        "reserved_qty": req.quantity,
        "remaining_available": available - req.quantity,
    }


@app.put("/inventory/{product_id}/release", tags=["inventory"])
def release_stock(product_id: str, req: ReserveRequest):
    """Release reserved stock (e.g., order cancelled)."""
    if product_id not in INVENTORY:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    INVENTORY[product_id]["reserved"] = max(0, INVENTORY[product_id]["reserved"] - req.quantity)
    return {"product_id": product_id, "released_qty": req.quantity}
