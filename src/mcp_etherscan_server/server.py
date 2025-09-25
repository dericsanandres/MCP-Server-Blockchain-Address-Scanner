"""MCP server implementation for Etherscan blockchain data."""

import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .etherscan_service import EtherscanService

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Etherscan Blockchain Scanner")

# Initialize Etherscan service
api_key = os.getenv("ETHERSCAN_API_KEY")
if not api_key:
    raise ValueError("ETHERSCAN_API_KEY environment variable is required")

rate_limit = int(os.getenv("RATE_LIMIT", "5"))
etherscan = EtherscanService(api_key, rate_limit)


@mcp.tool()
async def check_balance(address: str) -> str:
    """Get ETH balance for an Ethereum address.

    Args:
        address: Ethereum address to check balance for

    Returns:
        ETH balance as a formatted string
    """
    try:
        balance = await etherscan.get_balance(address)
        return f"ETH balance for {address}: {balance} ETH"
    except Exception as e:
        return f"Error getting balance: {str(e)}"


@mcp.tool()
async def get_transactions(
    address: str,
    start_block: int = 0,
    end_block: int = 99999999,
    page: int = 1,
    offset: int = 10
) -> str:
    """Get transaction history for an Ethereum address.

    Args:
        address: Ethereum address to get transactions for
        start_block: Starting block number (default: 0)
        end_block: Ending block number (default: 99999999)
        page: Page number (default: 1)
        offset: Number of transactions to return (default: 10)

    Returns:
        Formatted transaction history
    """
    try:
        transactions = await etherscan.get_transactions(
            address, start_block, end_block, page, offset
        )

        if not transactions:
            return "No transactions found"

        result = f"Found {len(transactions)} transactions for {address}:\n\n"
        for tx in transactions[:5]:  # Show first 5
            result += f"Hash: {tx['hash']}\n"
            result += f"From: {tx['from']}\n"
            result += f"To: {tx['to']}\n"
            result += f"Value: {int(tx['value']) / 10**18:.6f} ETH\n"
            result += f"Gas Used: {tx['gasUsed']}\n"
            result += f"Block: {tx['blockNumber']}\n\n"

        return result
    except Exception as e:
        return f"Error getting transactions: {str(e)}"


@mcp.tool()
async def get_token_transfers(
    address: str,
    contract_address: Optional[str] = None,
    page: int = 1,
    offset: int = 10
) -> str:
    """Get ERC20 token transfer events for an address.

    Args:
        address: Ethereum address to get token transfers for
        contract_address: Optional specific token contract address
        page: Page number (default: 1)
        offset: Number of transfers to return (default: 10)

    Returns:
        Formatted token transfer history
    """
    try:
        transfers = await etherscan.get_token_transfers(
            address, contract_address, page, offset
        )

        if not transfers:
            return "No token transfers found"

        result = f"Found {len(transfers)} token transfers for {address}:\n\n"
        for transfer in transfers[:5]:  # Show first 5
            result += f"Hash: {transfer['hash']}\n"
            result += f"Token: {transfer['tokenName']} ({transfer['tokenSymbol']})\n"
            result += f"From: {transfer['from']}\n"
            result += f"To: {transfer['to']}\n"
            decimals = int(transfer['tokenDecimal'])
            value = int(transfer['value']) / (10 ** decimals)
            result += f"Value: {value:.6f} {transfer['tokenSymbol']}\n"
            result += f"Block: {transfer['blockNumber']}\n\n"

        return result
    except Exception as e:
        return f"Error getting token transfers: {str(e)}"


@mcp.tool()
async def get_contract_abi(address: str) -> str:
    """Get ABI for a verified smart contract.

    Args:
        address: Contract address to get ABI for

    Returns:
        Contract ABI as JSON string
    """
    try:
        abi = await etherscan.get_contract_abi(address)
        return f"Contract ABI for {address}:\n\n{abi}"
    except Exception as e:
        return f"Error getting contract ABI: {str(e)}"


@mcp.tool()
async def get_gas_prices() -> str:
    """Get current gas prices on Ethereum network.

    Returns:
        Current gas prices (safe, standard, fast) in Gwei
    """
    try:
        gas_prices = await etherscan.get_gas_prices()
        result = "Current gas prices (in Gwei):\n"
        result += f"Safe: {gas_prices['safe']} Gwei\n"
        result += f"Standard: {gas_prices['standard']} Gwei\n"
        result += f"Fast: {gas_prices['fast']} Gwei"
        return result
    except Exception as e:
        return f"Error getting gas prices: {str(e)}"