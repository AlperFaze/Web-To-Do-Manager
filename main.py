import datetime
import os

from datetime import datetime

from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from data.tasks import Tasks
from data.users import User
from data.category import Category
from forms.login_form import LoginForm
from forms.tasks import TasksForm
from forms.user import RegisterForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/task_db.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()

    category = db_sess.query(Category).all()
    tasks_sorted = []
    if current_user.is_authenticated:
        tasks = db_sess.query(Tasks).filter(Tasks.user == current_user)

        tasks_sorted = sorted(tasks, key=lambda x: (int(x.is_completed),
                                                    abs((x.deadline - datetime.now()).total_seconds()),
                                                    abs((x.deadline - datetime.now()).total_seconds())))

    return render_template("index.html", tasks=tasks_sorted, categories=category, now=datetime.now())


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
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()

    if form.validate_on_submit():
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.content = form.content.data

        tasks.user_id = current_user.id

        tasks.deadline = form.deadline.data

        selected_ids = request.form.getlist('options')
        if selected_ids:
            selected_ids = [int(x) for x in selected_ids]

            chosen_categories = db_sess.query(Category).filter(Category.id.in_(selected_ids)).all()

            tasks.categories.extend(chosen_categories)

        db_sess.add(tasks)
        db_sess.commit()

        return redirect('/')
    return render_template('tasks.html', title='Добавление новости',
                           form=form, categories=categories, now=datetime.now())


@app.route('/tasks/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tasks(id):
    form = TasksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            form.title.data = tasks.title
            form.content.data = tasks.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            tasks.title = form.title.data
            tasks.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('tasks.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                        Tasks.user == current_user
                                        ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/tasks_clear_completed', methods=['GET', 'POST'])
@login_required
def clear_completed():
    db_sess = db_session.create_session()
    db_sess.query(Tasks).filter(Tasks.user == current_user,
                                Tasks.is_completed == 1
                                ).delete()

    db_sess.commit()
    return redirect('/')


@app.route('/tasks_complete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_complete(id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                        Tasks.user == current_user
                                        ).first()
    if tasks:
        tasks.is_completed = True
        tasks.completed_at = datetime.now()
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    category_name = request.form.get('category_name')
    if category_name:
        category = Category()
        category.name = category_name
        db_sess = db_session.create_session()
        if not db_sess.query(Category).filter(Category.name == category_name).first():
            db_sess.add(category)
            db_sess.commit()

    return redirect('/')


if __name__ == '__main__':
    db_session.global_init("db/task_db.db")
    app.run(port=5000)
