"""Etherscan API service for blockchain data."""

import asyncio
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel


class EtherscanService:
    """Service for interacting with Etherscan API."""

    BASE_URL = "https://api.etherscan.io/api"

    def __init__(self, api_key: str, rate_limit: int = 5):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self._client = httpx.AsyncClient()
        self._last_request_time = 0.0

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited request to Etherscan API."""
        # Basic rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        params["apikey"] = self.api_key

        try:
            response = await self._client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            self._last_request_time = asyncio.get_event_loop().time()

            if data.get("status") == "0":
                raise Exception(f"Etherscan API error: {data.get('message', 'Unknown error')}")

            return data
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error: {e}")

    async def get_balance(self, address: str) -> str:
        """Get ETH balance for an address."""
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest"
        }
        data = await self._make_request(params)
        # Convert wei to ETH
        wei_balance = int(data["result"])
        eth_balance = wei_balance / 10**18
        return f"{eth_balance:.6f}"

    async def get_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999, page: int = 1, offset: int = 10) -> List[Dict[str, Any]]:
        """Get transaction history for an address."""
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": "desc"
        }
        data = await self._make_request(params)
        return data["result"]

    async def get_token_transfers(self, address: str, contract_address: Optional[str] = None, page: int = 1, offset: int = 10) -> List[Dict[str, Any]]:
        """Get ERC20 token transfer events."""
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": page,
            "offset": offset,
            "sort": "desc"
        }

        if contract_address:
            params["contractaddress"] = contract_address

        data = await self._make_request(params)
        return data["result"]

    async def get_contract_abi(self, address: str) -> str:
        """Get contract ABI for a verified contract."""
        params = {
            "module": "contract",
            "action": "getabi",
            "address": address
        }
        data = await self._make_request(params)
        return data["result"]

    async def get_gas_prices(self) -> Dict[str, str]:
        """Get current gas prices."""
        params = {
            "module": "gastracker",
            "action": "gasoracle"
        }
        data = await self._make_request(params)
        result = data["result"]
        return {
            "safe": result["SafeGasPrice"],
            "standard": result["ProposeGasPrice"],
            "fast": result["FastGasPrice"]
        }

    async def get_ens_name(self, address: str) -> Optional[str]:
        """Resolve ENS name for an address (not directly supported by Etherscan)."""
        # Note: Etherscan doesn't have direct ENS resolution
        # This would typically require a separate ENS service
        return None

    async def close(self):
        """Clean up the HTTP client."""
        await self._client.aclose()