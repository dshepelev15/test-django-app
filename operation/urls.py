from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccountViewSet, OperationViewSet

router = DefaultRouter(trailing_slash=False)
router.register("accounts", AccountViewSet, basename="accounts")
router.register("operations", OperationViewSet, basename="operations")

urlpatterns = [path("", include(router.urls))]
