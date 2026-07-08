# ==================================================
# NovaPOS Global Constants
# ==================================================

PROJECT_NAME = "NovaPOS"
API_PREFIX = "/api/v1"

ENV_DEVELOPMENT = "development"
ENV_PRODUCTION = "production"
ENV_TESTING = "testing"

DATABASE_SQLITE = "sqlite"
DATABASE_POSTGRESQL = "postgresql"

PAYMENT_METHOD_CASH = "Efectivo"
PAYMENT_METHOD_YAPE = "Yape"
PAYMENT_METHOD_CREDIT = "Fiado"

ALLOWED_PAYMENT_METHODS = [
    PAYMENT_METHOD_CASH,
    PAYMENT_METHOD_YAPE,
    PAYMENT_METHOD_CREDIT,
]

RECEIPT_TYPE_BOLETA = "Boleta"
RECEIPT_TYPE_NOTA_VENTA = "Nota de Venta"

ALLOWED_RECEIPT_TYPES = [
    RECEIPT_TYPE_BOLETA,
    RECEIPT_TYPE_NOTA_VENTA,
]

DEFAULT_IGV_PERCENTAGE = 18