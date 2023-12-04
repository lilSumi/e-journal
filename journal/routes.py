from journal import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from models import Users, Students, Teachers, Marks, GroopsTeachers, Groops, Dates
from datetime import date


@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return Users().query.get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        try:
            user = Users.query.filter_by(username=login).first()
        except:
            flash('No such user exists!')
        if user and user.password == password:
            login_user(user)
            next_page = request.args.get('next')
            if user.type == "student":
                return redirect(next_page or url_for('profiles'))
            else:
                return redirect('/teacher')
        flash('Incorrect login or password')
    return render_template('login.html')


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)
    return response


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profiles():
    grp_id = Students.query.filter_by(id=current_user.id).first().groop_id
    teachers = GroopsTeachers.query.filter_by(groop_id=grp_id).all()
    mark = dict()
    mark_avg = dict()
    for i in teachers:
        tch = Teachers.query.filter_by(id=i.teacher_id).first()
        marks1 = Marks.query.filter_by(teacher_id=tch.id, student_id=current_user.id).order_by(Marks.date_id).all()
        mks = list()
        for j in marks1:
            mks.append(j.mark)
        mks1 = [str(m) for m in mks]
        mark[tch.subject] = ' '.join(mks1)
        if len(mks) != 0:
            avg = round(sum(mks) / len(mks), 2)
        else:
            avg = 0
        mark_avg[tch.subject] = avg
    subjects = mark.keys()
    return render_template('profile.html', marks=mark, marks_avg=mark_avg, subjects=subjects)


@app.route('/teacher')
@login_required
def profile():
    return 'you are a teacher!'


@app.route('/teacher/<int:id>', methods=['GET', 'POST'])
@login_required
def profilet(id):
    if request.method == 'POST':
        ds = Dates.query.order_by(Dates.id).all()
        stds = Students.query.filter_by(groop_id=id).all()
        for i in stds:
            for j in ds:
                mark = request.form.get(f'{i.id}_{j.id}')
                try:
                    mk = Marks.query.filter_by(teacher_id=current_user.id, student_id=i.id, date_id=j.id).first()
                except:
                    pass
                if mk:
                    if not mark or mark == '':
                        db.session.delete(mk)
                        db.session.commit()
                    elif int(mark) == 1 or int(mark) == 2 or int(mark) == 3 or int(mark) == 4 or int(mark) == 5:
                        mk.mark = int(mark)
                        db.session.commit()
                else:
                    if not mark or mark == '':
                        pass
                    elif int(mark) == 1 or int(mark) == 2 or int(mark) == 3 or int(mark) == 4 or int(mark) == 5:
                        mk = Marks(teacher_id=current_user.id, student_id=i.id, date_id=j.id, mark=int(mark))
                        db.session.add(mk)
                        db.session.commit()
    ds = Dates.query.order_by(Dates.id).all()
    dts = list()
    for i in ds:
        d = i.date.split('-')
        dts.append((i.id, f'{d[2]}.{d[1]}'))
    stds = Students.query.filter_by(groop_id=id).all()
    marks = dict()
    for i in stds:
        mks = dict()
        for j in ds:
            try:
                mark = Marks.query.filter_by(teacher_id=current_user.id, student_id=i.id, date_id=j.id).first()
            except:
                pass
            if mark:
                mks[j.id] = (f'{i.id}_{j.id}', mark.mark)
            else:
                mks[j.id] = (f'{i.id}_{j.id}', '')
        mr = Marks.query.filter_by(teacher_id=current_user.id, student_id=i.id).all()
        m = [n.mark for n in mr]
        if len(m) != 0:
            avg = round(sum(m) / len(m), 2)
        else:
            avg = 0
        mks[0] = avg
        marks[i.id] = mks
    students = list()
    for i in stds:
        student = Users.query.filter_by(id=i.id).first()
        students.append((i.id, f'{student.name} {student.last_name}'))
        print(marks, dts, students, sep='\n')
    return render_template('profilet.html', dates=dts, students=students, marks=marks)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        type = request.form.get('type')
        groop = request.form.get('groop')
        subject = request.form.get('subject')
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        isadmin = request.form.get('isadmin')
        tgroops = request.form.get('groops').split(',')
        print(tgroops)
        user = Users(username=username, password=password, type=type, name=name, last_name=last_name, isadmin=isadmin)
        if type == 'teacher':
            db.session.add(user)
            db.session.commit()
            tchr = Users.query.filter_by(username=username).first()
            teacher = Teachers(id=tchr.id, subject=subject)
            db.session.add(teacher)
            for i in tgroops:
                grp = Groops.query.filter_by(name=i).first()
                gteacher = GroopsTeachers(groop_id=grp.id, teacher_id=tchr.id)
                db.session.add(gteacher)
            db.session.commit()
        else:
            db.session.add(user)
            db.session.commit()
            sndt = Users.query.filter_by(username=username).first()
            grp = Groops.query.filter_by(name=groop).first()
            student = Students(id=sndt.id, groop_id=grp.id)
            db.session.add(student)
            db.session.commit()
        return redirect(url_for('admin'))
    else:
        groops = Groops.query.order_by(Groops.id).all()
        return render_template('admin.html', groops=groops)


if __name__ == '__main__':
    app.run(debug=True)


