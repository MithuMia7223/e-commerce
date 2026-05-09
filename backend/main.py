from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .db import engine
from . import models
from .websocket import manager

from .routers import user, product, cart, order, comments, likes, notifications, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "E-commerce API Running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Server received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
