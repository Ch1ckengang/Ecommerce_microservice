from django.test import TestCase

from shipments.models import Shipment
from shipments.serializers import ShipmentSerializer


class ShipmentSerializerTests(TestCase):
    def test_serializer_accepts_valid_payload(self):
        serializer = ShipmentSerializer(
            data={
                "order_id": 1,
                "address": "123 Test Street",
                "carrier": "DHL",
                "tracking_number": "trk-ser-001",
                "status": "pending",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_invalid_status(self):
        serializer = ShipmentSerializer(
            data={
                "order_id": 1,
                "address": "123 Test Street",
                "carrier": "DHL",
                "tracking_number": "trk-ser-002",
                "status": "unknown",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_serializer_requires_order_id(self):
        serializer = ShipmentSerializer(
            data={
                "address": "123 Test Street",
                "carrier": "DHL",
                "tracking_number": "trk-ser-003",
                "status": "pending",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("order_id", serializer.errors)

    def test_serializer_rejects_duplicate_tracking_number(self):
        Shipment.objects.create(
            order_id=1,
            address="123 Test Street",
            carrier="DHL",
            tracking_number="trk-ser-004",
            status="pending",
        )
        serializer = ShipmentSerializer(
            data={
                "order_id": 2,
                "address": "456 Test Street",
                "carrier": "FedEx",
                "tracking_number": "trk-ser-004",
                "status": "packed",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("tracking_number", serializer.errors)
