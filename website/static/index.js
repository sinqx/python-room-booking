function roomInfo(roomNumber) {
  fetch(`/roomInfo/?roomNumber=${roomNumber}`)
    .then((response) => response.json())
    .then((data) => {
      const bookingInfo = data.occupied_times;
      const currentDatetime = new Date().toLocaleString();
      const bookingInfoContainer = document.querySelector(
        `#bookingInfo${roomNumber}`
      );
      const currentDatetimeElement =
        bookingInfoContainer.querySelector("#currentDatetime");
      const occupiedTimesElement = bookingInfoContainer.querySelector(
        `#occupiedTimes${roomNumber}`
      );  

      if (bookingInfo.length > 0) {
        occupiedTimesElement.innerHTML = "";
        bookingInfo.forEach((booking) => {
          const occupiedTime = document.createElement("li");
          occupiedTime.innerHTML = `
              Начало: ${booking.start_time}, Конец: ${booking.end_time}<br>
              Имя пользователя: ${booking.booking_name}<br>
              Название мероприятия: ${booking.event_name}<br>
            `;
          if (booking.comment != null) {
            occupiedTime.innerHTML + `Комментарий: ${booking.comment} <br>`;
          }
          occupiedTimesElement.appendChild(occupiedTime);
        });
      } else {
        occupiedTimesElement.innerHTML =
          "<p>Нет забронированных временных интервалов.</p>";
      }
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
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
  const roomInfoButton = document.querySelectorAll(".button");
  // Добавляем обработчик событий к каждой кнопке зала
  roomInfoButton.forEach(function (button) {
    button.addEventListener("click", function () {
      console.log("9999999999999999999999");
      var roomNumber = button.getAttribute("data-room-number");
      roomInfo(roomNumber);
    });
  });

  const messageButtons = document.querySelectorAll(".message-button");
  messageButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const messageId = this.dataset.messageId;
      console.log("8888888888888888888888888888")
      console.log(messageId)
      messageInfo(messageId)
    });
  });
});
