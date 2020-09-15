from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from operation.models import TopUpOperation, TransferOperation, Account
from operation.utils.currency_operations import top_up_balance, transfer_currency
from operation.utils.exceptions import InvalidTransferException


class TestOperationTasks(TestCase):
    def setUp(self) -> None:
        self.user_from, _ = User.objects.get_or_create(username="user1")
        self.user_to, _ = User.objects.get_or_create(username="user2")

    def test_top_up_balance(self):
        account = Account.objects.create(owner=self.user_to, balance=Decimal("100.10"))
        operations_count_before = TopUpOperation.objects.filter(
            account_to=account
        ).count()

        value_difference = Decimal("15.05")
        top_up_balance(account.id, value_difference)

        updated_account = Account.objects.get(id=account.id)
        self.assertEqual(updated_account.balance, account.balance + value_difference)

        operations_count_after = TopUpOperation.objects.filter(
            account_to=account
        ).count()
        self.assertEqual(operations_count_after, operations_count_before + 1)

    def test_invalid_transfer_currency(self):
        account_from = Account.objects.create(
            owner=self.user_from, balance=Decimal("10.35")
        )
        account_to = Account.objects.create(
            owner=self.user_to, balance=Decimal("100.85")
        )

        value = Decimal("20.50")

        with self.assertRaises(InvalidTransferException):
            transfer_currency(account_from.id, account_to.id, value)

    def test_valid_transfer_currency(self):
        value = Decimal("15.89")

        account_from = Account.objects.create(owner=self.user_from, balance=value)
        account_to = Account.objects.create(owner=self.user_to, balance=0)
        operations_count_before = TransferOperation.objects.filter(
            account_to=account_to
        ).count()

        transfer_currency(account_from.id, account_to.id, value)

        updated_account_from = Account.objects.get(id=account_from.id)
        updated_account_to = Account.objects.get(id=account_to.id)
        self.assertEqual(updated_account_from.balance, 0)
        self.assertEqual(updated_account_to.balance, value)

        operations_count_after = TransferOperation.objects.filter(
            account_to=account_to
        ).count()
        self.assertEqual(operations_count_before + 1, operations_count_after)
