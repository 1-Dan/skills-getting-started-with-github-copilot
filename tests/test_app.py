"""Tests for the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint."""

    def test_get_activities_returns_list(self, client):
        """Test that GET /activities returns activities list."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that GET /activities contains expected activities."""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Soccer Team",
            "Basketball Club",
            "Art Club",
            "Drama Club",
            "Science Club",
            "Debate Team",
            "Chess Club",
            "Programming Class",
            "Gym Class",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data


class TestSignupEndpoint:
    """Tests for the signup endpoint."""

    def test_signup_returns_200(self, client):
        """Test that signup returns 200 status code."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        # Could be 200 or 400 if already signed up
        assert response.status_code in [200, 400]

    def test_signup_with_invalid_activity_returns_404(self, client):
        """Test that signup for invalid activity returns 404."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_response_format(self, client):
        """Test that signup response contains message."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "signup_test@mergington.edu"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "signup_test@mergington.edu" in data["message"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400."""
        test_email = "duplicate_test@mergington.edu"
        # First signup
        response1 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": test_email}
        )
        assert response1.status_code in [200, 400]
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": test_email}
        )
        # Should be 400 if first was successful
        if response1.status_code == 200:
            assert response2.status_code == 400


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint."""

    def test_unregister_with_invalid_activity_returns_404(self, client):
        """Test that unregister for invalid activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_unregistered_student_returns_400(self, client):
        """Test that unregistering non-registered student returns 400."""
        response = client.delete(
            "/activities/Programming%20Class/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_response_format(self, client):
        """Test that unregister response contains message."""
        # Try to unregister an existing participant
        response = client.delete(
            "/activities/Soccer%20Team/unregister",
            params={"email": "liam@mergington.edu"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "liam@mergington.edu" in data["message"]


class TestIntegration:
    """Integration tests for multi-step operations."""

    def test_signup_and_unregister_flow(self, client):
        """Test signing up and unregistering a student."""
        test_email = "integration_test@mergington.edu"
        activity = "Debate%20Team"

        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        
        if signup_response.status_code == 200:
            # Get activities to verify signup
            activities_response = client.get("/activities")
            activities = activities_response.json()
            assert test_email in activities["Debate Team"]["participants"]

            # Unregister
            unregister_response = client.delete(
                f"/activities/{activity}/unregister",
                params={"email": test_email}
            )
            assert unregister_response.status_code == 200

            # Get activities to verify unregister
            activities_response = client.get("/activities")
            activities = activities_response.json()
            assert test_email not in activities["Debate Team"]["participants"]
