from django.test import TestCase
from rest_framework.exceptions import NotFound

from shipments.models import Shipment
from shipments.services import ShipmentService


class ShipmentServiceTests(TestCase):
    def setUp(self):
        self.shipment_1 = Shipment.objects.create(
            order_id=1,
            address="123 Test Street",
            carrier="DHL",
            tracking_number="trk-svc-001",
            status="pending",
        )
        self.shipment_2 = Shipment.objects.create(
            order_id=2,
            address="456 Test Street",
            carrier="FedEx",
            tracking_number="trk-svc-002",
            status="delivered",
        )

    def test_list_shipments_filters_by_order_id(self):
        queryset = ShipmentService.list_shipments({"order_id": 1})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.shipment_1.id)

    def test_list_shipments_filters_by_status(self):
        queryset = ShipmentService.list_shipments({"status": "delivered"})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.shipment_2.id)

    def test_get_shipment_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            ShipmentService.get_shipment(999999)

    def test_update_shipment_persists_changes(self):
        ShipmentService.update_shipment(self.shipment_1, {"status": "in_transit", "address": "789 Updated Street"})
        self.shipment_1.refresh_from_db()

        self.assertEqual(self.shipment_1.status, "in_transit")
        self.assertEqual(self.shipment_1.address, "789 Updated Street")

    def test_delete_shipment_removes_record(self):
        ShipmentService.delete_shipment(self.shipment_1)

        self.assertFalse(Shipment.objects.filter(id=self.shipment_1.id).exists())
