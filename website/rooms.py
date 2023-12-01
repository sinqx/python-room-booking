from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, or_
from .filters import get_plural_form
from .models import Room
from . import db
import json


rooms = Blueprint("rooms", __name__)
with open("website\static/roomsNames.json", "r", encoding="utf-8") as file:
    roomsNames = json.load(file)


@rooms.route("/", methods=["GET"])
def home():
    """
    Отображает домашнюю страницу с информацией о забронированных комнатах и функцией брони.
    Returns:
        HTML-страница с информацией о забронированных комнатах.
    """

    return render_template(
        "home.html",
        user=current_user,
        current_datetime=datetime.now(),
        roomsNames=roomsNames,
    )


@rooms.route("/userRooms", methods=["GET"])
@login_required
def userRooms():
    """
    Отображает домашнюю страницу с информацией о забронированных комнатах пользователя.
    Returns:
        HTML-страница с информацией о забронированных комнатах.
    """
    currentDatetime = datetime.now(timezone.utc)
    my_rooms = Room.query.filter(
        Room.userId == current_user.id, Room.endDate > currentDatetime
    ).all()

    for room in my_rooms:
        room_start = room.startDate.replace(tzinfo=timezone.utc)
        room_end = room.endDate.replace(tzinfo=timezone.utc)

        if currentDatetime >= room_start and currentDatetime < room_end:
            room.status = "В процессе"
        elif room_start > currentDatetime:
            time_difference = room_start - currentDatetime
            days = time_difference.days
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            days_str = get_plural_form(days, "день", "дня", "дней")
            hours_str = get_plural_form(hours, "час", "часа", "часов")
            minutes_str = get_plural_form(minutes, "минута", "минуты", "минут")

            if days > 0:
                room.status = f"Начало через: {days_str}, {hours_str}, {minutes_str}"
            elif hours > 0:
                room.status = f"Начало через: {hours_str}, {minutes_str}"
            else:
                room.status = f"Начало через: {minutes_str}"
        else:
            room.status = "Мероприятие окончено"
    return render_template(
        "userRooms.html",
        user=current_user,
        current_datetime=currentDatetime,
        myRooms=my_rooms,
        roomsNames=roomsNames,
    )


@rooms.route("/roomInfo", methods=["GET"])
@login_required
def getRoomInfo():
    """
    Отображает домашнюю страницу с информацией о забронированных комнатах пользователя.
    Returns:
        HTML-страница с информацией о забронированных комнатах.
    """
    roomId = int(request.args.get("id"))
    # Получение всех забронированных комнат пользователя, дата окончания которых позднее текущей даты
    roomInfo = Room.query.filter(Room.id == roomId)

    return render_template("edit_Booking.html", roomInfo=roomInfo)


@rooms.route("/bookedRooms/", methods=["GET"])
def get_all_booked_rooms():
    """
    Возвращает информацию о забронированных временных слотах для указанной комнаты в указанное число.

    Args:
        roomName (int): Номер комнаты.
         reservationDate (datetime): Дата брони.

    Returns:
        JSON-объект с информацией о забронированных временных слотах.
    """
    room_name = request.args.get("roomName")
    reservation_date = request.args.get("reservationDate")
    reservation_datetime = datetime.strptime(reservation_date, "%Y-%m-%dT%H:%M:%S.%fZ")

    booking_list = Room.query.filter(
        (Room.roomName == room_name),
        (Room.startDate >= reservation_datetime.strftime("%Y-%m-%d 00:00:00")),
        (Room.endDate <= reservation_datetime.strftime("%Y-%m-%d 24:00:00")),
        (Room.endDate > datetime.now()),
    ).all()

    occupied_times = []
    for booking in booking_list:
        start_time = booking.startDate.strftime("%Y-%m-%d %H:%M")
        end_time = booking.endDate.strftime("%Y-%m-%d %H:%M")
        booking_name = f"{booking.user.department} - <u> {booking.user.firstName} {booking.user.secondName}</u>"
        event_name = booking.conferenceTitle
        event_comment = booking.comment
        occupied_times.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "booking_name": booking_name,
                "event_name": event_name,
                "comment": event_comment,
            }
        )

    return jsonify({"occupied_times": occupied_times})


@rooms.route("/book_room", methods=["POST"])
@login_required
def book_room():
    """
    Бронирует комнату на указанный временной интервал.

    Args:
        roomName (str): Номер комнаты.
        startDate (str): Дата и время начала бронирования в формате "%Y-%m-%dT%H:%M".
        endDate (str): Дата и время окончания бронирования в формате "%Y-%m-%dT%H:%M".
        title (str): Название конференции.
        days (int): количество дней, сколько будет длиться конференция.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    room_name = request.form.get("roomName")
    event_days = request.form.get("eventDates")
    timeStart = request.form.get("timeInputStart")
    timeEnd = request.form.get("timeInputEnd")
    dates = event_days.split(", ")
    current_year = datetime.now().year

    for date in dates:
        # Создаем полноценную дату в формате "%Y-%m-%dT%H:%M"
        full_date_start = f"{current_year}-{date.strip()}T{timeStart}"
        full_date_end = f"{current_year}-{date.strip()}T{timeEnd}"

        # Преобразуем строки в объекты datetime
        datetime_start = datetime.strptime(full_date_start, "%Y-%m-%dT%H:%M")
        datetime_end = datetime.strptime(full_date_end, "%Y-%m-%dT%H:%M")

        if datetime_end - datetime_start > timedelta(hours=24):
            flash("Нельзя бронировать зал более чем на 24 часа", category="error")
        elif datetime_end < datetime_start + timedelta(minutes=15):
            flash("Нельзя бронировать зал менее чем на 15 минут", category="error")
        else:
            existing_bookings = Room.query.filter(
                Room.roomName == room_name,
                or_(
                    and_(
                        Room.startDate < datetime_end, Room.endDate > datetime_start
                    ),  # Проверка перекрытия существующих броней
                    and_(
                        Room.startDate == datetime_start, Room.endDate == datetime_end
                    ),  # Проверка точного совпадения времени бронирования
                    and_(
                        Room.startDate < datetime_start, Room.endDate > datetime_start
                    ),  # Проверка частичного перекрытия броней
                    and_(
                        Room.startDate < datetime_end, Room.endDate > datetime_end
                    ),  # Проверка частичного перекрытия броней
                ),
            ).all()

        if existing_bookings:
            flash(
                "Вы не можете забронировать это время:"
                + datetime_start
                + " - "
                + datetime_end,
                category="error",
            )
        else:
            conference_title = request.form.get("title")
            room_comment = request.form.get("comment")
            new_booking = Room(
                roomName=room_name,
                conferenceTitle=conference_title,
                startDate=datetime_start,
                endDate=datetime_end,
                userId=current_user.id,
                comment=room_comment,
            )

            db.session.add(new_booking)
            db.session.commit()

    return flash("Комната успешно забронирована", category="success"), redirect(
        url_for("rooms.home")
    )


@rooms.route("/cancel_book", methods=["POST", "DELETE"])
@login_required
def cancel_book():
    """
    Отменяет или завершает бронирование комнаты.

    Args:
        bookingId (str): Идентификатор бронирования.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    if request.method == "POST" or request.method == "DELETE":
        room_id = request.form.get("room_id")

        booked_room = Room.query.filter_by(id=room_id).first()

        current_time = datetime.now().astimezone(booked_room.startDate.tzinfo)
        if booked_room.userId == current_user.id:
            if current_time < booked_room.startDate:
                db.session.delete(booked_room)
                flash("Бронь отменена", category="success")
            elif (
                current_time > booked_room.startDate
                and current_time < booked_room.endDate
            ):
                booked_room.endDate = current_time
                flash("Бронь закончена", category="success")
            db.session.commit()
        else:
            flash("Вы можете отменять только свои брони", category="error")

    return redirect(url_for("rooms.home"))


@rooms.route("/edit_booking", methods=["POST", "PATCH"])
@login_required
def edit_booking():
    """
    Редактирует существующую бронь комнаты.

    Args:
        roomId (int): Идентификатор брони.

    Request Body (JSON):
        startDate (str): Новая дата и время начала бронирования в формате "%Y-%m-%dT%H:%M".
        endDate (str): Новая дата и время окончания бронирования в формате "%Y-%m-%dT%H:%M".
        title (str): Новое название конференции.
        comment (str): Новый комментарий к брони.

    Returns:
        JSON response:
            {
                "message": "Бронь успешно отредактирована"
            }
    """

    if request.method == "POST" or request.form.get("_method") == "PATCH":
        roomId = request.form.get("roomId")
        booking = Room.query.get(roomId)  # лучение существующей брони по идентификатору

        if not booking:
            return jsonify({"message": "Бронь не найдена"}), 404
        elif (
            booking.userId != current_user.id
        ):  # Проверка, что пользователь может редактировать только свои брони
            return (
                jsonify({"message": "У вас нет прав для редактирования этой брони"}),
                403,
            )
        else:
            room_name = request.form.get("roomName")
            datetime_start = datetime.strptime(
                request.form["startDate"], "%Y-%m-%dT%H:%M"
            )
            datetime_end = datetime.strptime(request.form["endDate"], "%Y-%m-%dT%H:%M")
            conference_title = request.form["title"]
            room_comment = request.form["comment"]

            if datetime_end - datetime_start > timedelta(hours=24):
                return (
                    jsonify({"message": "Нельзя бронировать зал более чем на 24 часа"}),
                    400,
                )
            elif datetime_end < datetime_start + timedelta(minutes=15):
                return (
                    jsonify(
                        {"message": "Нельзя бронировать зал менее чем на 15 минут"}
                    ),
                    400,
                )
            else:
                existing_bookings = Room.query.filter(
                    Room.roomName == booking.roomName,
                    or_(
                        and_(
                            Room.startDate < datetime_end, Room.endDate > datetime_start
                        ),  # Проверка перекрытия существующих броней
                        and_(
                            Room.startDate == datetime_start,
                            Room.endDate == datetime_end,
                        ),  # Проверка точного совпадения времени бронирования
                        and_(
                            Room.startDate < datetime_start,
                            Room.endDate > datetime_start,
                        ),  # Проверка частичного перекрытия броней
                        and_(
                            Room.startDate < datetime_end, Room.endDate > datetime_end
                        ),  # Проверка частичного перекрытия броней
                    ),
                    Room.id
                    != roomId,  # Исключение текущей брони из проверки перекрытия
                ).all()

                if existing_bookings:
                    return (
                        jsonify({"message": "Вы не можете забронировать на это время"}),
                        400,
                    )
                else:
                    booking.roomName = room_name
                    booking.startDate = datetime_start
                    booking.endDate = datetime_end
                    booking.conferenceTitle = conference_title
                    booking.comment = room_comment

                    db.session.commit()
                    flash("Бронь успешно отредактирована", category="info")

    return redirect(url_for("rooms.userRooms"))


