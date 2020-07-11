from app import app
from config import Config

if __name__ == '__main__':
    app.run_server(debug=Config.debug)