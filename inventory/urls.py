from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    StockMovementViewSet,
    WarehouseItemListView,
    WarehouseItemViewSet,
)

router = DefaultRouter()
router.register("stock", WarehouseItemViewSet, basename="stock")
router.register("movements", StockMovementViewSet, basename="movements")

urlpatterns = router.urls
urlpatterns += [
    path("warehouse/", WarehouseItemListView.as_view(), name="warehouse-list"),
]