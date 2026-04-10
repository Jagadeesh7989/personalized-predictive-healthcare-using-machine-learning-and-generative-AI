import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
from src.pipeline.predict_pipeline import PredictPipeline, CustomData
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

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return "Invalid Email or Password ❌"

    return render_template("login.html")

from werkzeug.security import generate_password_hash

# ---------- REGISTER ----------import sqlite3

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # ✅ Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "⚠ User already exists! Please login."

        # ✅ Insert new user
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        print("✅ New user registered:", email)

        return redirect(url_for("login"))

    return render_template("register.html")
# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    suggestion = None
    future = None
    detected = None

    if request.method == "POST":
        problem = request.form["problem"].lower()

        # 🔍 Detect symptoms from text
        fever = 1 if "fever" in problem else 0
        cough = 1 if "cough" in problem else 0
        headache = 1 if "headache" in problem else 0
        fatigue = 1 if "tired" in problem or "fatigue" in problem else 0
        rashes = 1 if "rash" in problem else 0

        # 🧠 Show detected symptoms
        detected = []
        if fever: detected.append("Fever")
        if cough: detected.append("Cough")
        if headache: detected.append("Headache")
        if fatigue: detected.append("Fatigue")
        if rashes: detected.append("Rashes")

        # 🤖 ML Prediction (IMPORTANT)
        input_data = [[fever, cough, headache, fatigue, rashes]]
        prediction = model.predict(input_data)[0]

        # 🎯 Result logic
        if prediction == 1:
            result = "High Risk"
            suggestion = "Consult a doctor immediately."
            future = "Health risk may increase."
        else:
            result = "Low Risk"
            suggestion = "You are healthy."
            future = "Condition stable."

        # 💾 Save to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions 
        (user_id, fever, cough, headache, fatigue, rashes, risk)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            fever, cough, headache, fatigue, rashes,
            result
        ))

        conn.commit()
        conn.close()

    return render_template(
        "index.html",
        result=result,
        suggestion=suggestion,
        future=future,
        detected=detected
    )
@app.route("/heart", methods=["GET", "POST"])
def heart():
    if request.method == "POST":
        try:
            data = CustomData(
                age=int(request.form["age"]),
                sex=int(request.form["sex"]),
                cp=int(request.form["cp"]),
                trestbps=int(request.form["trestbps"]),
                chol=int(request.form["chol"]),
                fbs=int(request.form["fbs"]),
                restecg=int(request.form["restecg"]),
                thalach=int(request.form["thalach"]),
                exang=int(request.form["exang"]),
                oldpeak=float(request.form["oldpeak"]),
                slope=int(request.form["slope"]),
                ca=int(request.form["ca"]),
                thal=int(request.form["thal"])
            )

            pred_df = data.get_data_as_dataframe()

            predict_pipeline = PredictPipeline()
            result = predict_pipeline.predict(pred_df)

            if result[0] == 1:
                prediction = "⚠ High Risk of Heart Disease"
            else:
                prediction = "✅ Low Risk"

            return render_template("heart.html", result=prediction)

        except Exception as e:
            return str(e)

    return render_template("heart.html")
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form["message"].lower()

    if "fever" in msg:
        reply = "Drink fluids and take rest."
    elif "headache" in msg:
        reply = "Avoid stress and stay hydrated."
    elif "chest" in msg:
        reply = "Consult doctor if severe."
    else:
        reply = "Please consult a doctor."

    return {"reply": reply}

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
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    app.run(debug=True)
    