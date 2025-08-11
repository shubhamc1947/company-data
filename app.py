from flask import Flask
import logging_config  # to setup logging

from routes import company, search, info

app = Flask(__name__)

# Register Blueprints for modular routes
app.register_blueprint(company.bp)
app.register_blueprint(search.bp)
app.register_blueprint(info.bp)

if __name__ == "__main__":
    app.logger.info("🇺🇸 US Company Data API Starting...")
    app.run(debug=True, port=5000, host='0.0.0.0')
