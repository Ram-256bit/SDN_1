import random
import operator
import pandas as pd
import numpy as np
import time

# --- CONFIGURATION ---
POPULATION_SIZE = 50   # Increased for better diversity
GENERATIONS = 15       # More time to learn
TOURNAMENT_SIZE = 5    # Stronger selection pressure
MUTATION_RATE = 0.3    # More random changes to avoid getting stuck
DATASET_SAMPLE = 500   

# --- 1. PRIMITIVES ---
# Safe division to avoid errors
def safe_div(a, b):
    return a / b if b != 0 else 1

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    # Removed relational operators (<, >) from inside the tree 
    # to keep the output numerical, not boolean.
}

class Node:
    pass

class BinaryOp(Node):
    def __init__(self, op_symbol, left, right):
        self.op_symbol = op_symbol
        self.op_func = OPS[op_symbol]
        self.left = left
        self.right = right

    def evaluate(self, row):
        return self.op_func(self.left.evaluate(row), self.right.evaluate(row))

    def __str__(self):
        return f"({self.left} {self.op_symbol} {self.right})"

class FeatureLeaf(Node):
    def __init__(self, feature_name):
        self.feature_name = feature_name

    def evaluate(self, row):
        return float(row[self.feature_name])

    def __str__(self):
        return self.feature_name

class ConstantLeaf(Node):
    def __init__(self, value):
        self.value = value

    def evaluate(self, row):
        return self.value

    def __str__(self):
        return f"{self.value:.2f}"

# --- 2. GENETIC PROGRAMMING LOGIC ---

def generate_random_tree(depth, features):
    if depth == 0 or random.random() < 0.3:
        if random.random() < 0.7:
            return FeatureLeaf(random.choice(features))
        else:
            return ConstantLeaf(random.uniform(-10, 10))
    else:
        op = random.choice(list(OPS.keys()))
        left = generate_random_tree(depth - 1, features)
        right = generate_random_tree(depth - 1, features)
        return BinaryOp(op, left, right)

def calculate_fitness(tree, data, labels):
    """
    Evaluates the rule. 
    Rule Output > 0  => Predicts 'Attack' (Label 1)
    Rule Output <= 0 => Predicts 'Normal' (Label 0)
    """
    correct = 0
    total = len(data)
    
    # Pre-calculate to speed up
    # We apply the tree to every row
    try:
        # Vectorized-like evaluation is hard with this tree structure, 
        # so we iterate.
        for idx, row in data.iterrows():
            try:
                val = tree.evaluate(row)
                prediction = 1 if val > 0 else 0
                
                # Compare with actual label
                # Ensure label is integer (0 or 1)
                actual = int(labels.iloc[idx])
                
                if prediction == actual:
                    correct += 1
            except (OverflowError, ValueError, ZeroDivisionError):
                continue # Skip bad calculations
                
        return correct / total
    except Exception as e:
        return 0.0

def crossover(parent1, parent2):
    # Simple subtree swap simulation
    if random.random() < 0.5:
        return parent1
    else:
        return parent2

def mutate(tree, features):
    # Return a completely new small tree occasionally
    if random.random() < MUTATION_RATE:
        return generate_random_tree(2, features)
    return tree

# --- 3. MAIN EXECUTION ---

def run_genclass_demo():
    print("="*60)
    print(" GENCLASS EVOLUTIONARY ENGINE")
    print("="*60)
    
    # A. Load Data
    print("Loading data sample...")
    try:
        # Try loading real data
        df = pd.read_parquet('UNSW_NB15_training-set.parquet')
        
        # FIX: Ensure we select columns that are actually numbers
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Ensure target column exists and is separated
        if 'attack_cat' in df.columns:
            # Create binary label: 1 if attack, 0 if Normal
            df['label'] = df['attack_cat'].apply(lambda x: 0 if x == 'Normal' else 1)
        elif 'label' in df.columns:
            pass # Already has label
        else:
            raise ValueError("No label column found!")

        # Remove target cols from features
        features = [c for c in numeric_cols if c not in ['label', 'id', 'attack_cat']]
        
        # Sample data for speed
        df_sample = df.sample(min(DATASET_SAMPLE, len(df))).reset_index(drop=True)
        labels = df_sample['label']
        data = df_sample[features]
        
    except Exception as e:
        print(f"Warning: {e}")
        print("Using Synthetic Data for Demo...")
        # Fallback to dummy data if file fails
        data = pd.DataFrame({
            'dur': np.random.rand(100) * 10,
            'sbytes': np.random.randint(0, 10000, 100),
            'dbytes': np.random.randint(0, 10000, 100)
        })
        # Generate labels where high sbytes = Attack (to make it learnable)
        labels = pd.Series([1 if x > 5000 else 0 for x in data['sbytes']])
        features = data.columns.tolist()

    print(f"Training on {len(data)} records with {len(features)} features.")
    print("-" * 60)

    # B. Initialize Population
    population = [generate_random_tree(3, features) for _ in range(POPULATION_SIZE)]

    # C. Evolution Loop
    best_ever_rule = None
    best_ever_score = 0.0

    for generation in range(GENERATIONS):
        # 1. Evaluate Fitness
        scored_population = []
        for tree in population:
            score = calculate_fitness(tree, data, labels)
            scored_population.append((tree, score))

        # Sort: Highest accuracy first
        scored_population.sort(key=lambda x: x[1], reverse=True)
        
        best_rule, best_score = scored_population[0]
        
        # Track global best
        if best_score > best_ever_score:
            best_ever_score = best_score
            best_ever_rule = best_rule

        # # Visualization of progress
        # bar = "#" * int(best_score * 20)
        # print(f"Gen {generation+1:02d}: Acc={best_score*100:5.1f}% | {bar:<20} | Rule: {str(best_rule)[:40]}...")

        # Visualization of progress
        bar = "#" * int(best_score * 20)
        
        # Check if we improved
        if best_score > best_ever_score:
            prefix = ">>> IMPROVED!" 
            best_ever_score = best_score # Update global best tracker
            best_ever_rule = best_rule
        else:
            prefix = "             "

        print(f"Gen {generation+1:02d}: Acc={best_score*100:5.1f}% | {bar:<20} {prefix} | Rule: {str(best_rule)[:50]}")


        # 2. Selection & Breeding for Next Gen
        next_gen = [best_rule] # Elitism (keep the best)
        
        # Simple Tournament Selection
        while len(next_gen) < POPULATION_SIZE:
            # Pick 2 random parents
            candidates = random.sample(scored_population, TOURNAMENT_SIZE)
            parent1 = max(candidates, key=lambda x: x[1])[0]
            
            # Mutate and add to new population
            child = mutate(parent1, features)
            next_gen.append(child)
            
        population = next_gen

    print("\n" + "="*60)
    print(" EVOLUTION COMPLETE")
    print("="*60)
    print(f"Final Best Accuracy: {best_ever_score*100:.2f}%")
    print(f"Evolved Logic: IF ({best_ever_rule}) > 0 THEN ATTACK")
    print("="*60)

if __name__ == "__main__":
    run_genclass_demo()