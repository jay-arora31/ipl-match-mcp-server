import re
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc, func

from ..database.database import get_db_session
from ..database.models import *

class QueryEngine:
    def __init__(self):
        self.session = get_db_session()
        
        # Pre-defined query patterns and their SQL translations
        self.query_patterns = [
            # Basic match queries
            {
                'pattern': r'show.*all.*matches|list.*matches|all.*matches.*dataset',
                'handler': self.get_all_matches,
                'description': 'Show all matches'
            },
            {
                'pattern': r'how many.*matches|total.*matches|count.*matches',
                'handler': self.count_matches,
                'description': 'Count total matches'
            },
            
            # Team performance queries
            {
                'pattern': r'which team.*won.*most|team.*most.*wins|most.*wins.*team',
                'handler': self.team_most_wins,
                'description': 'Team with most wins'
            },
            {
                'pattern': r'team.*statistics|team.*stats|show.*team.*performance',
                'handler': self.get_team_stats,
                'description': 'Team statistics'
            },
            
            # Player performance queries  
            {
                'pattern': r'who.*scored.*most.*runs|most.*runs.*scored|highest.*run.*scorer',
                'handler': self.player_most_runs,
                'description': 'Player with most runs'
            },
            {
                'pattern': r'who.*took.*most.*wickets|most.*wickets|best.*bowler',
                'handler': self.player_most_wickets,
                'description': 'Player with most wickets'
            },
            {
                'pattern': r'(.*)\s+batting.*stats|(.*)\s+stats.*batting|show.*(.*)\s+batting',
                'handler': self.get_player_batting_stats,
                'description': 'Player batting statistics'
            },
            {
                'pattern': r'(.*)\s+bowling.*stats|(.*)\s+stats.*bowling|show.*(.*)\s+bowling',
                'handler': self.get_player_bowling_stats,
                'description': 'Player bowling statistics'  
            },
            
            # Match-specific queries
            {
                'pattern': r'highest.*total.*score|maximum.*score|biggest.*total',
                'handler': self.highest_total_score,
                'description': 'Highest team total'
            },
            {
                'pattern': r'lowest.*total.*score|minimum.*score|smallest.*total',
                'handler': self.lowest_total_score,
                'description': 'Lowest team total'
            },
            {
                'pattern': r'matches.*in.*(mumbai|delhi|bangalore|chennai|kolkata|hyderabad|pune|jaipur|mohali)',
                'handler': self.matches_by_city,
                'description': 'Matches by city'
            },
            {
                'pattern': r'matches.*at.*(.*stadium|.*ground)',
                'handler': self.matches_by_venue,
                'description': 'Matches by venue'
            },
            
            # Advanced analytics
            {
                'pattern': r'average.*first.*innings|first.*innings.*average',
                'handler': self.average_first_innings_score,
                'description': 'Average first innings score'
            },
            {
                'pattern': r'venue.*highest.*scoring|stadium.*highest.*scores',
                'handler': self.venue_highest_scores,
                'description': 'Venues with highest scores'
            },
            {
                'pattern': r'all.*centuries|centuries.*scored|100.*scores',
                'handler': self.all_centuries,
                'description': 'All centuries scored'
            },
            {
                'pattern': r'successful.*chase|highest.*chase|best.*chase',
                'handler': self.successful_chases,
                'description': 'Most successful chase targets'
            },
            {
                'pattern': r'powerplay.*performance|powerplay.*stats',
                'handler': self.powerplay_performance,
                'description': 'Powerplay performance by teams'
            }
        ]
    
    def process_query(self, query: str) -> str:
        """Process natural language query and return formatted results"""
        query_lower = query.lower().strip()
        
        # Try to match query patterns
        for pattern_info in self.query_patterns:
            pattern = pattern_info['pattern']
            handler = pattern_info['handler']
            
            match = re.search(pattern, query_lower)
            if match:
                try:
                    # Extract parameters from regex groups if any
                    groups = match.groups()
                    params = [g.strip() if g else None for g in groups if g and g.strip()]
                    
                    result = handler(*params) if params else handler()
                    return self.format_result(result, pattern_info['description'])
                except Exception as e:
                    return f"Error executing query: {str(e)}"
        
        # If no pattern matches, try to handle as a general query
        return self.handle_general_query(query)
    
    def format_result(self, result: Any, description: str) -> str:
        """Format query results for display"""
        if not result:
            return f"No results found for: {description}"
        
        if isinstance(result, str):
            return result
        
        if isinstance(result, (int, float)):
            return f"{description}: {result}"
        
        if isinstance(result, list):
            if not result:
                return f"No results found for: {description}"
            
            # Format list results
            formatted_lines = [f"📊 **{description}**", ""]
            
            for i, item in enumerate(result[:20], 1):  # Limit to 20 results
                if isinstance(item, tuple):
                    formatted_lines.append(f"{i}. {' | '.join(str(x) for x in item)}")
                else:
                    formatted_lines.append(f"{i}. {item}")
            
            if len(result) > 20:
                formatted_lines.append(f"\n... and {len(result) - 20} more results")
            
            return "\n".join(formatted_lines)
        
        return str(result)
    
    # Query handlers
    def get_all_matches(self) -> List[Tuple]:
        """Get all matches with basic info"""
        query = """
            SELECT date, team1, team2, winner, city, venue 
            FROM matches 
            ORDER BY date DESC 
            LIMIT 50
        """
        result = self.session.execute(text(query)).fetchall()
        return [(r[0], f"{r[1]} vs {r[2]}", r[3], r[4], r[5]) for r in result]
    
    def count_matches(self) -> str:
        """Count total matches"""
        count = self.session.query(Match).count()
        return f"Total matches in database: {count}"
    
    def team_most_wins(self) -> List[Tuple]:
        """Get teams with most wins"""
        query = """
            SELECT team_name, matches_won, matches_played, win_percentage
            FROM team_stats 
            ORDER BY matches_won DESC 
            LIMIT 10
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[0]}", f"{r[1]} wins", f"{r[2]} matches", f"{r[3]}% win rate") for r in result]
    
    def get_team_stats(self) -> List[Tuple]:
        """Get comprehensive team statistics"""
        query = """
            SELECT team_name, matches_played, matches_won, matches_lost, 
                   win_percentage, highest_score, lowest_score
            FROM team_stats 
            ORDER BY matches_won DESC
        """
        result = self.session.execute(text(query)).fetchall()
        return result
    
    def player_most_runs(self) -> List[Tuple]:
        """Get players with most runs"""
        query = """
            SELECT player_name, total_runs, matches_batted, highest_score, 
                   batting_average, strike_rate
            FROM player_stats 
            WHERE total_runs > 0
            ORDER BY total_runs DESC 
            LIMIT 20
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[0]}", f"{r[1]} runs", f"{r[2]} matches", f"HS: {r[3]}", 
                f"Avg: {r[4]}", f"SR: {r[5]}") for r in result]
    
    def player_most_wickets(self) -> List[Tuple]:
        """Get players with most wickets"""
        query = """
            SELECT player_name, wickets_taken, matches_bowled, 
                   bowling_average, economy_rate, overs_bowled
            FROM player_stats 
            WHERE wickets_taken > 0
            ORDER BY wickets_taken DESC 
            LIMIT 20
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[0]}", f"{r[1]} wickets", f"{r[2]} matches", 
                f"Avg: {r[3]}", f"Econ: {r[4]}", f"Overs: {r[5]}") for r in result]
    
    def get_player_batting_stats(self, player_name: str) -> str:
        """Get specific player's batting stats"""
        # Clean player name
        player_name = player_name.strip()
        if not player_name:
            return "Please specify a player name"
        
        query = """
            SELECT player_name, total_runs, matches_batted, highest_score,
                   batting_average, strike_rate, centuries, fifties, sixes, fours
            FROM player_stats 
            WHERE LOWER(player_name) LIKE LOWER(?)
            AND total_runs > 0
            ORDER BY total_runs DESC
            LIMIT 5
        """
        
        result = self.session.execute(text(query), (f"%{player_name}%",)).fetchall()
        
        if not result:
            return f"No batting stats found for player matching '{player_name}'"
        
        stats = []
        for r in result:
            stats.append(f"""
🏏 **{r[0]}** Batting Stats:
• Total Runs: {r[1]}
• Matches: {r[2]}
• Highest Score: {r[3]}
• Average: {r[4]}
• Strike Rate: {r[5]}
• Centuries: {r[8]}
• Fifties: {r[9]}
• Sixes: {r[10]}
• Fours: {r[11]}
            """.strip())
        
        return "\n\n".join(stats)
    
    def get_player_bowling_stats(self, player_name: str) -> str:
        """Get specific player's bowling stats"""
        player_name = player_name.strip()
        if not player_name:
            return "Please specify a player name"
        
        query = """
            SELECT player_name, wickets_taken, matches_bowled, runs_conceded,
                   bowling_average, economy_rate, overs_bowled
            FROM player_stats 
            WHERE LOWER(player_name) LIKE LOWER(?)
            AND wickets_taken > 0
            ORDER BY wickets_taken DESC
            LIMIT 5
        """
        
        result = self.session.execute(text(query), (f"%{player_name}%",)).fetchall()
        
        if not result:
            return f"No bowling stats found for player matching '{player_name}'"
        
        stats = []
        for r in result:
            stats.append(f"""
⚾ **{r[0]}** Bowling Stats:
• Wickets: {r[1]}
• Matches: {r[2]}
• Runs Conceded: {r[3]}
• Bowling Average: {r[4]}
• Economy Rate: {r[5]}
• Overs Bowled: {r[6]}
            """.strip())
        
        return "\n\n".join(stats)
    
    def highest_total_score(self) -> List[Tuple]:
        """Get highest team totals"""
        query = """
            SELECT i.total_runs, i.team, m.venue, m.city, m.date, 
                   m.team1, m.team2, m.winner
            FROM innings i
            JOIN matches m ON i.match_id = m.id
            ORDER BY i.total_runs DESC
            LIMIT 15
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[1]}: {r[0]}", f"{r[6]} vs {r[7]}", r[3], r[4], f"Won by: {r[8]}") 
                for r in result]
    
    def lowest_total_score(self) -> List[Tuple]:
        """Get lowest team totals"""
        query = """
            SELECT i.total_runs, i.team, m.venue, m.city, m.date,
                   m.team1, m.team2, m.winner
            FROM innings i
            JOIN matches m ON i.match_id = m.id
            WHERE i.total_runs > 0
            ORDER BY i.total_runs ASC
            LIMIT 15
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[1]}: {r[0]}", f"{r[5]} vs {r[6]}", r[2], r[3], f"Won by: {r[7]}") 
                for r in result]
    
    def matches_by_city(self, city: str) -> List[Tuple]:
        """Get matches by city"""
        query = """
            SELECT date, team1, team2, winner, venue
            FROM matches 
            WHERE LOWER(city) LIKE LOWER(?)
            ORDER BY date DESC
            LIMIT 30
        """
        result = self.session.execute(text(query), (f"%{city}%",)).fetchall()
        return [(r[0], f"{r[1]} vs {r[2]}", r[3], r[4]) for r in result]
    
    def matches_by_venue(self, venue: str) -> List[Tuple]:
        """Get matches by venue"""
        query = """
            SELECT date, team1, team2, winner, city
            FROM matches 
            WHERE LOWER(venue) LIKE LOWER(?)
            ORDER BY date DESC
            LIMIT 30
        """
        result = self.session.execute(text(query), (f"%{venue}%",)).fetchall()
        return [(r[0], f"{r[1]} vs {r[2]}", r[3], r[4]) for r in result]
    
    def average_first_innings_score(self) -> str:
        """Get average first innings score"""
        query = """
            SELECT AVG(total_runs) as avg_score, COUNT(*) as total_innings
            FROM innings 
            WHERE innings_number = 1 AND total_runs > 0
        """
        result = self.session.execute(text(query)).fetchone()
        return f"Average first innings score: {result[0]:.1f} runs (from {result[1]} innings)"
    
    def venue_highest_scores(self) -> List[Tuple]:
        """Get venues with highest scoring matches"""
        query = """
            SELECT m.venue, AVG(i.total_runs) as avg_score, 
                   MAX(i.total_runs) as highest_score, COUNT(i.id) as innings_count
            FROM matches m
            JOIN innings i ON m.id = i.match_id
            WHERE m.venue IS NOT NULL
            GROUP BY m.venue
            HAVING COUNT(i.id) >= 10
            ORDER BY avg_score DESC
            LIMIT 15
        """
        result = self.session.execute(text(query)).fetchall()
        return [(r[0], f"Avg: {r[1]:.1f}", f"Highest: {r[2]}", f"{r[3]} innings") 
                for r in result]
    
    def all_centuries(self) -> List[Tuple]:
        """Get all centuries scored (individual match performances)"""
        # This would require ball-by-ball analysis - simplified version
        query = """
            SELECT ps.player_name, ps.highest_score, ps.total_runs, ps.matches_batted
            FROM player_stats ps
            WHERE ps.highest_score >= 100
            ORDER BY ps.highest_score DESC
        """
        result = self.session.execute(text(query)).fetchall()
        return [(f"{r[0]}", f"Best: {r[1]}", f"Total: {r[2]} runs", f"{r[3]} matches") 
                for r in result]
    
    def successful_chases(self) -> List[Tuple]:
        """Get highest successful chase targets"""
        query = """
            SELECT m.date, i.total_runs, i.team as chasing_team,
                   m.team1, m.team2, m.winner, m.venue
            FROM innings i
            JOIN matches m ON i.match_id = m.id
            WHERE i.innings_number = 2 
            AND i.team = m.winner
            AND i.target IS NOT NULL
            ORDER BY i.total_runs DESC
            LIMIT 20
        """
        result = self.session.execute(text(query)).fetchall()
        return [(r[0], f"{r[2]}: {r[1]}", f"{r[3]} vs {r[4]}", r[6]) for r in result]
    
    def powerplay_performance(self) -> str:
        """Powerplay performance analysis"""
        # This is a simplified version - would need more complex analysis
        query = """
            SELECT i.team, AVG(i.total_runs) as avg_total,
                   COUNT(*) as matches_count
            FROM innings i
            JOIN matches m ON i.match_id = m.id
            GROUP BY i.team
            HAVING COUNT(*) >= 20
            ORDER BY avg_total DESC
            LIMIT 10
        """
        result = self.session.execute(text(query)).fetchall()
        
        formatted_result = ["🚀 **Team Performance Overview**", ""]
        for r in result:
            formatted_result.append(f"• {r[0]}: {r[1]:.1f} avg runs ({r[2]} matches)")
        
        return "\n".join(formatted_result)
    
    def handle_general_query(self, query: str) -> str:
        """Handle general queries that don't match specific patterns"""
        suggestions = [
            "• Show me all matches in the dataset",
            "• Which team won the most matches?", 
            "• Who scored the most runs across all matches?",
            "• What was the highest total score?",
            "• Show matches played in Mumbai",
            "• Show me Virat Kohli batting stats",
            "• Which venue has the highest scoring matches?",
            "• What's the average first innings score?",
            "• Show me all centuries scored",
            "• Who took the most wickets?"
        ]
        
        return f"""I couldn't understand your query: "{query}"

Here are some example queries you can try:

{chr(10).join(suggestions)}

Please rephrase your question or try one of the examples above.""" 