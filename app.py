from flask import Flask
from flask_migrate import Migrate
import logging_config  # to setup logging

from config import Config
from models import db  # Import the db instance
from routes import company, search, info

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate

# Register Blueprints for modular routes
app.register_blueprint(company.bp)
app.register_blueprint(search.bp)
app.register_blueprint(info.bp)

if __name__ == "__main__":
    app.logger.info("🇺🇸 US Company Data API Starting...")
    app.run(debug=True, port=5000, host='0.0.0.0')