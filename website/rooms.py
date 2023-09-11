from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from .models import Room
from . import db

rooms = Blueprint("rooms", __name__)


@rooms.route("/", methods=["GET"])
@login_required
def home():
    currentDatetime = datetime.now()

    my_rooms = Room.query.filter(
        Room.userId == current_user.id, Room.endDate > currentDatetime
    ).all()
    print(my_rooms)
    myRooms = []
    for room in my_rooms:
        start_time = room.startDate.strftime("%Y-%m-%d -- %H:%M")
        end_time = room.endDate.strftime("%Y-%m-%d -- %H:%M")
        room_name = room.roomNumber
        booked_by_name = f"{room.user.first_name} {room.user.second_name}"
        event_name = room.conferenceTitle
        myRooms.append(
            {
                "room_name": room_name,
                "start_time": start_time,
                "end_time": end_time,
                "booked_by_name": booked_by_name,
                "event_name": event_name,
            }
        )

    return render_template(
        "home.html",
        user=current_user,
        current_datetime=currentDatetime,
        myRooms=myRooms,
    )


@rooms.route("/roomInfo/", methods=["GET"])
def get_room_info():
    room_number = int(request.args.get("roomNumber"))
    booking_list = Room.query.filter((Room.roomNumber == room_number)).all()

    occupied_times = []
    for booking in booking_list:
        start_time = booking.startDate.strftime("%Y-%m-%dT%H:%M")
        end_time = booking.endDate.strftime("%Y-%m-%dT%H:%M")
        booking_name = f"{booking.user.first_name} {booking.user.second_name}"
        event_name = booking.conferenceTitle
        occupied_times.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "booking_name": booking_name,
                "event_name": event_name,
            }
        )

    return jsonify({"occupied_times": occupied_times})


@rooms.route("/book_room", methods=["POST"])
@login_required
def book_room():
    room_number = request.form.get("roomNumber")
    start_date = datetime.strptime(request.form.get("startDate"), "%Y-%m-%dT%H:%M")
    end_date = datetime.strptime(request.form.get("endDate"), "%Y-%m-%dT%H:%M")
    conference_title = request.form.get("title")

    if end_date - start_date > timedelta(hours=2):
        flash("Нельзя бронировать зал более чем на 2 часа", category="error")
    elif end_date < start_date + timedelta(minutes=15):
        flash("Нельзя бронировать зал менее чем на 15 минут", category="error")
    else:
        existing_bookings = Room.query.filter(
            Room.roomNumber == room_number,
            or_(
                and_(
                    Room.startDate < end_date, Room.endDate > start_date
                ),  # Проверка перекрытия существующих броней
                and_(
                    Room.startDate == start_date, Room.endDate == end_date
                ),  # Проверка точного совпадения времени бронирования
                and_(
                    Room.startDate < start_date, Room.endDate > start_date
                ),  # Проверка частичного перекрытия броней
                and_(
                    Room.startDate < end_date, Room.endDate > end_date
                ),  # Проверка частичного перекрытия броней
            ),
        ).all()

        if existing_bookings:
            flash("Вы не можете забронировать на это время", category="error")
        else:
            new_booking = Room(
                roomNumber=room_number,
                conferenceTitle=conference_title,
                startDate=start_date,
                endDate=end_date,
                userId=current_user.id,
            )

            db.session.add(new_booking)
            db.session.commit()
            flash("Комната успешно забронирована", category="success")

    return redirect(url_for("rooms.home"))


@rooms.route("/cancel_book", methods=["PATCH", "DELETE"])
@login_required
def canlcel_book():
    booking_id = request.args.get("bookingId")
    booked_room = Room.query.filter_by(id=booking_id).first()

    if booked_room.userId == current_user.id:
        if request.method == "DELETE" and datetime.now() < booked_room.startDate:
            db.session.delete(booked_room)
            flash("Бронь отменена")
        elif request.method == "PATCH" and datetime.now() > booked_room.startDate:
            booked_room.endDate = datetime.now()
            flash("Бронь закончена")
        db.session.commit()
    else:
        flash("Не вы бронировали комнату")

    return redirect(url_for("rooms.home"))
