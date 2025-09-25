"""Whale detection and analysis service."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .etherscan_service import EtherscanService


class WhaleClass(Enum):
    """Whale classification levels."""
    SHRIMP = "shrimp"          # < 10 ETH
    SMALL_WHALE = "small_whale"     # 10-100 ETH
    MEDIUM_WHALE = "medium_whale"   # 100-1,000 ETH
    LARGE_WHALE = "large_whale"     # 1,000-10,000 ETH
    MEGA_WHALE = "mega_whale"       # > 10,000 ETH


@dataclass
class WhaleMetrics:
    """Metrics for whale analysis."""
    address: str
    eth_balance: float
    whale_class: WhaleClass
    total_transactions: int
    large_transactions: int  # > 50 ETH
    avg_transaction_value: float
    max_transaction_value: float
    first_seen: Optional[str]
    last_activity: Optional[str]
    activity_score: float  # 0-100
    risk_score: float      # 0-100
    token_diversity: int   # Number of different tokens held


@dataclass
class WhaleMovement:
    """Large transaction movement data."""
    tx_hash: str
    from_addr: str
    to_addr: str
    value_eth: float
    timestamp: str
    block_number: str
    whale_class_from: WhaleClass
    whale_class_to: WhaleClass
    movement_type: str  # "accumulation", "distribution", "exchange_deposit", etc.


class WhaleDetector:
    """Advanced whale detection and analysis service."""

    # Known whale addresses (exchanges, foundations, etc.)
    KNOWN_WHALES = {
        "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae": "Ethereum Foundation",
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH Contract",
        "0xa090e606e30bd747d4e6245a1517ebe430f0057e": "Gemini Exchange",
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance Hot Wallet",
        # Add more known addresses
    }

    # Exchange addresses for movement classification
    EXCHANGE_ADDRESSES = {
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
        "0xa090e606e30bd747d4e6245a1517ebe430f0057e": "Gemini",
        "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKEx",
        "0x564286362092d8e7936f0549571a803b203aaced": "FTX",
        # Add more exchange addresses
    }

    def __init__(self, etherscan: EtherscanService):
        self.etherscan = etherscan

    def classify_whale(self, eth_balance: float) -> WhaleClass:
        """Classify address based on ETH balance."""
        if eth_balance >= 10000:
            return WhaleClass.MEGA_WHALE
        elif eth_balance >= 1000:
            return WhaleClass.LARGE_WHALE
        elif eth_balance >= 100:
            return WhaleClass.MEDIUM_WHALE
        elif eth_balance >= 10:
            return WhaleClass.SMALL_WHALE
        else:
            return WhaleClass.SHRIMP

    async def analyze_whale(self, address: str) -> WhaleMetrics:
        """Comprehensive whale analysis of an address."""
        try:
            # Get basic balance
            balance_str = await self.etherscan.get_balance(address)
            eth_balance = float(balance_str)
            whale_class = self.classify_whale(eth_balance)

            # Get transaction history for analysis
            transactions = await self.etherscan.get_transactions(address, page=1, offset=100)

            if not transactions:
                return WhaleMetrics(
                    address=address,
                    eth_balance=eth_balance,
                    whale_class=whale_class,
                    total_transactions=0,
                    large_transactions=0,
                    avg_transaction_value=0.0,
                    max_transaction_value=0.0,
                    first_seen=None,
                    last_activity=None,
                    activity_score=0.0,
                    risk_score=0.0,
                    token_diversity=0
                )

            # Analyze transactions
            total_transactions = len(transactions)
            transaction_values = []
            large_transactions = 0

            for tx in transactions:
                value_eth = int(tx['value']) / 10**18
                transaction_values.append(value_eth)
                if value_eth > 50:  # Large transaction threshold
                    large_transactions += 1

            avg_transaction_value = sum(transaction_values) / len(transaction_values) if transaction_values else 0
            max_transaction_value = max(transaction_values) if transaction_values else 0

            # Time analysis
            first_seen = transactions[-1]['timeStamp'] if transactions else None
            last_activity = transactions[0]['timeStamp'] if transactions else None

            # Calculate activity score (based on recent activity)
            activity_score = self._calculate_activity_score(transactions)

            # Calculate risk score (based on various factors)
            risk_score = self._calculate_risk_score(address, transactions, eth_balance)

            # Get token diversity (simplified - would need token transfer analysis)
            token_transfers = await self.etherscan.get_token_transfers(address, page=1, offset=50)
            unique_tokens = set()
            for transfer in token_transfers:
                unique_tokens.add(transfer.get('contractAddress', ''))
            token_diversity = len(unique_tokens)

            return WhaleMetrics(
                address=address,
                eth_balance=eth_balance,
                whale_class=whale_class,
                total_transactions=total_transactions,
                large_transactions=large_transactions,
                avg_transaction_value=avg_transaction_value,
                max_transaction_value=max_transaction_value,
                first_seen=first_seen,
                last_activity=last_activity,
                activity_score=activity_score,
                risk_score=risk_score,
                token_diversity=token_diversity
            )

        except Exception as e:
            raise Exception(f"Error analyzing whale: {str(e)}")

    def _calculate_activity_score(self, transactions: List[Dict]) -> float:
        """Calculate activity score based on recent transactions."""
        if not transactions:
            return 0.0

        now = datetime.now()
        recent_count = 0

        for tx in transactions[:20]:  # Check last 20 transactions
            tx_time = datetime.fromtimestamp(int(tx['timeStamp']))
            if (now - tx_time).days <= 30:  # Last 30 days
                recent_count += 1

        return min(100.0, (recent_count / 20) * 100)

    def _calculate_risk_score(self, address: str, transactions: List[Dict], balance: float) -> float:
        """Calculate risk score based on various factors."""
        risk_factors = []

        # High balance risk
        if balance > 1000:
            risk_factors.append(30)

        # Known whale/exchange bonus (lower risk)
        if address.lower() in [addr.lower() for addr in self.KNOWN_WHALES.keys()]:
            risk_factors.append(-20)

        # Transaction pattern analysis
        if transactions:
            large_tx_ratio = sum(1 for tx in transactions if int(tx['value']) / 10**18 > 100) / len(transactions)
            if large_tx_ratio > 0.5:
                risk_factors.append(25)

        # New address risk
        if transactions:
            first_tx_time = datetime.fromtimestamp(int(transactions[-1]['timeStamp']))
            if (datetime.now() - first_tx_time).days < 30:
                risk_factors.append(40)

        total_risk = sum(risk_factors)
        return max(0.0, min(100.0, total_risk))

    async def detect_whale_movements(self, min_value_eth: float = 100.0, hours_back: int = 24) -> List[WhaleMovement]:
        """Detect large whale movements in recent transactions."""
        # This would require monitoring multiple known whale addresses
        # For now, return empty list - would need a more comprehensive implementation
        return []

    def get_whale_label(self, address: str) -> Optional[str]:
        """Get label for known whale addresses."""
        return self.KNOWN_WHALES.get(address.lower())

    def is_exchange_address(self, address: str) -> Optional[str]:
        """Check if address is a known exchange."""
        return self.EXCHANGE_ADDRESSES.get(address.lower())

    async def compare_whales(self, addresses: List[str]) -> List[WhaleMetrics]:
        """Compare multiple whale addresses."""
        whale_metrics = []

        for address in addresses:
            try:
                metrics = await self.analyze_whale(address)
                whale_metrics.append(metrics)
                # Rate limiting
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"Error analyzing {address}: {e}")
                continue

        # Sort by ETH balance descending
        whale_metrics.sort(key=lambda x: x.eth_balance, reverse=True)
        return whale_metrics

    async def discover_whale_movements(self, min_eth_value: float = 100.0, hours_back: int = 24) -> List[Dict]:
        """Discover recent whale movements by analyzing large transactions.

        Since Etherscan doesn't provide a direct "large transactions" endpoint,
        we'll analyze transactions from known whale addresses and high-activity addresses.
        """
        whale_movements = []

        # Known whale addresses to monitor
        monitor_addresses = list(self.KNOWN_WHALES.keys()) + list(self.EXCHANGE_ADDRESSES.keys())

        for address in monitor_addresses[:10]:  # Limit to avoid rate limiting
            try:
                transactions = await self.etherscan.get_transactions(address, page=1, offset=20)

                for tx in transactions:
                    value_eth = int(tx['value']) / 10**18

                    if value_eth >= min_eth_value:
                        # Analyze both sender and receiver
                        from_whale_class = await self._get_whale_class_cached(tx['from'])
                        to_whale_class = await self._get_whale_class_cached(tx['to'])

                        movement = {
                            'hash': tx['hash'],
                            'from_address': tx['from'],
                            'to_address': tx['to'],
                            'value_eth': value_eth,
                            'timestamp': tx['timeStamp'],
                            'block_number': tx['blockNumber'],
                            'from_whale_class': from_whale_class.value if from_whale_class else 'unknown',
                            'to_whale_class': to_whale_class.value if to_whale_class else 'unknown',
                            'from_label': self.get_whale_label(tx['from']),
                            'to_label': self.get_whale_label(tx['to']),
                            'from_exchange': self.is_exchange_address(tx['from']),
                            'to_exchange': self.is_exchange_address(tx['to'])
                        }

                        whale_movements.append(movement)

                # Rate limiting
                await asyncio.sleep(0.3)

            except Exception as e:
                continue

        # Sort by value descending
        whale_movements.sort(key=lambda x: x['value_eth'], reverse=True)
        return whale_movements[:50]  # Return top 50 movements

    async def _get_whale_class_cached(self, address: str) -> Optional[WhaleClass]:
        """Get whale class with basic caching to avoid repeated API calls."""
        try:
            balance_str = await self.etherscan.get_balance(address)
            eth_balance = float(balance_str)
            return self.classify_whale(eth_balance)
        except:
            return None

    async def discover_top_whales(self, min_balance: float = 1000.0) -> List[Dict]:
        """Discover top whales by analyzing high-value transaction participants.

        This finds whale addresses by looking at participants in large transactions.
        """
        discovered_whales = {}

        # Start with known addresses and analyze their transaction partners
        seed_addresses = list(self.KNOWN_WHALES.keys())[:5]

        for seed_address in seed_addresses:
            try:
                transactions = await self.etherscan.get_transactions(seed_address, page=1, offset=50)

                # Collect unique addresses from large transactions
                for tx in transactions:
                    value_eth = int(tx['value']) / 10**18

                    if value_eth >= 50:  # Focus on significant transactions
                        for addr in [tx['from'], tx['to']]:
                            if addr.lower() not in discovered_whales:
                                discovered_whales[addr.lower()] = addr

                await asyncio.sleep(0.3)

            except Exception as e:
                continue

        # Analyze discovered addresses
        whale_list = []
        for address in list(discovered_whales.values())[:30]:  # Limit analysis
            try:
                balance_str = await self.etherscan.get_balance(address)
                eth_balance = float(balance_str)

                if eth_balance >= min_balance:
                    whale_class = self.classify_whale(eth_balance)

                    whale_info = {
                        'address': address,
                        'eth_balance': eth_balance,
                        'whale_class': whale_class.value,
                        'label': self.get_whale_label(address),
                        'exchange': self.is_exchange_address(address),
                        'discovery_method': 'transaction_analysis'
                    }

                    whale_list.append(whale_info)

                await asyncio.sleep(0.2)

            except Exception as e:
                continue

        # Sort by balance descending
        whale_list.sort(key=lambda x: x['eth_balance'], reverse=True)
        return whale_list[:20]  # Return top 20 discovered whales

    async def track_exchange_whales(self, min_amount: float = 500.0) -> List[Dict]:
        """Track whale movements to/from exchanges."""
        exchange_movements = []

        # Monitor known exchange addresses
        exchange_addresses = list(self.EXCHANGE_ADDRESSES.keys())

        for exchange_addr in exchange_addresses[:5]:  # Limit to avoid rate limits
            try:
                exchange_name = self.EXCHANGE_ADDRESSES[exchange_addr]
                transactions = await self.etherscan.get_transactions(exchange_addr, page=1, offset=30)

                for tx in transactions:
                    value_eth = int(tx['value']) / 10**18

                    if value_eth >= min_amount:
                        # Determine if it's deposit or withdrawal
                        if tx['to'].lower() == exchange_addr.lower():
                            movement_type = "deposit"
                            whale_address = tx['from']
                        else:
                            movement_type = "withdrawal"
                            whale_address = tx['to']

                        # Get whale classification
                        whale_class = await self._get_whale_class_cached(whale_address)

                        movement = {
                            'hash': tx['hash'],
                            'exchange': exchange_name,
                            'exchange_address': exchange_addr,
                            'whale_address': whale_address,
                            'movement_type': movement_type,
                            'value_eth': value_eth,
                            'whale_class': whale_class.value if whale_class else 'unknown',
                            'whale_label': self.get_whale_label(whale_address),
                            'timestamp': tx['timeStamp'],
                            'block_number': tx['blockNumber']
                        }

                        exchange_movements.append(movement)

                await asyncio.sleep(0.3)

            except Exception as e:
                continue

        # Sort by value descending
        exchange_movements.sort(key=lambda x: x['value_eth'], reverse=True)
        return exchange_movements[:30]  # Return top 30 movements

    def get_movement_significance(self, value_eth: float) -> str:
        """Get significance level of a movement."""
        if value_eth >= 10000:
            return "🚨 MEGA MOVEMENT"
        elif value_eth >= 5000:
            return "🔴 CRITICAL"
        elif value_eth >= 1000:
            return "🟠 MAJOR"
        elif value_eth >= 500:
            return "🟡 SIGNIFICANT"
        else:
            return "🟢 NOTABLE"