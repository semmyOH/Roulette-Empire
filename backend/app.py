from flask import Flask
from services.game_routes import game_bp

app = Flask(__name__)

app.register_blueprint(game_bp)

if __name__ == "__main__":
    app.run(debug=True)