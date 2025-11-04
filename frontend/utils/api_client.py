import requests
from typing import Optional, Dict, Any
import streamlit as st


class APIClient:
    """Client for interacting with the backend API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}

        if include_auth and st.session_state.get('access_token'):
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"

        return headers

    def _handle_error(self, response):
        """Handle API errors with detailed messages"""
        try:
            error = response.json()
            if 'detail' in error:
                if isinstance(error['detail'], list):
                    errors = [f"{err.get('loc', [''])[- 1]}: {err.get('msg', '')}" for err in error['detail']]
                    raise Exception("Validation errors:\n" + "\n".join(errors))
                else:
                    raise Exception(str(error['detail']))
        except:
            pass
        response.raise_for_status()

    def register_user(self, name: str, password: str, dob: str, mobile: int) -> Dict[str, Any]:
        """Register a new user (basic)"""
        url = f"{self.base_url}/users/"
        data = {
            "name": name,
            "password": password,
            "dob": dob,
            "mobile": int(mobile)
        }

        response = requests.post(url, json=data, headers=self._get_headers(include_auth=False))
        if response.status_code != 201:
            self._handle_error(response)
        return response.json()

    def register_user_with_condition(self, name: str, password: str, dob: str, mobile: int, condition_id: int) -> Dict[
        str, Any]:
        """Register a new user with health condition"""
        url = f"{self.base_url}/users/register-with-condition"
        data = {
            "name": name,
            "password": password,
            "dob": dob,
            "mobile": int(mobile),
            "condition_id": condition_id
        }

        response = requests.post(url, json=data, headers=self._get_headers(include_auth=False))
        if response.status_code != 201:
            self._handle_error(response)
        return response.json()

    def login(self, name: str, password: str) -> Dict[str, Any]:
        """Login user"""
        url = f"{self.base_url}/auth/login"
        data = {
            "name": name,
            "password": password
        }

        response = requests.post(url, json=data, headers=self._get_headers(include_auth=False))
        response.raise_for_status()
        return response.json()

    def logout(self) -> Dict[str, Any]:
        """Logout user"""
        url = f"{self.base_url}/auth/logout"

        try:
            response = requests.post(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as ex:
            # Even if logout fails on backend, we'll clear local session
            return {"message": "Logged out locally"}

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        url = f"{self.base_url}/auth/me"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_health_conditions(self) -> list:
        """Get all health conditions"""
        url = f"{self.base_url}/health_condition/"
        response = requests.get(url, headers=self._get_headers(include_auth=False))
        response.raise_for_status()
        return response.json()

    def get_user_conditions(self) -> Dict[str, Any]:
        """Get user's health conditions"""
        url = f"{self.base_url}/recommendations/user-conditions"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def add_user_conditions(self, condition_ids: list) -> Dict[str, Any]:
        """Add health conditions to user"""
        url = f"{self.base_url}/recommendations/user-conditions"
        data = {"condition_ids": condition_ids}

        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_all_foods(self, page: int = 1, limit: int = 100, food_type: str = None, category: str = None) -> Dict[
        str, Any]:
        """Get all foods with pagination and filters"""
        url = f"{self.base_url}/food/all"
        params = {
            "page": page,
            "limit": limit
        }
        if food_type:
            params["food_type"] = food_type
        if category:
            params["category"] = category

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_recommendations(self, n_recommendations: int = 100, category_filter: Optional[str] = None,
                            food_type: Optional[str] = None) -> Dict[str, Any]:
        """Get food recommendations"""
        url = f"{self.base_url}/recommendations/generate"
        data = {
            "n_recommendations": n_recommendations,
            "category_filter": category_filter,
            "food_type": food_type
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_food_categories(self) -> Dict[str, Any]:
        """Get list of available food categories"""
        url = f"{self.base_url}/recommendations/categories"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def search_food(self, name: str) -> list:
        """Search food by name"""
        url = f"{self.base_url}/food/{name}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


api_client = APIClient()