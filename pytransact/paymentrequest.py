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
        required_balance, 
        expiration, 
        confirmations
        ):
  
        self._rpc_connection = rpc_connection

        self._expiration = expiration
        self._expiry_time = time.time() + self._expiration
    
        self.required_balance = required_balance
        self.balance = None
        self.expiration = datetime.datetime.fromtimestamp(self._expiry_time).strftime("%Y-%m-%d %H:%M:%S")
        self.address = None
        self.required_confirmations = confirmations

    async def __aenter__(
        self
        ):
        await self._generate_new_address()
        log.debug(f"({self.address}) New payment request created.")
        return self

    async def __aexit__(
        self, 
        exc_type, 
        exc_val, 
        traceback
        ):

        return

    def __await__(
        self
        ):
        return self._generate_new_address().__await__()

    async def _generate_new_address(self):
        self.address = await self._rpc_connection.getnewaddress()
        return self

    async def result(self):
        pass