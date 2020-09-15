from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from .models import Account


class TopUpOperationSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )


class TransferOperationSerializer(TopUpOperationSerializer):
    account_to_id = serializers.UUIDField()

    def validate_account_to_id(self, account_to_id):
        account = Account.objects.filter(id=account_to_id).first()
        if account is None:
            raise serializers.ValidationError('Account by given id does\'not exist')

        return account.id
