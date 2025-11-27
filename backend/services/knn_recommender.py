import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.models.custom_tables import Food, HealthCondition, UserConditionAssociation
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()


class ImprovedKNNFoodRecommender:
    """KNN-based food recommendation with proper magnitude-based scoring"""

    NUTRIENT_FEATURES = [
        'Carbohydrates', 'Fats', 'Fiber', 'Protein','Sodium', 'Sugar'
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.knn_model = None
        self.food_data = None
        self.feature_matrix = None

    def load_food_data(self, db: Session):
        """Load food data from database"""
        try:
            foods = db.query(Food).all()
            food_list = []

            for food in foods:
                nutrients = food.nutrients if isinstance(food.nutrients, dict) else {}

                food_dict = {
                    'id': food.id,
                    'name': food.name,
                    'category': food.category,
                    'type': food.type,
                    'price': food.price,
                    'ingredients': food.ingredients
                }

                for nutrient in self.NUTRIENT_FEATURES:
                    raw_value = nutrients.get(nutrient, "0")
                    try:
                        cleaned_value = float(str(raw_value).replace("g", "").strip() or 0)
                    except ValueError:
                        LOGGER.warning(f"Invalid nutrient value '{raw_value}' for {nutrient}")
                        cleaned_value = 0.0
                    food_dict[nutrient] = cleaned_value

                food_list.append(food_dict)

            self.food_data = pd.DataFrame(food_list)
            LOGGER.info(f"Loaded {len(self.food_data)} food items")

        except Exception as ex:
            LOGGER.error(f"Error loading food data: {str(ex)}")
            raise

    def get_user_nutrient_requirements(self, user_id: int, db: Session) -> Dict[str, float]:
        """Get aggregated nutrient requirements for user based on health conditions"""
        try:
            user_conditions = db.query(UserConditionAssociation).filter(
                UserConditionAssociation.user_id == user_id
            ).all()

            if not user_conditions:
                LOGGER.warning(f"No health conditions found for user {user_id}")
                return self._get_default_requirements()

            requirements = {nutrient: 0.0 for nutrient in self.NUTRIENT_FEATURES}

            for uc in user_conditions:
                condition = db.query(HealthCondition).filter(
                    HealthCondition.id == uc.condition_id
                ).first()

                if condition:
                    # Only use nutrients available in the new dataset
                    requirements['Carbohydrates'] += condition.carbohydrates_grm or 0
                    requirements['Fats'] += condition.fats_grm or 0
                    requirements['Fiber'] += condition.fiber_grm or 0
                    requirements['Protein'] += condition.protein_grm or 0
                    requirements['Sodium'] += condition.sodium_grm or 0
                    # Calories, Saturated_Fat, Cholesterol, Sugar are not in health conditions table
                    # They will default to 0.0

            num_conditions = len(user_conditions)
            # Average across conditions
            requirements = {k: v / num_conditions for k, v in requirements.items()}

            # Normalize to per-meal scale (assuming 3 meals/day)
            requirements = {k: v / 3 for k, v in requirements.items()}

            LOGGER.info(f"Calculated nutrient requirements for user {user_id}")
            return requirements

        except Exception as ex:
            LOGGER.error(f"Error getting nutrient requirements: {str(ex)}")
            return self._get_default_requirements()

    def _get_default_requirements(self) -> Dict[str, float]:
        """Get default nutrient requirements based on new dataset nutrients"""
        return {
            'Calories': 2000.0,  # Average daily calories
            'Carbohydrates': 275.0,
            'Fats': 70.0,
            'Fiber': 28.0,
            'Protein': 50.0,
            'Sodium': 2.3,
            'Saturated_Fat': 20.0,  # Average daily saturated fat
            'Cholesterol': 300.0,  # Average daily cholesterol
            'Sugar': 50.0  # Average daily sugar
        }

    def calculate_magnitude_score(
            self,
            food_vector: np.ndarray,
            user_vector: np.ndarray,
            weights: np.ndarray,
            method: str = 'cosine'
    ) -> float:
        """
        Calculate magnitude-based similarity score

        Methods:
        - 'cosine': Cosine similarity (measures direction/proportion similarity)
        - 'percentage': Percentage match (ratio-based)
        - 'hybrid': Combines cosine and percentage
        """

        if method == 'cosine':
            # Cosine similarity: measures angle between vectors (0 to 1)
            # Good for: matching nutritional PROPORTIONS regardless of absolute amounts
            weighted_food = food_vector * weights
            weighted_user = user_vector * weights

            # Add small epsilon to avoid division by zero
            epsilon = 1e-10
            norm_food = np.linalg.norm(weighted_food) + epsilon
            norm_user = np.linalg.norm(weighted_user) + epsilon

            cosine_sim = np.dot(weighted_food, weighted_user) / (norm_food * norm_user)
            return max(0, min(1, cosine_sim))  # Clamp to [0, 1]

        elif method == 'percentage':
            # FIXED VERSION
            epsilon = 1e-10

            # Step 1: Calculate percentage for each nutrient (0-1 scale)
            percentages = np.minimum(food_vector, user_vector) / (user_vector + epsilon)
            # = min([10, 20, 6], [20, 40, 12]) / [20, 40, 12]
            # = [10, 20, 6] / [20, 40, 12]
            # = [0.5, 0.5, 0.5]

            # Step 2: Apply weights to the percentages
            weighted_percentages = percentages * weights
            # = [0.5, 0.5, 0.5] * [2, 2, 2]
            # = [1.0, 1.0, 1.0]

            # Step 3: Calculate weighted average
            return np.sum(weighted_percentages) / np.sum(weights)
            # = (1.0 + 1.0 + 1.0) / (2 + 2 + 2)
            # = 3.0 / 6.0
            # = 50%  ← Correct! And now weights have real effect

        elif method == 'hybrid':
            # Hybrid: combines proportion matching and absolute matching
            cosine_score = self.calculate_magnitude_score(food_vector, user_vector, weights, 'cosine')
            percentage_score = self.calculate_magnitude_score(food_vector, user_vector, weights, 'percentage')

            # Weight: 60% proportion match, 40% absolute match
            return 0.6 * cosine_score + 0.4 * percentage_score

        else:
            raise ValueError(f"Unknown scoring method: {method}")

    def recommend_foods(
            self,
            user_id: int,
            db: Session,
            n_recommendations: int = 20,
            category_filter: str = None,
            food_type_filter: str = None,
            scoring_method: str = 'hybrid'  # 'cosine', 'percentage', or 'hybrid'
    ) -> List[Dict[str, Any]]:
        """
        Generate food recommendations using KNN and magnitude-based scoring

        Args:
            user_id: User ID
            db: Database session
            n_recommendations: Number of recommendations to return
            category_filter: Optional category filter
            food_type_filter: Optional food type filter (e.g., 'Veg', 'Non-Veg')
            scoring_method: 'cosine' (proportion-based), 'percentage' (absolute), or 'hybrid'
        """
        try:
            if self.food_data is None:
                self.load_food_data(db)

            # Step 1: Get user nutrient requirements
            requirements = self.get_user_nutrient_requirements(user_id, db)
            user_vector_raw = np.array([float(requirements[f]) for f in self.NUTRIENT_FEATURES])

            # Step 2: Filter food data - ONLY priority nutrients need to be > 0
            PRIORITY_NUTRIENTS = ['Carbohydrates', 'Fats', 'Fiber', 'Protein','Sodium', 'Sugar']
            filtered_food_data = self.food_data[
                self.food_data[PRIORITY_NUTRIENTS].gt(0).all(axis=1)
            ].copy()

            if category_filter:
                filtered_food_data = filtered_food_data[
                    filtered_food_data['category'].str.lower() == category_filter.lower()
                    ]

            if food_type_filter:
                # Filter by food type (exact match, case-insensitive)
                filtered_food_data = filtered_food_data[
                    filtered_food_data['type'].str.lower() == food_type_filter.lower()
                    ]

            if filtered_food_data.empty:
                filter_msg = f"category '{category_filter}'" if category_filter else ""
                if food_type_filter:
                    filter_msg += f" and type '{food_type_filter}'" if filter_msg else f"type '{food_type_filter}'"
                LOGGER.warning(f"No foods found for {filter_msg} with required nutrients")
                return []

            # Step 3: Ensure nutrient columns are numeric
            for nutrient in self.NUTRIENT_FEATURES:
                filtered_food_data[nutrient] = pd.to_numeric(
                    filtered_food_data[nutrient],
                    errors='coerce'
                ).fillna(0)

            # Step 4: Extract raw nutrient matrix
            food_matrix_raw = filtered_food_data[self.NUTRIENT_FEATURES].values

            # Step 5: Use scaled data for KNN (finding similar foods)
            combined = pd.concat([
                filtered_food_data[self.NUTRIENT_FEATURES],
                pd.DataFrame([requirements])
            ], axis=0)
            scaled = self.scaler.fit_transform(combined)
            food_matrix_scaled = scaled[:-1]
            user_vector_scaled = scaled[-1].reshape(1, -1)

            # Step 6: KNN on scaled data to find candidates
            knn_model = NearestNeighbors(
                n_neighbors=min(n_recommendations, len(filtered_food_data)),  # Get more candidates
                algorithm='ball_tree',
                metric='euclidean'
            )
            knn_model.fit(food_matrix_scaled)
            distances, indices = knn_model.kneighbors(user_vector_scaled)

            # Step 7: Calculate magnitude-based match scores using raw values
            # Give priority nutrients higher weight
            weights = np.array([
                2.0 if nutrient in PRIORITY_NUTRIENTS else 1.0
                for nutrient in self.NUTRIENT_FEATURES
            ])

            recommendations = []
            for idx, distance in zip(indices[0], distances[0]):
                food_item = filtered_food_data.iloc[idx]
                food_vector_raw = food_matrix_raw[idx]

                # Calculate magnitude-based score
                match_score = self.calculate_magnitude_score(
                    food_vector_raw,
                    user_vector_raw,
                    weights,
                    method=scoring_method
                )

                recommendations.append({
                    'food_id': int(food_item['id']),
                    'name': food_item['name'],
                    'category': food_item['category'],
                    'type': food_item['type'],
                    'price': float(food_item['price']),
                    'match_score': float(match_score),
                    'distance': float(distance),
                    'nutrients': {
                        nutrient: float(food_item[nutrient])
                        for nutrient in self.NUTRIENT_FEATURES
                    }
                })

            # Sort by match_score (descending)
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)

            # Return top N
            recommendations = recommendations[:n_recommendations]

            LOGGER.info(
                f"Generated {len(recommendations)} recommendations for user {user_id} "
                f"using {scoring_method} scoring"
            )
            return recommendations

        except Exception as ex:
            LOGGER.error(f"Error generating recommendations: {str(ex)}")
            raise


# Usage example
recommender = ImprovedKNNFoodRecommender()