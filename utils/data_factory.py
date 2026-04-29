import uuid
from faker import Faker

fake = Faker()

PREFIX = "AUTO_TEST"


def order_id() -> str:
    return f"{PREFIX}_{uuid.uuid4().hex[:8].upper()}"


def generate_order_payload(warehouse: str = "internal", **overrides) -> dict:
    """
    Returns a minimal valid order creation payload.
    Update field names to match your actual API contract.
    """
    payload = {
        "order_ref": order_id(),
        "warehouse": warehouse,
        "customer_name": fake.name(),
        "customer_phone": fake.numerify("98########"),
        "delivery_address": fake.address(),
        "items": [
            {"sku": f"SKU_{uuid.uuid4().hex[:6].upper()}", "quantity": 1}
        ],
    }
    payload.update(overrides)
    return payload


def generate_rider_payload(**overrides) -> dict:
    """
    Returns a minimal valid rider creation payload.
    Update field names to match your actual API contract.
    """
    payload = {
        "name": f"{PREFIX}_{fake.first_name()}",
        "phone": fake.numerify("98########"),
        "email": fake.email(),
    }
    payload.update(overrides)
    return payload
