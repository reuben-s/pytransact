from .authproxy import AuthServiceProxy
from .paymentrequest import PaymentRequest

import asyncio

class BitcoinClient:
    def __init__(self, base_url, port, rpc_username, rpc_password):
        self._loop = asyncio.get_running_loop()
        service_url = f"http://{rpc_username}:{rpc_password}@{base_url}:{port}"
        self._rpc_connection = AuthServiceProxy(service_url=service_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        await self.release()

    def __del__(self):
        self._loop.create_task(self.release())

    def request_payment(self, btc_quantity, expiration=600):
        return PaymentRequest(self._rpc_connection, btc_quantity, expiration)

    async def release(self):
        if self._rpc_connection:
            await self._rpc_connection.close()
            self._rpc_connection = None