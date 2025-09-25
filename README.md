# MCP Etherscan Server (Python)

A Model Context Protocol (MCP) server that provides Ethereum blockchain data tools via Etherscan's API. This is a Python implementation inspired by the TypeScript version.

## Features

- **Balance Checking**: Get ETH balance for any Ethereum address
- **Transaction History**: Retrieve transaction history with filtering options
- **Token Transfers**: Track ERC20 token transfers
- **Contract ABIs**: Fetch smart contract ABIs for verified contracts
- **Gas Prices**: Monitor current network gas prices
- **Rate Limited**: Built-in rate limiting to respect API limits

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MCP-Server-Blockchain-Address-Scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Etherscan API key
```

4. Get an Etherscan API key:
   - Visit [etherscan.io/apis](https://etherscan.io/apis)
   - Create a free account and generate an API key
   - Add it to your `.env` file

## Usage

### Standalone Server
```bash
python -m mcp_etherscan_server.main
```

### With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "etherscan": {
      "command": "python",
      "args": ["-m", "mcp_etherscan_server.main"],
      "cwd": "/path/to/MCP-Server-Blockchain-Address-Scanner"
    }
  }
}
```

## Available Tools

### Basic Blockchain Data

**check-balance**
Get ETH balance for an address.
- **address**: Ethereum address to check

**get-transactions**
Retrieve transaction history for an address.
- **address**: Ethereum address
- **start_block** (optional): Starting block number
- **end_block** (optional): Ending block number
- **page** (optional): Page number (default: 1)
- **offset** (optional): Results per page (default: 10)

**get-token-transfers**
Get ERC20 token transfer events.
- **address**: Ethereum address
- **contract_address** (optional): Specific token contract
- **page** (optional): Page number (default: 1)
- **offset** (optional): Results per page (default: 10)

**get-contract-abi**
Fetch ABI for a verified smart contract.
- **address**: Contract address

**get-gas-prices**
Get current gas prices (safe, standard, fast).

### 🐋 Whale Detection & Analysis

**analyze-whale**
Comprehensive whale analysis of an Ethereum address.
- **address**: Ethereum address to analyze
- Provides detailed metrics including classification, activity scores, risk assessment, and transaction patterns

**detect-whale-class**
Quick whale classification based on ETH balance.
- **address**: Ethereum address to classify
- Returns whale category: Mega Whale (>10K ETH), Large Whale (1K-10K), Medium Whale (100-1K), Small Whale (10-100), or Shrimp (<10)

**compare-whales**
Compare multiple addresses for whale analysis.
- **addresses**: Comma-separated list of Ethereum addresses (max 10)
- Ranks addresses by whale size with comparative metrics

### 🔍 Whale Discovery & Tracking

**discover-whale-movements**
Find recent large whale movements and transactions.
- **min_eth_value** (optional): Minimum ETH value to consider (default: 100)
- Scans recent transactions from known whales and exchanges to identify significant movements

**discover-top-whales**
Discover whale addresses by analyzing transaction networks.
- **min_balance** (optional): Minimum ETH balance to qualify (default: 1000)
- Finds new whale addresses by analyzing participants in large transactions

**track-exchange-whales**
Track whale deposits and withdrawals from major exchanges.
- **min_amount** (optional): Minimum ETH amount to track (default: 500)
- Monitors exchange flows for potential market impact analysis

## Configuration

Environment variables:
- `ETHERSCAN_API_KEY`: Your Etherscan API key (required)
- `RATE_LIMIT`: Requests per second (default: 5)

## Development

Install in development mode:
```bash
pip install -e .
```

## License

MIT