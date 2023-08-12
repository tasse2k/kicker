import pandas as pd

# Path to the CSV file containing the players' data
file_name = "C:\\Users\\bjoer\\Documents\\GitHub\\kicker\\players-data.csv"
players_data = pd.read_csv(file_name)

# Budget constraint
BUDGET_CONSTRAINT = 30.7 * 10**6

# Initial players by IDs
player_ids = [
    "pl-k00133398", "pl-k00110717", "pl-k00076954", "pl-k00057343",
    "pl-k00058007", "pl-k00066753", "pl-k00086138", "pl-k00058003",
    "pl-k00111367", "pl-k00081465"
]
initial_indices = [players_data[players_data['ID'] == player_id].index[0] for player_id in player_ids]

# Optimization function
def optimize_team(initial_indices):
    current_team_indices = initial_indices.copy()

    while True:
        improvement_found = False
        for player_index in current_team_indices:
            player_to_replace = players_data.loc[player_index]
            available_players = players_data[
                (players_data['cost'] <= player_to_replace['cost']) &
                (players_data.index != player_index) &
                (players_data['predicted_points'] > player_to_replace['predicted_points']) &
                (players_data['position'] == player_to_replace['position'])
            ]

            if not available_players.empty:
                replacement_player = available_players.nlargest(1, 'predicted_points').iloc[0]
                current_team_indices[current_team_indices.index(player_index)] = replacement_player.name
                improvement_found = True
                break
        
        if not improvement_found:
            break

    return current_team_indices

optimized_indices = optimize_team(initial_indices)
best_players = players_data.loc[optimized_indices]

def print_section(title, players):
    print(title)
    for _, player in players.iterrows():
        print(f"{player['club']} - {player['name']} - Predicted Points: {player['predicted_points']}")

print_section("FORWARD", best_players[best_players['position'] == 'FORWARD'])
print_section("MIDFIELDER", best_players[best_players['position'] == 'MIDFIELDER'])
print_section("DEFENDER", best_players[best_players['position'] == 'DEFENDER'])

print("\nSummary")
print("Sum of predicted points:", best_players['predicted_points'].sum())
print("Sum of predicted lower bounds:", best_players['lower_bound'].sum())
print("Sum of predicted upper bounds:", best_players['upper_bound'].sum())

total_budget_used = best_players['cost'].sum()
print("\nTotal Budget Used:", total_budget_used)
print("Budget Remaining:", BUDGET_CONSTRAINT - total_budget_used)
