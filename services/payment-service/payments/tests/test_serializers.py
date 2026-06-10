from django.test import TestCase

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentSerializerTests(TestCase):
    def test_serializer_accepts_valid_payload(self):
        serializer = PaymentSerializer(
            data={
                "order_id": 1,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-ser-001",
                "status": "pending",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_invalid_status(self):
        serializer = PaymentSerializer(
            data={
                "order_id": 1,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-ser-002",
                "status": "unknown",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_serializer_requires_order_id(self):
        serializer = PaymentSerializer(
            data={
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-ser-003",
                "status": "pending",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("order_id", serializer.errors)

    def test_serializer_rejects_duplicate_transaction_id(self):
        Payment.objects.create(
            order_id=1,
            amount="50.00",
            provider="stripe",
            transaction_id="txn-ser-004",
            status="pending",
        )
        serializer = PaymentSerializer(
            data={
                "order_id": 2,
                "amount": "60.00",
                "provider": "stripe",
                "transaction_id": "txn-ser-004",
                "status": "completed",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("transaction_id", serializer.errors)
