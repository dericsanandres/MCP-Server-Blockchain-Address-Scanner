# 🐋 Ethereum Whale Scanner - MCP Server

An intelligent blockchain analysis tool that helps you discover and analyze Ethereum whales through the Model Context Protocol (MCP). Built as a Python MCP server for seamless integration with Claude Desktop.

## What This Does

This MCP server transforms Claude into a powerful blockchain intelligence assistant. It can:

- **Analyze any Ethereum address** to determine if it's a whale and assess its activity patterns
- **Discover whale addresses** through transaction network analysis
- **Track large ETH movements** across the network in real-time
- **Monitor exchange whale activity** to identify potential market movements
- **Compare multiple addresses** to rank whale sizes and behaviors

Perfect for crypto researchers, traders, and anyone curious about whale behavior on Ethereum.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (recommended: Python 3.12)
- Claude Desktop installed
- Etherscan API key (free from [etherscan.io](https://etherscan.io/apis))

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/MCP-Server-Blockchain-Address-Scanner
   cd MCP-Server-Blockchain-Address-Scanner
   make setup
   ```

2. **Configure your API key**

   Create a `.env` file:
   ```bash
   ETHERSCAN_API_KEY=your_api_key_here
   ```

3. **Add to Claude Desktop**

   Update your Claude Desktop config at `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "etherscan": {
         "command": "/full/path/to/your/project/venv/bin/python",
         "args": ["-m", "core.main"],
         "cwd": "/full/path/to/your/project",
         "env": {
           "ETHERSCAN_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and you're ready to go!

## 🐋 Features & Examples

### Comprehensive Whale Analysis
Get detailed insights about any Ethereum address including balance, transaction patterns, activity scores, and risk assessment.

**Example:**
```
Analyze this whale: 0xbe0eb53f46cd790cd13851d5eff43d12404d33e8
```

### Whale Discovery Through Network Analysis
Discover whale addresses by analyzing large transactions and their participants. Typically finds 10-30 real whale addresses.

**Example:**
```
Discover top whales with balances over 1000 ETH
```

### Large Movement Tracking
Monitor recent large ETH transfers across the network and identify whale participants.

**Example:**
```
Show me recent whale movements above 500 ETH
```

### Exchange Whale Monitoring
Track whale deposits and withdrawals from major exchanges to identify potential market movements.

**Example:**
```
Track whale deposits and withdrawals from exchanges above 1000 ETH
```

### Multi-Whale Comparison
Compare multiple addresses side-by-side with rankings and detailed metrics.

**Example:**
```
Compare these whales: 0xbe0eb53f46cd790cd13851d5eff43d12404d33e8, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2
```

## 📊 Screenshots

### Whale Analysis in Action
*[Screenshot showing comprehensive whale analysis results with balance, classification, activity scores, and transaction metrics]*

### Exchange Whale Tracking
*[Screenshot displaying whale deposits/withdrawals from major exchanges with market impact analysis]*

### Whale Discovery Results
*[Screenshot of discovered whale addresses with their balances and classifications]*

### Multi-Whale Comparison
*[Screenshot showing side-by-side whale comparison with rankings and detailed metrics]*

> **Note:** Add screenshots here showing the actual whale analysis results in Claude Desktop interface to help users understand what to expect.

## 🛠️ Available MCP Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `analyze_whale()` | Comprehensive whale analysis with activity scores | Analyze address behavior patterns |
| `detect_whale_class()` | Quick whale classification by balance | Classify as Shrimp/Small/Medium/Large/Mega Whale |
| `compare_whales()` | Compare multiple addresses | Rank whales by size and activity |
| `discover_whale_movements()` | Track large ETH movements | Find recent whale transactions |
| `discover_top_whales()` | Network analysis whale discovery | Find whales through transaction patterns |
| `track_exchange_whales()` | Monitor exchange whale activity | Track deposits/withdrawals |
| `check_balance()` | Get ETH balance for any address | Basic balance checking |
| `get_transactions()` | Detailed transaction history | Analyze transaction patterns |
| `get_token_transfers()` | ERC20 token transfer analysis | Track token movements |

## 🏗️ Architecture

Built with modern Python async patterns:

- **FastMCP**: Modern MCP server framework with `@mcp.tool()` decorators
- **Etherscan API**: Reliable blockchain data with rate limiting
- **Pydantic**: Type-safe data validation and serialization
- **Async/Await**: Non-blocking API calls for better performance

## ⚙️ Configuration

### Environment Variables
- `ETHERSCAN_API_KEY`: Your Etherscan API key (required)
- `RATE_LIMIT`: API requests per second (default: 5)

### Whale Classifications
- **Shrimp**: < 10 ETH
- **Small Whale**: 10-100 ETH
- **Medium Whale**: 100-1,000 ETH
- **Large Whale**: 1,000-10,000 ETH
- **Mega Whale**: > 10,000 ETH

## 📈 Sample Results

When you analyze a major whale address, you might see results like:

```
🐋 MEGA WHALE (>10,000 ETH)
Balance: 1,996,008 ETH
Known Entity: Binance 7

ACTIVITY METRICS:
Total Transactions: 45,892
Large Transactions (>50 ETH): 12,453
Activity Score: 85/100 (Very Active 🔥)
Risk Score: 45/100 (Medium Risk ⚡)
```

## 🚦 Rate Limiting & Best Practices

- Respects Etherscan's rate limits (5 requests/second by default)
- Implements intelligent caching to minimize API calls
- Graceful error handling for network issues
- Automatic retry logic with exponential backoff

## 🤝 Contributing

This project was built to demonstrate MCP server capabilities for blockchain analysis. Feel free to:

- Report issues or bugs
- Suggest new whale analysis features
- Submit pull requests for improvements
- Share interesting whale discoveries!

## 📄 License

MIT License - feel free to use this code for your own blockchain analysis projects.

## 🙋‍♂️ Support

Having issues? Check these common solutions:

1. **"Module not found"** - Run `make setup` to create the virtual environment
2. **"API key required"** - Make sure your `.env` file has a valid Etherscan API key
3. **"MCP connection failed"** - Verify the full path in your Claude Desktop config
4. **Rate limit errors** - Reduce the `RATE_LIMIT` environment variable

---

**Happy whale hunting!** 🐋 This tool has successfully identified major whales including Binance hot wallets, Robinhood holdings, and other institutional-level addresses. Use it responsibly for research and analysis purposes.