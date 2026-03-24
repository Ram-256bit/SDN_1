import joblib

# Load your GenClass model
model = joblib.load('genclass_model.pkl')

# If you used OneVsRestClassifier for multi-class (10 attack types)
# You can see the specific rule for each class:
for i, estimator in enumerate(model.estimators_):
    print(f"--- Rule for Class {i} ---")
    print(estimator._program)
    print("\n")