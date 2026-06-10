from django.test import TestCase
from rest_framework.exceptions import NotFound

from payments.models import Payment
from payments.services import PaymentService


class PaymentServiceTests(TestCase):
    def setUp(self):
        self.payment_1 = Payment.objects.create(
            order_id=1,
            amount="50.00",
            provider="stripe",
            transaction_id="txn-svc-001",
            status="pending",
        )
        self.payment_2 = Payment.objects.create(
            order_id=2,
            amount="30.00",
            provider="paypal",
            transaction_id="txn-svc-002",
            status="completed",
        )

    def test_list_payments_filters_by_order_id(self):
        queryset = PaymentService.list_payments({"order_id": 1})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.payment_1.id)

    def test_list_payments_filters_by_status(self):
        queryset = PaymentService.list_payments({"status": "completed"})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.payment_2.id)

    def test_get_payment_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            PaymentService.get_payment(999999)

    def test_update_payment_persists_changes(self):
        PaymentService.update_payment(self.payment_1, {"status": "failed", "amount": "10.00"})
        self.payment_1.refresh_from_db()

        self.assertEqual(self.payment_1.status, "failed")
        self.assertEqual(str(self.payment_1.amount), "10.00")

    def test_delete_payment_removes_record(self):
        PaymentService.delete_payment(self.payment_1)

        self.assertFalse(Payment.objects.filter(id=self.payment_1.id).exists())
