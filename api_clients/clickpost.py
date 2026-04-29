from api_clients.base_client import BaseClient


class ClickpostClient(BaseClient):
    def push_order(self, payload: dict) -> dict:
        return self.post("/clickpost/v1/orders", json=payload)

    def get_tracking_status(self, waybill: str) -> dict:
        return self.get(f"/clickpost/v1/track/{waybill}")
