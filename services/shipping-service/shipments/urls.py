from django.urls import path

from .views import ShipmentDetailView, ShipmentListCreateView

urlpatterns = [
    path("", ShipmentListCreateView.as_view(), name="shipment-list-create"),
    path("<int:shipment_id>/", ShipmentDetailView.as_view(), name="shipment-detail"),
]
