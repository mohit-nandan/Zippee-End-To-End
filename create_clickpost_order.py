"""
One-shot script to create a Clickpost staging order with delivery pincode 122022.
Run from the zippee-automation directory:
    python create_clickpost_order.py

Requires: STAGING_CLICKPOST_API_KEY in .env must be a valid UUID from the Clickpost dashboard.
"""
import uuid
import datetime
import requests
from dotenv import load_dotenv
from utils.config_loader import get_config

load_dotenv()
cfg = get_config("staging")

API_KEY  = cfg["clickpost_api_key"]
USERNAME = cfg["clickpost_shipment_username"]
BASE_URL = cfg["clickpost_api_url"].rstrip("/")

ORDER_REF = f"AT_{uuid.uuid4().hex[:8].upper()}"   # ≤ 20 chars

now = datetime.datetime.now(datetime.timezone.utc)

payload = {
    "pickup_info": {
        "pickup_name":    "Zippee Staging Warehouse",
        "pickup_address": "DLF Cyber City, Phase II",
        "pickup_city":    "Gurugram",
        "pickup_state":   "Haryana",
        "pickup_pincode": "122018",
        "pickup_country": "IN",
        "pickup_phone":   "9876543210",
        "email":          USERNAME,
        "pickup_time":    now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    },
    "drop_info": {
        "drop_name":    "Auto Test Customer",
        "drop_address": "Sector 56, Near Huda Market",
        "drop_city":    "Gurugram",
        "drop_state":   "Haryana",
        "drop_pincode": "122022",
        "drop_country": "IN",
        "drop_phone":   "9876543210",
    },
    "shipment_details": {
        "reference_number": ORDER_REF,
        "order_type":       "PREPAID",
        "delivery_type":    "FORWARD",
        "cod_value":        0,
        "invoice_value":    500.0,
        "invoice_date":     now.strftime("%Y-%m-%d"),
        "invoice_number":   f"INV-{ORDER_REF}",
        "weight":           500,
        "length":           10,
        "breadth":          10,
        "height":           10,
        "courier_partner":  1,
        "account_code":     "",
        "items": [
            {
                "description": "Test Product",
                "quantity":    1,
                "sku":         "SKU_TEST_001",
                "price":       500.0,
            }
        ],
    },
    "additional": {
        "async": False,
        "label": False,
    },
}

url    = f"{BASE_URL}/api/v3/create-order/"
params = {"username": USERNAME, "key": API_KEY}

print(f"Order ref   : {ORDER_REF}")
print(f"Endpoint    : POST {url}")
print(f"Drop pincode: 122022")
print()

response = requests.post(url, json=payload, params=params, timeout=30)
print(f"HTTP status : {response.status_code}")
try:
    resp = response.json()
    print(f"Response    : {resp}")
    meta = resp.get("meta", {})
    if meta.get("success"):
        result = resp.get("result", {})
        print(f"\nOrder created successfully!")
        print(f"  Waybill : {result.get('waybill')}")
        print(f"  Order ID: {result.get('order_id')}")
        print(f"  Label   : {result.get('label')}")
    else:
        print(f"\nOrder creation failed: {meta.get('message')}")
except Exception:
    print(f"Response    : {response.text[:800]}")
