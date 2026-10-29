from routes.errors import register_error_handlers
from routes.game_routes import game_bp
from routes.shop_routes import shop_bp


def register_routes(app) -> None:
    app.register_blueprint(game_bp)
    app.register_blueprint(shop_bp)
    register_error_handlers(app)
