from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Art Studio"
    encoded_activity_name = quote(activity_name, safe="")
    email = "student+artstudio@example.com"
    url = f"/activities/{encoded_activity_name}/signup"
    params = {"email": email}
    original_participants = deepcopy(activities[activity_name]["participants"])

    try:
        # Act
        response = client.post(url, params=params)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_remove_participant_removes_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{encoded_activity_name}/participants"
    original_participants = deepcopy(activities[activity_name]["participants"])

    try:
        # Act
        response = client.delete(url, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{encoded_activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    encoded_activity_name = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity_name}/signup"

    # Act
    response = client.post(url, params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": "unknown@student.example"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
