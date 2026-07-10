# shipwatch

A small service that captures payments and keeps order status in sync with
payment-provider webhooks.

## Run

    pip install -e ".[dev]"
    uvicorn src.app:app --reload

## Test

    pytest