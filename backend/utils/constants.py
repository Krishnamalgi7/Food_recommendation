from enum import Enum


class Nutrient(Enum):
    """
    Represents the nutrients actively tracked by the recommendation engine.
    These correspond to the NUTRIENT_FEATURES list in knn_recommender.py
    and the columns in the health_conditions table.
    """
    CARBOHYDRATES = 'Carbohydrates'
    FATS = 'Fats'
    FIBER = 'Fiber'
    PROTEIN = 'Protein'
    SODIUM = 'Sodium'
    SUGAR = 'Sugar'


class HealthCondition(Enum):
    """
    Represents different health conditions tracked.
    """
    SKIN = 'Skin'
    BP = 'BP'
    DIABETES = 'Diabetes'
    HEART = 'Heart'
    KIDNEY = 'Kidney'
    LIVER = 'Liver'
    LUNG = 'Lung'
    PCOD = 'PCOD'
    GASTRO = "Gastro"