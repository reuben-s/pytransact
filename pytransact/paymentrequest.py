from __future__ import annotations

import time
import datetime
import logging
import asyncio
from typing import (
    Optional,
    AsyncIterator,
    List,
    Dict,
    Any
)
import decimal

from .authproxy import AuthServiceProxy
from .forwardpayment import ForwardPayment

log = logging.getLogger("pytransact")

class PaymentResult:
    def __init__(
        self,
        address: str,
        message: str,
        rpc_connection: AuthServiceProxy,
        address_balance: float,
        requested_quantity: float,
        successful: Optional[bool] = True,
        ) -> None:
        self.address = address
        self.successful: Optional[bool] = successful
        self.message: str = message
        self.address_balance: float = address_balance
        self.requested_quantity: float = requested_quantity

        self._rpc_connection = rpc_connection

        log.debug(f"({self.address}) {self.message}")

    async def refund(
        self,
        refund_address: str,
        confirmations: Optional[int] = 6
        ) -> Any:
        if not self.successful:
            raise ValueError("Cannot give refund as the payment request was not successful!")

        # fee: dict[str, Any] = await self._rpc_connection.estimatesmartfee(confirmations)
        fee: decimal.Decimal() = 0.00001597
        change_address: str = await self._rpc_connection.getnewaddress()

        txid = await self._rpc_connection.sendtoaddress(refund_address, self.requested_quantity, "", "", True, False, confirmations)

        return txid

class PaymentRequest:
    def __init__(
        self,
        rpc_connection: AuthServiceProxy,
        required_balance: float, 
        expiration: int, 
        confirmations: int,
        forward: ForwardPayment
        ) -> None:
        self._rpc_connection: AuthServiceProxy = rpc_connection

        self._expiration: int = expiration
        self._expiry_time: int = time.time() + self._expiration
    
        self.required_balance: float = required_balance
        self.expiration: str = datetime.datetime.fromtimestamp(self._expiry_time).strftime("%Y-%m-%d %H:%M:%S")
        self.address: str = None
        self.required_confirmations: int = confirmations

        self._forward = forward

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
            balance: float = await self._rpc_connection.getreceivedbyaddress(self.address, self.required_confirmations)
            if balance >= self.required_balance:
                if self._forward:
                    await self._forward._forward_payment(
                        self._rpc_connection, 
                        balance, 
                        self.required_balance
                        )

                return PaymentResult(
                    self.address,
                    f"Payment of {self.required_balance} BTC was recieved at address {self.address}",
                    self._rpc_connection,
                    balance,
                    self.required_balance
                    )

            await asyncio.sleep(1)

        return PaymentResult(
            self.address,
            "Payment request expired.",
            self._rpc_connection,
            0,
            self.required_balance,
            successful = False,
            )
