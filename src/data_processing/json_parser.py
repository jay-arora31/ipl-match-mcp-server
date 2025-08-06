import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database.models import Match, Innings, Delivery, Player, Team, PlayerStats, TeamStats
from ..database.database import get_db_session

class IPLDataProcessor:
    def __init__(self):
        self.session = get_db_session()
    
    def process_all_matches(self, data_dir: str = "data") -> int:
        """Process all JSON files in the data directory"""
        processed_count = 0
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        print(f"Found {len(json_files)} JSON files to process...")
        
        for idx, filename in enumerate(json_files, 1):
            if idx % 100 == 0:
                print(f"Processed {idx}/{len(json_files)} matches...")
            
            try:
                file_path = os.path.join(data_dir, filename)
                match_data = self.load_match_json(file_path)
                if match_data:
                    self.process_match(match_data, filename.replace('.json', ''))
                    processed_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        self.session.commit()
        self.session.close()
        print(f"Successfully processed {processed_count} matches!")
        return processed_count
    
    def load_match_json(self, file_path: str) -> Optional[Dict]:
        """Load and return match data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def process_match(self, match_data: Dict, match_id: str):
        """Process a single match and insert into database"""
        info = match_data.get('info', {})
        
        # Parse date
        dates = info.get('dates', [])
        match_date = None
        if dates:
            try:
                match_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
            except:
                pass
        
        # Get teams
        teams = info.get('teams', [])
        team1 = teams[0] if len(teams) > 0 else None
        team2 = teams[1] if len(teams) > 1 else None
        
        # Process outcome
        outcome = info.get('outcome', {})
        winner = outcome.get('winner')
        win_by = outcome.get('by', {})
        win_by_runs = win_by.get('runs')
        win_by_wickets = win_by.get('wickets')
        result = outcome.get('result', 'normal')
        
        # Process toss
        toss = info.get('toss', {})
        toss_winner = toss.get('winner')
        toss_decision = toss.get('decision')
        
        # Process officials
        officials = info.get('officials', {})
        umpires = officials.get('umpires', [])
        match_referee = officials.get('match_referees', [None])[0] if officials.get('match_referees') else None
        tv_umpire = officials.get('tv_umpires', [None])[0] if officials.get('tv_umpires') else None
        reserve_umpire = officials.get('reserve_umpires', [None])[0] if officials.get('reserve_umpires') else None
        
        # Player of the match
        player_of_match = None
        pom = info.get('player_of_match', [])
        if pom:
            player_of_match = pom[0]
        
        # Event info
        event = info.get('event', {})
        event_name = event.get('name', 'Indian Premier League')
        match_number = event.get('match_number')
        
        # Create match record
        match = Match(
            match_id=match_id,
            city=info.get('city'),
            venue=info.get('venue'),
            date=match_date,
            season=info.get('season'),
            match_type=info.get('match_type', 'T20'),
            event_name=event_name,
            match_number=match_number,
            gender=info.get('gender', 'male'),
            overs=info.get('overs', 20),
            balls_per_over=info.get('balls_per_over', 6),
            winner=winner,
            result=result,
            win_by_runs=win_by_runs,
            win_by_wickets=win_by_wickets,
            win_method=outcome.get('method'),
            toss_winner=toss_winner,
            toss_decision=toss_decision,
            player_of_match=player_of_match,
            umpires=umpires,
            match_referee=match_referee,
            tv_umpire=tv_umpire,
            reserve_umpire=reserve_umpire,
            team1=team1,
            team2=team2,
            raw_data=match_data
        )
        
        # Check if match already exists
        existing_match = self.session.query(Match).filter(Match.match_id == match_id).first()
        if existing_match:
            return  # Skip if already processed
        
        self.session.add(match)
        self.session.flush()  # Get the match.id
        
        # Process innings and deliveries
        self.process_innings_and_deliveries(match_data, match.id)
        
        # Add teams if not exist
        self.add_teams([team1, team2])
        
        # Process players from registry
        self.process_players(info.get('registry', {}).get('people', {}))
    
    def process_innings_and_deliveries(self, match_data: Dict, match_db_id: int):
        """Process innings and ball-by-ball deliveries"""
        innings_list = match_data.get('innings', [])
        
        for idx, inning in enumerate(innings_list, 1):
            team = inning.get('team')
            overs_data = inning.get('overs', [])
            
            # Calculate innings totals
            total_runs = 0
            total_wickets = 0
            balls_bowled = 0
            
            for over in overs_data:
                deliveries = over.get('deliveries', [])
                for delivery in deliveries:
                    runs = delivery.get('runs', {})
                    total_runs += runs.get('total', 0)
                    balls_bowled += 1
                    
                    if delivery.get('wickets'):
                        total_wickets += len(delivery['wickets'])
            
            total_overs = balls_bowled / 6.0
            run_rate = total_runs / total_overs if total_overs > 0 else 0
            
            # Create innings record
            innings_record = Innings(
                match_id=match_db_id,
                innings_number=idx,
                team=team,
                total_runs=total_runs,
                total_wickets=total_wickets,
                total_overs=round(total_overs, 1),
                run_rate=round(run_rate, 2),
                target=inning.get('target', {}).get('runs') if idx == 2 else None
            )
            self.session.add(innings_record)
            
            # Process deliveries
            for over_num, over in enumerate(overs_data, 1):
                deliveries = over.get('deliveries', [])
                for ball_num, delivery in enumerate(deliveries, 1):
                    self.process_delivery(delivery, match_db_id, idx, over_num, ball_num)
    
    def process_delivery(self, delivery: Dict, match_id: int, innings: int, over: int, ball: int):
        """Process a single delivery"""
        runs = delivery.get('runs', {})
        extras = delivery.get('extras', {})
        wickets = delivery.get('wickets', [])
        
        # Determine extras type
        extras_type = None
        if extras:
            if 'wides' in extras:
                extras_type = 'wide'
            elif 'noballs' in extras:
                extras_type = 'noball'
            elif 'byes' in extras:
                extras_type = 'bye'
            elif 'legbyes' in extras:
                extras_type = 'legbye'
        
        # Wicket information
        wicket_taken = len(wickets) > 0
        wicket_type = None
        wicket_player_out = None
        wicket_fielders = None
        
        if wickets:
            wicket = wickets[0]  # Take first wicket
            wicket_type = wicket.get('kind')
            wicket_player_out = wicket.get('player_out')
            wicket_fielders = wicket.get('fielders', [])
        
        delivery_record = Delivery(
            match_id=match_id,
            innings=innings,
            over=over,
            ball=ball,
            batter=delivery.get('batter'),
            non_striker=delivery.get('non_striker'),
            bowler=delivery.get('bowler'),
            runs_batter=runs.get('batter', 0),
            runs_extras=runs.get('extras', 0),
            runs_total=runs.get('total', 0),
            extras_type=extras_type,
            wicket_taken=wicket_taken,
            wicket_type=wicket_type,
            wicket_player_out=wicket_player_out,
            wicket_fielders=wicket_fielders
        )
        
        self.session.add(delivery_record)
    
    def add_teams(self, team_names: List[str]):
        """Add teams if they don't exist"""
        for team_name in team_names:
            if team_name:
                existing_team = self.session.query(Team).filter(Team.name == team_name).first()
                if not existing_team:
                    team = Team(name=team_name)
                    self.session.add(team)
    
    def process_players(self, registry: Dict[str, str]):
        """Process players from registry"""
        for player_name, cricsheet_id in registry.items():
            existing_player = self.session.query(Player).filter(Player.cricsheet_id == cricsheet_id).first()
            if not existing_player:
                player = Player(
                    name=player_name,
                    cricsheet_id=cricsheet_id
                )
                self.session.add(player)
    
    def calculate_statistics(self):
        """Calculate and store player and team statistics"""
        print("Calculating basic statistics...")
        
        # For now, create basic stats without complex queries
        try:
            # Clear existing stats
            self.session.query(PlayerStats).delete()
            self.session.query(TeamStats).delete()
            
            # Create basic team stats
            teams = self.session.query(Team).all()
            for team in teams:
                matches = self.session.query(Match).filter(
                    (Match.team1 == team.name) | (Match.team2 == team.name)
                ).all()
                
                wins = self.session.query(Match).filter(Match.winner == team.name).count()
                total_matches = len(matches)
                
                team_stats = TeamStats(
                    team_name=team.name,
                    matches_played=total_matches,
                    matches_won=wins,
                    matches_lost=total_matches - wins,
                    win_percentage=round((wins * 100) / max(1, total_matches), 2) if total_matches > 0 else 0
                )
                self.session.add(team_stats)
            
            # Create basic player stats using ORM queries
            all_deliveries = self.session.query(Delivery).all()
            player_batting = {}
            player_bowling = {}
            
            for delivery in all_deliveries:
                # Batting stats
                if delivery.batter:
                    if delivery.batter not in player_batting:
                        player_batting[delivery.batter] = {
                            'total_runs': 0, 'balls_faced': 0, 'sixes': 0, 'fours': 0,
                            'matches': set()
                        }
                    
                    player_batting[delivery.batter]['total_runs'] += delivery.runs_batter or 0
                    player_batting[delivery.batter]['balls_faced'] += 1
                    player_batting[delivery.batter]['matches'].add(delivery.match_id)
                    
                    if delivery.runs_batter == 6:
                        player_batting[delivery.batter]['sixes'] += 1
                    elif delivery.runs_batter == 4:
                        player_batting[delivery.batter]['fours'] += 1
                
                # Bowling stats
                if delivery.bowler:
                    if delivery.bowler not in player_bowling:
                        player_bowling[delivery.bowler] = {
                            'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0,
                            'matches': set()
                        }
                    
                    player_bowling[delivery.bowler]['runs_conceded'] += delivery.runs_total or 0
                    player_bowling[delivery.bowler]['balls_bowled'] += 1
                    player_bowling[delivery.bowler]['matches'].add(delivery.match_id)
                    
                    if delivery.wicket_taken:
                        player_bowling[delivery.bowler]['wickets'] += 1
            
            # Create player stats records
            all_players = set(player_batting.keys()) | set(player_bowling.keys())
            
            for player in all_players:
                batting = player_batting.get(player, {})
                bowling = player_bowling.get(player, {})
                
                total_runs = batting.get('total_runs', 0)
                balls_faced = batting.get('balls_faced', 0)
                matches_batted = len(batting.get('matches', set()))
                
                wickets = bowling.get('wickets', 0)
                runs_conceded = bowling.get('runs_conceded', 0)
                balls_bowled = bowling.get('balls_bowled', 0)
                matches_bowled = len(bowling.get('matches', set()))
                
                # Calculate derived stats
                batting_avg = total_runs / max(1, matches_batted) if matches_batted > 0 else 0
                strike_rate = (total_runs * 100) / max(1, balls_faced) if balls_faced > 0 else 0
                bowling_avg = runs_conceded / max(1, wickets) if wickets > 0 else 0
                economy_rate = (runs_conceded * 6) / max(1, balls_bowled) if balls_bowled > 0 else 0
                
                player_stats = PlayerStats(
                    player_name=player,
                    matches_batted=matches_batted,
                    total_runs=total_runs,
                    highest_score=0,  # Would need more complex calculation
                    sixes=batting.get('sixes', 0),
                    fours=batting.get('fours', 0),
                    balls_faced=balls_faced,
                    batting_average=round(batting_avg, 2),
                    strike_rate=round(strike_rate, 2),
                    matches_bowled=matches_bowled,
                    wickets_taken=wickets,
                    runs_conceded=runs_conceded,
                    overs_bowled=round(balls_bowled / 6.0, 1),
                    bowling_average=round(bowling_avg, 2),
                    economy_rate=round(economy_rate, 2)
                )
                self.session.add(player_stats)
            
            self.session.commit()
            print("Statistics calculated successfully!")
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            self.session.rollback()
            raise
    
    def calculate_player_stats(self):
        """Legacy method - now handled in calculate_statistics"""
        pass
    
    def calculate_team_stats(self):
        """Legacy method - now handled in calculate_statistics"""
        pass 