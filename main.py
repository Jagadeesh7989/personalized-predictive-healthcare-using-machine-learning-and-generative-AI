import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from src.data_ingestion import DataIngestion
from src.data_transformation import DataTransformation
from src.model_trainer import ModelTrainer

if __name__ == "__main__":

    ingestion = DataIngestion()
    test_path, train_path = ingestion.initiate_data_ingestion()

    transformation = DataTransformation()
    train_arr, test_arr = transformation.initialize_data_transformation(train_path, test_path)

    trainer = ModelTrainer()
    trainer.initiate_model_training(train_arr, test_arr)

# Load dataset
data = pd.read_csv("diabetes.csv")

# Split features & target
X = data.drop("Outcome", axis=1)
y = data["Outcome"]

# Train test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model trained and saved!")