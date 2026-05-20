from datetime import date

from app.extensions import db
from app.models import Competition


def admin_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def user_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_competition_success(client, app, admin_token):
    response = client.post(
        "/api/v1/events/competitions",
        json={
            "name": "Climbing Challenge",
            "startDate": "2026-04-01",
            "endDate": "2026-04-15",
            "description": "Competition for the best climbers in the community.",
            "type": "cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Climbing Challenge"
    assert body["startDate"] == "2026-04-01"
    assert body["endDate"] == "2026-04-15"
    assert "createdAt" in body
    assert "updatedAt" in body

    with app.app_context():
        assert Competition.query.count() == 1


def test_create_competition_fails_with_missing_fields(client, app, admin_token):
    response = client.post(
        "/api/v1/events/competitions",
        json={
            "name": "Sprint Cup",
            "startDate": "2026-05-01",
            "description": "Missing endDate and type.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400

    with app.app_context():
        assert Competition.query.count() == 0


def test_create_competition_fails_when_end_date_is_before_start_date(client, admin_token):
    response = client.post(
        "/api/v1/events/competitions",
        json={
            "name": "Bad Dates Race",
            "startDate": "2026-06-10",
            "endDate": "2026-06-05",
            "description": "Invalid schedule.",
            "type": "cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400


def test_create_competition_fails_for_non_admin_user(client, user_token):
    response = client.post(
        "/api/v1/events/competitions",
        json={
            "name": "Community Ride",
            "startDate": "2026-04-01",
            "endDate": "2026-04-05",
            "description": "Attempt by non-admin user.",
            "type": "cycling",
        },
        headers=admin_headers(user_token),
    )

    assert response.status_code == 403


def test_created_competition_is_immediately_available_in_list(client, admin_token, user_token):
    create_response = client.post(
        "/api/v1/events/competitions",
        json={
            "name": "Mountain Tour",
            "startDate": "2026-07-01",
            "endDate": "2026-07-10",
            "description": "Competition now visible in the list.",
            "type": "cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/events/competitions",
        headers=user_headers(user_token),
    )

    assert list_response.status_code == 200
    body = list_response.get_json()
    assert len(body) == 1
    assert body[0]["name"] == "Mountain Tour"
    assert "createdAt" in body[0]
    assert "updatedAt" in body[0]


def test_list_competitions_returns_empty_array_when_no_data_exists(client, user_token):
    response = client.get(
        "/api/v1/events/competitions",
        headers=user_headers(user_token),
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_competitions_fails_for_unauthenticated_user(client):
    response = client.get("/api/v1/events/competitions")

    assert response.status_code == 401


def test_update_competition_success(client, app, admin_token):
    with app.app_context():
        competition = Competition(
            name="Weekend Ride",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 5),
            description="Original description.",
            type="cycling",
        )
        db.session.add(competition)
        db.session.commit()
        competition_id = competition.id
        original_created_at = competition.created_at
        original_updated_at = competition.updated_at

    response = client.put(
        f"/api/v1/events/competitions/{competition_id}",
        json={
            "name": "Weekend Ride Updated",
            "startDate": "2026-08-02",
            "endDate": "2026-08-06",
            "description": "Updated description.",
            "type": "road-cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == competition_id
    assert body["name"] == "Weekend Ride Updated"
    assert body["type"] == "road-cycling"
    assert body["createdAt"] == original_created_at.isoformat()
    assert body["updatedAt"] != original_updated_at.isoformat()

    with app.app_context():
        stored_competition = db.session.get(Competition, competition_id)
        assert stored_competition.name == "Weekend Ride Updated"
        assert stored_competition.description == "Updated description."


def test_update_competition_fails_when_it_does_not_exist(client, admin_token):
    response = client.put(
        "/api/v1/events/competitions/999",
        json={
            "name": "Ghost Competition",
            "startDate": "2026-08-02",
            "endDate": "2026-08-06",
            "description": "Does not exist.",
            "type": "cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 404


def test_update_competition_fails_with_invalid_date_range(client, app, admin_token):
    with app.app_context():
        competition = Competition(
            name="Dates Challenge",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 4),
            description="Original schedule.",
            type="cycling",
        )
        db.session.add(competition)
        db.session.commit()
        competition_id = competition.id

    response = client.put(
        f"/api/v1/events/competitions/{competition_id}",
        json={
            "name": "Dates Challenge",
            "startDate": "2026-09-10",
            "endDate": "2026-09-05",
            "description": "Invalid schedule.",
            "type": "cycling",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400


def test_update_competition_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        competition = Competition(
            name="Members Ride",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 3),
            description="Cannot be updated by non-admin.",
            type="cycling",
        )
        db.session.add(competition)
        db.session.commit()
        competition_id = competition.id

    response = client.put(
        f"/api/v1/events/competitions/{competition_id}",
        json={
            "name": "Members Ride Updated",
            "startDate": "2026-10-01",
            "endDate": "2026-10-04",
            "description": "Still blocked.",
            "type": "cycling",
        },
        headers=admin_headers(user_token),
    )

    assert response.status_code == 403


def test_delete_competition_success(client, app, admin_token, user_token):
    with app.app_context():
        competition = Competition(
            name="Delete Me",
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 3),
            description="Competition to be removed.",
            type="cycling",
        )
        db.session.add(competition)
        db.session.commit()
        competition_id = competition.id

    response = client.delete(
        f"/api/v1/events/competitions/{competition_id}",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Competition deleted successfully"}

    with app.app_context():
        stored_competition = db.session.get(Competition, competition_id)
        assert stored_competition is None

    list_response = client.get(
        "/api/v1/events/competitions",
        headers=user_headers(user_token),
    )
    assert list_response.status_code == 200
    assert list_response.get_json() == []


def test_delete_competition_fails_when_it_does_not_exist(client, admin_token):
    response = client.delete(
        "/api/v1/events/competitions/999",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 404


def test_delete_competition_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        competition = Competition(
            name="Protected Competition",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 4),
            description="Should not be deletable by regular users.",
            type="cycling",
        )
        db.session.add(competition)
        db.session.commit()
        competition_id = competition.id

    response = client.delete(
        f"/api/v1/events/competitions/{competition_id}",
        headers=user_headers(user_token),
    )

    assert response.status_code == 403

    with app.app_context():
        stored_competition = db.session.get(Competition, competition_id)
        assert stored_competition is not None
