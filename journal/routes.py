from journal import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, current_user, logout_user
from models import Users, Students, Subjects, Marks, GroopsTeachers, Groops, Dates, SubjectsTeachers
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
    grp_id = Students.query.filter_by(id=current_user.id).first().groop_id  # Ищем из какого класса чел
    teachers = GroopsTeachers.query.filter_by(groop_id=grp_id).all()  # Ищем какие учителя учат чела
    subjects = list()  # Список в котором названия предметов
    for i in teachers:
        subj = SubjectsTeachers.query.filter_by(teacher_id=i.teacher_id).all()  # Ищем какие предметы ведёт учитель
        for j in subj:
            sub = Subjects.query.filter_by(id=j.subject_id).all()  # Ищем названия предметов в соответствующей таблице
            for m in sub:
                subjects.append((m.id, m.name))
    mark = dict()
    mark_avg = dict()
    for i in subjects:
        marks = Marks.query.filter_by(student_id=current_user.id, subject_id=i[0]).order_by(Marks.date_id).all()
        mks = list()
        for j in marks:
            mks.append(j.mark)
        mks1 = [str(m) for m in mks]
        mark[i[0]] = ' '.join(mks1)
        if len(mks) != 0:
            avg = round(sum(mks) / len(mks), 2)
        else:
            avg = 0
        mark_avg[i[0]] = avg
        me = Users.query.filter_by(id=current_user.id).first()
        name = f'{me.last_name} {me.name}'
    return render_template('profile.html', marks=mark, marks_avg=mark_avg, subjects=subjects, name=name)


@app.route('/teacher')
@login_required
def profile():
    subjects = list()
    subj = SubjectsTeachers.query.filter_by(teacher_id=current_user.id).all()  # Ищем какие предметы ведёт учитель
    for j in subj:
        sub = Subjects.query.filter_by(id=j.subject_id).all()  # Ищем названия предметов в соответствующей таблице
        for m in sub:
            subjects.append((m.id, m.name))
    us = Users.query.filter_by(id=current_user.id).first()
    user = f'{us.last_name} {us.name}'
    return render_template('tasks.html', subjects=subjects, name=user)


@app.route('/teacher/<int:subject_id>')
@login_required
def choose_groop(subject_id):
    subjects = list()
    subj = SubjectsTeachers.query.filter_by(teacher_id=current_user.id).all()  # Ищем какие предметы ведёт учитель
    for j in subj:
        sub = Subjects.query.filter_by(id=j.subject_id).all()  # Ищем названия предметов в соответствующей таблице
        for m in sub:
            subjects.append((m.id, m.name))
    groops = list()
    grps = GroopsTeachers.query.filter_by(teacher_id=current_user.id).all()
    for j in grps:
        grp = Groops.query.filter_by(id=j.groop_id).all()
        for m in grp:
            groops.append((m.id, m.name))
    subject = Subjects.query.filter_by(id=subject_id).first()
    us = Users.query.filter_by(id=current_user.id).first()
    user = f'{us.last_name} {us.name}'
    return render_template('groops.html', subjects=subjects, groops=groops, id=subject_id, task=subject.name, name=user)


@app.route('/teacher/<int:subject_id>/<int:groop_id>', methods=['GET', 'POST'])
@login_required
def profilet(subject_id, groop_id):
    user = Users.query.filter_by(id=current_user.id).first()
    if user.type == 'teacher':
        gt = [i.groop_id for i in GroopsTeachers.query.filter_by(teacher_id=current_user.id).all()]
        st = [i.subject_id for i in SubjectsTeachers.query.filter_by(teacher_id=current_user.id).all()]
        if groop_id in gt and subject_id in st:
            if request.method == 'POST':
                ds = Dates.query.filter_by(groop_id=groop_id, subject_id=subject_id).order_by(Dates.date).all()
                stds = Students.query.filter_by(groop_id=groop_id).all()
                for i in stds:
                    for j in ds:
                        mark = request.form.get(f'{i.id}_{j.id}')
                        try:
                            mk = Marks.query.filter_by(subject_id=subject_id, student_id=i.id, date_id=j.id).first()
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
                                mk = Marks(subject_id=subject_id, student_id=i.id, date_id=j.id, mark=int(mark))
                                db.session.add(mk)
                                db.session.commit()
            subjects = list()
            subj = SubjectsTeachers.query.filter_by(
                teacher_id=current_user.id).all()  # Ищем какие предметы ведёт учитель
            for j in subj:
                sub = Subjects.query.filter_by(
                    id=j.subject_id).all()  # Ищем названия предметов в соответствующей таблице
                for m in sub:
                    subjects.append((m.id, m.name))
            groops = list()
            grps = GroopsTeachers.query.filter_by(teacher_id=current_user.id).all()
            for j in grps:
                grp = Groops.query.filter_by(id=j.groop_id).all()
                for m in grp:
                    groops.append((m.id, m.name))
            ds = Dates.query.filter_by(groop_id=groop_id, subject_id=subject_id).order_by(Dates.date).all()
            dts = list()
            for i in ds:
                d = i.date.split('-')
                dts.append((i.id, f'{d[2]}.{d[1]}'))
            stds = Students.query.filter_by(groop_id=groop_id).all()
            marks = dict()
            for i in stds:
                mks = dict()
                for j in ds:
                    try:
                        mark = Marks.query.filter_by(subject_id=subject_id, student_id=i.id, date_id=j.id).first()
                    except:
                        pass
                    if mark:
                        mks[j.id] = (f'{i.id}_{j.id}', mark.mark)
                    else:
                        mks[j.id] = (f'{i.id}_{j.id}', '')
                mr = Marks.query.filter_by(subject_id=subject_id, student_id=i.id).all()
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
                students.append((i.id, f'{student.last_name} {student.name}'))
            students.sort(key=lambda w: w[1])
            subject = Subjects.query.filter_by(id=subject_id).first()
            us = Users.query.filter_by(id=current_user.id).first()
            user = f'{us.last_name} {us.name}'
            g = Groops.query.filter_by(id=groop_id).first()
            return render_template('profilet.html', dates=dts, students=students, marks=marks,
                                   subject_id=str(subject_id), groop_id=groop_id, subjects=subjects, groops=groops,
                                   task=subject.name, name=user, groop=g.name)
        return abort(403)
    return abort(403)


@app.route('/teacher/<int:subject_id>/<int:groop_id>/create', methods=['GET', 'POST'])
@login_required
def create(subject_id, groop_id):
    if request.method == 'POST':
        date1 = date.today()
        dt = request.form.get('date')
        if dt <= str(date1):
            try:
                dat = Dates.query.filter_by(date=dt, subject_id=subject_id, groop_id=groop_id).first()
            except:
                pass
            if not dat:
                dat = Dates(date=dt, subject_id=subject_id, groop_id=groop_id)
                db.session.add(dat)
                db.session.commit()
            return redirect(f'/teacher/{subject_id}/{groop_id}')
        return redirect(f'/teacher/{subject_id}/{groop_id}/create')
    return render_template('create.html', subject_id=subject_id, groop_id=groop_id)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        type = request.form.get('type')
        groop = request.form.get('groop')
        subject = request.form.get('subject').split(',')
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        isadmin = request.form.get('isadmin')
        tgroops = request.form.get('groops').split(',')
        user = Users(username=username, password=password, type=type, name=name, last_name=last_name, isadmin=isadmin)
        if type == 'teacher':
            db.session.add(user)
            db.session.commit()
            tchr = Users.query.filter_by(username=username).first()
            for i in tgroops:
                grp = Groops.query.filter_by(name=i).first()
                gteacher = GroopsTeachers(groop_id=grp.id, teacher_id=tchr.id)
                db.session.add(gteacher)
            for i in subject:
                sbj = Subjects.query.filter_by(name=i).first()
                steacher = SubjectsTeachers(teacher_id=tchr.id, subject_id=sbj.id)
                db.session.add(steacher)
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


