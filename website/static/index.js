async function roomInfo(roomNumber, reservationDate) {
  try {
    const response = await fetch(
      `/roomInfo/?roomNumber=${roomNumber}&reservationDate=${reservationDate}`
    );
    const data = await response.json();
    const bookingInfo = data.occupied_times;
    const currentDatetime = reservationDate;
    const bookingInfoContainer = document.querySelector(
      `#bookingInfo${roomNumber}`
    );
    const occupiedTimesElement = bookingInfoContainer.querySelector(
      `#occupiedTimes${roomNumber}`
    );

    occupiedTimesElement.innerHTML = "";

    if (bookingInfo.length > 0) {
      bookingInfo.forEach((booking) => {
        const occupiedTime = document.createElement("li");
        occupiedTime.innerHTML = `
          <strong> ${booking.event_name}</strong><br>
          Начало: ${booking.start_time},<br>
           Конец: ${booking.end_time}<br>
          Имя пользователя: ${booking.booking_name}<br>
       
        `;
        if (booking.comment != null) {
          occupiedTime.innerHTML += `Комментарий: ${booking.comment} <br>`;
        }
        occupiedTimesElement.appendChild(occupiedTime);
      });
    } else {
      const noBookingsMessage = document.createElement("p");
      noBookingsMessage.textContent =
        "Нет забронированных временных интервалов.";
      occupiedTimesElement.appendChild(noBookingsMessage);
    }
  } catch (error) {
    console.error("Ошибка:", error);
  }
}

function messageInfo(messageId) {
  fetch(`/get_message_info?messageId=${messageId}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      // Полученный объект сообщения
      const message = data.message;

      // Пример обновления контейнера с текстом сообщения
      const messageContainer = document.getElementById("messageContainer");
      if (messageContainer) {
        messageContainer.message = message;
      }
    })
    .catch((error) => {
      console.error("Ошибка при получении сообщения:", error);
    });
}

// Получение информации о бронировании комнаты и сообщениях
document.addEventListener("DOMContentLoaded", function () {
  // Получаем все кнопки зала
  const currentDateElement = document.getElementById("currentDate");
  let currentDate = new Date();

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
      roomInfo(i, formattedDate);
    }
  }

  const messageButtons = document.querySelectorAll(".message-button");
  messageButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const messageId = this.dataset.messageId;
      console.log(messageId);
      messageInfo(messageId);
    });
  });

  const prevDateButton = document.getElementById("prevDate");
  prevDateButton.addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate() - 1);
    updateCurrentDate();
    updateRoomInfo();
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

  function updateCurrentDate() {
    currentDateElement.textContent = currentDate.toLocaleDateString();
  }
});
