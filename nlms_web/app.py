
from flask import Flask
from db_config import get_db_connection  
import auth, admin_routes, user_routes

app = Flask(__name__)
app.secret_key = 'group8'

auth.register_auth(app)
admin_routes.register_admin(app)
user_routes.register_user(app)

if __name__ == "__main__":
    app.run(debug=True)
