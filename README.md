# pytransact
pytransact aims to simplify payment processing with Bitcoin in python by abstracting away Bitcoin Core RPC calls

## Installation

```
pip install pytransact
```

## Payment request example

```python
from pytransact import bitcoin
import asyncio

async def main():
    btc = bitcoin.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

    async with btc.request_payment(10) as request:
        print(f"Please transfer {request.quantity} BTC to {request.address}.")
        print(f"This request will expire at {request.expiration}!")
        result = await request.result()
        if result:
            print("Payment recieved!")
        else:
            print("Payment not recieved.")
```

Because the exchange rate fluctuates over time, payment request quantities pegged to fiat must expire to prevent spenders from delaying payment in the hope that satoshis will drop in price. With pytransact, a payment request automatically expires after 10 minutes, however this can be customised by setting the default parameter `expiration` to an integer value representing the amount of seconds before expiration.