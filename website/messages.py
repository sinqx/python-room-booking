from flask import Blueprint, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime
from .models import Message, Room
from . import db

messages = Blueprint("messages", __name__)


@messages.route("/get_all_messages", methods=["GET"])
def get_all_messages():
    start_date = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0
    )
    author = (
        f"{current_user.firstName} {current_user.secondName} {current_user.surname}"
    )
    all_messages = Message.query.filter(Message.creationDate > start_date).all()
    messages = []
    for message in all_messages:
        message_dict = {
            "messageId": message.id,
            "creationDate": message.creationDate.strftime("%m-%d %H:%M:"),
            "message_theme": message.messageTheme,
            "author": author,
        }

        messages.append(message_dict)
    # Преобразование объектов сообщений в словари или другой формат при необходимости
    return messages


@messages.route("/get_message_info", methods=["GET"])
def get_message_info():
    message_id = request.args.get("messageId")
    print(message_id)
    if not message_id:
        flash("Неверный запрос", category="error")
        return redirect(url_for("rooms.home"))

    messageInfo = Message.query.filter_by(id=message_id).first()
    print("777777777777777777777")
    print(jsonify({messageInfo}))
    return jsonify({"message": messageInfo})


@messages.route("/new_message", methods=["GET", "POST"])
@login_required
def new_message():
    data = request.get_json()

    main_text = data.get("mainText")
    message_theme = data.get("messageTheme")
    sent_to = data.get("sentTo")
    sent_to_head = data.get("sentToHead")
    user_position = data.get("userPosition")
    user_initials = data.get("userInitials")

    if not all(
        [main_text, message_theme, sent_to, sent_to_head, user_position, user_initials]
    ):
        return jsonify({"error": "Missing required fields"}), 400

    author = (
        f"{current_user.firstName} {current_user.secondName} {current_user.surname}"
    )

    new_message = Message(
        mainText=main_text,
        messageTheme=message_theme,
        creationDate=datetime.now(),
        sentFrom=author,
        sentTo=sent_to,
        sentToHead=sent_to_head,
        userPosition=user_position,
        userInitials=user_initials,
        isViewed=False,
    )

    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for("rooms.home"))


@messages.route("/edit_message", methods=["PATCH"])
@login_required
def edit_message():
    message_id = request.args.get("messageId")
    edited_message = Message.query.filter(Message.id == message_id).first()

    if edited_message and edited_message.user.id == current_user.id:
        message = request.form.get("message")

        if len(message.text) < 650:
            edited_message = message
            edited_message.creationDate = datetime.now()

            db.session.commit()
            flash("Сообщение отредактировано", category="success")
        else:
            flash("Не удалось отредактировать сообщение", category="error")
    else:
        flash("Вы не можете редактировать это сообщение", category="error")

    return redirect(url_for("messages.home"))


@messages.route("/message_is_done", methods=["PATCH"])
@login_required
def message_is_done():
    message_id = request.args.get("messageId")

    if not message_id:
        flash("Неверный запрос", category="error")
        return redirect(url_for("messages.home"))

    edited_message = Message.query.filter_by(id=message_id).first()

    if not edited_message:
        flash("Сообщение не найдено", category="error")
        return redirect(url_for("messages.home"))

    if edited_message.user.id != current_user.id:
        flash("Сообщение не принадлежит вам", category="error")
        return redirect(url_for("messages.home"))

    edited_message.isDone = True

    try:
        db.session.commit()
        flash("Выполнено", category="success")
    except Exception as e:
        db.session.rollback()
        flash("Произошла ошибка при сохранении изменений", category="error")

    return redirect(url_for("messages.home"))


@messages.route("/delete_message", methods=["DELETE"])
@login_required
def delete_message():
    message_id = request.args.get("messageId")

    delete_message = Message.query.filter(Message.id == message_id).first()

    if delete_message and delete_message.user.id == current_user.id:
        db.session.delete(delete_message)
        db.session.commit()
        flash("Сообщение удалено", category="success")
    else:
        flash("Вы не можете удалить это сообщение", category="error")

    return redirect(url_for("messages.home"))
