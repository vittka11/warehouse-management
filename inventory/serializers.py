from rest_framework import serializers

from .models import StockMovement, WarehouseItem


class WarehouseItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = WarehouseItem
        fields = (
            "id",
            "book_id",
            "book_title",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "updated_at",
        )
        read_only_fields = ("reserved_quantity", "updated_at")


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = (
            "id",
            "item",
            "movement_type",
            "quantity",
            "created_at",
        )
        read_only_fields = ("created_at",)