# IPL MCP Server

A Model Context Protocol (MCP) server that provides natural language access to IPL (Indian Premier League) cricket match data. Built using data from [Cricsheet](https://cricsheet.org) with an enhanced sample of 18 IPL matches including Virat Kohli games and CSK vs MI classics.

## 🏏 Features

- **Natural Language Queries**: Ask questions about IPL data in plain English
- **Enhanced Dataset**: 18 carefully selected IPL matches including:
  - Virat Kohli batting performances (99 runs in 4 matches)
  - CSK vs MI classic encounters (3 matches)
  - All major IPL teams represented
- **Rich Analytics**: Player stats, team performance, match analysis
- **Claude Desktop Integration**: Works seamlessly with Claude Desktop
- **Fast SQL Backend**: Efficient SQLite database with optimized queries
- **Extensible**: Can easily be extended to work with the full 1,169+ match dataset

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- `uv` package manager
- Claude Desktop (for MCP integration)

### Installation

1. **Clone and setup**:
```bash
git clone <your-repo>
cd ipl-mcp-server
```

2. **Install dependencies**:
```bash
uv install
```

3. **Setup database and load data**:
```bash
uv run python main.py --setup --data-dir data_small
```
This will:
- Create SQLite database tables
- Process 18 sample JSON match files (includes V Kohli & CSK vs MI)
- Calculate player and team statistics
- Takes ~10-15 seconds to complete

4. **Test the queries** (optional):
```bash
uv run python test_queries.py
```

5. **Start the MCP server**:
```bash
uv run python main.py --server
```

## 🎯 Example Queries

### Basic Match Information
- "Show me all matches in the dataset"
- "How many matches are in the database?"
- "Which team won the most matches?"
- "What was the highest total score?"
- "Show matches played in Mumbai"

### Player Performance
- "Who scored the most runs across all matches?"
- "Which bowler took the most wickets?"
- "Show me Virat Kohli's batting stats"
- "Who has the best bowling figures in a single match?"
- "Show all centuries scored"

### Advanced Analytics
- "What's the average first innings score?"
- "Which venue has the highest scoring matches?"
- "What's the most successful chase target?"
- "Which team has the best powerplay performance?"
- "Show me partnership records over 100 runs"

### Match-Specific Queries
- "Show me the scorecard for match between CSK and MI"
- "How many sixes were hit in the final?"
- "What was the winning margin in the closest match?"

## 🔧 Claude Desktop Integration

1. **Add to Claude Desktop config**:

Edit your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ipl-cricket-server": {
      "command": "uv",
      "args": ["run", "python", "main.py", "--server"],
      "cwd": "/path/to/your/ipl-mcp-server"
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Test the connection**:
Ask Claude: "Show me IPL team statistics"

## 📊 Database Schema

The server uses SQLite with the following key tables:

- **matches**: Match metadata (teams, venue, date, outcome)
- **innings**: Innings-level data (totals, wickets, overs)
- **deliveries**: Ball-by-ball data (runs, wickets, extras)
- **player_stats**: Aggregated batting/bowling statistics
- **team_stats**: Team performance metrics
- **players**: Player registry with Cricsheet IDs
- **teams**: Team information

## 🛠️ Advanced Usage

### Command Line Options

```bash
# Setup database (first time only)
uv run python main.py --setup

# Reset database and reload data
uv run python main.py --reset

# Start server (default)
uv run python main.py --server

# Custom data directory
uv run python main.py --setup --data-dir /path/to/data
```

### API Integration

The server can be extended to work with other MCP clients beyond Claude Desktop. The query engine supports pattern matching for natural language understanding.

### Adding Custom Queries

Extend the `QueryEngine` class in `src/mcp_server/query_engine.py`:

```python
{
    'pattern': r'your.*query.*pattern',
    'handler': self.your_handler_method,
    'description': 'Your query description'
}
```

## 📈 Performance

- **Database Size**: ~3MB for 18 sample matches
- **Setup Time**: 10-15 seconds for data load
- **Query Response**: <1 second for most queries
- **Memory Usage**: ~50MB typical runtime

### 🚀 Scaling to Full Dataset
The system can easily handle the complete 1,169 match dataset:
- **Full Database Size**: ~50MB
- **Full Setup Time**: 2-3 minutes
- Simply use `--data-dir data` instead of `--data-dir data_small`

## 🔍 Sample Query Results

**Query**: "Which team won the most matches?"
```
📊 **Team with most wins**

1. Mumbai Indians | 120 wins | 203 matches | 59.11% win rate
2. Chennai Super Kings | 118 wins | 195 matches | 60.51% win rate
3. Royal Challengers Bangalore | 88 wins | 203 matches | 43.35% win rate
...
```

**Query**: "Show me Virat Kohli batting stats"
```
🏏 **V Kohli** Batting Stats:
• Total Runs: 99
• Matches: 4  
• Highest Score: N/A
• Average: 24.75
• Strike Rate: 117.86
• Sixes: 4
• Fours: 8
```

## 🗄️ Data Source

All data comes from [Cricsheet](https://cricsheet.org), which provides:
- Ball-by-ball data for IPL matches from 2008-2017 seasons (enhanced sample of 18 matches)
- Player registry with unique identifiers  
- Match metadata including officials, venues, outcomes
- JSON format with comprehensive match details
- **Full dataset available**: 1,169+ matches (2008-2024) can be loaded by using `--data-dir data`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test with sample queries
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License. Data provided by Cricsheet under their terms of use.

## 🚀 Working with Full Dataset

To use the complete 1,169 match dataset instead of the sample:

1. **Reset and load full data**:
```bash
uv run python main.py --reset --data-dir data
```
⚠️ This will take 2-3 minutes to complete

2. **Benefits of full dataset**:
- Complete IPL history (2008-2024)
- More accurate player statistics
- Comprehensive team performance data
- Better trend analysis capabilities

## ✅ Verify Installation

Test your setup with these commands:

```bash
# Quick database check
uv run python -c "from src.database.database import get_db_session; from src.database.models import *; session = get_db_session(); print(f'✅ Database ready: {session.query(Match).count()} matches loaded')"

# Test natural language query
uv run python -c "from src.mcp_server.query_engine import QueryEngine; print(QueryEngine().process_query('how many matches'))"

# Run interactive demo
uv run python test_queries.py
```

## 🔗 Links

- [Cricsheet](https://cricsheet.org) - Data source
- [Claude Desktop](https://claude.ai/desktop) - MCP client  
- [MCP Protocol](https://modelcontextprotocol.io) - Protocol specification

---

**Built with ❤️ for cricket analytics and AI-powered data exploration** 