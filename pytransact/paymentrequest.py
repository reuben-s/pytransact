import asyncio
import time
from .authproxy import JSONRPCException

class PaymentRequest:
    def __init__(self, rpc_connection, btc_quantity, expiration):
        self._rpc_connection = rpc_connection
        self._btc_quantity = btc_quantity
        self._expiration = expiration
        self._expiry_time = time.time() + self._expiration
    
        self.address = None

    async def __aenter__(self):
        self.address = await self._rpc_connection.getnewaddress()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        return

    def __str__(self):
        return f"{'Address:':15} {self.address} {'BTC quantity:':15} {self._btc_quantity}\n{'Payment expiry:':15} {self._expiration} seconds\n{'TTL:':15} {self._expiry_time - time.time()} seconds"

    async def result(self):
        while self._expiry_time - time.time() > 0:
            
            await asyncio.sleep(1)

            try:
                transactions = await self._rpc_connection.listtransactions("*", 1000)

                filtered_transactions = [transaction for transaction in transactions if transaction["address"] == self.address]
                if not filtered_transactions:
                    print("No transactions for address")
                    continue

                incoming_transactions = [transaction for transaction in filtered_transactions if transaction["category"] == "receive"]
                if not incoming_transactions:
                    print("No incoming transactions for address")
                    continue

                total = sum([transaction["amount"] for transaction in incoming_transactions])

                if total >= self._btc_quantity:
                    return {"status": "success", "address_balance": total}
                print(f"{total} BTC at address. But not {self._btc_quantity}")

            except JSONRPCException as e:
                return {"status": "error", "message": str(e)}
        
        return False