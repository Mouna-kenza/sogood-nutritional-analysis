import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

from backend.config import settings
from backend.schemas.product import MLPredictionRequest, MLPredictionResponse

logger = logging.getLogger(__name__)

class MLService:
    """
    Service de Machine Learning pour la prédiction nutritionnelle
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """
        Charge le modèle ML depuis le fichier
        """
        try:
            model_path = Path(settings.ML_MODEL_PATH)
            if model_path.exists():
                self.model = joblib.load(model_path)
                self.is_trained = True
                logger.info(f"✅ Modèle ML chargé depuis {model_path}")
            else:
                logger.warning(f"⚠️ Modèle ML non trouvé: {model_path}")
                self.is_trained = False
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle ML: {e}")
            self.is_trained = False
    
    def predict_nutriscore(self, nutrition_data: Dict[str, float]) -> MLPredictionResponse:
        """
        Prédit le Nutri-Score basé sur les données nutritionnelles
        """
        if not self.is_trained:
            raise ValueError("Modèle ML non disponible")
        
        try:
            # Préparation des features
            features = self._prepare_features(nutrition_data)
            
            # Prédiction
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            
            # Préparation de la réponse
            grade_mapping = ['A', 'B', 'C', 'D', 'E']
            predicted_grade = grade_mapping[prediction]
            confidence = max(probabilities)
            
            prob_dict = {
                grade: float(prob) for grade, prob in zip(grade_mapping, probabilities)
            }
            
            return MLPredictionResponse(
                predicted_nutriscore=predicted_grade,
                confidence=float(confidence),
                probabilities=prob_dict
            )
            
        except Exception as e:
            logger.error(f"Erreur prédiction ML: {e}")
            raise ValueError(f"Impossible de faire la prédiction: {e}")
    
    def _prepare_features(self, nutrition_data: Dict[str, float]) -> List[float]:
        """
        Prépare les features pour le modèle ML
        """
        # Features de base pour la prédiction du Nutri-Score
        features = [
            nutrition_data.get('energy_100g', 0),
            nutrition_data.get('fat_100g', 0),
            nutrition_data.get('saturated_fat_100g', 0),
            nutrition_data.get('carbohydrates_100g', 0),
            nutrition_data.get('sugars_100g', 0),
            nutrition_data.get('fiber_100g', 0),
            nutrition_data.get('proteins_100g', 0),
            nutrition_data.get('salt_100g', 0)
        ]
        
        return features
    
    def train_model(self, training_data: pd.DataFrame):
        """
        Entraîne le modèle ML (à implémenter selon vos besoins)
        """
        # TODO: Implémenter l'entraînement du modèle
        # Ceci sera fait dans un script séparé
        pass
    
    def evaluate_model(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Évalue les performances du modèle
        """
        if not self.is_trained:
            raise ValueError("Modèle ML non disponible")
        
        # TODO: Implémenter l'évaluation
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        } 