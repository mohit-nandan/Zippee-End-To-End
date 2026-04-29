from api_clients.base_client import BaseClient


class InternalClient(BaseClient):
    def create_order(self, payload: dict) -> dict:
        return self.post("/api/v1/orders", json=payload)

    def get_order(self, order_id: str) -> dict:
        return self.get(f"/api/v1/orders/{order_id}")

    def cancel_order(self, order_id: str) -> dict | None:
        return self.patch(f"/api/v1/orders/{order_id}/cancel")

    def get_order_status(self, order_id: str) -> str:
        order = self.get_order(order_id)
        return order["status"]

    def mark_attendance(self, rider_id: str, payload: dict) -> dict:
        return self.post(f"/api/v1/riders/{rider_id}/attendance", json=payload)

    def get_rider(self, rider_id: str) -> dict:
        return self.get(f"/api/v1/riders/{rider_id}")

    def assign_order_to_rider(self, order_id: str, rider_id: str) -> dict:
        return self.patch(
            f"/api/v1/orders/{order_id}/assign",
            json={"rider_id": rider_id},
        )
