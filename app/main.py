from fastapi import FastAPI
from app.routers import (
    auth, 
    restaurant,
    admin,
     menu_item, 
     address, 
     cart, 
     order, 
     restaurant_orders,
     delivery,
     order_history,
     ratings,
     notification,
     order_tracking
)


app = FastAPI(title="Food Delivery System")

app.include_router(auth.router)
app.include_router(restaurant.router)
app.include_router(admin.router)
app.include_router(menu_item.router)
app.include_router(address.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(restaurant_orders.router)
app.include_router(delivery.router)
app.include_router(order_history.router)
app.include_router(ratings.router)
app.include_router(notification.router)
app.include_router(order_tracking.router)

@app.get("/")
def home():
    return {"message": "Food Delivery System API is running"}