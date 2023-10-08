from flask import Flask, render_template, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from forms import AddTaskForm, UpdateTaskForm, DeleteTaskForm, GetOneTaskForm, LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = "insert-your-super-secret-key-over-here"
app.json.sort_keys = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

limiter = Limiter(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@limiter.request_filter
def custom_response():
    return "Rate limit exceeded. Please try again later.", 429

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.name

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    task_name = db.Column(db.String(80), nullable=False)
    task_description = db.Column(db.String(120), nullable=False)
    task_deadline = db.Column(db.DateTime, nullable=False)
    task_status = db.Column(db.String(120), nullable=False)
    task_priority = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.name

@app.route("/")
@app.route("/home")
@limiter.limit("1 per minute")
def home():
    return render_template('layout.html')

@app.route("/add-task", methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def add_task():
    form = AddTaskForm()
    user = current_user
    if form.validate_on_submit():
        data = Task(
            task_name=form.task_name.data,
            user_id=user.id,
            task_description=form.task_description.data,
            task_deadline=form.task_deadline.data,
            task_status=form.task_status.data,
            task_priority=form.task_priority.data
        )
        db.session.add(data)
        db.session.commit()
        flash('Task added successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_task.html', form=form, username=user.username)

@app.route("/update-task", methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def update_task():
    form = UpdateTaskForm()
    data = Task.query.all()
    for i in data:
        if i.user_id == current_user.id and i.task_id == form.task_id.data:
            if form.validate_on_submit():
                i.task_name = form.task_name.data if form.task_name.data else i.task_name
                i.task_description = form.task_description.data if form.task_description.data else i.task_description
                i.task_deadline = form.task_deadline.data if form.task_deadline.data else i.task_deadline
                i.task_status = form.task_status.data if form.task_status.data else i.task_status
                i.task_priority = form.task_priority.data if form.task_priority.data else i.task_priority
                db.session.commit()
                flash('Task updated successfully.', 'success')
                return redirect(url_for('dashboard'))
    return render_template('update_task.html', form=form, username=current_user.username)

@app.route("/get-tasks")
@login_required
@limiter.limit("10 per minute")
def get_tasks():
    data = Task.query.all()
    json = {}
    try:
        for i in data:
            if i.user_id == current_user.id:
                json[i.task_id] = {
                    "task_name": i.task_name,
                    "task_description": i.task_description,
                    "task_deadline": i.task_deadline,
                    "task_status": i.task_status,
                    "task_priority": i.task_priority
                }
        return jsonify(json)
    except:
        print("No data")

@app.route("/get-task")
@login_required
@limiter.limit("10 per minute")
def get_task():
    data = Task.query.all()
    json = {}
    try:
        for i in data:
            task_id = session.get('task_id')
            if i.user_id == current_user.id and i.task_id == task_id:
                json[i.task_id] = {
                    "task_name": i.task_name,
                    "task_description": i.task_description,
                    "task_deadline": i.task_deadline,
                    "task_status": i.task_status,
                    "task_priority": i.task_priority
                }
        return jsonify(json)
    except:
        print("No data")

@app.route("/delete-task", methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def delete_task():
    form = DeleteTaskForm()
    if form.validate_on_submit():
        data = Task.query.get(form.task_id.data)
        if data:
            if data.user_id == current_user.id:
                db.session.delete(data)
                db.session.commit()
                flash('Task deleted successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Task not found.', 'danger')
                return redirect(url_for('delete_task'))
        else:
            flash('Task not found.', 'danger')
            return redirect(url_for('delete_task'))
    return render_template('delete_task.html', form=form, username=current_user.username)

@app.route("/all-tasks")
@login_required
@limiter.limit("10 per minute")
def all_tasks():
    data = Task.query.all()
    return render_template('all_tasks.html', data=data, user=current_user, username=current_user.username)

@app.route("/get-one-task", methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def get_one_task():
    form = GetOneTaskForm()
    if form.validate_on_submit():
        data = Task.query.get(form.task_id.data)
        if data:
            if data.user_id == current_user.id:
                session['task_id'] = form.task_id.data
                return render_template('get_one_task.html', form=form, data=data, user=current_user, username=current_user.username)
            else:
                flash('Task not found.', 'danger')
                return redirect(url_for('get_one_task'))
        else:
            flash('Task not found.', 'danger')
            return redirect(url_for('get_one_task'))
    return render_template('get_one_task.html', form=form, user=current_user, username=current_user.username)

@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user:
            check_pwd = bcrypt.check_password_hash(user.password_hash, login_form.password.data)
            if check_pwd:
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=login_form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        existing_user = User.query.filter_by(username=register_form.username.data).first()
        if not existing_user:
            user = User(username=register_form.username.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', form=register_form)

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.app_context().push()
    db.create_alL()
    app.run(debug=True)
