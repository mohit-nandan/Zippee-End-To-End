from api_clients.base_client import BaseClient


class UniwareClient(BaseClient):
    def push_order(self, payload: dict) -> dict:
        return self.post("/uniware/v1/orders/push", json=payload)

    def get_order_sync_status(self, order_ref: str) -> dict:
        return self.get(f"/uniware/v1/orders/{order_ref}/status")
