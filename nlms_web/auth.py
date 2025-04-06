from flask import request, render_template, redirect, session, flash
from db_config import get_db_connection

def register_auth(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            email = request.form["email"].strip()
            password = request.form["password"].strip()
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM Users WHERE email=%s", (email,))
            user = cur.fetchone()
            conn.close()
            if not user or user["password"] != password:
                error = "Invalid email or password."
            else:
                session["user_id"]   = user["user_id"]
                session["user_name"] = user["name"]
                session["user_role"] = user["role"]
                if user["role"] == "admin":
                    return redirect("/books")
                else:
                    return redirect("/copies")
        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/")
    def index():
        role = session.get("user_role")
        if not role:
            return redirect("/login")
        return redirect("/books") if role=="admin" else redirect("/copies")
