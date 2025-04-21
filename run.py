import os
from app import create_app

# Get environment from environment variable, default to development
env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host='0.0.0.0', port=5678) 