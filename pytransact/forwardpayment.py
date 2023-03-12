from __future__ import annotations

class ForwardPayment:
    def __init__(
        self,
        address: str,
        btc_quantity: Optional[int] = None,
        percentage: Optional[int] = None
        ) -> None:
        if btc_quantity and percentage:
            raise ValueError("Both a BTC Quantity and Percentage cannot be specified.")
        elif not btc_quantity and not percentage:
            raise ValueError("You must specify a BTC Quantity or a Percentage to be forwarded.")

        if percentage and (percentage > 100 or percentage < 0):
            raise ValueError(f"'{percentage}' Not a valid percentage.")

        self.address: str = address
        
        self.btc_quantity: int = btc_quantity
        self.percentage: int = percentage / 100 if percentage else percentage

    async def _forward_payment(
        self, 
        rpc_connection: AuthServiceProxy,
        balance: int,
        initial_quantity: int
        ) -> bool:
        forward_quantity: int = initial_quantity * self.percentage if self.percentage else self.btc_quantity

        if forward_quantity > balance:
            raise ValueError(f"Insufficient funds to forward {self.btc_quantity} to {self.address}")

        result: str = await rpc_connection.sendtoaddress(
            self.address,
            forward_quantity
        )

        return result