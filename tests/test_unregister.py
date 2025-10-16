"""
Tests for the unregister functionality of the High School Management System.
"""

import pytest
from fastapi.testclient import TestClient


class TestUnregisterEndpoint:
    """Test class for unregister functionality."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"  # Existing participant
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        assert email_to_remove in response.json()[activity_name]["participants"]
        
        # Unregister from activity
        response = client.delete(f"/activities/{activity_name}/unregister?email={email_to_remove}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert len(updated_activity["participants"]) == initial_count - 1
        assert email_to_remove not in updated_activity["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity."""
        email = "test@mergington.edu"
        
        response = client.delete(f"/activities/Nonexistent Activity/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_non_participant(self, client, reset_activities):
        """Test unregister when participant is not registered."""
        activity_name = "Chess Club"
        non_participant_email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={non_participant_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregister with URL encoding in activity name."""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        email_to_remove = "emma@mergington.edu"  # Existing participant
        
        response = client.delete(f"/activities/{encoded_name}/unregister?email={email_to_remove}")
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert email_to_remove not in updated_activity["participants"]

    def test_unregister_special_characters_in_email(self, client, reset_activities):
        """Test unregister with special characters in email."""
        activity_name = "Chess Club"
        special_email = "test.user+tag@mergington.edu"
        
        # First sign up the user
        response = client.post(f"/activities/{activity_name}/signup?email={special_email}")
        assert response.status_code == 200
        
        # Then unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={special_email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert special_email not in updated_activity["participants"]

    def test_unregister_last_participant(self, client, reset_activities):
        """Test unregistering the last participant from an activity."""
        activity_name = "Math Olympiad"
        
        # Get all current participants
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"].copy()
        
        # Unregister all participants
        for email in participants:
            response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify activity has no participants
        response = client.get("/activities")
        updated_activity = response.json()[activity_name]
        assert len(updated_activity["participants"]) == 0

    def test_signup_then_unregister_cycle(self, client, reset_activities, sample_email):
        """Test signup followed by unregister."""
        activity_name = "Art Workshop"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        # Sign up
        response = client.post(f"/activities/{activity_name}/signup?email={sample_email}")
        assert response.status_code == 200
        
        # Verify signup worked
        response = client.get("/activities")
        assert sample_email in response.json()[activity_name]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={sample_email}")
        assert response.status_code == 200
        
        # Verify back to original state
        response = client.get("/activities")
        final_participants = response.json()[activity_name]["participants"]
        assert final_participants == initial_participants
        assert sample_email not in final_participants

    def test_unregister_empty_email(self, client, reset_activities):
        """Test unregister with empty email parameter."""
        activity_name = "Chess Club"
        
        # First add an empty email participant to test removal
        response = client.post(f"/activities/{activity_name}/signup?email=")
        assert response.status_code == 200
        
        # Now try to unregister the empty email
        response = client.delete(f"/activities/{activity_name}/unregister?email=")
        # The API currently accepts empty emails, so this should work
        assert response.status_code == 200