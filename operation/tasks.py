import logging

from operation.utils import currency_operations
from operation.utils.exceptions import InvalidTransferException
from project.celery import app
from decimal import Decimal


@app.task(bind=False)
def top_up_balance_task(account_to_id, value):
    try:
        logging.info(f"top up by `{account_to_id}` with {value} $")
        currency_operations.top_up_balance(account_to_id, Decimal(value))
    except Exception as exp:
        logging.error(exp)


@app.task(bind=False)
def transfer_currency_task(account_from_id, account_to_id, value):
    message = f"transfer currency from `{account_from_id}` to `{account_to_id}` with {value} $"
    try:
        logging.info(f"attempt to {message}")
        currency_operations.transfer_currency(
            account_from_id, account_to_id, Decimal(value)
        )
        logging.info(f"success {message}")
    except InvalidTransferException as exp:
        logging.error(f"failed {message} because {exp}")
