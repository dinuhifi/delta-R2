from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateTimeField
from wtforms.validators import DataRequired

class AddTaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    task_description = StringField('Task Description', validators=[DataRequired()])
    task_deadline = DateTimeField('Task Deadline', validators=[DataRequired()])
    task_status = StringField('Task Status', validators=[DataRequired()])
    task_priority = StringField('Task Priority', validators=[DataRequired()])
    submit = SubmitField('Add Task')

class UpdateTaskForm(FlaskForm):
    task_id = IntegerField('Task ID', validators=[DataRequired()])
    task_name = StringField('Task Name')
    task_description = StringField('Task Description')
    task_deadline = DateTimeField('Task Deadline', validators=[DataRequired()])
    task_status = StringField('Task Status')
    task_priority = StringField('Task Priority')
    submit = SubmitField('Update Task')

class GetOneTaskForm(FlaskForm):
    task_id = IntegerField('Task ID', validators=[DataRequired()])
    submit = SubmitField('Get Task')

class DeleteTaskForm(FlaskForm):
    task_id = IntegerField('Task ID', validators=[DataRequired()])
    submit = SubmitField('Delete Task')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit_login = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit_register = SubmitField('Register')