from backend.app import app

if __name__ == "__main__":
    # Get Heroku port, fall back to port 5000
    app.run()