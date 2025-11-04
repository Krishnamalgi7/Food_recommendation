from enum import Enum


class Nutrient(Enum):
    """
    Represents the key nutrients tracked.
    """
    CALCIUM = 'Calcium'
    CARBOHYDRATES = 'Carbohydrates'
    FATS = 'Fats'
    FIBER = 'Fiber'
    IRON = 'Iron'
    MAGNESIUM = 'Magnesium'
    POTASSIUM = 'Potassium'
    PROTEIN = 'Protein'
    SODIUM = 'Sodium'
    VITAMIN_A = 'Vitamin_A'
    VITAMIN_B12 = 'Vitamin_B12'
    VITAMIN_C = 'Vitamin_C'


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