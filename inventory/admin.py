from django.contrib import admin

from .models import StockMovement, WarehouseItem


@admin.register(WarehouseItem)
class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = (
        "book_id",
        "book_title",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "updated_at",
    )
    search_fields = ("book_title", "book_id")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "movement_type",
        "quantity",
        "created_at",
    )
    list_filter = ("movement_type",)
    search_fields = ("item__book_title",)
