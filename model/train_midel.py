import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import pickle

# Load dataset
df = pd.read_csv('heart_2020_cleaned.csv')
df = df.drop(columns='Race')  # Ensure 'Race' column is dropped
df = df.replace({'No': 0, 'Yes': 1})
df['Sex'] = df['Sex'].replace({'Female': 0, 'Male': 1})
df['AgeCategory'] = df['AgeCategory'].replace({
    '18-24': 0, '25-29': 1, '30-34': 2, '35-39': 3,
    '40-44': 4, '45-49': 5, '50-54': 6, '55-59': 7,
    '60-64': 8, '65-69': 9, '70-74': 10, '75-79': 11,
    '80 or older': 12
})
df['Diabetic'] = df['Diabetic'].replace({
    'No': 0, 'No, borderline diabetes': 0,
    'Yes': 1, 'Yes (during pregnancy)': 1
})
df['GenHealth'] = df['GenHealth'].replace({
    'Poor': 0, 'Fair': 1, 'Good': 2,
    'Very good': 3, 'Excellent': 4
})

X = df.drop(columns='HeartDisease')
y = df['HeartDisease']

# Save the feature names
feature_names = X.columns.tolist()
print("Features used for training:", feature_names)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# Save model and feature names
with open('heart_disease_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('feature_names.pkl', 'wb') as f:
    pickle.dump(feature_names, f)
