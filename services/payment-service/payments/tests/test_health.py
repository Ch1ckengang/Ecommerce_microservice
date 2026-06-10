from django.test import RequestFactory, SimpleTestCase

from payment_service.health import health_check


class PaymentHealthCheckTests(SimpleTestCase):
    def test_health_endpoint_returns_ok_payload(self):
        request = RequestFactory().get("/health/")
        response = health_check(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"status": "ok", "service": "payment-service"},
        )
