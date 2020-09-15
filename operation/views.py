from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from operation.tasks import top_up_balance_task, transfer_currency_task
from .models import Account
from .serializers import TopUpOperationSerializer, TransferOperationSerializer


class AccountViewSet(ViewSet):
    @action(methods=["post"], detail=False, url_path="init", url_name="init")
    def init_user_account(self, request):
        user = request.user
        if not Account.objects.filter(owner=user).exists():
            Account.objects.create(owner=user)
            return Response(status=status.HTTP_201_CREATED)

        return Response(
            data={"error": "account already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OperationViewSet(ViewSet):
    @action(methods=["post"], detail=False, url_path="top_up", url_name="top-up")
    def apply_top_up_operation(self, request):
        account = Account.objects.filter(owner=request.user).first()
        if account is None:
            return Response(
                data={"error": "account doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TopUpOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        top_up_balance_task.delay(
            account_to_id=account.id, value=serializer.data["value"]
        )
        return Response(status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False, url_path="transfer", url_name="transfer")
    def apply_transfer_operation(self, request):
        account_from = Account.objects.filter(owner=request.user).first()
        if account_from is None:
            return Response(
                data={"error": "account doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TransferOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        transfer_currency_task.delay(
            account_from.id, validated_data["account_to_id"], validated_data["value"]
        )

        return Response(status=status.HTTP_200_OK)
