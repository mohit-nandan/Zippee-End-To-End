from pages.base_page import BasePage


class OrderDetailPage(BasePage):
    """Update selectors to match your actual order detail page HTML."""
    ORDER_ID_LABEL = "[data-testid='order-id'], .order-id"
    STATUS_LABEL   = "[data-testid='order-status'], .order-status"
    RIDER_LABEL    = "[data-testid='assigned-rider'], .rider-name"

    def get_order_id(self) -> str:
        return self.get_text(self.ORDER_ID_LABEL)

    def get_status(self) -> str:
        return self.get_text(self.STATUS_LABEL)

    def get_assigned_rider(self) -> str:
        return self.get_text(self.RIDER_LABEL)
