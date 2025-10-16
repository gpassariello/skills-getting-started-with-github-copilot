"""
Integration tests for the High School Management System.
"""

import pytest
from fastapi.testclient import TestClient


class TestIntegration:
    """Test class for integration scenarios."""

    def test_complete_activity_lifecycle(self, client, reset_activities):
        """Test complete lifecycle of activity management."""
        activity_name = "Drama Club"
        test_emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        initial_count = len(initial_participants)
        
        # Sign up multiple students
        for email in test_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        current_participants = response.json()[activity_name]["participants"]
        assert len(current_participants) == initial_count + len(test_emails)
        
        for email in test_emails:
            assert email in current_participants
        
        # Unregister some students
        emails_to_remove = test_emails[:2]
        for email in emails_to_remove:
            response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify correct students were removed
        response = client.get("/activities")
        final_participants = response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count + 1  # Only one test email should remain
        
        for email in emails_to_remove:
            assert email not in final_participants
        
        assert test_emails[2] in final_participants  # Last test email should still be there

    def test_activity_capacity_management(self, client, reset_activities):
        """Test behavior when activities reach capacity."""
        activity_name = "Math Olympiad"  # Has max_participants: 10
        
        # Get current state
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        current_count = len(activity_data["participants"])
        max_participants = activity_data["max_participants"]
        spots_available = max_participants - current_count
        
        # Fill remaining spots
        test_emails = []
        for i in range(spots_available):
            email = f"student{i}@mergington.edu"
            test_emails.append(email)
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify activity is now full
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        assert len(activity_data["participants"]) == max_participants
        
        # Try to add one more (should still work as there's no capacity check in the API)
        overflow_email = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
        assert response.status_code == 200  # API doesn't enforce capacity limits
        
        # Verify it was added (over capacity)
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        assert len(activity_data["participants"]) == max_participants + 1
        assert overflow_email in activity_data["participants"]

    def test_multiple_activities_same_student(self, client, reset_activities):
        """Test student signing up for multiple activities."""
        student_email = "busy.student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Workshop", "Science Club"]
        
        # Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={student_email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity in activities_to_join:
            assert student_email in all_activities[activity]["participants"]
        
        # Unregister from some activities
        activities_to_leave = activities_to_join[:2]
        for activity in activities_to_leave:
            response = client.delete(f"/activities/{activity}/unregister?email={student_email}")
            assert response.status_code == 200
        
        # Verify student is removed from correct activities
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity in activities_to_leave:
            assert student_email not in all_activities[activity]["participants"]
        
        for activity in activities_to_join[2:]:
            assert student_email in all_activities[activity]["participants"]

    def test_concurrent_operations_same_activity(self, client, reset_activities):
        """Test multiple operations on the same activity."""
        activity_name = "Basketball Club"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        # Perform multiple operations
        new_students = ["new1@mergington.edu", "new2@mergington.edu"]
        existing_student = initial_participants[0] if initial_participants else None
        
        # Add new students
        for email in new_students:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Remove existing student (if any)
        if existing_student:
            response = client.delete(f"/activities/{activity_name}/unregister?email={existing_student}")
            assert response.status_code == 200
        
        # Verify final state
        response = client.get("/activities")
        final_participants = response.json()[activity_name]["participants"]
        
        for email in new_students:
            assert email in final_participants
        
        if existing_student:
            assert existing_student not in final_participants

    def test_data_consistency_after_operations(self, client, reset_activities):
        """Test that data remains consistent after multiple operations."""
        # Get initial state of all activities
        response = client.get("/activities")
        initial_state = response.json()
        
        # Perform various operations
        operations = [
            ("POST", "Chess Club", "newstudent1@mergington.edu"),
            ("DELETE", "Programming Class", "emma@mergington.edu"),
            ("POST", "Gym Class", "newstudent2@mergington.edu"),
            ("DELETE", "Soccer Team", "lucas@mergington.edu"),
            ("POST", "Art Workshop", "newstudent3@mergington.edu"),
        ]
        
        for method, activity, email in operations:
            if method == "POST":
                response = client.post(f"/activities/{activity}/signup?email={email}")
            else:  # DELETE
                response = client.delete(f"/activities/{activity}/unregister?email={email}")
            
            # Each operation should succeed or fail predictably
            assert response.status_code in [200, 400]  # 400 for expected errors like duplicate signup
        
        # Verify data structure is still valid
        response = client.get("/activities")
        assert response.status_code == 200
        
        final_state = response.json()
        
        # Verify all activities still exist
        for activity_name in initial_state.keys():
            assert activity_name in final_state
        
        # Verify structure is maintained
        for activity_name, activity_data in final_state.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)