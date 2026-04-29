from api_clients.base_client import BaseClient


class EasycomClient(BaseClient):
    def push_order(self, payload: dict) -> dict:
        return self.post("/easycom/api/orders", json=payload)

    def get_order_sync_status(self, order_ref: str) -> dict:
        return self.get(f"/easycom/api/orders/{order_ref}")
