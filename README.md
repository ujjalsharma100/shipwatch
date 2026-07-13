# shipwatch

This is the **demo repo from the [TracesHub demo video](https://www.youtube.com/watch?v=J4LPhV9wURg)** — a small payment-capture service with a mixed human + multi-agent commit history, so you can poke real line-level AI attribution yourself.

| | |
|---|---|
| ▶ 3-min demo | [YouTube](https://www.youtube.com/watch?v=J4LPhV9wURg) |
| Live attribution view | [TracesHub project](https://app.traceshub.com/p/ujjalsharma100/shipwatch) |
| CLI | [`agent-trace-cli`](https://github.com/ujjalsharma100/agent-trace-cli) |
| Hosted hub | [traceshub.com](https://traceshub.com) |

A small service that captures payments and keeps order status in sync with
payment-provider webhooks.

## Run

    pip install -e ".[dev]"
    uvicorn src.app:app --reload

## Test

    pytest
