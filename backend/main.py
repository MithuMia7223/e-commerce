from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import engine
import models
from websocket import manager

from routers import (
    user,
    product,
    cart,
    order,
    comments,
    likes,
    notifications,
    admin,
    wishlist,
    review,
    rating,
    category,
    shipping,
    coupons,
    variants,
    refunds,
    analytics,
    profile,
)

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
app.include_router(wishlist.router)
app.include_router(review.router)
app.include_router(rating.router)
app.include_router(category.router)
app.include_router(shipping.router)
app.include_router(coupons.router)
app.include_router(variants.router)
app.include_router(refunds.router)
app.include_router(analytics.router)
app.include_router(profile.router)


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
