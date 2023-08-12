import pandas as pd
import random

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

# Additional optimization to replace top two most expensive players
for iteration in range(10):
    print(f"\nIteration {iteration + 1}")

    # Get top two most expensive players
    expensive_players = sorted(best_indices, key=lambda x: players_data.loc[x, 'cost'], reverse=True)[:2]

    # Attempt to replace with cheaper players
    for player_index in expensive_players:
        position = players_data.loc[player_index, 'position']
        original_cost = players_data.loc[player_index, 'cost']
        replacements = []

        # Look for alternatives that cost exactly 2,000,000 less
        target_cost = original_cost - 2000000
        alternatives = players_data[(players_data['position'] == position) & (players_data['cost'] == target_cost)]
        replacements.extend(alternatives.index.tolist())

        # If no alternatives found, look for alternatives that cost exactly 500,000 less
        if not replacements:
            target_cost = original_cost - 500000
            alternatives = players_data[(players_data['position'] == position) & (players_data['cost'] == target_cost)]
            replacements.extend(alternatives.index.tolist())

        if replacements:
            replacement = random.choice(replacements)
            best_indices.remove(player_index)
            best_indices.append(replacement)

    # Print results
    print("Current Team:")
    team = players_data.loc[best_indices]
    print_section("FORWARD", team[team['position'] == 'FORWARD'])
    print_section("MIDFIELDER", team[team['position'] == 'MIDFIELDER'])
    print_section("DEFENDER", team[team['position'] == 'DEFENDER'])
    print("\nTotal Predicted Points:", team['predicted_points'].sum())
    print("Total Cost:", team['cost'].sum())
    print("Budget Remaining:", BUDGET_CONSTRAINT - team['cost'].sum())
    print("=" * 50)
