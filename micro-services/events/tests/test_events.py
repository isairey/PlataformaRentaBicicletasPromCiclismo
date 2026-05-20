from datetime import date

from app.extensions import db
from app.models import Event


def admin_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def user_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_event_success(client, app, admin_token):
    response = client.post(
        "/api/v1/events/events",
        json={
            "name": "Sunday Community Ride",
            "date": "2026-09-20",
            "location": "Medellin",
            "description": "A social ride for the whole cycling community.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Sunday Community Ride"
    assert body["date"] == "2026-09-20"
    assert body["location"] == "Medellin"
    assert "createdAt" in body
    assert "updatedAt" in body

    with app.app_context():
        assert Event.query.count() == 1


def test_create_event_fails_with_missing_fields(client, app, admin_token):
    response = client.post(
        "/api/v1/events/events",
        json={
            "name": "Night Ride",
            "date": "2026-09-25",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400

    with app.app_context():
        assert Event.query.count() == 0


def test_create_event_fails_for_non_admin_user(client, user_token):
    response = client.post(
        "/api/v1/events/events",
        json={
            "name": "Unauthorized Ride",
            "date": "2026-09-21",
            "location": "Bogota",
            "description": "Should not be created.",
        },
        headers=user_headers(user_token),
    )

    assert response.status_code == 403


def test_created_event_is_immediately_available_in_list(client, admin_token, user_token):
    create_response = client.post(
        "/api/v1/events/events",
        json={
            "name": "Coffee Ride",
            "date": "2026-09-22",
            "location": "Envigado",
            "description": "Morning ride with coffee stop.",
        },
        headers=admin_headers(admin_token),
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/events/events",
        headers=user_headers(user_token),
    )

    assert list_response.status_code == 200
    body = list_response.get_json()
    assert len(body) == 1
    assert body[0]["name"] == "Coffee Ride"
    assert "createdAt" in body[0]


def test_list_events_returns_empty_array_when_no_data_exists(client, user_token):
    response = client.get(
        "/api/v1/events/events",
        headers=user_headers(user_token),
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_events_fails_for_unauthenticated_user(client):
    response = client.get("/api/v1/events/events")

    assert response.status_code == 401


def test_update_event_success(client, app, admin_token):
    with app.app_context():
        event = Event(
            name="Hill Climb Meetup",
            date=date(2026, 10, 1),
            location="Sabaneta",
            description="Original event description.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id
        original_created_at = event.created_at
        original_updated_at = event.updated_at

    response = client.put(
        f"/api/v1/events/events/{event_id}",
        json={
            "name": "Hill Climb Meetup Updated",
            "date": "2026-10-05",
            "location": "La Ceja",
            "description": "Updated event description.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == event_id
    assert body["name"] == "Hill Climb Meetup Updated"
    assert body["location"] == "La Ceja"
    assert body["createdAt"] == original_created_at.isoformat()
    assert body["updatedAt"] != original_updated_at.isoformat()

    with app.app_context():
        stored_event = db.session.get(Event, event_id)
        assert stored_event.name == "Hill Climb Meetup Updated"
        assert stored_event.description == "Updated event description."


def test_update_event_fails_when_it_does_not_exist(client, admin_token):
    response = client.put(
        "/api/v1/events/events/999",
        json={
            "name": "Ghost Event",
            "date": "2026-10-06",
            "location": "Nowhere",
            "description": "Does not exist.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 404


def test_update_event_fails_with_invalid_date_format(client, app, admin_token):
    with app.app_context():
        event = Event(
            name="Training Camp",
            date=date(2026, 10, 10),
            location="Rionegro",
            description="Original training camp.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.put(
        f"/api/v1/events/events/{event_id}",
        json={
            "name": "Training Camp Updated",
            "date": "10-10-2026",
            "location": "Rionegro",
            "description": "Updated training camp.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400


def test_update_event_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        event = Event(
            name="Community Race",
            date=date(2026, 10, 15),
            location="Bello",
            description="Should stay protected.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.put(
        f"/api/v1/events/events/{event_id}",
        json={
            "name": "Community Race Updated",
            "date": "2026-10-16",
            "location": "Bello",
            "description": "Unauthorized update attempt.",
        },
        headers=user_headers(user_token),
    )

    assert response.status_code == 403


def test_delete_event_success(client, app, admin_token, user_token):
    with app.app_context():
        event = Event(
            name="Delete Event",
            date=date(2026, 11, 1),
            location="Itagui",
            description="Event to remove.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.delete(
        f"/api/v1/events/events/{event_id}",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Event deleted successfully"}

    with app.app_context():
        stored_event = db.session.get(Event, event_id)
        assert stored_event is None

    list_response = client.get(
        "/api/v1/events/events",
        headers=user_headers(user_token),
    )
    assert list_response.status_code == 200
    assert list_response.get_json() == []


def test_delete_event_fails_when_it_does_not_exist(client, admin_token):
    response = client.delete(
        "/api/v1/events/events/999",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 404


def test_delete_event_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        event = Event(
            name="Protected Event",
            date=date(2026, 11, 10),
            location="Copacabana",
            description="Should remain available.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.delete(
        f"/api/v1/events/events/{event_id}",
        headers=user_headers(user_token),
    )

    assert response.status_code == 403

    with app.app_context():
        stored_event = db.session.get(Event, event_id)
        assert stored_event is not None
