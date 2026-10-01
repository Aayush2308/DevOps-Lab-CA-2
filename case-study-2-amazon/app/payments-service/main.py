"""
Amazon Payments Service
Independently deployable — processes payments for orders.
Demonstrates isolation: billing team ships features without
coordination with orders or inventory teams.
"""
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import Optional
import time
import uuid
import random

app = FastAPI(
    title="Amazon Payments Service",
    description="Payments microservice — Amazon two-pizza team demo",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

# --- In-memory payment records ---
PAYMENTS: dict[str, dict] = {}


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str = "USD"
    payment_method: str  # "card", "upi", "wallet"
    customer_id: str


@app.get("/health", tags=["ops"])
def health_check():
    return {"status": "healthy", "service": "payments-service", "timestamp": time.time()}


@app.get("/", tags=["ops"])
def root():
    return {"service": "payments-service", "version": "1.0.0"}


@app.post("/payments", tags=["payments"], status_code=201)
def process_payment(payment: PaymentRequest):
    """
    Process a payment for an order.
    Simulates a real payment gateway with ~95% success rate.
    """
    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"

    # Simulate occasional payment failure (5% chance)
    success = random.random() > 0.05

    payment_data = {
        "payment_id": payment_id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_method": payment.payment_method,
        "customer_id": payment.customer_id,
        "status": "SUCCESS" if success else "FAILED",
        "processed_at": time.time(),
        "gateway_ref": f"GW-{uuid.uuid4().hex[:12].upper()}",
    }
    PAYMENTS[payment_id] = payment_data

    if not success:
        raise HTTPException(status_code=402, detail={
            "payment_id": payment_id,
            "status": "FAILED",
            "reason": "Payment declined by gateway",
        })

    return payment_data


@app.get("/payments/{payment_id}", tags=["payments"])
def get_payment(payment_id: str):
    """Retrieve a payment record by ID."""
    if payment_id not in PAYMENTS:
        raise HTTPException(status_code=404, detail=f"Payment '{payment_id}' not found")
    return PAYMENTS[payment_id]


@app.get("/payments", tags=["payments"])
def list_payments(order_id: Optional[str] = None, customer_id: Optional[str] = None):
    """List all payments, optionally filtered."""
    payments = list(PAYMENTS.values())
    if order_id:
        payments = [p for p in payments if p["order_id"] == order_id]
    if customer_id:
        payments = [p for p in payments if p["customer_id"] == customer_id]
    return {"total": len(payments), "payments": payments}


@app.post("/payments/{payment_id}/refund", tags=["payments"])
def refund_payment(payment_id: str):
    """Issue a refund for a successful payment."""
    if payment_id not in PAYMENTS:
        raise HTTPException(status_code=404, detail=f"Payment '{payment_id}' not found")
    payment = PAYMENTS[payment_id]
    if payment["status"] != "SUCCESS":
        raise HTTPException(status_code=400, detail="Can only refund successful payments")
    PAYMENTS[payment_id]["status"] = "REFUNDED"
    return {"payment_id": payment_id, "refund_status": "REFUNDED", "amount": payment["amount"]}
