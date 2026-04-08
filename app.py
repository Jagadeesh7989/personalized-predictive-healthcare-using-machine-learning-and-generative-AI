import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
from werkzeug.security import check_password_hash
from database import create_tables

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ CREATE TABLES (VERY IMPORTANT)
create_tables()

# ✅ Load model properly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "model.pkl")
model = pickle.load(open(model_path, "rb"))

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, password FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if check_password_hash(user[1], password):
                session["user_id"] = user[0]
                return redirect(url_for("home"))
            else:
                return "Wrong Password ❌"
        else:
            return "User not found ❌"

    # ✅ VERY IMPORTANT (this was missing or wrongly indented)
    return render_template("login.html")

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        fever = int(request.form["fever"])
        cough = int(request.form["cough"])
        headache = int(request.form["headache"])
        fatigue = int(request.form["fatigue"])
        rashes = int(request.form["rashes"])
        chestpain = int(request.form["chestpain"])

        prediction = model.predict([[fever, cough, headache, fatigue, rashes, chestpain]])

        return render_template("index.html", result=prediction[0])

    return render_template("index.html")


# ---------- HISTORY ----------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fever,cough,headache,fatigue,rashes,chest,risk,date
    FROM predictions WHERE user_id=?
    """, (session["user_id"],))

    data = cursor.fetchall()
    conn.close()

    return render_template("history.html", data=data)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)