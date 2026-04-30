from api_clients.base_client import BaseClient


class ClickpostClient(BaseClient):
    """
    Clickpost uses API key auth via query param, not Bearer token.
    Shipment API uses Basic auth (username/password).
    """

    def __init__(self, base_url: str, api_key: str, shipment_username: str = None, shipment_password: str = None, **kwargs):
        super().__init__(base_url=base_url, token=None)
        self._api_key = api_key
        self._shipment_username = shipment_username
        self._shipment_password = shipment_password

    def push_order(self, payload: dict) -> dict:
        return self.post("/api/v3/create-order/", json=payload, params={"username": self._shipment_username, "key": self._api_key})

    def get_tracking_status(self, waybill: str) -> dict:
        return self.get(f"/api/v2/track/", params={"username": self._shipment_username, "key": self._api_key, "waybill": waybill})
