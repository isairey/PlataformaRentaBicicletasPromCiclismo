from flask import jsonify
from pydantic import ValidationError


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "code": "BAD_REQUEST",
            "message": str(e.description) if hasattr(e, "description") else "Bad request.",
            "details": {},
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "code": "BIKE_NOT_FOUND",
            "message": str(e.description) if hasattr(e, "description") else "Resource not found.",
            "details": {},
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": str(e.description) if hasattr(e, "description") else "Validation error.",
            "details": {},
        }), 422

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred.",
            "details": {},
        }), 500

    @app.errorhandler(502)
    def bad_gateway(e):
        return jsonify({
            "code": "BROKER_REPLY_REJECTED",
            "message": str(e.description) if hasattr(e, "description") else "Broker reply rejected.",
            "details": {},
        }), 502

    @app.errorhandler(503)
    def service_unavailable(e):
        return jsonify({
            "code": "BROKER_UNAVAILABLE",
            "message": str(e.description) if hasattr(e, "description") else "Broker unavailable.",
            "details": {},
        }), 503

    @app.errorhandler(504)
    def gateway_timeout(e):
        return jsonify({
            "code": "BROKER_REPLY_TIMEOUT",
            "message": str(e.description) if hasattr(e, "description") else "Broker reply timeout.",
            "details": {},
        }), 504

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation(e):
        errors = e.errors()
        first = errors[0] if errors else {}
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Invalid value for field '{first.get('loc', ['unknown'])[0]}'.",
            "details": {"errors": [{
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
            } for err in errors]},
        }), 422
