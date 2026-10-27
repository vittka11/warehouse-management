from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import StockMovement, WarehouseItem


User = get_user_model()


class WarehouseItemModelTests(TestCase):
    def setUp(self):
        self.item = WarehouseItem.objects.create(
            book_id=1,
            book_title="Harry Potter",
            quantity=10,
            reserved_quantity=2,
        )

    def test_available_quantity(self):
        self.assertEqual(self.item.available_quantity, 8)

    def test_string_representation(self):
        self.assertEqual(str(self.item), "Harry Potter (10)")

    def test_stock_movement_string_representation(self):
        movement = StockMovement.objects.create(
            item=self.item,
            movement_type=StockMovement.MovementType.RESERVE,
            quantity=2,
        )

        self.assertIn("Harry Potter", str(movement))
        self.assertIn("RESERVE", str(movement))


class WarehouseAPITests(APITestCase):
    def setUp(self):
        self.manager_group = Group.objects.create(
            name="Warehouse Managers"
        )

        self.user = User.objects.create_user(
            username="manager",
            password="testpassword123",
        )

        self.user.groups.add(self.manager_group)

        self.item = WarehouseItem.objects.create(
            book_id=1,
            book_title="Harry Potter",
            quantity=10,
            reserved_quantity=0,
        )

        self.client.force_authenticate(user=self.user)

    def test_list_stock(self):
        response = self.client.get("/api/stock/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_stock(self):
        response = self.client.get("/api/stock/1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["book_title"], "Harry Potter")

    def test_reserve_stock(self):
        response = self.client.post(
            "/api/stock/1/reserve/",
            {"quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.item.refresh_from_db()

        self.assertEqual(self.item.reserved_quantity, 2)
        self.assertEqual(self.item.available_quantity, 8)

    def test_reserve_creates_stock_movement(self):
        self.client.post(
            "/api/stock/1/reserve/",
            {"quantity": 2},
            format="json",
        )

        movement = StockMovement.objects.get(
            movement_type=StockMovement.MovementType.RESERVE
        )

        self.assertEqual(movement.quantity, 2)
        self.assertEqual(movement.item, self.item)

    def test_reserve_insufficient_stock(self):
        response = self.client.post(
            "/api/stock/1/reserve/",
            {"quantity": 20},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    def test_reserve_zero_quantity(self):
        response = self.client.post(
            "/api/stock/1/reserve/",
            {"quantity": 0},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_reserve_invalid_quantity(self):
        response = self.client.post(
            "/api/stock/1/reserve/",
            {"quantity": "abc"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_release_stock(self):
        self.item.reserved_quantity = 5
        self.item.save()

        response = self.client.post(
            "/api/stock/1/release/",
            {"quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.item.refresh_from_db()

        self.assertEqual(self.item.reserved_quantity, 3)

    def test_release_creates_stock_movement(self):
        self.item.reserved_quantity = 5
        self.item.save()

        self.client.post(
            "/api/stock/1/release/",
            {"quantity": 2},
            format="json",
        )

        movement = StockMovement.objects.get(
            movement_type=StockMovement.MovementType.RELEASE
        )

        self.assertEqual(movement.quantity, 2)

    def test_release_more_than_reserved(self):
        self.item.reserved_quantity = 2
        self.item.save()

        response = self.client.post(
            "/api/stock/1/release/",
            {"quantity": 5},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    def test_release_zero_quantity(self):
        response = self.client.post(
            "/api/stock/1/release/",
            {"quantity": 0},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unauthenticated_user_cannot_access_stock(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/stock/")

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
