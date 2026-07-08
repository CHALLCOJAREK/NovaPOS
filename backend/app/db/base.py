from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models in NovaPOS.
    """

    pass


from app.models.supplier import Supplier  # noqa: F401, E402
from app.models.customer import Customer  # noqa: F401, E402
from app.models.product_category import ProductCategory  # noqa: F401, E402
from app.models.product import Product  # noqa: F401, E402
from app.models.inventory_movement import InventoryMovement  # noqa: F401, E402
from app.models.purchase import Purchase  # noqa: F401, E402
from app.models.purchase_item import PurchaseItem  # noqa: F401, E402
from app.models.sale import Sale  # noqa: F401, E402
from app.models.sale_item import SaleItem  # noqa: F401, E402