from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.db.models import F

from operation.models import TopUpOperation, Account
from operation.models import TransferOperation
from operation.utils.exceptions import InvalidTransferException


def top_up_balance(account_to_id: UUID, value: Decimal):
    with transaction.atomic():
        account = Account.objects.select_for_update().get(id=account_to_id)
        account.balance = F("balance") + value
        account.save()

        TopUpOperation.objects.create(account_to=account, value=value)


def transfer_currency(account_from_id: UUID, account_to_id: UUID, value: Decimal):
    with transaction.atomic():
        accounts = (
            Account.objects.filter(id__in=[account_to_id, account_from_id])
            .select_for_update()
            .all()
        )
        if accounts[0].id == account_from_id:
            account_from = accounts[0]
            account_to = accounts[1]
        else:
            account_from = accounts[1]
            account_to = accounts[0]

        if account_from.balance < value:
            raise InvalidTransferException("Insufficient funds on the account")

        account_from.balance = F("balance") - value
        account_to.balance = F("balance") + value
        account_from.save()
        account_to.save()

        TransferOperation.objects.create(
            account_from=account_from, account_to=account_to, value=value
        )
