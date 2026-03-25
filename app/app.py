import threading
import time
from flask import Flask, jsonify, render_template, redirect, url_for, request, session, flash
from app.models.database import get_connection, hash_password, verify_password

app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
app.secret_key = 'your_secret_key_here'  # Change to a secure key

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def rowlist_to_dicts(cursor, rows):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, r)) for r in rows]

def sensor_worker():
    from app.utils.serial_reader import read_serial_data
    read_serial_data()

def scheduler_worker():
    from app.utils.scheduler import check_and_dispense
    while True:
        check_and_dispense()
        time.sleep(60)

_sensor_thread = None
_scheduler_thread = None

def start_sensor_thread():
    global _sensor_thread
    if _sensor_thread is None or not _sensor_thread.is_alive():
        _sensor_thread = threading.Thread(target=sensor_worker, daemon=True)
        _sensor_thread.start()

def start_scheduler_thread():
    global _scheduler_thread
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        _scheduler_thread.start()

@app.route("/")
def index():
    if 'user' in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
        result = cur.fetchone()
        conn.close()
        if result and verify_password(password, result[0]):
            session['user'] = username
            session['role'] = result[1]
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hash_password(password), role))
            conn.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except:
            flash('Username already exists')
        conn.close()
    return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    patients = rowlist_to_dicts(cur, cur.fetchall())
    cur.execute("SELECT * FROM prescriptions WHERE status='active'")
    prescriptions = rowlist_to_dicts(cur, cur.fetchall())
    conn.close()
    return render_template("dashboard.html", patients=patients, prescriptions=prescriptions)

@app.route("/register_patient", methods=["GET", "POST"])
@login_required
def register_patient():
    if request.method == "POST":
        data = request.form
        from app.models.patient import register_patient
        register_patient(
            data["name"], data["room"], int(data["age"]), data["gender"], data["contact"],
            data["medicine"], data["dosage"], data["schedule"]
        )
        return redirect(url_for("dashboard"))
    return render_template("register_patient.html")

@app.route("/schedules")
@login_required
def schedules():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.full_name, pr.medicine_name, pr.dosage, pr.schedule_time, pr.last_dispensed
        FROM prescriptions pr
        JOIN patients p ON pr.patient_id = p.patient_id
        WHERE pr.status='active'
        ORDER BY p.full_name
    """)
    schedules_data = rowlist_to_dicts(cur, cur.fetchall())
    conn.close()
    return render_template("schedules.html", schedules=schedules_data)

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('change_password'))
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username=?", (session['user'],))
        result = cur.fetchone()
        
        if not result or not verify_password(old_password, result[0]):
            flash('Incorrect old password')
            conn.close()
            return redirect(url_for('change_password'))
        
        # Create password change request
        new_pass_hash = hash_password(new_password)
        cur.execute("INSERT INTO password_requests (username, new_password_hash, status) VALUES (?, ?, ?)", 
                   (session['user'], new_pass_hash, 'pending'))
        conn.commit()
        conn.close()
        
        flash('Password change request submitted. Awaiting admin approval.')
        return redirect(url_for('dashboard'))
    
    return render_template("change_password.html")

@app.route("/admin/password_requests")
@login_required
def password_requests():
    if session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT request_id, username, status FROM password_requests WHERE status='pending' ORDER BY request_id")
    requests = rowlist_to_dicts(cur, cur.fetchall())
    conn.close()
    
    return render_template("password_requests.html", requests=requests)

@app.route("/admin/approve_password/<int:request_id>", methods=["POST"])
@login_required
def approve_password(request_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get the password request
    cur.execute("SELECT username, new_password_hash FROM password_requests WHERE request_id=?", (request_id,))
    result = cur.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Request not found'}), 404
    
    username, new_password_hash = result
    
    # Update user password
    cur.execute("UPDATE users SET password_hash=? WHERE username=?", (new_password_hash, username))
    
    # Mark request as approved
    cur.execute("UPDATE password_requests SET status='approved' WHERE request_id=?", (request_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Password for {username} has been updated')
    return redirect(url_for('password_requests'))

@app.route("/admin/reject_password/<int:request_id>", methods=["POST"])
@login_required
def reject_password(request_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE password_requests SET status='rejected' WHERE request_id=?", (request_id,))
    conn.commit()
    conn.close()
    
    flash('Password change request rejected')
    return redirect(url_for('password_requests'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    start_sensor_thread()
    start_scheduler_thread()
    app.run(debug=True, port=5001)
