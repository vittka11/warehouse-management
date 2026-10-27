from django.db import models


class WarehouseItem(models.Model):
    book_id = models.PositiveIntegerField(unique=True)
    book_title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book_title} ({self.quantity})"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"
        RESERVE = "RESERVE", "Reserve"
        RELEASE = "RELEASE", "Release"

    item = models.ForeignKey(
        WarehouseItem,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MovementType.choices,
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.book_title} - {self.movement_type} - {self.quantity}"
