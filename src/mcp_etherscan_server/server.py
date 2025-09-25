"""MCP server implementation for Etherscan blockchain data."""

import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .etherscan_service import EtherscanService
from .whale_detector import WhaleDetector, WhaleClass

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
whale_detector = WhaleDetector(etherscan)


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


@mcp.tool()
async def analyze_whale(address: str) -> str:
    """Comprehensive whale analysis of an Ethereum address.

    Analyzes an address to determine whale classification, activity patterns,
    and risk metrics based on balance, transaction history, and behavior.

    Args:
        address: Ethereum address to analyze for whale characteristics

    Returns:
        Detailed whale analysis including classification, metrics, and risk assessment
    """
    try:
        metrics = await whale_detector.analyze_whale(address)

        # Format whale class
        whale_class_names = {
            WhaleClass.MEGA_WHALE: "🐋 MEGA WHALE (>10,000 ETH)",
            WhaleClass.LARGE_WHALE: "🐋 Large Whale (1,000-10,000 ETH)",
            WhaleClass.MEDIUM_WHALE: "🐟 Medium Whale (100-1,000 ETH)",
            WhaleClass.SMALL_WHALE: "🦐 Small Whale (10-100 ETH)",
            WhaleClass.SHRIMP: "🦐 Shrimp (<10 ETH)"
        }

        result = f"WHALE ANALYSIS: {address}\n"
        result += "=" * 50 + "\n\n"

        # Classification and balance
        result += f"Classification: {whale_class_names[metrics.whale_class]}\n"
        result += f"ETH Balance: {metrics.eth_balance:.6f} ETH\n\n"

        # Known whale check
        label = whale_detector.get_whale_label(address)
        if label:
            result += f"🏷️  Known Entity: {label}\n"

        exchange = whale_detector.is_exchange_address(address)
        if exchange:
            result += f"🏦 Exchange: {exchange}\n"

        result += "\n"

        # Transaction metrics
        result += "ACTIVITY METRICS:\n"
        result += f"Total Transactions: {metrics.total_transactions:,}\n"
        result += f"Large Transactions (>50 ETH): {metrics.large_transactions:,}\n"
        result += f"Average Transaction: {metrics.avg_transaction_value:.6f} ETH\n"
        result += f"Largest Transaction: {metrics.max_transaction_value:.6f} ETH\n\n"

        # Scores and analysis
        result += "ANALYSIS SCORES:\n"
        result += f"Activity Score: {metrics.activity_score:.1f}/100 "
        if metrics.activity_score > 70:
            result += "(Very Active 🔥)\n"
        elif metrics.activity_score > 40:
            result += "(Active ⚡)\n"
        else:
            result += "(Inactive 💤)\n"

        result += f"Risk Score: {metrics.risk_score:.1f}/100 "
        if metrics.risk_score > 70:
            result += "(High Risk ⚠️)\n"
        elif metrics.risk_score > 40:
            result += "(Medium Risk ⚡)\n"
        else:
            result += "(Low Risk ✅)\n"

        result += f"Token Diversity: {metrics.token_diversity} different tokens\n\n"

        # Timestamps
        if metrics.first_seen:
            first_seen = metrics.first_seen
            result += f"First Activity: {first_seen}\n"
        if metrics.last_activity:
            last_activity = metrics.last_activity
            result += f"Last Activity: {last_activity}\n"

        return result

    except Exception as e:
        return f"Error analyzing whale: {str(e)}"


@mcp.tool()
async def detect_whale_class(address: str) -> str:
    """Quick whale classification based on ETH balance.

    Provides a simple classification of an address as whale, dolphin, or shrimp
    based solely on their current ETH balance.

    Args:
        address: Ethereum address to classify

    Returns:
        Whale classification with balance and emoji
    """
    try:
        balance_str = await etherscan.get_balance(address)
        eth_balance = float(balance_str)
        whale_class = whale_detector.classify_whale(eth_balance)

        class_info = {
            WhaleClass.MEGA_WHALE: ("🐋 MEGA WHALE", "Institutional-level holdings"),
            WhaleClass.LARGE_WHALE: ("🐋 Large Whale", "Major market participant"),
            WhaleClass.MEDIUM_WHALE: ("🐟 Medium Whale", "Significant holder"),
            WhaleClass.SMALL_WHALE: ("🦐 Small Whale", "Notable position"),
            WhaleClass.SHRIMP: ("🦐 Shrimp", "Retail holder")
        }

        emoji_name, description = class_info[whale_class]

        result = f"WHALE CLASSIFICATION: {address}\n\n"
        result += f"Class: {emoji_name}\n"
        result += f"Balance: {eth_balance:.6f} ETH\n"
        result += f"Description: {description}\n"

        # Add some context about their position
        if whale_class in [WhaleClass.MEGA_WHALE, WhaleClass.LARGE_WHALE]:
            result += "\n⚠️  This address holds significant ETH - movements may impact market"
        elif whale_class == WhaleClass.MEDIUM_WHALE:
            result += "\n📊 Moderate holder - worth monitoring for large movements"

        return result

    except Exception as e:
        return f"Error detecting whale class: {str(e)}"


@mcp.tool()
async def compare_whales(addresses: str) -> str:
    """Compare multiple addresses for whale analysis.

    Analyzes multiple Ethereum addresses and ranks them by whale size,
    providing comparative metrics and insights.

    Args:
        addresses: Comma-separated list of Ethereum addresses to compare

    Returns:
        Comparative analysis of all addresses ranked by whale size
    """
    try:
        # Parse addresses
        addr_list = [addr.strip() for addr in addresses.split(',') if addr.strip()]

        if len(addr_list) > 10:
            return "Error: Maximum 10 addresses allowed for comparison"

        if len(addr_list) < 2:
            return "Error: At least 2 addresses required for comparison"

        # Analyze all whales
        whale_metrics = await whale_detector.compare_whales(addr_list)

        if not whale_metrics:
            return "Error: Could not analyze any of the provided addresses"

        result = f"WHALE COMPARISON ({len(whale_metrics)} addresses)\n"
        result += "=" * 60 + "\n\n"

        for i, metrics in enumerate(whale_metrics, 1):
            # Whale class emoji
            class_emoji = {
                WhaleClass.MEGA_WHALE: "🐋",
                WhaleClass.LARGE_WHALE: "🐋",
                WhaleClass.MEDIUM_WHALE: "🐟",
                WhaleClass.SMALL_WHALE: "🦐",
                WhaleClass.SHRIMP: "🦐"
            }

            result += f"{i}. {class_emoji[metrics.whale_class]} {metrics.address[:10]}...{metrics.address[-6:]}\n"
            result += f"   Balance: {metrics.eth_balance:.2f} ETH | "
            result += f"Class: {metrics.whale_class.value.replace('_', ' ').title()}\n"
            result += f"   Activity: {metrics.activity_score:.0f}/100 | "
            result += f"Risk: {metrics.risk_score:.0f}/100 | "
            result += f"Tokens: {metrics.token_diversity}\n"

            # Add known label if available
            label = whale_detector.get_whale_label(metrics.address)
            if label:
                result += f"   🏷️  Known as: {label}\n"

            result += "\n"

        # Summary stats
        total_eth = sum(m.eth_balance for m in whale_metrics)
        avg_activity = sum(m.activity_score for m in whale_metrics) / len(whale_metrics)

        result += f"SUMMARY:\n"
        result += f"Total ETH: {total_eth:.2f} ETH\n"
        result += f"Average Activity Score: {avg_activity:.1f}/100\n"
        result += f"Largest Whale: {whale_metrics[0].eth_balance:.2f} ETH\n"

        return result

    except Exception as e:
        return f"Error comparing whales: {str(e)}"


@mcp.tool()
async def discover_whale_movements(min_eth_value: float = 100.0) -> str:
    """Discover recent large whale movements and transactions.

    Scans recent transactions from known whale addresses and exchanges to find
    significant ETH movements that may indicate whale activity.

    Args:
        min_eth_value: Minimum ETH value to consider as whale movement (default: 100)

    Returns:
        List of recent whale movements with sender/receiver classification and significance
    """
    try:
        movements = await whale_detector.discover_whale_movements(min_eth_value)

        if not movements:
            return f"No whale movements found above {min_eth_value} ETH"

        result = f"🐋 RECENT WHALE MOVEMENTS (>{min_eth_value} ETH)\n"
        result += "=" * 60 + "\n\n"

        for i, movement in enumerate(movements[:15], 1):  # Show top 15
            significance = whale_detector.get_movement_significance(movement['value_eth'])

            result += f"{i}. {significance}\n"
            result += f"Amount: {movement['value_eth']:.2f} ETH\n"
            result += f"From: {movement['from_address'][:10]}...{movement['from_address'][-6:]}"

            # Add from labels/exchanges
            if movement['from_label']:
                result += f" ({movement['from_label']})"
            elif movement['from_exchange']:
                result += f" ({movement['from_exchange']} Exchange)"
            else:
                result += f" [{movement['from_whale_class'].replace('_', ' ').title()}]"

            result += f"\nTo: {movement['to_address'][:10]}...{movement['to_address'][-6:]}"

            # Add to labels/exchanges
            if movement['to_label']:
                result += f" ({movement['to_label']})"
            elif movement['to_exchange']:
                result += f" ({movement['to_exchange']} Exchange)"
            else:
                result += f" [{movement['to_whale_class'].replace('_', ' ').title()}]"

            result += f"\nTx Hash: {movement['hash']}\n"
            result += f"Block: {movement['block_number']}\n\n"

        result += f"📊 SUMMARY:\n"
        result += f"Total movements found: {len(movements)}\n"
        result += f"Total value: {sum(m['value_eth'] for m in movements):.2f} ETH\n"
        result += f"Largest movement: {movements[0]['value_eth']:.2f} ETH\n"

        return result

    except Exception as e:
        return f"Error discovering whale movements: {str(e)}"


@mcp.tool()
async def discover_top_whales(min_balance: float = 1000.0) -> str:
    """Discover top whale addresses by analyzing transaction networks.

    Finds whale addresses by analyzing participants in large transactions,
    starting from known whales and exchanges to discover their counterparties.

    Args:
        min_balance: Minimum ETH balance to qualify as discovered whale (default: 1000)

    Returns:
        List of discovered whale addresses ranked by balance with classifications
    """
    try:
        whales = await whale_detector.discover_top_whales(min_balance)

        if not whales:
            return f"No whales discovered with balance >{min_balance} ETH"

        result = f"🐋 DISCOVERED TOP WHALES (>{min_balance} ETH)\n"
        result += "=" * 60 + "\n\n"

        for i, whale in enumerate(whales, 1):
            # Whale emoji based on class
            class_emoji = {
                'mega_whale': '🐋',
                'large_whale': '🐋',
                'medium_whale': '🐟',
                'small_whale': '🦐',
                'shrimp': '🦐'
            }

            emoji = class_emoji.get(whale['whale_class'], '🐟')

            result += f"{i}. {emoji} {whale['address'][:10]}...{whale['address'][-6:]}\n"
            result += f"   Balance: {whale['eth_balance']:.2f} ETH\n"
            result += f"   Class: {whale['whale_class'].replace('_', ' ').title()}\n"

            if whale['label']:
                result += f"   🏷️  Known as: {whale['label']}\n"
            elif whale['exchange']:
                result += f"   🏦 Exchange: {whale['exchange']}\n"

            result += f"   📊 Discovery: {whale['discovery_method'].replace('_', ' ').title()}\n\n"

        # Summary statistics
        total_eth = sum(w['eth_balance'] for w in whales)
        mega_whales = len([w for w in whales if w['whale_class'] == 'mega_whale'])
        large_whales = len([w for w in whales if w['whale_class'] == 'large_whale'])

        result += f"📊 DISCOVERY SUMMARY:\n"
        result += f"Whales discovered: {len(whales)}\n"
        result += f"Total ETH discovered: {total_eth:.2f} ETH\n"
        result += f"Mega whales (>10K): {mega_whales}\n"
        result += f"Large whales (1K-10K): {large_whales}\n"
        result += f"Largest whale: {whales[0]['eth_balance']:.2f} ETH\n"

        return result

    except Exception as e:
        return f"Error discovering top whales: {str(e)}"


@mcp.tool()
async def track_exchange_whales(min_amount: float = 500.0) -> str:
    """Track whale deposits and withdrawals from major exchanges.

    Monitors large ETH movements to/from known exchange addresses to identify
    whale trading activity and potential market impact movements.

    Args:
        min_amount: Minimum ETH amount to track (default: 500)

    Returns:
        List of whale exchange movements with deposit/withdrawal classification
    """
    try:
        movements = await whale_detector.track_exchange_whales(min_amount)

        if not movements:
            return f"No exchange whale movements found above {min_amount} ETH"

        result = f"🏦 EXCHANGE WHALE TRACKING (>{min_amount} ETH)\n"
        result += "=" * 60 + "\n\n"

        # Group by movement type
        deposits = [m for m in movements if m['movement_type'] == 'deposit']
        withdrawals = [m for m in movements if m['movement_type'] == 'withdrawal']

        # Show deposits
        if deposits:
            result += "📥 WHALE DEPOSITS (Potential Selling Pressure):\n\n"
            for i, movement in enumerate(deposits[:8], 1):
                significance = whale_detector.get_movement_significance(movement['value_eth'])

                result += f"{i}. {significance}\n"
                result += f"   Amount: {movement['value_eth']:.2f} ETH → {movement['exchange']}\n"
                result += f"   Whale: {movement['whale_address'][:10]}...{movement['whale_address'][-6:]}"

                if movement['whale_label']:
                    result += f" ({movement['whale_label']})"
                else:
                    result += f" [{movement['whale_class'].replace('_', ' ').title()}]"

                result += f"\n   Tx: {movement['hash']}\n\n"

        # Show withdrawals
        if withdrawals:
            result += "📤 WHALE WITHDRAWALS (Potential Accumulation):\n\n"
            for i, movement in enumerate(withdrawals[:8], 1):
                significance = whale_detector.get_movement_significance(movement['value_eth'])

                result += f"{i}. {significance}\n"
                result += f"   Amount: {movement['value_eth']:.2f} ETH ← {movement['exchange']}\n"
                result += f"   Whale: {movement['whale_address'][:10]}...{movement['whale_address'][-6:]}"

                if movement['whale_label']:
                    result += f" ({movement['whale_label']})"
                else:
                    result += f" [{movement['whale_class'].replace('_', ' ').title()}]"

                result += f"\n   Tx: {movement['hash']}\n\n"

        # Summary analysis
        total_deposits = sum(m['value_eth'] for m in deposits)
        total_withdrawals = sum(m['value_eth'] for m in withdrawals)
        net_flow = total_withdrawals - total_deposits

        result += "📊 MARKET IMPACT ANALYSIS:\n"
        result += f"Total Deposits: {total_deposits:.2f} ETH (Selling pressure)\n"
        result += f"Total Withdrawals: {total_withdrawals:.2f} ETH (Accumulation)\n"
        result += f"Net Flow: {net_flow:.2f} ETH "

        if net_flow > 0:
            result += "(📈 Net accumulation - Bullish signal)\n"
        elif net_flow < 0:
            result += "(📉 Net selling - Bearish signal)\n"
        else:
            result += "(⚖️ Balanced flow)\n"

        result += f"Active exchanges: {len(set(m['exchange'] for m in movements))}\n"

        return result

    except Exception as e:
        return f"Error tracking exchange whales: {str(e)}"