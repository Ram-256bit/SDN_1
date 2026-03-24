import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.multiclass import OneVsRestClassifier # <-- The magic wrapper
from gplearn.genetic import SymbolicClassifier
import joblib

print("Loading UNSW-NB15 Parquet dataset...")
df = pd.read_parquet('UNSW_NB15_training-set.parquet')

features = ['sbytes', 'dbytes', 'sload', 'dload', 'rate']
df = df.dropna(subset=features + ['attack_cat'])

X = df[features]
y_text = df['attack_cat']

print("Encoding text labels to numeric values...")
encoder = LabelEncoder()
y = encoder.fit_transform(y_text)

class_mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
print(f"Detected Classes: {class_mapping}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

print(f"Training GenClass (One-vs-Rest) on {len(X_train)} samples. This may take a few minutes...")

# 1. Initialize the Base Genetic Classifier
base_genclass = SymbolicClassifier(
    population_size=150,  # Reduced slightly for faster 10x training
    generations=5,        # Reduced slightly for faster 10x training
    tournament_size=20,
    stopping_criteria=0.01,
    p_crossover=0.7,
    p_subtree_mutation=0.1,
    p_hoist_mutation=0.05,
    p_point_mutation=0.1,
    verbose=0,            # Turned off to keep terminal clean during multi-training
    random_state=42
)

# 2. Wrap it to support all 10 classes simultaneously 
genclass_model = OneVsRestClassifier(base_genclass, n_jobs=-1) # n_jobs=-1 uses all CPU cores

# Train the model
genclass_model.fit(X_train_scaled, y_train)

print("Training complete! Saving model assets...")
joblib.dump(genclass_model, 'genclass_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(encoder, 'encoder.pkl')

print("Models Saved successfully")