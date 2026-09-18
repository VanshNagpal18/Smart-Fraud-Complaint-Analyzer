import pandas as pd
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv("complaints.csv")

required_columns = ["Complaint", "Fraud_Category", "IT_Act_Section"]

for col in required_columns:
    if col not in df.columns:
        raise Exception(f"Column '{col}' not found in dataset.")

df = df.dropna()
df = df.drop_duplicates(subset=["Complaint"])

category_counts = df["Fraud_Category"].value_counts()
single_instance_categories = category_counts[category_counts == 1].index

df_filtered = df[~df["Fraud_Category"].isin(single_instance_categories)]

X = df_filtered["Complaint"]
y = df_filtered["Fraud_Category"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# -----------------------------
# TF-IDF
# -----------------------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1,2)
)

X_vector = vectorizer.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_vector,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

model = LinearSVC()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("\nModel Accuracy : {:.2f}%".format(accuracy*100))
print("\nClassification Report\n")
print(classification_report(
    y_test,
    y_pred,
    target_names=label_encoder.classes_
))


pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(label_encoder, open("label_encoder.pkl", "wb"))

mapping = {}

for _, row in df_filtered.iterrows(): # Use df_filtered here as well
    mapping[row["Fraud_Category"]] = row["IT_Act_Section"]

with open("mapping.json", "w") as f:
    json.dump(mapping, f, indent=4)

print("\nFiles Saved Successfully")
print("model.pkl")
print("vectorizer.pkl")
print("label_encoder.pkl")
print("mapping.json")