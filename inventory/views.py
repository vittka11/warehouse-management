from django.core.cache import cache
from django.db import transaction
from django.views.generic import ListView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StockMovement, WarehouseItem
from .permissions import IsWarehouseManager, IsWarehouseStaffOrManager
from .serializers import StockMovementSerializer, WarehouseItemSerializer


class WarehouseItemViewSet(viewsets.ModelViewSet):
    queryset = WarehouseItem.objects.all()
    serializer_class = WarehouseItemSerializer
    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "reserve",
            "release",
        ]:
            return [IsWarehouseManager()]

        return [IsWarehouseStaffOrManager()]

    def list(self, request, *args, **kwargs):
        cache_key = "warehouse_items"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)

        return response

    @action(detail=True, methods=["post"])
    def reserve(self, request, book_id=None):
        item = self.get_object()

        try:
            quantity = int(request.data.get("quantity", 0))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid quantity."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item.available_quantity < quantity:
            return Response(
                {"error": "Not enough stock available."},
                status=status.HTTP_409_CONFLICT,
            )

        with transaction.atomic():
            item.reserved_quantity += quantity
            item.save(update_fields=["reserved_quantity", "updated_at"])

            StockMovement.objects.create(
                item=item,
                movement_type=StockMovement.MovementType.RESERVE,
                quantity=quantity,
            )

        cache.delete("warehouse_items")

        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=["post"])
    def release(self, request, book_id=None):
        item = self.get_object()

        try:
            quantity = int(request.data.get("quantity", 0))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid quantity."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item.reserved_quantity < quantity:
            return Response(
                {"error": "Cannot release more than reserved."},
                status=status.HTTP_409_CONFLICT,
            )

        with transaction.atomic():
            item.reserved_quantity -= quantity
            item.save(update_fields=["reserved_quantity", "updated_at"])

            StockMovement.objects.create(
                item=item,
                movement_type=StockMovement.MovementType.RELEASE,
                quantity=quantity,
            )

        cache.delete("warehouse_items")

        return Response(self.get_serializer(item).data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related("item").all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsWarehouseStaffOrManager]


class BaseWarehouseView:
    model = WarehouseItem
    context_object_name = "items"


class WarehouseItemListView(BaseWarehouseView, ListView):
    template_name = "inventory/warehouse_list.html"