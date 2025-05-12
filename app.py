from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from webforms import StudentForm, DirectorForm, ProfessorForm, LoginForm, UpdateStudentProfileForm, TeamForm, ProjectForm , SuggestProjectForm
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import pandas as pd
from joblib import load
import os
from werkzeug.utils import secure_filename
import uuid as uuid
from sqlalchemy import func, extract, or_

# Load the model
ProjectModel = load('./savedModels/projectSuggest.joblib')

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/student_profiles')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = Professors.query.get(user_id)
    if user:
        return user
    user = Directors.query.get(user_id)
    if user:
        return user
    return Students.query.get(user_id)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    form = SuggestProjectForm()
    if form.validate_on_submit():
        domain = form.domain.data
        difficulty = form.difficulty.data
        required_skills = form.skills.data
        estimated_time = form.estimated_time.data
        
        print(domain, difficulty, required_skills, estimated_time)
        
        # Create a DataFrame for the input
        input_data = pd.DataFrame({
            'domain': [domain],
            'difficulty': [difficulty],
            'required_skills': [required_skills],
            'estimated_time': [int(estimated_time)]
        })
        print(input_data)
        
        # Make prediction
        predicted_project = ProjectModel.predict(input_data)
        print(predicted_project)
        predicted_project = " ".join(map(str, predicted_project))
        print(f"Predicted Project: {predicted_project}")
        
        # Set the flag to show the modal
        show_modal = True
        
        # Clear the form by reinitializing it
        form.domain.data = ''  # Reset the form
        form.difficulty.data = ''
        form.skills.data = ''
        form.estimated_time.data = ''
        return render_template('project_suggest.html', form=form, predicted_project=predicted_project,show_modal=show_modal)
    
    return render_template('project_suggest.html', form=form)


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/professor_dashboard/<string:prof_id>', methods=['GET'])
@login_required
def professor_dashboard(prof_id):
    if hasattr(current_user, 'prof_id') and current_user.prof_id == prof_id:
        professor = Professors.query.filter_by(prof_id=prof_id).first()
        total_projects = Projects.query.filter_by(prof_id=prof_id).count()
        unique_teams = Teams.query.join(Projects, Teams.team_id == Projects.team_id).filter(
            Projects.prof_id == prof_id
        ).distinct().all()
        total_teams = len(unique_teams)
        projects = Projects.query.filter_by(prof_id=prof_id).all()
        inprogress_count = Projects.query.filter_by(prof_id=prof_id, progress='inprogress').count()
        completed_count = Projects.query.filter_by(prof_id=prof_id, progress='completed').count()
        submitted_projects = Projects.query.filter_by(prof_id=prof_id, is_submitted=True, is_approved=False).all()
        teams = Teams.query.join(Projects, Teams.team_id == Projects.team_id).filter(
            Projects.prof_id == prof_id
        ).distinct().all()

        return render_template(
            'professor_dashboard.html',
            professor=professor,
            total_projects=total_projects,
            total_teams=total_teams,
            projects=projects,
            teams=teams,
            inprogress_count=inprogress_count,
            completed_count=completed_count,
            submitted_projects=submitted_projects
        )
    else:
        flash("Access restricted to the professor.")
        return redirect(url_for('home'))

@app.route('/hod_dashboard/<string:prof_id>', methods=['GET'])
@login_required
def hod_dashboard(prof_id):
    if hasattr(current_user, 'prof_id') and current_user.prof_id == prof_id:
        professor = Professors.query.filter_by(prof_id=prof_id).first()
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        total_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(
            Students, Teams.team_lead_id == Students.stu_id
        ).filter(Students.dept == professor.dept).count()

        total_teams = Teams.query.join(Students, Teams.team_lead_id == Students.stu_id).filter(
            Students.dept == professor.dept
        ).count()

        total_students = Students.query.filter_by(dept=professor.dept).count()
        total_professors = Professors.query.filter_by(dept=professor.dept).count()

        inprogress_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(
            Students, Teams.team_lead_id == Students.stu_id
        ).filter(Students.dept == professor.dept, Projects.progress == 'inprogress').count()

        completed_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(
            Students, Teams.team_lead_id == Students.stu_id
        ).filter(Students.dept == professor.dept, Projects.progress == 'completed').count()

        pending_submissions = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(
            Students, Teams.team_lead_id == Students.stu_id
        ).filter(Students.dept == professor.dept, Projects.progress == 'pending').count()

        # Paginated projects
        projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(
            Students, Teams.team_lead_id == Students.stu_id
        ).filter(Students.dept == professor.dept).offset(offset).limit(per_page).all()

        teams = Teams.query.join(Students, Teams.team_lead_id == Students.stu_id).filter(
            Students.dept == professor.dept
        ).all()

        # Calculate project count for each team
        for team in teams:
            team.project_count = Projects.query.filter_by(team_id=team.team_id).count()

        return render_template(
            'hod_dashboard.html',
            professor=professor,
            total_projects=total_projects,
            total_teams=total_teams,
            total_students=total_students,
            total_professors=total_professors,
            inprogress_projects=inprogress_projects,
            completed_projects=completed_projects,
            pending_submissions=pending_submissions,
            teams=teams,
            projects=projects,
            page=page,
            per_page=per_page,
            total_pages=(total_projects + per_page - 1) // per_page
        )
    else:
        flash("Access restricted to the HOD.")
        return redirect(url_for('home'))

@app.route('/student_dashboard/<string:stu_id>', methods=['GET'])
@login_required
def student_dashboard(stu_id):
    if hasattr(current_user, 'stu_id') and current_user.stu_id == stu_id:
        student = Students.query.filter_by(stu_id=stu_id).first()
        teams = Teams.query.filter(or_(
            Teams.team_lead_id == stu_id,
            Teams.member_1 == stu_id,
            Teams.member_2 == stu_id,
            Teams.member_3 == stu_id,
            Teams.member_4 == stu_id
        )).all()

        team_projects = {}
        for team in teams:
            project = Projects.query.filter_by(team_id=team.team_id).first()
            team_projects[team.team_id] = project.project_title if project else "No Project Assigned"

        total_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).filter(
            (Teams.team_lead_id == stu_id) |
            (Teams.member_1 == stu_id) |
            (Teams.member_2 == stu_id) |
            (Teams.member_3 == stu_id) |
            (Teams.member_4 == stu_id)
        ).count()

        inprogress_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).filter(
            (Teams.team_lead_id == stu_id) |
            (Teams.member_1 == stu_id) |
            (Teams.member_2 == stu_id) |
            (Teams.member_3 == stu_id) |
            (Teams.member_4 == stu_id),
            Projects.progress == 'inprogress'
        ).all()
        completed_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).filter(
            (Teams.team_lead_id == stu_id) |
            (Teams.member_1 == stu_id) |
            (Teams.member_2 == stu_id) |
            (Teams.member_3 == stu_id) |
            (Teams.member_4 == stu_id),
            Projects.progress == 'completed'
        ).all()

        return render_template(
            'student_dashboard.html',
            student=student,
            teams=teams,
            team_projects=team_projects, 
            total_projects=total_projects,
            inprogress_count=len(inprogress_projects),
            completed_count=len(completed_projects),
            inprogress_projects=inprogress_projects,
            completed_projects=completed_projects
        )
    else:
        flash("Access restricted to the student.")
        return redirect(url_for('home'))

@app.route("/dashboard/<int:clg_id>")
@login_required
def dashboard(clg_id):
    if current_user.is_authenticated:
        if hasattr(current_user, 'clg_id'):
            clg_id = current_user.clg_id
            total_students = Students.query.filter_by(clg_id=clg_id).count()
            total_professors = Professors.query.filter_by(clg_id=clg_id).count()
            total_departments = db.session.query(func.count(func.distinct(Students.dept))).filter(Students.clg_id == clg_id).scalar()
            total_teams_in_each_dept = db.session.query(
                Students.dept, func.count(Teams.team_id).label('count')
            ).join(Teams, Students.stu_id == Teams.team_lead_id).filter(Students.clg_id == clg_id).group_by(Students.dept).all()
            total_professors_in_each_dept = db.session.query(
                Professors.dept, func.count(func.distinct(Professors.prof_id)).label('count')
            ).filter(Professors.clg_id == clg_id).group_by(Professors.dept).all()
            total_students_in_each_dept = db.session.query(
                Students.dept, func.count(Students.stu_id).label('count')
            ).filter(Students.clg_id == clg_id).group_by(Students.dept).all()
            print(total_professors_in_each_dept)
            print(total_teams_in_each_dept)
            total_teams = sum([row[1] for row in total_teams_in_each_dept])
            print(total_teams)
            total_teams = Teams.query.join(Students, Teams.team_lead_id == Students.stu_id).filter(Students.clg_id == clg_id).count()
            total_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(Students.clg_id == clg_id).count()
            
            # Get the current date and calculate the past 12 months
            current_date = datetime.now()
            past_12_months = [(current_date - timedelta(days=30 * i)).strftime('%B %Y') for i in range(11, -1, -1)]

            # Query to get the number of projects per month for the college
            project_counts = db.session.query(
                extract('year', Projects.date_added).label('year'),
                extract('month', Projects.date_added).label('month'),
                func.count(Projects.project_id).label('count')
            ).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                Students.clg_id == clg_id
            ).group_by(extract('year', Projects.date_added), extract('month', Projects.date_added)).all()

            # Prepare data for the chart
            months_dict = {month: 0 for month in past_12_months}
            for row in project_counts:
                month_year = datetime(year=int(row[0]), month=int(row[1]), day=1).strftime('%B %Y')
                if month_year in months_dict:
                    months_dict[month_year] = row[2]
            months = list(months_dict.keys())
            counts = list(months_dict.values())

            # Query to get the count of projects in progress and completed for the college
            inprogress_count = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                Students.clg_id == clg_id, Projects.progress == 'inprogress'
            ).count()
            completed_count = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                Students.clg_id == clg_id, Projects.progress == 'completed'
            ).count()

            # Query to get the department-wise total projects for the college
            dept_wise_projects = db.session.query(
                Students.dept, func.count(Projects.project_id).label('count')
            ).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                Students.clg_id == clg_id
            ).group_by(Students.dept).all()

            depts = [row[0] for row in dept_wise_projects]
            dept_counts = [row[1] for row in dept_wise_projects]

            return render_template('director_dashboard.html', total_students=total_students, total_professors=total_professors, total_teams=total_teams, total_projects=total_projects, months=months, counts=counts, inprogress_count=inprogress_count, completed_count=completed_count, depts=depts, dept_counts=dept_counts , total_departments = total_departments,total_teams_in_each_dept = total_teams_in_each_dept , total_professors_in_each_dept = total_professors_in_each_dept , total_students_in_each_dept = total_students_in_each_dept)
    else:
        flash("Please log in to view the dashboard.")
        return redirect(url_for('login'))

@app.route("/projects", methods=["GET"])
def projects():
    if current_user.is_authenticated:
        search_query = request.args.get('search', '').strip() 
        department_projects = []  
        myprojects = [] 
        projects = [] 

        if hasattr(current_user, 'clg_id'):
            if hasattr(current_user, 'prof_id'):
                prof_id = current_user.prof_id
                clg_id = current_user.clg_id
                dept = current_user.dept

                # Filter all projects of the college
                if search_query:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Professors, Projects.prof_id == Professors.prof_id).filter(
                        Professors.clg_id == clg_id, Projects.project_title.ilike(f"%{search_query}%")
                    ).order_by(Projects.project_id).all()
                else:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Professors, Projects.prof_id == Professors.prof_id).filter(
                        Professors.clg_id == clg_id
                    ).order_by(Projects.project_id).all()
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Professors, Projects.prof_id == Professors.prof_id).filter(
                        Professors.clg_id == clg_id
                    ).order_by(Projects.project_id).all()
                # Filter projects by department of professor
                if search_query:
                    department_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(Professors, Projects.prof_id == Professors.prof_id).filter(
                        Professors.dept == dept, Projects.project_title.ilike(f"%{search_query}%")
                    ).all()
                else:
                    department_projects = Projects.query.join(Teams, Projects.team_id == Teams.team_id).join(Professors, Projects.prof_id == Professors.prof_id).filter(
                        Professors.dept == dept
                    ).all()
                    
                # Filter projects assigned to the professor
                if search_query:
                    myprojects = Projects.query.filter(
                        Projects.prof_id == prof_id, Projects.project_title.ilike(f"%{search_query}%")
                    ).all()
                else:
                    myprojects = Projects.query.filter(
                        Projects.prof_id == prof_id
                    ).all()

            elif hasattr(current_user, 'stu_id'):
                stu_id = current_user.stu_id
                clg_id = current_user.clg_id
                dept = current_user.dept

                # Query for department projects
                if search_query:
                    department_projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.dept == dept, Projects.project_title.ilike(f"%{search_query}%")
                    ).order_by(Projects.project_id).all()
                else:
                    department_projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.dept == dept
                    ).order_by(Projects.project_id).all()

                # Query for college projects
                if search_query:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.clg_id == clg_id, Projects.project_title.ilike(f"%{search_query}%")
                    ).order_by(Projects.project_id).all()
                else:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.clg_id == clg_id
                    ).order_by(Projects.project_id).all()

                # Query for my projects
                if search_query:
                    myprojects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).filter(
                        (Teams.team_lead_id == stu_id) |
                        (Teams.member_1 == stu_id) |
                        (Teams.member_2 == stu_id) |
                        (Teams.member_3 == stu_id) |
                        (Teams.member_4 == stu_id),
                        Projects.project_title.ilike(f"%{search_query}%")
                    ).order_by(Projects.project_id).all()
                else:
                    myprojects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).filter(
                        (Teams.team_lead_id == stu_id) |
                        (Teams.member_1 == stu_id) |
                        (Teams.member_2 == stu_id) |
                        (Teams.member_3 == stu_id) |
                        (Teams.member_4 == stu_id)
                    ).order_by(Projects.project_id).all()
            else:
                clg_id = current_user.clg_id
                if search_query:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.clg_id == clg_id, Projects.project_title.ilike(f"%{search_query}%")
                    ).order_by(Projects.project_id).all()
                else:
                    projects = Projects.query.select_from(Projects).join(Teams, Projects.team_id == Teams.team_id).join(Students, Teams.team_lead_id == Students.stu_id).filter(
                        Students.clg_id == clg_id
                    ).order_by(Projects.project_id).all()
        else:
            projects = []
            department_projects = []
            myprojects = []

        return render_template('projects.html', projects=projects, department_projects=department_projects, myprojects=myprojects)
    else:
        flash("Please log in to view the projects.")
        return redirect(url_for('login'))

@app.route('/assign_project', methods=['GET', 'POST'])
@login_required
def assign_project():
    form = ProjectForm()
    if form.validate_on_submit():
        current_year = datetime.now().year
        team_id = form.team_id.data
        last_project = Projects.query.order_by(Projects.project_id.desc()).first()
        if last_project:
            last_seq = int(last_project.project_id[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        project_id = f"{current_year}{team_id}{new_seq}"
        prof_id = current_user.prof_id
        
        project = Projects(
            project_id=project_id,
            project_title=form.project_title.data,
            team_id=team_id,
            prof_id= prof_id ,
            description=form.project_description.data
        )
        db.session.add(project)
        db.session.commit()
        flash("Project assigned successfully!")
        return redirect(url_for('home'))
    return render_template('assign_project.html', form=form)


@app.route('/make_team', methods=['GET', 'POST'])
def make_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Teams.query.filter_by(team_id=form.team_id.data).first()
        if team is None:
            team = Teams(
                team_id=form.team_id.data,
                team_lead_id=form.team_lead_id.data,
                member_1=form.member_1.data,
                member_2=form.member_2.data,
                member_3=form.member_3.data,
                member_4=form.member_4.data
            )
            db.session.add(team)
            db.session.commit()
        
        form.team_id.data = ''
        form.team_lead_id.data = ''
        form.member_1.data = ''
        form.member_2.data = ''
        form.member_3.data = ''
        form.member_4.data = ''
    
    teams = Teams.query.order_by(Teams.team_id).all()
    return render_template('make_team.html', form=form, teams=teams)



@app.route('/student_dashboard/profile/<string:stu_id>', methods=['GET', 'POST'])
@login_required
def student_profile(stu_id):
    student = Students.query.filter_by(stu_id=stu_id).first()
    university = Directors.query.filter_by(clg_id=student.clg_id).first()
    teams = Teams.query.filter(or_(Teams.team_lead_id == stu_id, Teams.member_1 == stu_id, Teams.member_2 == stu_id, Teams.member_3 == stu_id, Teams.member_4 == stu_id)).all()
    
    # Query to get the number of projects per month
    project_counts = db.session.query(
        extract('month', Projects.date_added).label('month'),
        func.count(Projects.project_id).label('count')
    ).join(Teams, Projects.team_id == Teams.team_id).filter(
        (Teams.team_lead_id == stu_id) |
        (Teams.member_1 == stu_id) |
        (Teams.member_2 == stu_id) |
        (Teams.member_3 == stu_id) |
        (Teams.member_4 == stu_id)
    ).group_by('month').all()

    # Prepare data for the chart
    months = [row[0] for row in project_counts]
    counts = [row[1] for row in project_counts]
    print('Months:', months)
    print('Counts:', counts)

    return render_template('student_profile.html', student=student, university=university, teams=teams, months=months, counts=counts)

@app.route('/professor_dashboard/profile/<string:prof_id>' , methods = ['GET', 'POST'])
@login_required
def professor_profile(prof_id):
    professor = Professors.query.filter_by(prof_id=prof_id).first()
    print(professor)
    university = Directors.query.filter_by(clg_id = professor.clg_id).first()
    print(university)
    return render_template('professor_profile.html', professor=professor , university = university)

@app.route('/director_dashboard/profile/<string:clg_id>' , methods = ['GET', 'POST'])
@login_required
def director_profile(clg_id):
    director = Directors.query.filter_by(clg_id=clg_id).first()
    print(director)
    return render_template('director_profile.html', director=director )

# update student profile
@app.route('/student_dashboard/update_profile/<string:stu_id>', methods=['GET', 'POST'])
@login_required
def update_student_profile(stu_id):
    form = UpdateStudentProfileForm()
    updatestudent = Students.query.filter_by(stu_id=stu_id).first()
    if request.method == 'POST':
        updatestudent.stu_id = request.form['stu_id']
        updatestudent.stu_name = request.form['stu_name']
        updatestudent.year_of_study = request.form['year_of_study']
        updatestudent.about_me = request.form['aboutme']
        if 'profile_pic' in request.files:
            pic_file = request.files['profile_pic']
            pic_filename = secure_filename(pic_file.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            updatestudent.profile_pic = pic_name
            try:
                pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                db.session.commit()
                flash("Profile picture updated successfully")
                return redirect(url_for('student_profile', stu_id=updatestudent.stu_id))
            except:
                flash("Error..!! looks like there was a problem ... Try again later...")
                return render_template('update_student_profile.html', form=form, stu_id=updatestudent.stu_id)
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return redirect(url_for('student_profile', stu_id=updatestudent.stu_id))
        except:
            return render_template('update_student_profile.html', form=form, stu_id=updatestudent.stu_id)
    else:
        form.stu_id.data = updatestudent.stu_id
        form.stu_name.data = updatestudent.stu_name
        form.year_of_study.data = updatestudent.year_of_study
        form.aboutme.data = updatestudent.about_me
        return render_template('update_student_profile.html', form=form)

        
# log in page
@app.route('/login',methods = ["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.login_as.data == 'student':
            student = Students.query.filter_by(stu_id=form.id.data).first()
            if student and student.verify_password(form.password.data):
                login_user(student)
                flash("Login successful!")
                return redirect(url_for('home'))
            else:
                flash("Invalid student credentials.")   
        elif form.login_as.data == 'professor' :
            professor = Professors.query.filter_by(prof_id=form.id.data).first()
            if professor and professor.verify_password(form.password.data):
                login_user(professor)
                flash("PLogin successful!")
                return redirect(url_for('home'))
            else:
                flash("Invalid student credentials.")
        else :
            director = Directors.query.filter_by(clg_id=form.id.data).first()
            if director and director.verify_password(form.password.data):
                login_user(director)
                flash("PLogin successful!")
                return redirect(url_for('home'))
                 
    return render_template("login.html",form = form)

@app.route('/logout',methods = ["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You are logged out")
    return redirect(url_for('login'))

@app.route('/register/student' , methods =['GET','POST'])
def register_stu():
    form = StudentForm()
    if form.validate_on_submit():
        student = Students.query.filter_by(stu_id = form.stu_id.data).first()
        if student is None :
            password_hash = generate_password_hash(form.password.data)
            student = Students(stu_id = form.stu_id.data, stu_name = form.stu_name.data , gender = form.gender.data, email = form.email.data , clg_id = form.clg_id.data , year_of_study = form.year_of_study.data , dept = form.department.data , password_hash = password_hash)
            db.session.add(student)
            db.session.commit()
        
        form.stu_id.data = ''
        form.stu_name.data = ''
        form.email.data = ''
        form.clg_id.data = ''
        form.year_of_study.data = ''
        students = Students.query.order_by(Students.stu_id).all()
        return render_template('register_stu.html' ,form = form ,students = students)
    students = Students.query.order_by(Students.stu_id).all()
    return render_template('register_stu.html' , form = form ,students = students)

@app.route('/register/professor' , methods =['GET','POST'])
def register_prof():
    form = ProfessorForm()
    if form.validate_on_submit():
        professor = Professors.query.filter_by(prof_id = form.prof_id.data).first()
        if professor is None :
            password_hash = generate_password_hash(form.password.data)
            professors = Professors( prof_id = form.prof_id.data , prof_name = form.prof_name.data, gender = form.gender.data, clg_id = form.clg_id.data,  email = form.email.data , dept = form.department.data , doj = form.date_of_join.data , password_hash = password_hash  ,role = form.role.data)
            db.session.add(professors)
            db.session.commit()

        form.prof_id.data = ''
        form.prof_name.data = ''
        form.email.data = ''
        form.clg_id.data = ''
        form.date_of_join.data = ''
        
        professors = Professors.query.order_by(Professors.date_added).all()
        return render_template('register_prof.html' ,form = form ,professors = professors)
    professors = Professors.query.order_by(Professors.date_added).all()
    return render_template('register_prof.html' ,form = form,professors = professors)


@app.route('/register/director' , methods =['GET','POST'])
def register_director():
    form = DirectorForm()
    if form.validate_on_submit():
        director = Directors.query.filter_by(email = form.email.data).first()
        if director is None :
            password_hash = generate_password_hash(form.password.data)
            director = Directors(clg_id = form.clg_id.data, clg_name = form.clg_name.data , director_name = form.director_name.data , email = form.email.data , password_hash = password_hash )
            db.session.add(director)
            db.session.commit()
            
        directors = Directors.query.order_by(Directors.date_added).all()
        form.clg_id.data = ''
        form.clg_name.data = ''
        form.email.data = ''
        form.director_name.data = ''
        return render_template('register_director.html' ,form = form , directors = directors)

    prof = Professors.query.filter_by(clg_id = 102).all()
    directors = Directors.query.order_by(Directors.date_added).all()
    return render_template('register_director.html' ,form = form , directors = directors,professors = prof)

@app.route('/review_project/<string:project_id>/<string:action>', methods=['POST'])
@login_required
def review_project(project_id, action):
    project = Projects.query.get(project_id)
    if project and current_user.prof_id == project.prof_id:
        if action == 'approve':
            project.progress = 'completed'
            project.date_completed = datetime.utcnow()  
            project.is_approved = True
            db.session.commit()
            flash("Project approved successfully!")
        elif action == 'reject':
            project.is_submitted = False  
            db.session.commit()
            flash("Project rejected successfully!")
        return redirect(url_for('professor_dashboard', prof_id=current_user.prof_id))
    else:
        flash("You are not authorized to review this project.")
        return redirect(url_for('home'))

@app.route('/submit_project/<string:project_id>', methods=['POST'])
@login_required
def submit_project(project_id):
    project = Projects.query.get(project_id)
    if project and current_user.stu_id == project.team.team_lead_id:
        project.is_submitted = True 
        db.session.commit()
        flash("Project submitted successfully! Waiting for professor's approval.")
        return redirect(url_for('student_dashboard', stu_id=current_user.stu_id))
    else:
        flash("You are not authorized to submit this project.")
        return redirect(url_for('home'))


# STUDENTS
class Students(db.Model,UserMixin):
    stu_id = db.Column(db.String(50), primary_key = True )
    stu_name = db.Column(db.String(200),nullable = False)
    gender = db.Column(db.String(200),nullable = False)
    email = db.Column(db.String(100),nullable = False , unique =True)
    clg_id = db.Column(db.Integer,db.ForeignKey('directors.clg_id') )
    dept = db.Column(db.String(200),nullable = False)
    year_of_study = db.Column(db.String(200),nullable = False)
    about_me = db.Column(db.String(250))
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(),nullable = True)
    date_added = db.Column(db.DateTime , default = datetime.utcnow)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    def get_id(self):
        return self.stu_id
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    #create string
    def __repr__(self):
        return '<Name %r>' % self.stu_name

# PROFESSOR
class Professors(db.Model,UserMixin):
    prof_id = db.Column(db.String(50), primary_key = True )
    prof_name = db.Column(db.String(200),nullable = False)
    gender = db.Column(db.String(200),nullable = False)
    email = db.Column(db.String(100),nullable = False , unique =True)
    clg_id = db.Column(db.Integer,db.ForeignKey('directors.clg_id') )
    dept = db.Column(db.String(200),nullable = False)
    doj = db.Column(db.Date(),nullable = False)
    role = db.Column(db.String(100), nullable = False)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime , default = datetime.utcnow)
    
    def get_id(self):
        return self.prof_id
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    #create string
    def __repr__(self):
        return '<Name %r>' % self.prof_name

# DIRECTORS
class Directors(db.Model,UserMixin):
    clg_id = db.Column(db.String(50), primary_key = True )
    clg_name = db.Column(db.String(200),nullable = False)
    director_name = db.Column(db.String(200),nullable = False)
    email = db.Column(db.String(100),nullable = False , unique =True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime , default = datetime.utcnow)

    students = db.relationship('Students', backref='college', lazy=True)
    professors = db.relationship('Professors', backref='college', lazy=True)
    
    
    def get_id(self):
        return self.clg_id
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    #create string
    def __repr__(self):
        return '<Name %r>' % self.director_name

class Teams(db.Model, UserMixin):
    team_id = db.Column(db.String(50), primary_key=True)
    team_lead_id = db.Column(db.String(200), db.ForeignKey('students.stu_id'), nullable=False)
    member_1 = db.Column(db.String(200), db.ForeignKey('students.stu_id'), nullable=False)
    member_2 = db.Column(db.String(200), db.ForeignKey('students.stu_id'), nullable=False)
    member_3 = db.Column(db.String(200), db.ForeignKey('students.stu_id'), nullable=False)
    member_4 = db.Column(db.String(200), db.ForeignKey('students.stu_id'), nullable=True)  # optional

    # Relationships to Students model
    team_lead = db.relationship('Students', foreign_keys=[team_lead_id])
    member_1_student = db.relationship('Students', foreign_keys=[member_1])
    member_2_student = db.relationship('Students', foreign_keys=[member_2])
    member_3_student = db.relationship('Students', foreign_keys=[member_3])
    member_4_student = db.relationship('Students', foreign_keys=[member_4])

    def get_id(self):
        return self.team_id

class Projects(db.Model):
    project_id = db.Column(db.String(50), primary_key=True)
    project_title = db.Column(db.String(200), nullable=False)
    team_id = db.Column(db.String(50), db.ForeignKey('teams.team_id'), nullable=False)
    prof_id = db.Column(db.String(50), db.ForeignKey('professors.prof_id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    progress = db.Column(db.String(50), default='inprogress', nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the project was added
    date_completed = db.Column(db.DateTime, nullable=True)  # Date when the project was completed
    is_submitted = db.Column(db.Boolean, default=False)  # Track if the project is submitted
    is_approved = db.Column(db.Boolean, default=False)  # Track if the project is approved

    team = db.relationship('Teams', backref='project', lazy=True)
    professor = db.relationship('Professors', backref='projects', lazy=True)

    def get_id(self):
        return self.project_id

if __name__ == "__main__":
    app.run(debug=True)