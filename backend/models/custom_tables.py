from sqlalchemy import Column, Integer, String, Text, JSON, Float, ForeignKey, Date, Index, Boolean
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import relationship
from backend.utils.database import Base, BaseMixin


class User(Base, BaseMixin):
    """User table"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    mobile = Column(BIGINT, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user_conditions = relationship("UserConditionAssociation", back_populates="user")
    user_foods = relationship("UserFood", back_populates="user")


class HealthCondition(Base, BaseMixin):
    """Health conditions table"""
    __tablename__ = "health_conditions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)

    # Nutrient requirements in grams
    calcium_grm = Column(Float(precision=5))
    carbohydrates_grm = Column(Float(precision=5))
    fats_grm = Column(Float(precision=5))
    fiber_grm = Column(Float(precision=5))
    iron_grm = Column(Float(precision=5))
    magnesium_grm = Column(Float(precision=5))
    potassium_grm = Column(Float(precision=5))
    protein_grm = Column(Float(precision=5))
    sodium_grm = Column(Float(precision=5))
    vitamin_a_grm = Column(Float(precision=5))
    vitamin_b12_grm = Column(Float(precision=5))
    vitamin_c_grm = Column(Float(precision=5))

    # Relationships
    user_conditions = relationship("UserConditionAssociation", back_populates="health_condition")


class Food(Base, BaseMixin):
    """Food items table"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)
    type = Column(String(100))
    ingredients = Column(Text)
    nutrients = Column(JSON)  # Stores all nutrient information
    price = Column(Float(precision=5), nullable=False)

    # Relationships
    user_foods = relationship("UserFood", back_populates="food")

    # Indexes for better search performance
    __table_args__ = (
        Index('idx_food_name_category', 'name', 'category'),
    )


class UserConditionAssociation(Base, BaseMixin):
    """Association between users and their health conditions"""
    __tablename__ = "user_condition_associations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    condition_id = Column(Integer, ForeignKey("health_conditions.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_conditions")
    health_condition = relationship("HealthCondition", back_populates="user_conditions")

    # Unique constraint to prevent duplicate associations
    __table_args__ = (
        Index('idx_user_condition', 'user_id', 'condition_id', unique=True),
    )


class UserFood(Base, BaseMixin):
    """User's favorite/consumed foods"""
    __tablename__ = "user_foods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    is_favorite = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="user_foods")
    food = relationship("Food", back_populates="user_foods")