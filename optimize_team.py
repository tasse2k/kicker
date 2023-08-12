import random
import pandas as pd
from deap import base, creator, tools, algorithms

# Path to the CSV file containing the players' data (adjust this path)
file_name = file_name = "C:\\Users\\bjoer\\Documents\\GitHub\\kicker\\players-data.csv"
players_data = pd.read_csv(file_name)

# Filter players for valid positions and reset index
valid_positions = ['DEFENDER', 'MIDFIELDER', 'FORWARD']
players_data = players_data[players_data['position'].isin(valid_positions)].reset_index(drop=True)

# Budget constraint
BUDGET_CONSTRAINT = 30.7 * 10**6

# Define the fitness function
def fitness(individual):
    selected_players = players_data.loc[individual]
    total_cost = selected_players['cost'].sum()
    total_points = selected_players['predicted_points'].sum()

    # Position constraints
    num_defenders = (selected_players['position'] == 'DEFENDER').sum()
    num_midfielders = (selected_players['position'] == 'MIDFIELDER').sum()
    num_forwards = (selected_players['position'] == 'FORWARD').sum()
    total_players = num_defenders + num_midfielders + num_forwards

    if total_cost > BUDGET_CONSTRAINT:
        return (-1,)
    if num_defenders != 3 or num_midfielders < 3 or num_midfielders > 5 or num_forwards < 1 or num_forwards > 3 or total_players != 10:
        return (-1,)
    
    return (total_points,)


# Create individual initialization function
def create_individual():
    individual = [0] * len(players_data)
    for position, count in [('DEFENDER', 3), ('MIDFIELDER', 4), ('FORWARD', 3)]:
        available_players = players_data[players_data['position'] == position].index.tolist()
        selected_players = random.sample(available_players, min(count, len(available_players)))
        for idx in selected_players:
            individual[idx] = 1
    return creator.Individual(individual)

# Custom mutation function to respect constraints
def custom_mutation(individual):
    position_counts = {'DEFENDER': 0, 'MIDFIELDER': 0, 'FORWARD': 0}
    for i, selected in enumerate(individual):
        if selected:
            position = players_data.iloc[i]['position']
            position_counts[position] += 1

    # Mutate by flipping one bit and ensuring constraints
    for _ in range(10):  # Try 10 times
        i = random.randint(0, len(individual) - 1)
        position = players_data.iloc[i]['position']
        if individual[i] == 0 and position_counts[position] < {'DEFENDER': 3, 'MIDFIELDER': 4, 'FORWARD': 3}[position]:
            individual[i] = 1
            return individual,
        elif individual[i] == 1 and position_counts[position] > {'DEFENDER': 3, 'MIDFIELDER': 4, 'FORWARD': 3}[position]:
            individual[i] = 0
            return individual,
    return individual,  # Return original if no successful mutation

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

population, log = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, stats=stats)

# Print the best individual
best_individual = tools.selBest(population, 1)[0]
selected_players = players_data[players_data.index.isin([i for i, selected in enumerate(best_individual) if selected])]
print(selected_players)
print("Total Predicted Points:", sum(selected_players['predicted_points']))
print("Total Cost:", sum(selected_players['cost']))

# Extract and Display Results
best_individual = tools.selBest(population, 1)[0]
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
