async function getAllBookedRooms(reservationDate) {
  try {
    const [bookedRoomsData, roomsNamesData] = await Promise.all([
      fetch(`/bookedRooms/?reservationDate=${reservationDate}`),
      fetch("static/roomsNames.json"),
    ]);
    const [bookedRooms, roomsNames] = await Promise.all([
      bookedRoomsData.json(),
      roomsNamesData.json(),
    ]);

    const bookedRoomNames = bookedRooms.occupied_times.map(
      (booking) => booking.roomName
    );
    const unbookedRoomNames = roomsNames.filter(
      (roomName) => !bookedRoomNames.includes(roomName)
    );

    roomsNames.forEach((roomName) => {
      const occupiedTimesElement = document.getElementById(roomName);
      occupiedTimesElement.innerHTML = "";
      if (unbookedRoomNames.includes(roomName)) {
        noReservationSign(occupiedTimesElement);
      }
    });

    bookedRooms.occupied_times.forEach((booking) => {
      const occupiedTimesElement = document.getElementById(booking.roomName);
      const occupiedTime = document.createElement("li");
      occupiedTime.style.marginBottom = "10px";

      const startTime = new Date(booking.start_time);
      const endTime = new Date(booking.end_time);
      const currentDateTime = new Date();

      const timeRange = document.createElement("span");
      timeRange.innerHTML =
        new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(startTime) +
        " - " +
        new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(endTime);

      if (currentDateTime >= startTime && currentDateTime <= endTime) {
        timeRange.style.backgroundColor = "green";
      } else if (currentDateTime > endTime) {
        timeRange.style.backgroundColor = "red";
      } else {
        timeRange.style.backgroundColor = "orange";
      }
      timeRange.style.borderRadius = "30px";
      timeRange.style.padding = "5px 10px";
      timeRange.style.color = "white";

      occupiedTime.innerHTML = `
        <div class="booking-details__list_item">
          <div class="booking-details__info">
            <strong>${booking.event_name}</strong>
            ${timeRange.outerHTML}
            Забронированно на: ${booking.booking_name}
          </div>
          ${
            booking.comment && booking.comment.length > 0
              ? `<div>
                <button
                  type="button"
                  class="btn btn-xs"
                  data-bs-toggle="popover"
                  data-bs-title="Информация:"
                  data-bs-placement="right"
                  >
                  <img
                      width="25"
                      height="25"
                      src="../static/info_icon.svg"
                      alt="Info Icon"
                    />
                </button>
              </div>`
              : ""
          }
        </div>`;
      if (booking.comment && booking.comment.length > 0) {
        const newButton = occupiedTime.querySelector(
          "button[data-bs-toggle='popover']"
        );
        const popover = new bootstrap.Popover(newButton, {
          content: booking.comment,
        });
        newButton.addEventListener("click", function () {
          popover.toggle();
        });
      }

      occupiedTimesElement.appendChild(occupiedTime);
    });
  } catch (error) {
    console.error("Ошибка: ", error);
  }

  function noReservationSign(element) {
    element.innerHTML = `<p>Броней нет.</p>`;
  }
}

function fillModalForm(roomId, conferenceTitle, startDate, endDate, comment) {
  // Заполняем значениями из аргументов функции
  var titleInput = document.getElementById("title");
  var startDateInput = document.getElementById("startDate");
  var endDateInput = document.getElementById("endDate");
  var commentInput = document.getElementById("comment");
  var roomIdInput = document.getElementById("roomId");

  titleInput.value = conferenceTitle;
  //eventDay.value = formatDate(document.getElementById("startDate"));
  console.log(comment);
  commentInput.value = comment;
  roomIdInput.value = roomId;
  startDateInput.value = formatDate(startDate);
  endDateInput.value = formatDate(endDate);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

async function roomInfo(roomId) {
  fetch(`/roomInfo=${roomId}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      // Полученный объект сообщения
      const room = data.room;

      // Пример обновления контейнера с текстом сообщения
      const roomContainer = document.getElementById("roomContainer");
      if (roomContainer) {
        roomContainer.room = room;
      }
    })
    .catch((error) => {
      console.error("Ошибка при получении информации о брони:", error);
    });
}

// Получение информации о бронировании комнаты и сообщениях
document.addEventListener("DOMContentLoaded", function () {
  // Получаем все кнопки зала
  const modalButtons = document.querySelectorAll(
    '.button[data-bs-toggle="modal"]'
  );
  modalButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const roomName = this.getAttribute("data-room-name");
      const modalIndex = this.getAttribute("data-room-number");
      const roomNameElement = document.getElementById("roomName" + modalIndex);
      if (roomNameElement) {
        roomNameElement.textContent = roomName;
      }
      const today = new Date();
      const dateInput = document.getElementById("eventDates" + modalIndex);

      flatpickr(dateInput, {
        mode: "multiple",
        defaultDate: today,
        minDate: today,
        maxDate: new Date().fp_incr(18), // Ограничение на 7 дней вперед
        dateFormat: "d-m",
      });

      const timeInputStart = document.getElementById(
        "timeInputStart" + modalIndex
      );
      flatpickr(timeInputStart, {
        enableTime: true,
        noCalendar: true,
        minTime: "8:30",
        maxTime: "16:30",
        dateFormat: "H:i",
        time_24hr: true,
        defaultDate: "8:30",
      });

      const timeInputEnd = document.getElementById("timeInputEnd" + modalIndex);
      flatpickr(timeInputEnd, {
        enableTime: true,
        noCalendar: true,
        minTime: "9:30",
        maxTime: "17:30",
        dateFormat: "H:i",
        time_24hr: true,
        defaultDate: "17:30",
      });
    });
  });

  let currentDate = new Date().toISOString();
  getAllBookedRooms(currentDate.replace(/T/, " ").slice(0, 16));

  const currentDateElement = document.getElementById("currentDate");
  function updateCurrentDate() {
    currentDateElement.textContent = currentDate.slice(0, 10);
  }
  updateCurrentDate();

  const prevDateButton = document.getElementById("prevDate");
  prevDateButton.addEventListener("click", () => {
    const today = new Date(); // Текущая дата
    const previousDate = new Date(currentDate); // Создание копии текущей даты
    today.setDate(today.getDate() - 1);
    previousDate.setDate(previousDate.getDate() - 1); // Установка предыдущей даты
    // Проверка, если предыдущая дата находится в прошлом относительно текущей даты
    if (previousDate >= today) {
      currentDate = previousDate.toISOString(); // Обновление текущей даты
      updateCurrentDate();
      getAllBookedRooms(currentDate.replace(/T/, " ").slice(0, 16));
    }
  });

  // Обработчик события для кнопки "Следующая дата"
  const nextDateButton = document.getElementById("nextDate");
  nextDateButton.addEventListener("click", () => {
    const nextDate = new Date(currentDate); // Создание копии текущей даты
    nextDate.setDate(nextDate.getDate() + 1); // Установка следующей даты

    const nextDateString = nextDate.toISOString(); // Преобразование следующей даты в строку
    currentDate = nextDateString; // Обновление текущей даты
    updateCurrentDate();
    getAllBookedRooms(currentDate.replace(/T/, " ").slice(0, 16));
  });

  const closeButton = document.querySelectorAll('[data-dismiss="alert"]');
  closeButton.forEach(function (button) {
    button.addEventListener("click", function () {
      const alert = this.closest(".alert");
      alert.remove();
    });
  });
});

let popoverTriggerList = [].slice.call(
  document.querySelectorAll("[data-bs-toggle='popover']")
);
let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl);
});

// Получаем все кнопки с атрибутом data-bs-toggle="popover"
const popoverButtons = document.querySelectorAll('[data-bs-toggle="popover"]');

// Добавляем обработчик события "click" для всего документа
document.addEventListener("click", function (event) {
  const target = event.target;

  // Проверяем, является ли цель события popover или находится ли она внутри popover
  const isClickInsidePopover = Array.from(popoverButtons).some(function (
    button
  ) {
    const popover = bootstrap.Popover.getInstance(button);
    return popover && popover._element.contains(target);
  });

  // Если щелчок был сделан вне popover, скрываем все popover
  if (!isClickInsidePopover) {
    Array.from(popoverButtons).forEach(function (button) {
      const popoverInstance = bootstrap.Popover.getInstance(button);
      if (popoverInstance && popoverInstance._activeTrigger.click) {
        popoverInstance.hide();
      }
    });
  }
});
