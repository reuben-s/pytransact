# pytransact
pytransact aims to simplify payment processing with Bitcoin in python by abstracting away Bitcoin Core RPC calls

It has the following features:

- Full async support
- Payment Request expiration to prevent fraud
- Bitcoin transaction confirmation checking

## Installation

- Ensure Bitcoin Core is installed and the RPC API is set up and enabled.
- Bitcoin Core can be installed here https://bitcoin.org/en/bitcoin-core/.

```
pip install pytransact
```

# Examples

### Payment request

```python
import asyncio
import pytransact

async def main():
    btc = pytransact.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

    async with btc.request_payment(10) as request:
        print(f"Please transfer {request.required_balance} BTC to {request.address}.")
        print(f"This request will expire at {request.expiration}!")
        result = await request.result()
        if result.successful:
            print(result.message)
        else:
            print(result.message)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

Because the exchange rate fluctuates over time, payment request quantities pegged to fiat must expire to prevent spenders from delaying payment in the hope that satoshis will drop in price. With pytransact, a payment request automatically expires after 10 minutes, however this can be customised by setting the `expiration` argument in the `request_payment` method to an integer value representing the amount of seconds before expiration.

Other `request_payment` arguments:
- `confirmations` Integer value of number of confirmations required before payment request is accepted.
- `forward` Takes `ForwardPayment` object.

### Payment forwarding

Payment forwarding automates the deduction of fees from payments, making it useful for product sales and simplifying payment processing.

```python
import asyncio
import pytransact

async def main():
    btc = pytransact.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

    f = pytransact.ForwardPayment("BTC Address", percentage=4)
    async with btc.request_payment(10, forward=f) as request:
        result = await request.result()
        if result.successful:
            print(result.message)
        else:
            print(result.message)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
`ForwardPayment` arguments:
- `address` BTC Address of where funds will be forwarded to.
- `percentage` Percentage of payment request which will be forwarded.
- `btc_quantity` Quantity of Bitcoin to be forwarded.

Note: Either `percentage` or `btc_quantity` must be set, however they cannot both be set at the same time.

### Refunds

You can refund payments by passing a return address into the `refund` method of the `PaymentResult` class.
```python
import asyncio
import pytransact

async def main():
    btc = pytransact.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

    f = pytransact.ForwardPayment("BTC Address", percentage=4)
    async with btc.request_payment(10, forward=f) as request:
        result = await request.result()
        tx_id = await result.refund("Return address")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
`refund` arguments:
- `address` Refund return address
- `confirmations` Number of blocks before transaction included in blockchain (Note: the lower the blocks, the higher the transaction fee).

### Logging transaction details

```python
import asyncio
import logging
import pytransact

logging.basicConfig()
logger = logging.getLogger("pytransact").setLevel(logging.DEBUG)

async def main():
    btc = pytransact.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
