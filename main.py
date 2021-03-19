from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.users import User
from data.news import News
from data.jobs import Jobs

from data.job_form import JobForm
from data.news_form import NewsForm
from data.login_form import LoginForm
from data.register_form import RegisterForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import jobs_api
import datetime

import sqlalchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    # user = User()
    # user.surname = "Scott"
    # user.name = "Ridley"
    # user.age = "21"
    # user.position = "captain"
    # user.speciality = "research engineer"
    # user.address = "module_1"
    # user.email = "scott_chief@mars.org"
    #
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()
    #
    # user = db_sess.query(User).first()
    # for user in db_sess.query(User).filter(addres='module_1'):
    #     print(user)
    db_sess = db_session.create_session()
    app.run()


@app.route('/news')
def news():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template('news.html', news=news.all()[::-1])


@app.route('/jobs')
@app.route('/')
def work_log():
    db_sess = db_session.create_session()
    return render_template('jobs.html', jobs=db_sess.query(Jobs).all()[::-1])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.position = form.speciality.data
        user.address = form.adress.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/create_news', methods=['GET', 'POST'])
@login_required
def news_add():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/news')
    return render_template('create_news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/create_jobs', methods=['GET', 'POST'])
@login_required
def jobs_add():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.team_leader = current_user
        jobs.job = form.job.data
        jobs.work_size = float(form.work_size.data)
        jobs.collaborators = form.collaborators.data
        jobs.start_date = datetime.datetime.now()
        jobs.end_date = datetime.datetime.now() + datetime.timedelta(hours=float(form.work_size.data))
        jobs.is_finished = form.is_finished.data
        current_user.jobs.append(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/jobs')
    return render_template('create_jobs.html', title='Создание работы',
                           form=form)


@app.route('/jobs_delete/<int:job_id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(job_id):
    db_sess = db_session.create_session()
    if current_user.id == 1 or db_sess.query(Jobs).filter(Jobs.team_leader == current_user.id, Jobs.id == job_id).all():
        db_sess.query(Jobs).filter(Jobs.id == job_id).delete()
        db_sess.commit()
        return redirect('/jobs')


@app.route('/jobs/<int:job_id>', methods=['GET', 'POST'])
@login_required
def jobs_edit(job_id):
    db_sess = db_session.create_session()
    form = JobForm()
    if form.validate_on_submit():
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
        jobs.job = form.job.data
        jobs.work_size = float(form.work_size.data)
        jobs.collaborators = form.collaborators.data
        jobs.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/jobs')
    if current_user.id == 1 or db_sess.query(Jobs).filter(Jobs.team_leader == current_user.id, Jobs.id == job_id).all():
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
        form.job.data = jobs.job
        form.work_size.data = jobs.work_size
        form.collaborators.data = jobs.collaborators
        form.is_finished.data = jobs.is_finished
        form.is_finished = form.is_finished.data

        return render_template('create_jobs.html', title='Создание работы',
                               form=form)
    return redirect('/')


if __name__ == '__main__':
    main()
