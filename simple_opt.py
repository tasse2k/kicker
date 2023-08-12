import pandas as pd

# Read the data from the CSV file
file_name = "C:\\Users\\bjoer\\Documents\\GitHub\\kicker\\players-data.csv"
players_data = pd.read_csv(file_name)

# Define the initial players by their IDs
player_ids = ["pl-k00133398", "pl-k00110717", "pl-k00076954", "pl-k00057343", "pl-k00058007", "pl-k00066753", "pl-k00086138", "pl-k00058003", "pl-k00111367", "pl-k00081465"]
initial_indices = [players_data[players_data['ID'] == player_id].index[0] for player_id in player_ids]

# Define the budget constraint
BUDGET_CONSTRAINT = 32.5 * 10**6

# Function to calculate the total score and cost
def calculate_score_and_cost(indices):
    total_score = players_data.loc[indices, 'predicted_points'].sum()
    total_cost = players_data.loc[indices, 'cost'].sum()
    return total_score, total_cost

# Function to check if the team is valid
def is_valid_team(indices):
    selected_players = players_data.loc[indices]
    num_defenders = (selected_players['position'] == 'DEFENDER').sum()
    num_midfielders = (selected_players['position'] == 'MIDFIELDER').sum()
    num_forwards = (selected_players['position'] == 'FORWARD').sum()
    return (
        num_defenders >= 3 and num_defenders <= 4 and
        num_midfielders >= 3 and num_midfielders <= 5 and
        num_forwards >= 1 and num_forwards <= 3 and
        len(indices) == 10
    )

# Optimization logic
best_indices = initial_indices.copy()
best_score, best_cost = calculate_score_and_cost(best_indices)

# Iterate over each player in the team
for idx in initial_indices:
    # Iterate over each player in the dataset
    for replacement_idx in players_data.index:
        # Skip if the replacement player is already in the team
        if replacement_idx in best_indices:
            continue
        
        # Check if the replacement player has the same position
        if players_data.loc[idx, 'position'] != players_data.loc[replacement_idx, 'position']:
            continue
        
        # Replace the player and check the new score and cost
        new_indices = [replacement_idx if i == idx else i for i in best_indices]
        new_score, new_cost = calculate_score_and_cost(new_indices)
        
        # If the new team is valid and the score is improved, update the best team
        if new_score > best_score and new_cost <= BUDGET_CONSTRAINT and is_valid_team(new_indices):
            best_score = new_score
            best_indices = new_indices

# Display the results
best_players = players_data.loc[best_indices]

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
