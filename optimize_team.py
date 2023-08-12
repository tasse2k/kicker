import random
import pandas as pd
import numpy as np
from deap import base, creator, tools, algorithms

# Path to the CSV file containing the players' data (adjust this path)
file_name = "C:\\Users\\bjoer\\Documents\\GitHub\\kicker\\players-data.csv"
players_data = pd.read_csv(file_name)

# Calculate points per cost
players_data['points_per_cost'] = players_data['predicted_points'] / players_data['cost']

# Filter players for valid positions and reset index
valid_positions = ['DEFENDER', 'MIDFIELDER', 'FORWARD']
players_data = players_data[players_data['position'].isin(valid_positions)].reset_index(drop=True)

# Budget constraint
BUDGET_CONSTRAINT = 30.7 * 10**6

# Define the fitness function
def fitness(individual):
    num_defenders = sum(players_data.loc[individual, 'position'] == 'DEFENDER')
    num_midfielders = sum(players_data.loc[individual, 'position'] == 'MIDFIELDER')
    num_forwards = sum(players_data.loc[individual, 'position'] == 'FORWARD')
    total_players = sum(individual)

    if (num_defenders < 3 or num_defenders > 4 or
        num_midfielders < 3 or num_midfielders > 5 or
        num_forwards < 1 or num_forwards > 3 or
        total_players != 10):
        return (-1,)

    if total_cost > BUDGET_CONSTRAINT:
        return (-1,)
    if num_defenders != 3 or num_midfielders < 3 or num_midfielders > 5 or num_forwards < 1 or num_forwards > 3 or total_players != 10:
        return (-1,)
    
    return (total_points,)



# Create individual initialization function
def create_individual():
    individual = [0] * len(players_data)

    # Select the best FORWARD, MIDFIELDER, and DEFENDER based on points_per_cost
    for position, count in [('FORWARD', 1), ('MIDFIELDER', 2), ('DEFENDER', 2)]:
        selected_players = players_data[(players_data['position'] == position) &
                                        (players_data['predicted_points'] > 150)].nlargest(count, 'points_per_cost').index
        for idx in selected_players:
            individual[idx] = 1

    # Select remaining players randomly based on points_per_cost
    remaining_count = 10 - sum(individual)
    remaining_players = players_data.loc[individual == np.zeros_like(individual)].nlargest(remaining_count, 'points_per_cost').index
    for idx in remaining_players:
        individual[idx] = 1

    return creator.Individual(individual)


# Custom mutation function to respect constraints
def custom_mutation(individual):
    i = random.randint(0, len(individual) - 1)
    if individual[i] == 0:
        individual[i] = 1
    else:
        individual[i] = 0

    # Ensure constraints are met
    num_defenders = sum(players_data.loc[individual, 'position'] == 'DEFENDER')
    num_midfielders = sum(players_data.loc[individual, 'position'] == 'MIDFIELDER')
    num_forwards = sum(players_data.loc[individual, 'position'] == 'FORWARD')
    total_players = sum(individual)

    if (num_defenders < 3 or num_defenders > 4 or
        num_midfielders < 3 or num_midfielders > 5 or
        num_forwards < 1 or num_forwards > 3 or
        total_players != 10):
        # Reverse the mutation if constraints are violated
        if individual[i] == 0:
            individual[i] = 1
        else:
            individual[i] = 0

    return individual,

# Create DEAP tools and algorithms
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("mutate", custom_mutation)
toolbox.register("select", tools.selTournament, tournsize=3)

# Create population
population = toolbox.population(n=300)

# Run genetic algorithm
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", lambda x: sum(val[0] for val in x) / len(x))
stats.register("min", min)
stats.register("max", max)

population, log = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=500, stats=stats)

# Print the best individual
best_individual = tools.selBest(population, 1)[0]
selected_players = players_data[players_data.index.isin([i for i, selected in enumerate(best_individual) if selected])]
print(selected_players)
print("Total Predicted Points:", sum(selected_players['predicted_points']))
print("Total Cost:", sum(selected_players['cost']))

# Extract and Display Results
best_individual = [bool(val) for val in tools.selBest(population, 1)[0]]
best_players = players_data.loc[best_individual]

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
