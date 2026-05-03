from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import csv
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "koi-risk-system-2024"

SENDER_EMAIL = "mmonibah3@gmail.com"
SENDER_PASSWORD = "mbklrdynywpdipvw"

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

        def get_col(row, *names):
            for name in names:
                val = row.get(name)
                if val is not None and str(val).strip() != '':
                    return val
            return ''

        for _, row in df.iterrows():
            student = {
                "id":         str(get_col(row, 'Student_ID', 'student_id', 'ID', 'id', 'StudentID', 'student id')),
                "name":       str(get_col(row, 'Name', 'name', 'Student_Name', 'student_name', 'full_name', 'FullName')),
                "subject":    str(get_col(row, 'Subject', 'subject', 'Course', 'course', 'Subject_Code', 'subject_code')),
                "attendance": float(get_col(row, 'Attendance', 'attendance', 'Att', 'att', 'attendance_%', 'Attendance_%') or 0),
                "tutorials":  float(get_col(row, 'Tutorials', 'tutorials', 'Tutorial', 'tutorial', 'Tut', 'tut', 'tutorial_score') or 0),
                "assessment": str(get_col(row, 'Assessment', 'assessment', 'Assess', 'assess', 'assessment_result') or 'Not Done'),
                "email":      str(get_col(row, 'Email', 'email', 'Student_Email', 'student_email') or ''),
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


# ================= EXPORT CSV =================
@app.route("/export/csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name', 'Subject', 'Attendance', 'Tutorials', 'Assessment', 'Status', 'Reasons'])
    for s in students_data:
        writer.writerow([s['id'], s['name'], s['subject'], s['attendance'], s['tutorials'], s['assessment'], s['status'], ', '.join(s['reasons'])])
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=KOI_Student_Report.csv"})

@app.route("/export/atrisk/csv")
def export_atrisk_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name', 'Subject', 'Attendance', 'Tutorials', 'Assessment', 'Risk Reason'])
    for s in at_risk_students:
        writer.writerow([s['id'], s['name'], s['subject'], s['attendance'], s['tutorials'], s['assessment'], ', '.join(s['reasons'])])
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=KOI_AtRisk_Report.csv"})


# ================= STUDENT DETAIL =================
@app.route("/student/<student_id>")
def student_detail(student_id):
    student = next((s for s in students_data if str(s['id']) == str(student_id)), None)
    if not student:
        return redirect(url_for('results'))
    return render_template('student_detail.html', student=student)


# ================= SEND ALERT =================
@app.route("/send-alert/<path:student_id>")
def send_alert(student_id):
    student = next((s for s in students_data if str(s['id']).strip() == str(student_id).strip()), None)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('at_risk'))
    try:
        student_email = student.get('email', '')
        if not student_email:
            flash(f"No email found for {student['name']}.", "danger")
            return redirect(url_for('at_risk'))
        msg = MIMEMultipart()
        msg['From']    = SENDER_EMAIL
        msg['To']      = student_email
        msg['Subject'] = f"Academic Alert: Action Required — {student['subject']}"
        body = f"""
Dear {student['name']},

You have been identified as at-risk in your current subject.

Student ID:     {student['id']}
Subject:        {student['subject']}
Attendance:     {student['attendance']}%
Tutorial Score: {student['tutorials']}
Assessment:     {student['assessment']}
Risk Reasons:   {', '.join(student['reasons'])}

Please contact your academic coordinator immediately.

Regards,
KOI Academic Support Team
        """
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, student_email, msg.as_string())
        server.quit()
        flash(f"✓ Email alert sent to {student['name']} at {student_email}.", "success")
    except Exception as e:
        flash(f"✗ Email failed: {str(e)}", "danger")
    return redirect(url_for('at_risk'))


# ================= PROFILE =================
@app.route("/profile")
def profile():
    return render_template('profile.html')


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "")
        email    = request.form.get("email", "")
        password = request.form.get("password", "")
        role     = request.form.get("role", "admin")
        if fullname and email and password:
            session["logged_in"]  = True
            session["user_email"] = email
            session["user_name"]  = fullname
            session["user_role"]  = role
            flash(f"Welcome {fullname}! Account created successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Please fill all fields.", "danger")
    return redirect(url_for("login"))


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)