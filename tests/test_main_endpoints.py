"""
Tests for the main API endpoints of the High School Management System.
"""

import pytest
from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test class for main API endpoints."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client, reset_activities):
        """Test getting all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        
        # Check that Chess Club exists and has correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        assert chess_club["max_participants"] == 12

    def test_activities_structure(self, client, reset_activities):
        """Test that all activities have the correct structure."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0

    def test_activities_participants_are_emails(self, client, reset_activities):
        """Test that all participants are valid email formats."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert participant.endswith("@mergington.edu")