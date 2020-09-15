import base64
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from operation.models import Account


class TestOperationViews(TestCase):
    def setUp(self) -> None:
        username = "temp_user"
        password = "password"

        self._prepare_user(username, password)
        self.client = APIClient(
            HTTP_AUTHORIZATION=self._get_http_auth(username, password)
        )

        self.account_init_url = reverse("accounts-init")
        self.top_up_operation_url = reverse("operations-top-up")
        self.transfer_operation_url = reverse("operations-transfer")

    def _prepare_user(self, username, password):
        self.user, _ = User.objects.get_or_create(username=username)
        self.user.set_password(password)
        self.user.save()

    def _get_http_auth(self, username, password):
        data = f"{username}:{password}"
        credentials = base64.b64encode(data.encode("utf-8")).strip()
        auth = f'Basic {credentials.decode("utf-8")}'
        return auth

    def test_incorrect_auth_request(self):
        client = APIClient()
        response = client.post(self.account_init_url)
        self.assertEqual(response.status_code, 401)

    def test_new_account_creation(self):
        self.assertFalse(Account.objects.filter(owner=self.user).exists())

        response = self.client.post(self.account_init_url)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Account.objects.filter(owner=self.user).exists())

    def test_existed_account_creation(self):
        Account.objects.create(owner=self.user)

        response = self.client.post(self.account_init_url)
        self.assertEqual(response.status_code, 400)

    def test_top_up_operation_with_incorrect_value(self):
        data = dict(value=Decimal("-150.75"))

        response = self.client.post(self.top_up_operation_url, data)
        self.assertEqual(response.status_code, 400)

    def test_top_up_operation_with_missing_account(self):
        self.assertFalse(Account.objects.filter(owner=self.user).exists())

        data = dict(value=Decimal("385.15"))
        response = self.client.post(self.top_up_operation_url, data)
        self.assertEqual(response.status_code, 400)

    def test_top_up_operation_with_correct_data(self):
        account = Account.objects.create(owner=self.user)

        value = Decimal("257.29")
        data = dict(value=value)

        with patch(
            "operation.utils.currency_operations.top_up_balance"
        ) as top_up_balance_mock:
            top_up_balance_mock.return_value = None

            response = self.client.post(self.top_up_operation_url, data)
            self.assertEqual(response.status_code, 200)
            top_up_balance_mock.assert_called_once_with(str(account.id), value)

    def test_transfer_operation_on_missing_account(self):
        account = Account.objects.create(owner=self.user)

        value = Decimal("257.18")
        account_to_id = uuid4()
        self.assertNotEqual(account.id, account_to_id)
        data = dict(value=value, accout_to_id=account_to_id)
        response = self.client.post(self.transfer_operation_url, data)
        self.assertEqual(response.status_code, 400)

    def test_transfer_operation_with_correct_data(self):
        account_from = Account.objects.create(owner=self.user)
        other_user = User.objects.create(
            username="other_user", password="other_user_password"
        )
        other_account = Account.objects.create(owner=other_user)

        value = Decimal("257.05")
        data = dict(value=value, account_to_id=other_account.id)

        with patch(
            "operation.utils.currency_operations.transfer_currency"
        ) as transfer_currency_mock:
            transfer_currency_mock.return_value = None

            response = self.client.post(self.transfer_operation_url, data)
            self.assertEqual(response.status_code, 200)

            transfer_currency_mock.assert_called_once_with(
                str(account_from.id),
                str(other_account.id),
                value,
            )
