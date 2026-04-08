import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

# Features: Fever, Cough, Headache, Fatigue, Rashes, ChestPain
X = np.array([
    [1,1,0,1,0,0],
    [0,0,1,0,0,0],
    [1,1,1,1,0,0],
    [0,0,0,0,1,0],
    [1,0,0,1,0,1],
    [0,0,0,0,0,0]
])

y = np.array([1,0,1,0,1,0])

model = LogisticRegression()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model created successfully!")