import json
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load datasets
train_path = r"D:\Prooject\FreeFinance-main (1)\FreeFinance-main\database\loan_model\loan_train.csv"
test_path = r"D:\Prooject\FreeFinance-main (1)\FreeFinance-main\database\loan_model\loan_test.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Handle missing values
for col in ['Gender', 'Married', 'Self_Employed', 'Dependents', 'Property_Area']:
    train_df[col].fillna(train_df[col].mode()[0], inplace=True)
    test_df[col].fillna(test_df[col].mode()[0], inplace=True)

for col in ['LoanAmount', 'Loan_Amount_Term', 'Credit_History']:
    train_df[col].fillna(train_df[col].median(), inplace=True)
    test_df[col].fillna(test_df[col].median(), inplace=True)

# Encode categorical features
encoder = LabelEncoder()
categorical_cols = ['Gender', 'Married', 'Education', 'Self_Employed', 'Property_Area', 'Dependents']
for col in categorical_cols:
    train_df[col] = encoder.fit_transform(train_df[col])
    test_df[col] = encoder.transform(test_df[col])

# Define features and target
X = train_df.drop(columns=['Loan_ID', 'Loan_Status'])
y = train_df['Loan_Status']
X_test = test_df.drop(columns=['Loan_ID'])

# Save feature names
joblib.dump(X.columns.tolist(),r"D:/Prooject/FreeFinance-main (1)/FreeFinance-main/database/loan_model/loan_features.pkl")

# Scale numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_test_scaled = scaler.transform(X_test)

# Save scaler
joblib.dump(scaler,r"D:/Prooject/FreeFinance-main (1)/FreeFinance-main/database/loan_model/loan_scaler.pkl")

# Split data for validation
X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train a RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model,r"D:/Prooject/FreeFinance-main (1)/FreeFinance-main/database/loan_model/loan_model.pkl")

# Save label encoder classes
joblib.dump(encoder.classes_,r"D:/Prooject/FreeFinance-main (1)/FreeFinance-main/database/loan_model/loan_encoder_classes.pkl")

# Validate model
y_pred = model.predict(X_val)
accuracy = accuracy_score(y_val, y_pred)
report = classification_report(y_val, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
print("Classification Report:\n", report)

# Predict on test data
test_predictions = model.predict(X_test_scaled)

test_df['Loan_Status'] = test_predictions
test_df[['Loan_ID', 'Loan_Status']].to_csv(r"D:\Prooject\FreeFinance-main (1)\FreeFinance-main\database\loan_prediction.csv")
print("Predictions saved to loan_predictions.csv")
