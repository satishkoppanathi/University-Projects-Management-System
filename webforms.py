from flask_wtf import FlaskForm 
from wtforms import StringField,SubmitField ,PasswordField , SelectField ,DateField ,FileField
from wtforms.validators import DataRequired,EqualTo,Length
from wtforms_sqlalchemy.fields import QuerySelectField




# User Form 
class StudentForm(FlaskForm):
    stu_id = StringField("Student Id" , validators=[DataRequired()])
    stu_name = StringField("Name",validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    clg_id = StringField("College Id",validators=[DataRequired()])
    department = SelectField("Department" ,choices=[('cse', 'CSE'), ('ece', 'ECE'), ('mech', 'MECH'), ('civil', 'CIVIL') , ('eee','EEE')], validators=[DataRequired()])
    year_of_study = SelectField("Year of Study", choices=[('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year')], validators=[DataRequired()])
    password =PasswordField("Password",validators=[DataRequired(), EqualTo('confirmpassword',              message = 'Passwords Must Match!!')])
    confirmpassword=PasswordField("Confirm Password",validators=[DataRequired()])
    submit = SubmitField(("submit"))
    
class ProfessorForm(FlaskForm):
    prof_id = StringField("Professor Id" , validators=[DataRequired()])
    prof_name = StringField("Name",validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])   
    email = StringField("Email",validators=[DataRequired()])
    clg_id = StringField("College Id",validators=[DataRequired()])
    department = SelectField("Department" ,choices=[('cse', 'CSE'), ('ece', 'ECE'), ('mech', 'MECH'), ('civil', 'CIVIL') , ('eee','EEE')], validators=[DataRequired()])
    role = SelectField("Role" ,choices=[('professor', 'Professor'), ('hod', 'HOD')], validators=[DataRequired()])
    date_of_join = DateField("Year Of Join ", validators=[DataRequired()])

    password =PasswordField("Password",validators=[DataRequired(), EqualTo('confirmpassword',              message = 'Passwords Must Match!!')])
    confirmpassword=PasswordField("Confirm Password",validators=[DataRequired()])
    submit = SubmitField(("submit"))
    
class DirectorForm(FlaskForm):
    clg_id = StringField("College Id" , validators=[DataRequired()])
    clg_name = StringField("College Name" , validators=[DataRequired()])
    director_name = StringField("Director Name" , validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    password =PasswordField("Password",validators=[DataRequired(), EqualTo('confirmpassword',              message = 'Passwords Must Match!!')])
    confirmpassword=PasswordField("Confirm Password",validators=[DataRequired()])
    submit = SubmitField(("submit"))


class LoginForm(FlaskForm):
    login_as = SelectField("Login as ", choices=[('student', 'Student'), ('professor', 'Professor'), ('director', 'Director')], validators=[DataRequired()])
    id = StringField("College Id" , validators=[DataRequired()])
    password =PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField(("submit"))

# update forms
class UpdateStudentProfileForm(FlaskForm):
    stu_id = StringField("Student Id" , validators=[DataRequired()])
    stu_name = StringField("Name",validators=[DataRequired()])
    year_of_study = SelectField("Year of Study", choices=[('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year')], validators=[DataRequired()])
    profile_pic = FileField('Profile pic')
    aboutme = StringField('About Me')
    submit = SubmitField(("submit"))
    
    
class TeamForm(FlaskForm):
    team_id = StringField("Team Id",validators=[DataRequired()])
    team_lead_id = StringField("Team Lead Id",validators=[DataRequired()])
    member_1 = StringField("member Id :" , validators=[DataRequired()])
    member_2 = StringField("member Id :" , validators=[DataRequired()])
    member_3 = StringField("member Id :" , validators=[DataRequired()])
    member_4 = StringField("member Id :")
    submit = SubmitField(("submit"))
    
    
class ProjectForm(FlaskForm):
    team_id = StringField("Team Id",validators=[DataRequired()])
    project_title = StringField("Project Title",validators=[DataRequired()])
    project_description = StringField("Project Description",validators=[DataRequired()])
    submit = SubmitField(("submit"))
    
class SuggestProjectForm(FlaskForm):
    domain = StringField("Domain",validators=[DataRequired()])
    difficulty = SelectField("Difficulty", choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], validators=[DataRequired()])
    skills = StringField("Skills",validators=[DataRequired()])
    estimated_time = StringField("Estimated Time", validators=[DataRequired()])
    submit = SubmitField(("submit"))