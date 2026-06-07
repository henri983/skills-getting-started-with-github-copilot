from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "aaa-signer@example.com"
    url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activity_response = client.get("/activities")
    assert email in activity_response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_error():
    # Arrange
    activity_name = "Chess Club"
    email = "aaa-duplicate@example.com"
    signup_url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    first_response = client.post(signup_url)
    second_response = client.post(signup_url)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Programming Class"
    email = "aaa-remove@example.com"
    signup_url = f"/activities/{activity_name}/signup?email={email}"
    delete_url = f"/activities/{activity_name}/participants?email={email}"

    # Act
    signup_response = client.post(signup_url)
    delete_response = client.delete(delete_url)

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"Removed {email} from {activity_name}"}

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]
