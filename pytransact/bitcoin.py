from __future__ import annotations

import asyncio
import time
from typing import Optional

from .authproxy import AuthServiceProxy
from .paymentrequest import PaymentRequest


class BitcoinClient:
    def __init__(
        self, 
        base_url: str, 
        port: int, 
        rpc_username: str, 
        rpc_password: str
        ) -> None:
        service_url: str = f"http://{rpc_username}:{rpc_password}@{base_url}:{port}"
        self._rpc_connection: AuthServiceProxy = AuthServiceProxy(service_url = service_url)
        self._loop: AbstractEventLoop = asyncio.get_running_loop()

    async def __aenter__(self) -> BitcoinClient:
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType]
        ) -> None:
        await self.release()

    def __del__(self) -> None:
        self._loop.create_task(self.release())

    def request_payment(
        self, 
        btc_quantity: int, 
        expiration: Optional[int] = 600, 
        confirmations: Optional[int] = 6,
        forward: Optional[ForwardPayment] = None
        ) -> PaymentRequest:
        new_payment_request: PaymentRequest = PaymentRequest(
            self._rpc_connection,
            btc_quantity, 
            expiration, 
            confirmations,
            forward
        )
        return new_payment_request

    async def release(self) -> None:
        if self._rpc_connection:
            await self._rpc_connection.close()
            self._rpc_connection = None