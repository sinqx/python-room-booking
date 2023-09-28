from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ## означает из __init__.py импортировать db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Регистрирует пользователя и выполняет вход в систему.

    Args:
        email (str): Электронная почта пользователя.
        password (str): Пароль пользователя.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("rooms.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    """
    Выходит из системы текущего пользователя.

    Returns:
        Перенаправление на страницу входа в систему.
    """
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """
    Регистрирует нового пользователя.

    Args:
        email (str): Электронная почта пользователя.
        first_name (str): Имя пользователя.
        second_name (str): Фамилия пользователя.
        password1 (str): Пароль пользователя.
        password2 (str): Подтверждение пароля пользователя.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        second_name = request.form.get("secondName")
        surname = request.form.get("surname")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_exists = db.session.query(
            User.query.filter_by(email=email).exists()
        ).scalar()
        if user_exists:
            flash("Пользователь с таким email уже существует.", category="error")
        elif len(email) < 4:
            flash("Email должен содержать более 3 символов.", category="error")
        elif len(first_name) < 2:
            flash("Имя должно содержать более 1 символа.", category="error")
        elif len(second_name) < 2:
            flash("Фамилия должна содержать более 1 символа.", category="error")
        elif password1 != password2:
            flash("Пароли не совпадают.", category="error")
        elif len(password1) < 6:
            flash("Пароль должен содержать не менее 6 символов.", category="error")
        else:
            new_user = User(
                email=email,
                firstName=first_name,
                secondName=second_name,
                surname=surname,
                password=generate_password_hash(password1, method="sha256"),
                role="user",
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("rooms.home"))

    return render_template("sign_up.html", user=current_user)
