# pytransact
pytransact aims to simplify payment processing with Bitcoin in python by abstracting away Bitcoin Core RPC calls

## Installation

```
pip install pytransact
```

## Request payment example

```python
from pytransact import bitcoin
import asyncio

async def main():
    btc = bitcoin.BitcoinClient("127.0.0.1", port=8332, rpc_username=username, rpc_password=password)

    async with btc.request_payment(10) as request:
        print(f"Please transfer 10 BTC to {request.address}")
        result = await request.result()
        if result:
            print("Payment recieved!")
        else:
            print("Payment not recieved.")
```
