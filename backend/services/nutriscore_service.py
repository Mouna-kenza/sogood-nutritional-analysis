import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class NutriscoreService:
    """
    Service pour le calcul du Nutri-Score selon l'algorithme officiel
    """
    
    def __init__(self):
        # Points négatifs (éléments à limiter)
        self.energy_thresholds = [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350]
        self.saturated_fat_thresholds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.sugars_thresholds = [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45]
        self.sodium_thresholds = [90, 180, 270, 360, 450, 540, 630, 720, 810, 900]
        
        # Points positifs (éléments bénéfiques)
        self.fiber_thresholds = [0.9, 1.9, 2.8, 3.7, 4.7]
        self.protein_thresholds = [1.6, 3.2, 4.8, 6.4, 8.0]
        self.fruits_vegetables_thresholds = [40, 60, 80]
        
        # Correspondance score -> grade
        self.grade_thresholds = {
            'A': (-1, 2),
            'B': (3, 10),
            'C': (11, 18),
            'D': (19, 26),
            'E': (27, 100)
        }
    
    def _calculate_points(self, value: float, thresholds: list) -> int:
        """Calcule les points selon les seuils"""
        if value is None:
            return 0
        
        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return i
        return len(thresholds)
    
    def _calculate_negative_points(self, energy: float, saturated_fat: float, 
                                 sugars: float, sodium: float) -> Dict[str, int]:
        """Calcule les points négatifs"""
        return {
            'energy': self._calculate_points(energy, self.energy_thresholds),
            'saturated_fat': self._calculate_points(saturated_fat, self.saturated_fat_thresholds),
            'sugars': self._calculate_points(sugars, self.sugars_thresholds),
            'sodium': self._calculate_points(sodium * 1000, self.sodium_thresholds)  # Conversion g -> mg
        }
    
    def _calculate_positive_points(self, fiber: float, proteins: float, 
                                 fruits_vegetables_percent: float) -> Dict[str, int]:
        """Calcule les points positifs"""
        # Points fibres
        fiber_points = min(self._calculate_points(fiber, self.fiber_thresholds), 5)
        
        # Points protéines
        protein_points = min(self._calculate_points(proteins, self.protein_thresholds), 5)
        
        # Points fruits/légumes/noix
        if fruits_vegetables_percent >= 80:
            fv_points = 5
        elif fruits_vegetables_percent >= 60:
            fv_points = 2
        elif fruits_vegetables_percent >= 40:
            fv_points = 1
        else:
            fv_points = 0
        
        return {
            'fiber': fiber_points,
            'proteins': protein_points,
            'fruits_vegetables': fv_points
        }
    
    def _score_to_grade(self, score: int) -> str:
        """Convertit le score en grade"""
        for grade, (min_score, max_score) in self.grade_thresholds.items():
            if min_score <= score <= max_score:
                return grade
        return 'E'
    
    def calculate_nutriscore(
        self,
        energy_100g: float,
        fat_100g: float,
        saturated_fat_100g: float,
        carbohydrates_100g: float,
        sugars_100g: float,
        fiber_100g: Optional[float] = None,
        proteins_100g: Optional[float] = None,
        salt_100g: Optional[float] = None,
        sodium_100g: Optional[float] = None,
        fruits_vegetables_nuts_percent: float = 0
    ) -> Dict[str, Any]:
        """
        Calcule le Nutri-Score complet
        """
        try:
            # Validation des données d'entrée
            if energy_100g is None or energy_100g < 0:
                raise ValueError("L'énergie doit être un nombre positif")
            
            if saturated_fat_100g is None or saturated_fat_100g < 0:
                raise ValueError("Les acides gras saturés doivent être un nombre positif")
            
            if sugars_100g is None or sugars_100g < 0:
                raise ValueError("Les sucres doivent être un nombre positif")
            
            # Calcul du sodium (priorité au sel si fourni)
            if salt_100g is not None:
                sodium_calc = salt_100g / 2.5  # Conversion sel -> sodium
            elif sodium_100g is not None:
                sodium_calc = sodium_100g
            else:
                sodium_calc = 0
            
            # Valeurs par défaut pour les nutriments optionnels
            fiber_calc = fiber_100g if fiber_100g is not None else 0
            proteins_calc = proteins_100g if proteins_100g is not None else 0
            
            # Calcul des points négatifs
            negative_points = self._calculate_negative_points(
                energy_100g, saturated_fat_100g, sugars_100g, sodium_calc
            )
            total_negative = sum(negative_points.values())
            
            # Calcul des points positifs
            positive_points = self._calculate_positive_points(
                fiber_calc, proteins_calc, fruits_vegetables_nuts_percent
            )
            total_positive = sum(positive_points.values())
            
            # Score final
            final_score = total_negative - total_positive
            
            # Cas particulier : si les points négatifs sont >= 11 et 
            # fruits/légumes < 80%, les protéines ne comptent pas
            if total_negative >= 11 and fruits_vegetables_nuts_percent < 80:
                adjusted_positive = positive_points['fiber'] + positive_points['fruits_vegetables']
                final_score = total_negative - adjusted_positive
                protein_applied = False
            else:
                protein_applied = True
            
            # Grade final
            grade = self._score_to_grade(final_score)
            
            return {
                'nutriscore_grade': grade,
                'nutriscore_score': final_score,
                'details': {
                    'negative_points': {
                        **negative_points,
                        'total': total_negative
                    },
                    'positive_points': {
                        **positive_points,
                        'total': total_positive,
                        'protein_applied': protein_applied
                    },
                    'calculation': {
                        'final_score': final_score,
                        'grade_thresholds': self.grade_thresholds,
                        'calculated_at': datetime.now().isoformat()
                    },
                    'input_values': {
                        'energy_100g': energy_100g,
                        'saturated_fat_100g': saturated_fat_100g,
                        'sugars_100g': sugars_100g,
                        'sodium_100g': sodium_calc,
                        'fiber_100g': fiber_calc,
                        'proteins_100g': proteins_calc,
                        'fruits_vegetables_nuts_percent': fruits_vegetables_nuts_percent
                    }
                }
            }
            
        except Exception as e:
            logging.error(f"Erreur calcul Nutri-Score: {e}")
            raise ValueError(f"Impossible de calculer le Nutri-Score: {e}")
    
    def validate_nutrition_data(self, nutrition_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valide les données nutritionnelles pour le calcul du Nutri-Score
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Vérification des champs obligatoires
            required_fields = ['energy_100g', 'saturated_fat_100g', 'sugars_100g']
            missing_fields = []
            
            for field in required_fields:
                if field not in nutrition_data or nutrition_data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            
            # Vérification des valeurs numériques
            numeric_fields = [
                'energy_100g', 'fat_100g', 'saturated_fat_100g', 'carbohydrates_100g',
                'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g', 'sodium_100g'
            ]
            
            for field in numeric_fields:
                if field in nutrition_data and nutrition_data[field] is not None:
                    try:
                        value = float(nutrition_data[field])
                        if value < 0:
                            return False, f"La valeur de {field} ne peut pas être négative"
                        # Vérification de cohérence (valeurs raisonnables)
                        if field == 'energy_100g' and value > 10000:  # Plus de 10000 kJ semble irréaliste
                            return False, f"Valeur d'énergie irréaliste: {value} kJ"
                        if field in ['fat_100g', 'proteins_100g', 'carbohydrates_100g'] and value > 100:
                            return False, f"Valeur de {field} irréaliste: {value}g (>100g pour 100g de produit)"
                    except (ValueError, TypeError):
                        return False, f"Valeur invalide pour {field}: {nutrition_data[field]}"
            
            # Vérifications de cohérence nutritionnelle
            if 'saturated_fat_100g' in nutrition_data and 'fat_100g' in nutrition_data:
                if (nutrition_data['saturated_fat_100g'] and nutrition_data['fat_100g'] and
                    nutrition_data['saturated_fat_100g'] > nutrition_data['fat_100g']):
                    return False, "Les graisses saturées ne peuvent pas être supérieures aux graisses totales"
            
            if 'sugars_100g' in nutrition_data and 'carbohydrates_100g' in nutrition_data:
                if (nutrition_data['sugars_100g'] and nutrition_data['carbohydrates_100g'] and
                    nutrition_data['sugars_100g'] > nutrition_data['carbohydrates_100g']):
                    return False, "Les sucres ne peuvent pas être supérieurs aux glucides totaux"
            
            return True, "Données valides"
            
        except Exception as e:
            return False, f"Erreur de validation: {str(e)}"
    
    def get_nutriscore_interpretation(self, grade: str) -> Dict[str, str]:
        """
        Retourne l'interprétation du grade Nutri-Score
        """
        interpretations = {
            'A': {
                'quality': 'Très bonne qualité nutritionnelle',
                'description': 'Produit à privilégier pour une alimentation équilibrée',
                'color': '#00A651',
                'recommendation': 'Consommation recommandée'
            },
            'B': {
                'quality': 'Bonne qualité nutritionnelle',
                'description': 'Produit de bonne qualité nutritionnelle',
                'color': '#85B92D',
                'recommendation': 'Consommation modérée recommandée'
            },
            'C': {
                'quality': 'Qualité nutritionnelle correcte',
                'description': 'Produit de qualité nutritionnelle moyenne',
                'color': '#FECB02',
                'recommendation': 'Consommation occasionnelle'
            },
            'D': {
                'quality': 'Qualité nutritionnelle faible',
                'description': 'Produit de qualité nutritionnelle médiocre',
                'color': '#F07F00',
                'recommendation': 'Consommation limitée'
            },
            'E': {
                'quality': 'Mauvaise qualité nutritionnelle',
                'description': 'Produit de mauvaise qualité nutritionnelle',
                'color': '#E63E11',
                'recommendation': 'Consommation très occasionnelle'
            }
        }
        
        return interpretations.get(grade, interpretations['E']) 