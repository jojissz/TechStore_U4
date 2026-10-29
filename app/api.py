from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from cargar_csv import load_fixture
from app.domain import InvalidOrderTransition, InvalidOrderData
from app.discounts import discount_details

# Variable global para almacenar los pedidos en memoria
orders = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global orders
    try:
        orders = load_fixture()
        print(f"¡Fixtures cargados con éxito! Total de pedidos: {len(orders)}")
        print(f"IDs disponibles en memoria: {list(orders.keys())}")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO AL CARGAR LOS CSV: {str(e)}")
        raise e
    yield

app = FastAPI(title="TechStore U4", version="1.0.0", lifespan=lifespan)

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    return {
        "id": order.id,
        "status": order.status.value,
        "units": order.units,
        "total": str(order.total.amount),
        "customer_id": order.customer.id
    }

@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    try:
        order.confirm()
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"id": order.id, "status": order.status.value, "events": [e.name for e in order.events]}

@app.post("/orders/{order_id}/ship")
def ship_order(order_id: str, tracking_number: str = "GUIA-12345"):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    try:
        order.ship(tracking_number)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"id": order.id, "status": order.status.value, "events": [e.name for e in order.events]}

@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, reason: str = "Cliente solicita cancelación"):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    try:
        order.cancel(reason)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"id": order.id, "status": order.status.value, "events": [e.name for e in order.events]}

@app.get("/orders")
def list_orders():
    return [{"id": order.id, "status": order.status.value, "units": order.units,
             "total": str(order.total.amount)} for order in orders.values()]

@app.get("/orders/{order_id}/discount")
def get_discount(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    return discount_details(order)

@app.post("/orders/{order_id}/deliver")
def deliver_order(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    try:
        order.deliver()
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": order.id, "status": order.status.value, "events": [e.name for e in order.events]}

@app.post("/orders/{order_id}/return")
def return_order(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="El pedido no existe")
    try:
        order.return_order()
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": order.id, "status": order.status.value, "events": [e.name for e in order.events]}
