"""
Interactive order creator for fabbox brand across stg / preprod / prod.
Prompts for: environment, WMS, payment mode, order count, pincode, barcodes.

Usage:
    python create_preprod_orders.py
"""
import uuid
import datetime
import requests
from dotenv import load_dotenv
load_dotenv()

from utils.barcode_generator import generate


def _raise(r: "requests.Response"):
    """raise_for_status but include the actual response body in the error message."""
    if not r.ok:
        try:
            body = r.json()
            msg = body.get("message") or body.get("detail") or body.get("error") or str(body)[:300]
        except Exception:
            msg = r.text[:300] or r.reason
        raise requests.HTTPError(
            f"{r.status_code} — {msg}", response=r
        )

# ─── Per-environment config ──────────────────────────────────────────────────

ENVS = {
    "stg": {
        "wms_url":    "https://zorms.zfwhospitality.in",
        "username":   "fabbox@zfwhospitality.com",
        "password":   "QWERTY!@#$%",
        "cp_password": "QWERTY!@#$%",
        "cp_api_key": "clickpost_stg_hzkXpJCz9ET19KTlX2aK34VRbG537yhBsRrb951ZPtdy0HkZpM2wx6D",
        # Fixed ref workaround removed — INSERT path now works after backend fix.
    },
    "preprod": {
        "wms_url":    "https://preprod.zorms.zfwhospitality.in",
        "username":   "fabbox@zfwhospitality.com",
        "password":   "QWERTY!@#$%",
        "cp_password": "QWERTY!@#$%",
        "cp_api_key": "clickpost_preprod_aEmgZn14UozwomtDfQR2Wx1s4LJpOTt9I6XfyfKY34siKs6S7aEWbYVCzRKD4UtX",
    },
    "prod": {
        "wms_url":    "https://zorms.zippee.delivery",
        "username":   "fabbox@zfwhospitality.com",
        "password":   "fabbox@379",
        "cp_password": "fabbox@379",
        "cp_api_key": "clickpost_prod_aEmgZn14UozwomtDfQR2Wx1s4LJpOTt9I6XfyfKY34siKs6S7aEWbYVCzRKD4UtX",
    },
}

# ─── Static order data (fabbox) ───────────────────────────────────────────────

PICKUP = {
    "name": "Mohit Nandan",
    "contact_num": "9140151251",
    "address_line_1": "Taj Mahal, Eastern Gate, Forest Colony, Tajganj, Agra, Uttar Pradesh 282001",
    "address_line_2": "Agra",
    "city": "Agra",
    "state": "Uttar Pradesh",
    "country": "India",
    "latitude": 27.171088,
    "longitude": 78.0409694,
    "email": "mohitnandan81825@gmail.com",
    "pin_code": "560034",
}

RETURN_ADDR = {
    "name": "Darsktore captain Diljeet",
    "contact_num": "9532385430",
    "address_line_1": "okhla",
    "address_line_2": "Delhi",
    "city": "Delhi",
    "state": "Delhi",
    "country": "India",
    "latitude": 28.4940959,
    "longitude": 77.0927495,
    "email": "mohitnandan81825@gmail.com",
    "pin_code": "110002",
}

ORDER_ITEMS = [
    {
        "item_quantity": 2,
        "selling_price": 100,
        "sku": "SKU_TEST_2026_001",
        "product_name": "Herbal Green Tea Pack",
        "description": "Refreshing herbal green tea blend",
        "mrp": 199,
        "ean": "EAN2026000001",
        "category": "Beverages",
        "is_returnable": False,
        "image": "",
        "meta": {"flavor": "herbal", "weight": "150g", "origin": "India"},
    },
    {
        "item_quantity": 1,
        "selling_price": 200,
        "sku": "SKU_TEST_2026_002",
        "product_name": "Black Coffee Premium",
        "description": "Strong roasted black coffee beans",
        "mrp": 349,
        "ean": "EAN2026000002",
        "category": "Beverages",
        "is_returnable": False,
        "image": "",
        "meta": {"flavor": "dark_roast", "weight": "500g", "origin": "Colombia"},
    },
]


def _ref():
    return f"AT_{uuid.uuid4().hex[:10].upper()}"


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ─── Prompt helpers ──────────────────────────────────────────────────────────

def _ask(prompt: str, default: str) -> str:
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default


def _ask_choice(prompt: str, options: list, default: str) -> str:
    opts = " / ".join(options)
    while True:
        val = input(f"{prompt} ({opts}) [{default}]: ").strip().lower() or default.lower()
        if val in [o.lower() for o in options]:
            return val
        print(f"  Invalid. Choose from: {opts}")


def _ask_int(prompt: str, default: int, min_val: int = 1, max_val: int = 20) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and min_val <= int(raw) <= max_val:
            return int(raw)
        print(f"  Enter a number between {min_val} and {max_val}.")


def prompt_config() -> dict:
    print("=" * 55)
    print("  WMS Order Creator  —  fabbox brand")
    print("=" * 55)
    print()

    env = _ask_choice("Environment?", ["stg", "preprod", "prod"], default="preprod")


    if env == "prod":
        print()
        print("  WARNING: You are about to create REAL PRODUCTION orders.")
        confirm = input("  Type 'yes' to continue: ").strip().lower()
        if confirm != "yes":
            print("  Aborted.")
            raise SystemExit(0)
        print()

    wms = _ask_choice(
        "Which WMS?",
        ["all", "clickpost", "uniware", "easycom"],
        default="all",
    )

    pm = _ask_choice(
        "Payment mode?",
        ["both", "prepaid", "cod"],
        default="both",
    )

    count = _ask_int("Orders per type?", default=1)

    pincode = _ask("Delivery pincode?", default="122008")

    barcodes = _ask_choice("Generate barcodes?", ["yes", "no"], default="yes") == "yes"

    print()
    return {
        "env": env,
        "wms": wms,
        "payment_mode": pm,
        "count": count,
        "pincode": pincode,
        "barcodes": barcodes,
    }


def build_steps(cfg: dict, cp_token: str, uw_token: str) -> list:
    wms = cfg["wms"]
    pm  = cfg["payment_mode"]

    include_cp      = wms in ("all", "clickpost")
    include_uw      = wms in ("all", "uniware")
    include_ec      = wms in ("all", "easycom")
    include_prepaid = pm in ("both", "prepaid")
    include_cod     = pm in ("both", "cod")

    env_cfg = ENVS[cfg["env"]]
    steps = []
    if include_cp and include_prepaid:
        steps.append(("Clickpost", "PREPAID", lambda t=cp_token: create_clickpost(t, False, cfg["pincode"], env_cfg)))
    if include_cp and include_cod:
        steps.append(("Clickpost", "COD",     lambda t=cp_token: create_clickpost(t, True,  cfg["pincode"], env_cfg)))
    if include_uw and include_prepaid:
        steps.append(("Uniware",   "PREPAID", lambda t=uw_token: create_uniware(t,  False, cfg["pincode"], env_cfg)))
    if include_uw and include_cod:
        steps.append(("Uniware",   "COD",     lambda t=uw_token: create_uniware(t,  True,  cfg["pincode"], env_cfg)))
    if include_ec and include_prepaid:
        steps.append(("Easycom",   "PREPAID", lambda: create_easycom(False, cfg["pincode"], env_cfg)))
    if include_ec and include_cod:
        steps.append(("Easycom",   "COD",     lambda: create_easycom(True,  cfg["pincode"], env_cfg)))
    return steps


# ─── Auth ────────────────────────────────────────────────────────────────────

def get_clickpost_token(env_cfg: dict) -> str:
    r = requests.post(
        f"{env_cfg['wms_url']}/api/1/mainsite/token",
        json={"username": env_cfg["username"], "password": env_cfg["cp_password"]},
        headers={"X-API-KEY": env_cfg["cp_api_key"]},
        timeout=30,
    )
    _raise(r)
    data = r.json()
    token = (data.get("data") or {}).get("token") or data.get("token")
    if not token:
        raise ValueError(f"No token in Clickpost auth response: {data}")
    return token


def get_uniware_token(env_cfg: dict) -> str:
    r = requests.post(
        f"{env_cfg['wms_url']}/api/1/unicommerce/authToken",
        json={"username": env_cfg["username"], "password": env_cfg["password"]},
        timeout=30,
    )
    _raise(r)
    data = r.json()
    token = data.get("token") or data.get("access") or data.get("access_token")
    if not token:
        raise ValueError(f"No token in Uniware auth response: {data}")
    return token


# ─── Clickpost ───────────────────────────────────────────────────────────────

def create_clickpost(token: str, is_cod: bool, pincode: str, env_cfg: dict) -> str:
    ref = env_cfg.get("stg_cp_ref") or _ref()
    delivery = {
        "name": "Priya Verma",
        "contact_num": "9123456780",
        "address_line_1": "Hastings Ave, Azad Nagar, Nawabganj, Kanpur, Uttar Pradesh 208002",
        "address_line_2": "Kanpur",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "country": "India",
        "latitude": 26.4843968,
        "longitude": 80.269205,
        "email": "priya.verma@gmail.com",
        "pin_code": pincode,
    }
    payload = {
        "reference_code": ref,
        "original_reference_code": ref,
        "order_date": _now(),
        "reverse_pickup": False,
        "shipment_type": "FORWARD",
        "multi_select": False,
        "is_tnb": False,
        "meta": {"tags": ["COD" if is_cod else "PREPAID"]},
        "delivery_details": delivery,
        "return_details": RETURN_ADDR,
        "pickup_details": PICKUP,
        "cod_details": {
            "is_cod": is_cod,
            "collectable_amount": 200 if is_cod else 0,
            "total_value": 200,
            "dynamic_adjustment_required": False,
            "miscellaneous_charges": {"handling_fee": 10, "packing_cost": 10, "priority_fee": 10},
        },
        "package_weight": 700,
        "package_length": 40,
        "package_width": 28,
        "package_height": 20,
        "order_items": ORDER_ITEMS,
    }
    r = requests.post(
        f"{env_cfg['wms_url']}/api/1/mainsite/shipment/create",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "x-api-key": env_cfg["cp_api_key"]},
        timeout=30,
    )
    _raise(r)
    data = r.json()
    inner = data.get("data") or data.get("result") or data
    awb = inner.get("zippee_awb") or inner.get("awb") or inner.get("waybill")
    if not awb:
        raise ValueError(f"No AWB in Clickpost response: {data}")
    return awb


# ─── Uniware ─────────────────────────────────────────────────────────────────

def create_uniware(token: str, is_cod: bool, pincode: str, env_cfg: dict) -> str:
    order_code = env_cfg.get("stg_uw_code") or _ref()
    now_str = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    tat_str = (datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%d-%b-%Y %H:%M:%S")

    payload = {
        "serviceType": "",
        "handOverMode": "",
        "returnShipmentFlag": "false",
        "Shipment": {
            "shipmentTag": "",
            "code": order_code,
            "customField": [],
            "SaleOrderCode": order_code,
            "orderCode": order_code,
            "channelCode": "CUSTOM",
            "channelName": "Regular_Orders",
            "invoiceCode": f"INV-{order_code}",
            "orderDate": now_str,
            "fullFilllmentTat": tat_str,
            "weight": "700.000",
            "length": "40",
            "height": "20",
            "breadth": "28",
            "source": "unicommerce",
            "numberOfBoxes": "1",
            "items": [
                {
                    "name": "Herbal Green Tea Pack",
                    "description": "Refreshing herbal green tea blend",
                    "quantity": 2,
                    "skuCode": "SKU_TEST_2026_001",
                    "itemPrice": 199,
                    "brand": "FabBox",
                    "color": "",
                    "category": "Beverages",
                    "size": "",
                    "item_details": "",
                    "ean": "EAN2026000001",
                    "imageURL": "",
                    "hsnCode": "21012090",
                    "tags": "",
                },
                {
                    "name": "Black Coffee Premium",
                    "description": "Strong roasted black coffee beans",
                    "quantity": 1,
                    "skuCode": "SKU_TEST_2026_002",
                    "itemPrice": 349,
                    "brand": "FabBox",
                    "color": "",
                    "category": "Beverages",
                    "size": "",
                    "item_details": "",
                    "ean": "EAN2026000002",
                    "imageURL": "",
                    "hsnCode": "21012090",
                    "tags": "",
                },
            ],
        },
        "deliveryAddressId": "",
        "deliveryAddressDetails": {
            "name": "Priya Verma",
            "email": "priya.verma@gmail.com",
            "phone": "9123456780",
            "address1": "Hastings Ave, Azad Nagar, Nawabganj, Kanpur",
            "address2": "Kanpur",
            "district": "",
            "pincode": pincode,
            "city": "Kanpur",
            "state": "Uttar Pradesh",
            "country": "India",
            "stateCode": "UP",
            "countryCode": "IN",
            "gstin": "",
            "alternatePhone": "",
        },
        "pickupAddressId": "",
        "pickupAddressDetails": {
            "name": "Mohit Nandan",
            "email": "mohitnandan81825@gmail.com",
            "phone": "9140151251",
            "address1": "Taj Mahal, Eastern Gate, Tajganj, Agra",
            "address2": "Agra",
            "pincode": "560034",
            "city": "Agra",
            "state": "Uttar Pradesh",
            "country": "India",
            "stateCode": "UP",
            "countryCode": "IN",
            "gstin": "",
            "latitude": "",
            "longitude": "",
        },
        "returnAddressId": "",
        "returnAddressDetails": {
            "name": "Darsktore captain Diljeet",
            "email": "mohitnandan81825@gmail.com",
            "phone": "9532385430",
            "address1": "okhla",
            "address2": "Delhi",
            "pincode": "110002",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "stateCode": "DL",
            "countryCode": "IN",
            "gstin": "",
            "latitude": "",
            "longitude": "",
        },
        "currencyCode": "INR",
        "paymentMode": "COD" if is_cod else "Prepaid",
        "totalAmount": "200.00",
        "collectableAmount": "200" if is_cod else "0",
        "courierName": "",
    }
    r = requests.post(
        f"{env_cfg['wms_url']}/api/1/unicommerce/waybill",
        json=payload,
        headers={"Authorization": token},
        timeout=30,
    )
    _raise(r)
    data = r.json()
    inner = data.get("data") or data.get("result") or data
    awb = inner.get("waybill") or inner.get("zippee_awb") or inner.get("awb")
    if not awb:
        raise ValueError(f"No AWB in Uniware response: {data}")
    return awb


# ─── Easycom ─────────────────────────────────────────────────────────────────

def create_easycom(is_cod: bool, pincode: str, env_cfg: dict) -> str:
    invoice_id = env_cfg.get("stg_ec_inv") or _ref()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "order_data": {
            "invoice_id": invoice_id,
            "order_id": int(uuid.uuid4().int % 100000000),
            "blockSplit": 0,
            "reference_code": invoice_id,
            "company_name": "EasyEcom Test Company",
            "warehouse_id": 59032,
            "seller_gst": "",
            "assigned_company_name": "EasyEcom Test Company",
            "assigned_warehouse_id": 59032,
            "assigned_company_gst": "",
            "warehouse_contact": "",
            "pickup_address": "Taj Mahal, Eastern Gate, Tajganj",
            "pickup_city": "Agra",
            "pickup_state": "Uttar Pradesh",
            "pickup_state_code": "09",
            "pickup_pin_code": "560034",
            "pickup_country": "India",
            "invoice_currency_code": "INR",
            "order_type": "B2C",
            "order_type_key": "retailorder",
            "replacement_order": 0,
            "marketplace": "Offline",
            "MarketCId": 123,
            "marketplace_id": 10,
            "market_shipped": 0,
            "merchant_c_id": 123,
            "qcPassed": 1,
            "salesmanUserId": 0,
            "order_date": now_str,
            "tat": now_str,
            "available_after": None,
            "invoice_date": "",
            "import_date": now_str,
            "last_update_date": now_str,
            "manifest_date": None,
            "manifest_no": None,
            "invoice_number": None,
            "marketplace_invoice_num": invoice_id,
            "shipping_last_update_date": None,
            "batch_id": 1022237,
            "batch_created_at": now_str,
            "message": None,
            "courier_aggregator_name": None,
            "courier": "Zippee Outbound",
            "carrier_id": 61546,
            "awb_number": None,
            "Package Weight": 700,
            "Package Height": 20,
            "Package Length": 40,
            "Package Width": 28,
            "order_status": "Open",
            "order_status_id": 2,
            "easyecom_order_history": None,
            "shipping_status": None,
            "shipping_status_id": None,
            "tracking_url": None,
            "shipping_history": None,
            "payment_mode": "COD" if is_cod else "Online",
            "payment_mode_id": 2 if is_cod else 5,
            "payment_gateway_transaction_number": None,
            "buyer_gst": "NA",
            "customer_name": "Priya Verma",
            "shipping_name": "Priya Verma",
            "contact_num": "9123456780",
            "address_line_1": "Hastings Ave, Azad Nagar, Nawabganj, Kanpur",
            "address_line_2": None,
            "city": "Kanpur",
            "pin_code": pincode,
            "state": "Uttar Pradesh",
            "state_code": "09",
            "country": "India",
            "country_code": 0,
            "email": "priya.verma@gmail.com",
            "latitude": None,
            "longitude": None,
            "billing_name": "Priya Verma",
            "billing_address_1": "Hastings Ave, Azad Nagar, Nawabganj, Kanpur",
            "billing_address_2": None,
            "billing_city": "Kanpur",
            "billing_state": "Uttar Pradesh",
            "billing_state_code": "09",
            "billing_pin_code": pincode,
            "billing_country": "India",
            "billing_mobile": "9123456780",
            "order_quantity": 2,
            "documents": None,
            "invoice_documents": None,
            "collectable_amount": 200 if is_cod else 0,
            "total_amount": 200,
            "total_tax": 3.0508,
            "breakup_types": {"Item Amount Excluding Tax": 16.9492, "Item Amount IGST": 3.0508},
            "tcs_rate": 0,
            "tcs_amount": 0,
            "customer_code": "NA",
            "order_items": [
                {
                    "suborder_id": int(uuid.uuid4().int % 100000000),
                    "suborder_num": invoice_id,
                    "invoicecode": None,
                    "item_collectable_amount": 0,
                    "shipment_type": "Zippee Outbound",
                    "suborder_quantity": 1,
                    "item_quantity": 1,
                    "returned_quantity": 0,
                    "cancelled_quantity": 0,
                    "shipped_quantity": 1,
                    "tax_type": "GST",
                    "product_id": 19452180,
                    "company_product_id": 76120647,
                    "sku": "CCSKU23",
                    "expiry_type": 0,
                    "sku_type": "Normal",
                    "sub_product_count": 1,
                    "marketplace_sku": "CCSKU23",
                    "listing_ref_number": "-",
                    "listing_id": "-",
                    "productName": "Herbal Green Tea Pack",
                    "description": "Refreshing herbal green tea blend",
                    "category": "Beverages",
                    "brand": "FabBox",
                    "brand_id": 7147017,
                    "model_no": "6513",
                    "product_tax_code": None,
                    "ean": "EAN2026000001",
                    "size": "NA",
                    "cost": 150,
                    "mrp": 199,
                    "weight": 700,
                    "length": 40,
                    "width": 28,
                    "height": 20,
                    "scheme_applied": 0,
                    "custom_fields": [],
                    "serials": [None],
                    "tax_rate": 18,
                    "selling_price": "100",
                    "breakup_types": {"Item Amount Excluding Tax": 16.9492, "Item Amount IGST": 3.0508},
                    "station_scanned_quantity": 0,
                    "batch_scanned_quantity": 0,
                    "assigned_quantity": 1,
                }
            ],
        },
        "credentials": {
            "username": env_cfg["username"],
            "password": env_cfg["password"],
            "token": "wo3876556644",
            "account_no": "",
            "service_type": "",
            "eeApiToken": f"{env_cfg['username']}, {env_cfg['password']}, wo3876556644",
            "attempts_offered": "3",
        },
    }
    r = requests.post(
        f"{env_cfg['wms_url']}/api/1/easyecom/createShipment",
        json=payload,
        timeout=30,
    )
    _raise(r)
    data = r.json()
    inner = data.get("data") or data.get("result") or data
    awb = inner.get("tracking_number") or inner.get("zippee_awb") or inner.get("awb")
    if not awb:
        raise ValueError(f"No AWB in Easycom response: {data}")
    return awb


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    cfg = prompt_config()
    env_cfg = ENVS[cfg["env"]]

    cp_token = uw_token = None
    if cfg["wms"] in ("all", "clickpost"):
        print(f"Authenticating Clickpost ({cfg['env']})...")
        cp_token = get_clickpost_token(env_cfg)
        print(f"  token: {cp_token[:30]}...")
    if cfg["wms"] in ("all", "uniware"):
        print(f"Authenticating Uniware ({cfg['env']})...")
        uw_token = get_uniware_token(env_cfg)
        print(f"  token: {uw_token[:30]}...")
    print()

    steps = build_steps(cfg, cp_token, uw_token)
    if not steps:
        print("No order types selected. Exiting.")
        return

    total = len(steps) * cfg["count"]
    print(f"Creating {total} order(s)  [{len(steps)} type(s) × {cfg['count']}]  env={cfg['env']}")
    print("-" * 55)

    results, errors = [], []

    for source, order_type, fn in steps:
        for i in range(cfg["count"]):
            label = f"{source} {order_type}" + (f" #{i+1}" if cfg["count"] > 1 else "")
            try:
                awb = fn()
                results.append((source, order_type, awb))
                print(f"  [OK]  {label:30s}  {awb}")
            except Exception as exc:
                errors.append((source, order_type, str(exc)))
                print(f"  [ERR] {label:30s}  {exc}")

    print()

    if results and cfg["barcodes"]:
        print("Generating barcodes...")
        generate(results)
        print()

    print("AWB Summary")
    print("=" * 55)
    for source, order_type, awb in results:
        print(f"  {source:10s}  {order_type:8s}  {awb}")

    if errors:
        print()
        print(f"FAILED ({len(errors)}):")
        for source, order_type, msg in errors:
            print(f"  {source} {order_type}: {msg}")


if __name__ == "__main__":
    main()
