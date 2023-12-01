async function getAllBookedRooms(roomName, reservationDate) {
  try {
    const response = await fetch(
      `/bookedRooms/?roomName=${roomName}&reservationDate=${reservationDate}`
    );
    const data = await response.json();
    const bookingInfo = data.occupied_times;
    // const bookingInfoContainer = document.getElementById(
    //   `${roomName}`
    // );
    // console.log(bookingInfoContainer);
    const occupiedTimesElement = document.getElementById(`${roomName}`);
    console.log(bookingInfo);
    occupiedTimesElement.innerHTML = "";

    if (bookingInfo.length > 0) {
      bookingInfo.forEach((booking) => {
        const occupiedTime = document.createElement("li");
        occupiedTime.style.marginBottom = "10px";

        const startTime = new Date(booking.start_time);
        const endTime = new Date(booking.end_time);

        const formattedStartTime = new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(startTime);

        const formattedEndTime = new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(endTime);

        const currentDateTime = new Date();

        const timeRange = document.createElement("span");
        timeRange.innerHTML = `${formattedStartTime} - ${formattedEndTime}`;

        if (currentDateTime >= startTime && currentDateTime <= endTime) {
          timeRange.style.backgroundColor = "orange";
        } else if (currentDateTime > endTime) {
          timeRange.style.backgroundColor = "red";
        } else {
          timeRange.style.backgroundColor = "green";
        }

        timeRange.style.borderRadius = "30px";
        timeRange.style.padding = "5px 10px";
        timeRange.style.color = "white";
        console.log(booking.comment);
        occupiedTime.innerHTML = `
        <div class="booking-details__list_item">
          <div class="booking-details__info">
            <strong >${booking.event_name}</strong>
            ${timeRange.outerHTML}
            Забронированно на: ${booking.booking_name}
          </div>
          ${
            booking.comment.length > 0
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
        </div>
        `;
        const newButton = occupiedTime.querySelector(
          "button[data-bs-toggle='popover']"
        );
        const popover = new bootstrap.Popover(newButton, {
          content: booking.comment,
        });

        newButton.addEventListener("click", function () {
          popover.toggle();
        });
        occupiedTimesElement.appendChild(occupiedTime);
      });
    } else {
      const noBookingsMessage = document.createElement("p");
      noBookingsMessage.textContent = "Броней нет.";
      occupiedTimesElement.appendChild(noBookingsMessage);
    }
  } catch (error) {
    console.error("Ошибка:", error);
  }
}

function fillModalForm() {
  // Заполняем значениями из аргументов функции
  titleInput.value = document.getElementById("title");
  startDateInput.value = formatDate(document.getElementById("startDate"));
  endDateInput.value = formatDate(document.getElementById("endDate"));
  commentInput.value = document.getElementById("comment");
  roomIdInput.value = document.getElementById("roomId");
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
  function updateRoomInfo() {
    const buttonNames = [
      "Конференц-зал",
      "Компьютерный зал",
      "Зал для презентаций",
      "Аудитория",
      "Мультимедийный зал",
      "Тренинг-зал",
    ];

    const formattedDate = currentDate.toISOString();
    for (let i = 0; i < buttonNames.length; i++) {
      getAllBookedRooms(buttonNames[i], formattedDate);
    }
  }

  let currentDate = new Date();

  const currentDateElement = document.getElementById("currentDate");
  function updateCurrentDate() {
    currentDateElement.textContent = currentDate.toLocaleDateString();
  }

  const prevDateButton = document.getElementById("prevDate");
  prevDateButton.addEventListener("click", () => {
    const today = new Date(); // Текущая дата
    const previousDate = new Date(currentDate); // Создание копии текущей даты
    today.setDate(today.getDate() - 1);
    previousDate.setDate(previousDate.getDate() - 1); // Установка предыдущей даты
    // Проверка, если предыдущая дата находится в прошлом относительно текущей даты
    if (previousDate >= today) {
      currentDate = previousDate; // Обновление текущей даты
      updateCurrentDate();
      updateRoomInfo();
    }
  });

  // Обработчик события для кнопки "Следующая дата"
  const nextDateButton = document.getElementById("nextDate");
  nextDateButton.addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate() + 1);
    updateCurrentDate();
    updateRoomInfo();
  });

  updateCurrentDate();
  updateRoomInfo();

  const closeButton = document.querySelectorAll('[data-dismiss="alert"]');
  closeButton.forEach(function (button) {
    button.addEventListener("click", function () {
      const alert = this.closest(".alert");
      alert.remove();
    });
  });
});

let popoverTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="popover"]')
);
let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl);
});
