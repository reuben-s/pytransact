from .authproxy import JSONRPCException
import asyncio

import time
import datetime

import logging

log = logging.getLogger("pytransact")

class PaymentRequest:
    def __init__(
        self, 
        rpc_connection, 
        quantity, 
        expiration, 
        confirmations
        ):

        self._rpc_connection = rpc_connection
        self._expiration = expiration
        self._expiry_time = time.time() + self._expiration
    
        self.quantity = quantity
        self.expiration = datetime.datetime.fromtimestamp(self._expiry_time).strftime("%Y-%m-%d %H:%M:%S")
        self.address = None
        self.required_confirmations = confirmations

    async def __aenter__(self):
        self.address = await self._rpc_connection.getnewaddress()
        log.debug(f"({self.address}) New payment request created.")
        return self

    async def __aexit__(self, 
        exc_type, 
        exc_val, 
        traceback
        ):

        return

    def __str__(self):
        return f"{'Address:':15} {self.address} {'BTC quantity:':15} {self.quantity}\n{'Payment expiry:':15} {self._expiration} seconds\n{'TTL:':15} {self._expiry_time - time.time()} seconds"

    async def result(self):
        while self._expiry_time - time.time() > 0:
            
            await asyncio.sleep(5)

            try:
                transactions = await self._rpc_connection.listtransactions("*", 1000)

                filtered_transactions = [transaction for transaction in transactions if transaction["address"] == self.address]
                if not filtered_transactions:
                    log.debug(f"({self.address}) No transactions found")
                    continue

                incoming_transactions = [transaction for transaction in filtered_transactions if transaction["category"] == "receive"]

                total = sum([transaction["amount"] for transaction in incoming_transactions])

                if total >= self.quantity:
                    log.debug(f"({self.address}) {total} recieved. Awaiting {self.required_confirmations} confirmations on each transaction.")
                    check_confirmations = await self._check_confirmations({ transaction["txid"]: False for transaction in incoming_transactions})
                    return {"status": "success", "address_balance": total}

                log.debug(f"({self.address}) {total} found. {total} < {self.quantity}, not enough funds.")

            except JSONRPCException as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Transaction Expired."}

    async def _check_confirmations(
        self, 
        transaction_ids
        ):
        
        while True:
            for transaction_id in transaction_ids:
                transaction_info = await self._rpc_connection.gettransaction(transaction_id)
                confirmations = transaction_info["confirmations"]
                if confirmations > self.required_confirmations:
                    transaction_ids[transaction_id] = True

                log.debug(f"({transaction_id}) Confirmations: {confirmations}")

            if all(transaction_id for transaction_id in transaction_ids.values()):
                log.debug(f"({self.address}) Payment recieved. Confirmation quota ({self.required_confirmations}) reached!")
                return

            await asyncio.sleep(5)