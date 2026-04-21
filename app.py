from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "koi-risk-system-2024"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global data store
students_data = []
at_risk_students = []


# ── Helper: subject_data builder ──────────────────────────────
def build_subject_data():
    subject_data = {}
    for s in students_data:
        sub = s["subject"]
        if sub not in subject_data:
            subject_data[sub] = {"at_risk": 0, "safe": 0, "total": 0}
        subject_data[sub]["total"] += 1
        if s["status"] == "At Risk":
            subject_data[sub]["at_risk"] += 1
        else:
            subject_data[sub]["safe"] += 1
    return subject_data


# ── Helper: inject at_risk_count into every template ─────────
@app.context_processor
def inject_globals():
    return dict(at_risk_count=len(at_risk_students))


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "")
        password = request.form.get("password", "")
        # Demo: accept any email/password
        if email and password:
            session["logged_in"] = True
            session["user_email"] = email
            return redirect(url_for("dashboard"))
        flash("Please enter email and password.", "danger")
    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    total         = len(students_data)
    at_risk       = len(at_risk_students)
    safe          = total - at_risk
    subject_data  = build_subject_data()
    subject_count = len(subject_data)

    # Recent 5 at-risk students for dashboard list
    recent_at_risk = []
    for s in at_risk_students[:5]:
        recent_at_risk.append({
            "name":       s["name"],
            "subject":    s["subject"],
            "attendance": s["attendance"],
            "tutorials":  s["tutorials"],
            "assessment": s["assessment"],
            "reason":     ", ".join(s["reasons"]) if s["reasons"] else "Flagged"
        })

    return render_template(
        "dashboard.html",
        total         = total,
        at_risk       = at_risk,
        safe          = safe,
        subject_data  = subject_data,
        subject_count = subject_count,
        recent_at_risk= recent_at_risk
    )


# ================= UPLOAD =================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    global students_data, at_risk_students

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No file selected. Please choose a CSV or Excel file.", "danger")
            return redirect(url_for("upload"))

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
        except Exception as e:
            flash(f"Could not read file: {str(e)}", "danger")
            return redirect(url_for("upload"))

        students_data    = []
        at_risk_students = []

        for _, row in df.iterrows():
            student = {
                "id":         str(row.get("Student_ID", row.get("student_id", ""))),
                "name":       str(row.get("Name",       row.get("name", ""))),
                "subject":    str(row.get("Subject",    row.get("subject", ""))),
                "attendance": float(row.get("Attendance", row.get("attendance", 0))),
                "tutorials":  float(row.get("Tutorials",  row.get("tutorials", 0))),
                "assessment": str(row.get("Assessment",   row.get("assessment", "Not Done"))),
                "status":     "Safe",
                "reasons":    []
            }

            # Risk checks
            if student["attendance"] < 50:
                student["status"] = "At Risk"
                student["reasons"].append("Low Attendance")

            if student["tutorials"] < 50:
                student["status"] = "At Risk"
                student["reasons"].append("Low Tutorials")

            if student["assessment"].strip().lower() != "done":
                student["status"] = "At Risk"
                student["reasons"].append("Missing Assessment")

            students_data.append(student)
            if student["status"] == "At Risk":
                at_risk_students.append(student)

        flash(f"Successfully uploaded {len(students_data)} students. {len(at_risk_students)} flagged at risk.", "success")
        return redirect(url_for("dashboard"))

    return render_template("upload.html")


# ================= ALL STUDENTS =================
@app.route("/results")
def results():
    return render_template(
        "results.html",
        students = students_data,
        total    = len(students_data)
    )


# ================= AT RISK =================
@app.route("/at-risk")
def at_risk():
    total    = len(students_data)
    risk     = len(at_risk_students)
    risk_pct = round((risk / total) * 100, 1) if total > 0 else 0

    # Add reason string for template
    display = []
    for s in at_risk_students:
        reasons = s["reasons"]
        if len(reasons) > 1:
            reason_label = "Multiple Flags"
        elif reasons:
            reason_label = reasons[0]
        else:
            reason_label = "Flagged"

        display.append({**s, "reason": reason_label})

    return render_template(
        "at_risk.html",
        at_risk_students = display,
        risk_pct         = risk_pct
    )


# ================= REPORT =================
@app.route("/report")
def report():
    total        = len(students_data)
    at_risk      = len(at_risk_students)
    safe         = total - at_risk
    subject_data = build_subject_data()

    reason_attendance = 0
    reason_tutorial   = 0
    reason_assessment = 0
    reason_multiple   = 0

    for s in at_risk_students:
        flags = len(s["reasons"])
        if flags > 1:
            reason_multiple   += 1
        if "Low Attendance"     in s["reasons"]:
            reason_attendance += 1
        if "Low Tutorials"      in s["reasons"]:
            reason_tutorial   += 1
        if "Missing Assessment" in s["reasons"]:
            reason_assessment += 1

    return render_template(
        "report.html",
        total             = total,
        at_risk           = at_risk,
        safe              = safe,
        subject_data      = subject_data,
        reason_attendance = reason_attendance,
        reason_tutorial   = reason_tutorial,
        reason_assessment = reason_assessment,
        reason_multiple   = reason_multiple
    )


# ================= NOTIFICATIONS =================
@app.route("/notifications")
def notifications():
    notif_list = [
        {"icon": "fa-triangle-exclamation", "color": "red",    "text": "New at-risk students detected after last upload", "time": "Just now"},
        {"icon": "fa-upload",               "color": "blue",   "text": "File uploaded successfully",                      "time": "2 minutes ago"},
        {"icon": "fa-chart-bar",            "color": "orange", "text": "Weekly report is ready to view",                  "time": "1 hour ago"},
        {"icon": "fa-circle-check",         "color": "green",  "text": "System check completed successfully",              "time": "Yesterday"},
    ]
    return render_template("notifications.html", notif_list=notif_list)


# ================= SETTINGS =================
@app.route("/settings")
def settings():
    return render_template("settings.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)