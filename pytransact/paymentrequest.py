from __future__ import annotations

import time
import datetime
import logging
import asyncio
from typing import Optional, AsyncIterator

log = logging.getLogger("pytransact")

class PaymentResult:
    def __init__(
        self,
        address: str,
        message: str,
        successful: Optional[bool] = True
        ) -> None:
        self.address = address
        self.successful: bool = successful
        self.message: str = message

        log.debug(f"({self.address}) {self.message}")

class PaymentRequest:
    def __init__(
        self,
        rpc_connection: AuthServiceProxy,
        required_balance: int, 
        expiration: int, 
        confirmations: int
        ) -> None:
        self._rpc_connection: AuthServiceProxy = rpc_connection

        self._expiration: int = expiration
        self._expiry_time: int = time.time() + self._expiration
    
        self.required_balance: int = required_balance
        self.expiration: str = datetime.datetime.fromtimestamp(self._expiry_time).strftime("%Y-%m-%d %H:%M:%S")
        self.address: str = None
        self.required_confirmations: int = confirmations

    async def __aenter__(self) -> PaymentRequest:
        await self._generate_new_address()
        log.debug(f"({self.address}) New payment request created.")
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType]
        ) -> None:
        return

    def __await__(self) -> AsyncIterator[None]:
        return self._generate_new_address().__await__()

    async def _generate_new_address(self) -> PaymentRequest:
        self.address = await self._rpc_connection.getnewaddress()
        return self

    async def result(self) -> PaymentResult:
        while time.time() < self._expiry_time:
            balance: Decimal = await self._rpc_connection.getreceivedbyaddress(self.address, self.required_confirmations)
            if balance >= self.required_balance:
                return PaymentResult(
                    self.address,
                    f"Payment of {self.required_balance} BTC was recieved at address {self.address}"
                    )

            await asyncio.sleep(1)

        return PaymentResult(
            self.address,
            "Payment request expired.", 
            successful = False
            )
