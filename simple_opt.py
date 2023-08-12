import pandas as pd

# Read the players data
file_name = "C:\\Users\\bjoer\\Documents\\GitHub\\kicker\\players-data.csv"
players_data = pd.read_csv(file_name)

# Given player IDs
player_ids = ["pl-k00133398", "pl-k00110717", "pl-k00076954", "pl-k00057343",
              "pl-k00058007", "pl-k00066753", "pl-k00086138", "pl-k00058003",
              "pl-k00111367", "pl-k00081465"]

# Convert IDs to indices
initial_indices = [players_data[players_data['id'] == player_id].index[0] for player_id in player_ids]

# Initialize team
team = [0] * len(players_data)
for index in initial_indices:
    team[index] = 1

# Function to evaluate the team
def evaluate_team(team):
    return sum(players_data.loc[team == 1, 'predicted_points'])

# Optimization loop
current_score = evaluate_team(team)
improved = True

while improved:
    improved = False
    # Sort team members by points per cost
    team_indices = [i for i, x in enumerate(team) if x == 1]
    team_indices.sort(key=lambda idx: players_data.loc[idx, 'predicted_points'] / players_data.loc[idx, 'cost'])

    # Try to replace each team member
    for min_index in team_indices:
        # Find potential replacements
        replacements = players_data.loc[(team == 0) & (players_data['cost'] <= players_data.loc[min_index, 'cost'])]

        # Try to find a replacement that improves the score
        found_replacement = False
        for _, replacement in replacements.iterrows():
            new_team = team.copy()
            new_team[min_index] = 0
            new_team[replacement.name] = 1
            new_score = evaluate_team(new_team)
            if new_score > current_score:
                team = new_team
                current_score = new_score
                found_replacement = True
                improved = True
                break

# Final team
final_team = players_data.loc[team == 1]
print(final_team)
