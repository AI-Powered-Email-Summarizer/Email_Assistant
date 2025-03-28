import pickle

# Load the trained classification model
with open("email_classification.pkl", "rb") as f:
    model = pickle.load(f)

def classify_email(email_body):
    """Classifies an email using the trained model."""
    return model.predict([email_body])[0]
