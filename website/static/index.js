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

      currentDatetimeElement.textContent = currentDatetime;

      if (bookingInfo.length > 0) {
        occupiedTimesElement.innerHTML = "";
        bookingInfo.forEach((booking) => {
          const occupiedTime = document.createElement("li");
          occupiedTime.innerHTML = `
              Начало: ${booking.start_time}, Конец: ${booking.end_time}<br>
              Имя пользователя: ${booking.booking_name}<br>
              Название мероприятия: ${booking.event_name}
            `;
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


// Получение информации о бронировании комнаты
document.addEventListener("DOMContentLoaded", function () {
  // Получаем все кнопки зала
  var buttons = document.querySelectorAll(".button");

  // Добавляем обработчик событий к каждой кнопке зала
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var roomNumber = button.getAttribute("data-room-number");
      roomInfo(roomNumber);
    });
  });
});
