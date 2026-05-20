from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(401)
    def handle_unauthorized(error):
        message = getattr(error, "description", "Unauthorized")
        return jsonify({"error": message}), 401

    @app.errorhandler(400)
    def handle_bad_request(error):
        message = getattr(error, "description", "Bad request")
        return jsonify({"error": message}), 400

    @app.errorhandler(403)
    def handle_forbidden(error):
        message = getattr(error, "description", "Forbidden")
        return jsonify({"error": message}), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        message = getattr(error, "description", "Not found")
        return jsonify({"error": message}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
