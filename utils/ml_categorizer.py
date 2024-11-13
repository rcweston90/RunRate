from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib
import os
from typing import List, Optional

class MLCategorizer:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                strip_accents='unicode',
                lowercase=True,
                stop_words='english'
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                random_state=42
            ))
        ])
        self.model_path = 'assets/ml_model.joblib'
        self.min_samples_per_category = 5
        self._load_model()

    def _load_model(self) -> None:
        """Load pre-trained model if it exists"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                pass

    def _save_model(self) -> None:
        """Save trained model"""
        joblib.dump(self.model, self.model_path)

    def train(self, descriptions: List[str], categories: List[str]) -> bool:
        """Train the model with transaction descriptions and their categories"""
        if len(descriptions) != len(categories):
            return False

        # Convert to DataFrame for easier processing
        df = pd.DataFrame({
            'Description': descriptions,
            'Category': categories
        })

        # Check if we have enough samples per category
        category_counts = df['Category'].value_counts()
        valid_categories = category_counts[category_counts >= self.min_samples_per_category].index
        df = df[df['Category'].isin(valid_categories)]

        if len(df) < 10:  # Minimum total samples
            return False

        self.model.fit(df['Description'], df['Category'])
        self._save_model()
        return True

    def predict(self, descriptions: List[str]) -> List[str]:
        """Predict categories for given descriptions"""
        try:
            return self.model.predict(descriptions)
        except:
            return ['Other'] * len(descriptions)

    def predict_proba(self, descriptions: List[str]) -> List[float]:
        """Get prediction probabilities for given descriptions"""
        try:
            probas = self.model.predict_proba(descriptions)
            return [max(proba) for proba in probas]
        except:
            return [0.0] * len(descriptions)
