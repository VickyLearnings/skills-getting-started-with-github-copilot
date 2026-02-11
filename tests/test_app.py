"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that required activities are present"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"


class TestSignupForActivity:
    """Tests for signing up for an activity"""

    def test_signup_with_valid_activity_and_email(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student1@mergington.edu" in data["message"]

    def test_signup_with_invalid_activity_returns_404(self):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Invalid Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self):
        """Test that signing up with duplicate email returns 400"""
        # First signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        
        # Attempt duplicate signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_adds_participant_to_list(self):
        """Test that signup actually adds participant to the activity"""
        email = "newparticipant@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        # Check participant count increased
        response = client.get("/activities")
        new_count = len(response.json()["Tennis Club"]["participants"])
        assert new_count == initial_count + 1
        assert email in response.json()["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for unregistering from an activity"""

    def test_unregister_with_valid_activity_and_email(self):
        """Test successful unregistration from an activity"""
        email = "unregister_test@mergington.edu"
        
        # First sign up
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Art Studio/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes participant from list"""
        email = "remove_me@mergington.edu"
        
        # Sign up first
        client.post(
            "/activities/Debate Team/signup",
            params={"email": email}
        )
        
        # Verify they're in the list
        response = client.get("/activities")
        assert email in response.json()["Debate Team"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Debate Team/unregister",
            params={"email": email}
        )
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()["Debate Team"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test unregister for nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Fake Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregister for participant not signed up returns 400"""
        response = client.delete(
            "/activities/Science Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
