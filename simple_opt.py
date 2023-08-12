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
    return len(indices) == len(set(indices)) and len(indices) == 10

# Function to print the sections of the team
def print_section(title, players):
    print(title)
    for _, player in players.iterrows():
        print(f"{player['club']} - {player['name']} - Predicted Points: {player['predicted_points']}")

# Function to print the current team
def print_team(team, iteration):
    print(f"\nIteration {iteration}")
    print("Current Team:")
    print_section("FORWARD", team[team['position'] == 'FORWARD'])
    print_section("MIDFIELDER", team[team['position'] == 'MIDFIELDER'])
    print_section("DEFENDER", team[team['position'] == 'DEFENDER'])
    total_points = team['predicted_points'].sum()
    total_cost = team['cost'].sum()
    print(f"Total Points: {total_points}")
    print(f"Total Cost: {total_cost}")

# Optimization logic
best_indices = initial_indices.copy()
best_score, best_cost = calculate_score_and_cost(best_indices)

# Optimization logic after initial optimization
for iteration in range(1, 11):
    # Print the current team
    team = players_data.loc[best_indices]
    print_team(team, iteration)
    
    # Select a random player to replace
    random_idx = random.choice(best_indices)
    
    # Iterate over each player in the dataset to find a replacement
    for replacement_idx in players_data.index:
        # Skip if the replacement player is already in the team
        if replacement_idx in best_indices:
            continue
        
        # Check if the replacement player has the same position
        if players_data.loc[random_idx, 'position'] != players_data.loc[replacement_idx, 'position']:
            continue
        
        # Replace the player and check the new score and cost
        new_indices = [replacement_idx if i == random_idx else i for i in best_indices]
        new_score, new_cost = calculate_score_and_cost(new_indices)
        
        # If the new team is valid and the score is improved or the same, update the best team
        if new_score >= best_score and new_cost <= BUDGET_CONSTRAINT and is_valid_team(new_indices):
            best_score = new_score
            best_indices = new_indices
            break

# Display the final results
best_players = players_data.loc[best_indices]
print_team(best_players, 'Final')
