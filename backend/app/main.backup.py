from fastapi import FastAPI

from app.routers.role_router import router as role_router
from app.routers.permission_router import router as permission_router
from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.store_setting_router import router as store_setting_router
from app.routers.supplier_router import router as supplier_router
from app.routers.customer_router import router as customer_router
from app.routers.product_category_router import router as product_category_router
from app.routers.product_router import router as product_router
from app.routers.inventory_movement_router import router as inventory_movement_router
from app.routers.purchase_router import router as purchase_router
from app.routers.sale_router import router as sale_router
from app.routers.cash_router import router as cash_router
from app.routers.customer_debt_router import router as customer_debt_router

app = FastAPI(
    title="NovaPOS API",
    version="0.1.0",
    description="Backend oficial de NovaPOS"
)


API_PREFIX = "/api/v1"


app.include_router(
    role_router,
    prefix=API_PREFIX,
)

app.include_router(
    permission_router,
    prefix=API_PREFIX,
)

app.include_router(
    user_router,
    prefix=API_PREFIX,
)

app.include_router(
    auth_router,
    prefix=API_PREFIX,
)

app.include_router(
    store_setting_router,
    prefix=API_PREFIX,
)

app.include_router(
    supplier_router,
    prefix=API_PREFIX,
)

app.include_router(
    customer_router,
    prefix=API_PREFIX,
)

app.include_router(
    product_category_router,
    prefix=API_PREFIX,
)

app.include_router(
    product_router,
    prefix=API_PREFIX,
)

app.include_router(
    inventory_movement_router,
    prefix=API_PREFIX,
)

app.include_router(
    purchase_router,
    prefix=API_PREFIX,
)

app.include_router(
    sale_router,
    prefix=API_PREFIX,
)

app.include_router(
    cash_router,
    prefix=API_PREFIX,
)

app.include_router(
    customer_debt_router,
    prefix=API_PREFIX
)

@app.get("/")
def health_check():
    return {
        "app": "NovaPOS",
        "status": "running",
        "version": "0.1.0"
    }