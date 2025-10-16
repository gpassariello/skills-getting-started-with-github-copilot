"""
Tests for the signup functionality of the High School Management System.
"""

import pytest
from fastapi.testclient import TestClient


class TestSignupEndpoint:
    """Test class for signup functionality."""

    def test_signup_success(self, client, reset_activities, sample_email):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up for activity
        response = client.post(f"/activities/{activity_name}/signup?email={sample_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert len(updated_activity["participants"]) == initial_count + 1
        assert sample_email in updated_activity["participants"]

    def test_signup_nonexistent_activity(self, client, sample_email):
        """Test signup for a non-existent activity."""
        response = client.post(f"/activities/Nonexistent Activity/signup?email={sample_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test signup when participant is already registered."""
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_url_encoding(self, client, reset_activities, sample_email):
        """Test signup with URL encoding in activity name."""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_name}/signup?email={sample_email}")
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert sample_email in updated_activity["participants"]

    def test_signup_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email."""
        activity_name = "Chess Club"
        special_email = "test.user%2Btag@mergington.edu"  # URL encoded + character
        expected_email = "test.user+tag@mergington.edu"  # What we expect after decoding
        
        response = client.post(f"/activities/{activity_name}/signup?email={special_email}")
        assert response.status_code == 200
        
        # Verify participant was added (with decoded email)
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert expected_email in updated_activity["participants"]

    def test_signup_multiple_different_activities(self, client, reset_activities, sample_email):
        """Test signing up for multiple different activities."""
        activities = ["Chess Club", "Programming Class", "Art Workshop"]
        
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={sample_email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity in activities:
            assert sample_email in all_activities[activity]["participants"]

    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email parameter."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email=")
        # The API currently accepts empty emails (no validation), so it returns 200
        assert response.status_code == 200
        
        # Verify empty string was added as participant
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert "" in updated_activity["participants"]