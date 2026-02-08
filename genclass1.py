import random
import operator
import pandas as pd
import numpy as np
import time

# --- CONFIGURATION ---
POPULATION_SIZE = 50   
GENERATIONS = 20       
TOURNAMENT_SIZE = 5    
MUTATION_RATE = 0.2
STAGNATION_LIMIT = 3   # Triggers "Rescue" if stuck for 3 gens

# --- 1. PRIMITIVES ---
OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
}

class Node: pass

class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.func = OPS[op]
        self.left = left
        self.right = right
    def evaluate(self, row):
        return self.func(self.left.evaluate(row), self.right.evaluate(row))
    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

class FeatureLeaf(Node):
    def __init__(self, name): self.name = name
    def evaluate(self, row): return float(row[self.name])
    def __str__(self): return self.name

class ConstantLeaf(Node):
    def __init__(self, val): self.val = val
    def evaluate(self, row): return self.val
    def __str__(self): return f"{self.val:.2f}"

# --- 2. GP LOGIC ---
def generate_random_tree(depth, features):
    if depth == 0 or random.random() < 0.3:
        if random.random() < 0.7: return FeatureLeaf(random.choice(features))
        else: return ConstantLeaf(random.uniform(-10, 10))
    op = random.choice(list(OPS.keys()))
    return BinaryOp(op, generate_random_tree(depth-1, features), generate_random_tree(depth-1, features))

def calculate_fitness(tree, data, labels):
    try:
        correct = 0
        for i, row in data.iterrows():
            pred = 1 if tree.evaluate(row) > 0 else 0
            if pred == labels.iloc[i]: correct += 1
        return correct / len(data)
    except: return 0.0

def mutate(tree, features, rate=MUTATION_RATE):
    if random.random() < rate: return generate_random_tree(2, features)
    return tree

# --- 3. EXECUTION ---
def run_genclass_demo():
    print("="*60)
    print(" GENCLASS EVOLUTIONARY ENGINE")
    print("="*60)
    
    # Load Data (Simulate if file missing)
    try:
        df = pd.read_parquet('UNSW_NB15_training-set.parquet')
        numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        features = [c for c in numeric if c not in ['id', 'label', 'attack_cat']]
        df['label'] = df['attack_cat'].apply(lambda x: 0 if x == 'Normal' else 1)
        data = df.sample(500).reset_index(drop=True)
    except:
        # Fallback: Create a solvable pattern for the demo
        print("(!) Using Synthetic Data for Demo Mode")
        data = pd.DataFrame({
            'dur': np.random.rand(500) * 10,
            'sbytes': np.random.randint(0, 10000, 500),
            'dbytes': np.random.randint(0, 10000, 500)
        })
        # Rule: If sbytes > 4000, it's an attack. Easy to learn.
        data['label'] = [1 if x > 4000 else 0 for x in data['sbytes']]
        features = ['dur', 'sbytes', 'dbytes']

    labels = data['label']
    print(f"Training on {len(data)} records. Features: {len(features)}")
    print("-" * 60)

    # Init Population
    population = [generate_random_tree(3, features) for _ in range(POPULATION_SIZE)]
    best_ever_score = 0.0
    stagnant_gens = 0

    for gen in range(GENERATIONS):
        # Evaluate
        scored = [(t, calculate_fitness(t, data, labels)) for t in population]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        current_best_rule, current_best_score = scored[0]

        # Check Progress
        if current_best_score > best_ever_score:
            prefix = ">>> IMPROVED!"
            best_ever_score = current_best_score
            best_ever_rule = current_best_rule
            stagnant_gens = 0 # Reset counter
        else:
            prefix = ""
            stagnant_gens += 1

        # Visualization
        bar = "#" * int(current_best_score * 20)
        rule_str = str(current_best_rule)
        # Truncate rule string for clean display
        if len(rule_str) > 45: rule_str = rule_str[:42] + "..."
            
        print(f"Gen {gen+1:02d}: Acc={current_best_score*100:5.1f}% | {bar:<20} {prefix:<13} | Rule: {rule_str}")

        # AUTO-RESCUE: Stagnation Check
        current_mutation_rate = MUTATION_RATE
        if stagnant_gens >= STAGNATION_LIMIT:
            # Force diversity!
            print(f"        [!] Stagnation detected. Injecting high variance...")
            current_mutation_rate = 0.8 # Massive mutation
            stagnant_gens = 0

        # Breeding
        next_gen = [current_best_rule] # Elitism
        while len(next_gen) < POPULATION_SIZE:
            # Tournament
            cands = random.sample(scored, TOURNAMENT_SIZE)
            parent = max(cands, key=lambda x: x[1])[0]
            # Mutate child
            child = mutate(parent, features, rate=current_mutation_rate)
            next_gen.append(child)
        population = next_gen

    print("\n" + "="*60)
    print(" EVOLUTION COMPLETE")
    print("="*60)
    print(f"Final Best Accuracy: {best_ever_score*100:.2f}%")
    print(f"Evolved Logic: IF ({best_ever_rule}) > 0 THEN ATTACK")
    print("="*60)

if __name__ == "__main__":
    run_genclass_demo()S