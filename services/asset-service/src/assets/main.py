from assets.api import routes
from flask import Flask
from asset_common.logging_utils import setup_logger

log = setup_logger("asset-service")

app = Flask(__name__)
app.register_blueprint(routes.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)