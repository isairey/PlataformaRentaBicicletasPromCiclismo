from app.extensions import db
from app.models import Route


def admin_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def user_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_route_success(client, app, admin_token):
    response = client.post(
        "/api/v1/events/routes",
        json={
            "name": "Alto de Palmas",
            "distance": 24.5,
            "difficulty": "hard",
            "description": "A demanding climbing route.",
            "coordinates": [{"lat": 6.167, "lng": -75.531}],
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Alto de Palmas"
    assert body["distance"] == 24.5
    assert body["difficulty"] == "hard"
    assert body["coordinates"] == [{"lat": 6.167, "lng": -75.531}]
    assert "createdAt" in body
    assert "updatedAt" in body

    with app.app_context():
        assert Route.query.count() == 1


def test_create_route_fails_with_missing_fields(client, app, admin_token):
    response = client.post(
        "/api/v1/events/routes",
        json={
            "name": "Incomplete Route",
            "distance": 15,
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400

    with app.app_context():
        assert Route.query.count() == 0


def test_create_route_fails_for_non_admin_user(client, user_token):
    response = client.post(
        "/api/v1/events/routes",
        json={
            "name": "Blocked Route",
            "distance": 18,
            "difficulty": "medium",
            "description": "Should not be created.",
        },
        headers=user_headers(user_token),
    )

    assert response.status_code == 403


def test_created_route_is_immediately_available_in_list(client, admin_token, user_token):
    create_response = client.post(
        "/api/v1/events/routes",
        json={
            "name": "River Route",
            "distance": 12,
            "difficulty": "easy",
            "description": "Scenic route by the river.",
        },
        headers=admin_headers(admin_token),
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/events/routes",
        headers=user_headers(user_token),
    )

    assert list_response.status_code == 200
    body = list_response.get_json()
    assert len(body) == 1
    assert body[0]["name"] == "River Route"


def test_list_routes_returns_empty_array_when_no_data_exists(client, user_token):
    response = client.get(
        "/api/v1/events/routes",
        headers=user_headers(user_token),
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_routes_fails_for_unauthenticated_user(client):
    response = client.get("/api/v1/events/routes")

    assert response.status_code == 401


def test_update_route_success(client, app, admin_token):
    with app.app_context():
        route = Route(
            name="Starter Route",
            distance=10.5,
            difficulty="easy",
            description="Original route.",
            coordinates=[{"lat": 6.1, "lng": -75.5}],
        )
        db.session.add(route)
        db.session.commit()
        route_id = route.id
        original_created_at = route.created_at
        original_updated_at = route.updated_at

    response = client.put(
        f"/api/v1/events/routes/{route_id}",
        json={
            "name": "Starter Route Updated",
            "distance": 16.2,
            "difficulty": "medium",
            "description": "Updated route.",
            "coordinates": [{"lat": 6.2, "lng": -75.6}],
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == route_id
    assert body["name"] == "Starter Route Updated"
    assert body["distance"] == 16.2
    assert body["createdAt"] == original_created_at.isoformat()
    assert body["updatedAt"] != original_updated_at.isoformat()

    with app.app_context():
        stored_route = db.session.get(Route, route_id)
        assert stored_route.name == "Starter Route Updated"
        assert stored_route.distance == 16.2


def test_update_route_fails_when_it_does_not_exist(client, admin_token):
    response = client.put(
        "/api/v1/events/routes/999",
        json={
            "name": "Ghost Route",
            "distance": 11,
            "difficulty": "easy",
            "description": "Does not exist.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 404


def test_update_route_fails_with_negative_distance(client, app, admin_token):
    with app.app_context():
        route = Route(
            name="Climb",
            distance=8.5,
            difficulty="hard",
            description="Original climb.",
        )
        db.session.add(route)
        db.session.commit()
        route_id = route.id

    response = client.put(
        f"/api/v1/events/routes/{route_id}",
        json={
            "name": "Climb",
            "distance": -5,
            "difficulty": "hard",
            "description": "Invalid update.",
        },
        headers=admin_headers(admin_token),
    )

    assert response.status_code == 400


def test_update_route_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        route = Route(
            name="Protected Route",
            distance=20,
            difficulty="hard",
            description="Protected route.",
        )
        db.session.add(route)
        db.session.commit()
        route_id = route.id

    response = client.put(
        f"/api/v1/events/routes/{route_id}",
        json={
            "name": "Protected Route Updated",
            "distance": 22,
            "difficulty": "hard",
            "description": "Unauthorized update.",
        },
        headers=user_headers(user_token),
    )

    assert response.status_code == 403


def test_delete_route_success(client, app, admin_token, user_token):
    with app.app_context():
        route = Route(
            name="Delete Route",
            distance=14,
            difficulty="medium",
            description="Route to remove.",
            coordinates=[{"lat": 6.25, "lng": -75.57}],
        )
        db.session.add(route)
        db.session.commit()
        route_id = route.id

    response = client.delete(
        f"/api/v1/events/routes/{route_id}",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Route deleted successfully"}

    with app.app_context():
        stored_route = db.session.get(Route, route_id)
        assert stored_route is None

    list_response = client.get(
        "/api/v1/events/routes",
        headers=user_headers(user_token),
    )
    assert list_response.status_code == 200
    assert list_response.get_json() == []


def test_delete_route_fails_when_it_does_not_exist(client, admin_token):
    response = client.delete(
        "/api/v1/events/routes/999",
        headers=user_headers(admin_token),
    )

    assert response.status_code == 404


def test_delete_route_fails_for_non_admin_user(client, app, user_token):
    with app.app_context():
        route = Route(
            name="Protected Route",
            distance=19,
            difficulty="hard",
            description="Should remain available.",
        )
        db.session.add(route)
        db.session.commit()
        route_id = route.id

    response = client.delete(
        f"/api/v1/events/routes/{route_id}",
        headers=user_headers(user_token),
    )

    assert response.status_code == 403

    with app.app_context():
        stored_route = db.session.get(Route, route_id)
        assert stored_route is not None
