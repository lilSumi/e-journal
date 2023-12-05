from journal import db, app
from flask_login import UserMixin
from sqlalchemy import Integer, String, ForeignKey, delete
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    type: Mapped[str] = mapped_column(String(7), nullable=False)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    isadmin: Mapped[int] = mapped_column(Integer, nullable=True)

    student = relationship('Students', back_populates='user', cascade='save-update, merge, delete')

    def __repr__(self):
        return '<Users %r>' % self.id


class Groops(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(3), nullable=False)

    student = relationship('Students', back_populates='groop', cascade='save-update, merge, delete')
    teacher = relationship('GroopsTeachers', back_populates='groop', cascade='save-update, merge, delete')

    def __repr__(self):
        return '<Groops %r>' % self.id


class Subjects(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self):
        return '<Subjects %r>' % self.id


class Students(db.Model):
    id: Mapped[int] = mapped_column(Integer, ForeignKey(Users.id), primary_key=True)
    groop_id: Mapped[int] = mapped_column(Integer, ForeignKey(Groops.id))

    groop = relationship('Groops', back_populates='student')
    user = relationship('Users', back_populates='student')
    mark = relationship('Marks', back_populates='student', cascade='save-update, merge, delete')

    def __repr__(self):
        return '<Students %r>' % self.id


class SubjectsTeachers(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey(Subjects.id), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey(Users.id), nullable=False)


class GroopsTeachers(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    groop_id: Mapped[int] = mapped_column(Integer, ForeignKey(Groops.id), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey(Users.id), nullable=False)

    groop = relationship('Groops', back_populates='teacher')


class Dates(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey(Subjects.id), nullable=False)
    groop_id: Mapped[int] = mapped_column(Integer, ForeignKey(Groops.id), nullable=False)

    def __repr__(self):
        return '<Dates %r>' % self.id


class Marks(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mark: Mapped[int] = mapped_column(Integer, nullable=False)
    date_id: Mapped[str] = mapped_column(Integer, ForeignKey(Dates.id), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey(Subjects.id))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey(Students.id))

    student = relationship('Students', back_populates='mark')

    def __repr__(self):
        return '<Marks %r>' % self.id


