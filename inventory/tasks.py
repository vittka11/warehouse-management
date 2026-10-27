from celery import shared_task

from .models import WarehouseItem


@shared_task
def get_low_stock_items():
    low_stock_items = WarehouseItem.objects.filter(quantity__lte=5)

    return [
        {
            "book_id": item.book_id,
            "book_title": item.book_title,
            "quantity": item.quantity,
        }
        for item in low_stock_items
    ]