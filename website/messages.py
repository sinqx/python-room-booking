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
    
    all_messages = Message.query.filter(Message.creationDate > start_date).all() 
    messages = []
    for message in all_messages:
        message_dict = {
            "text": message.text,
            "creationDate": message.creationDate.strftime("%Y-%m-%d %H:%M:%S"),
            "roomNum": message.room.roomNumber,
            "event_name": message.room.conferenceTitle,
            "author":message.room.user.id
        }
        
        messages.append(message_dict)
    # Преобразование объектов сообщений в словари или другой формат при необходимости
    return messages


@messages.route("/get_room_messages", methods=["GET"])
def get_room_messages(room_number):  # Добавление параметра room_number
    current_datetime = datetime.now()

    booked_room = Room.query.filter(
        Room.roomNumber == room_number, Room.endDate >= current_datetime
    ).first()

    if booked_room is None:
        return jsonify({"error": "Room not found or booking has ended"})

    room_messages = Message.query.filter(
        Message.roomId == booked_room.id,
        Message.creationDate >= booked_room.startDate,
        Message.creationDate <= current_datetime,
    ).all()

    messages = []
    for message in room_messages:
        message_dict = {
            "text": message.text,
            "creationDate": message.creationDate.strftime("%Y-%m-%d %H:%M:%S"),
            "bookingId": message.roomId,
        }
        messages.append(message_dict)
    # Преобразование объектов сообщений в словари или другой формат при необходимости
    return messages  # Возвращение списка сообщений вместо jsonify()


@messages.route("/new_message", methods=["GET", "POST"])
@login_required
def new_message():
    booking_id = request.args.get("booking_id")
    booked_room = Room.query.get(booking_id)

    print(booked_room.userId)
    print(current_user.id)

    if booked_room.userId == current_user.id:
        message = session.get("message")
        session.pop("message", None)

        if message and len(message) < 250:
            new_message_obj = Message(
                text=message,
                creationDate=datetime.now(),
                roomId=booking_id,
            )
            db.session.add(new_message_obj)
            db.session.commit()
            flash("Сообщение добавлено.", category="success")
        else:
            flash("Не удалось добавить сообщение", category="error")
    return redirect(url_for("rooms.home"))


@messages.route("/edit_message", methods=["PATCH"])
@login_required
def edit_message():
    message_id = request.args.get("messageId")
    edited_message = Message.query.filter(Message.id == message_id).first()

    if edited_message and edited_message.user_id == current_user.id:
        message = request.form.get("message")

        if len(message) < 250:
            edited_message.text = message
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

    if edited_message.room.userId != current_user.id:
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

    if delete_message and delete_message.user_id == current_user.id:
        db.session.delete(delete_message)
        db.session.commit()
        flash("Сообщение удалено", category="success")
    else:
        flash("Вы не можете удалить это сообщение", category="error")

    return redirect(url_for("messages.home"))
