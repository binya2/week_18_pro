import uvicorn
from fastapi import FastAPI

from routers import order_router, upload_router

app = FastAPI(title="Pizza Order API")

app.include_router(order_router)
app.include_router(upload_router)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
