// Функция для инициализации карты
function initMap() {
    // Инициализация карты
    var mapCenter = [55.7558, 37.6173]; // Координаты центра Москвы
    var map = DG.map('map', {
        center: mapCenter, // Начальные координаты центра карты
        zoom: 10 // Начальное масштабирование карты
    });

    // Получаем текущее местоположение пользователя
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var userCoords = [position.coords.latitude, position.coords.longitude];
            // Используем местоположение пользователя в качестве центра карты
            map.setView(userCoords, 15); // Устанавливаем приближение на местоположение пользователя

            // Добавляем маркер на местоположение пользователя
            var userMarker = DG.marker(userCoords).addTo(map);
            userMarker.bindPopup('Ваше местоположение').openPopup(); // Отображаем всплывающее окно с названием местоположения

            // Получаем адрес по координатам пользователя
            var xhr = new XMLHttpRequest();
            var url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat=' + userCoords[0] + '&lon=' + userCoords[1] + '&zoom=18&addressdetails=1';
            xhr.open('GET', url, true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var response = JSON.parse(xhr.responseText);
                    if (response && response.address) {
                        var addressDetails = response.address;

                        // Получаем необходимые части адреса (например, улицу и город)
                        var street = addressDetails.road || '';
                        var city = addressDetails.city || '';
                        var address = street + ', ' + city;

                        console.log('Ваше местоположение:', address);

                        // Обновляем значение поля "Откуда"
                        document.getElementById('pickupLocation').value = address;

                        // Центрируем карту на текущем местоположении
                        centerMap(address);
                    }
                }
            };
            xhr.send(null);

        }, function () {
            console.log('Не удалось получить текущее местоположение.');
        });
    } else {
        console.log('Геолокация не поддерживается данным браузером.');
    }

    // Обработчик события нажатия клавиши Enter в поле "Откуда"
    document.getElementById('pickupLocation').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            var address = this.value;
            centerMap(address);
        }
    });
}

// Функция для центрирования и приближения карты к указанному адресу
function centerMap(address) {
    // Получаем координаты по адресу
    var url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(address);
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                var coords = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
                map.setView(coords, 15); // Центрируем карту на указанных координатах
                // Добавляем маркер на указанные координаты
                var marker = DG.marker(coords).addTo(map);
                marker.bindPopup(address).openPopup(); // Показываем всплывающее окно с указанным адресом
            } else {
                console.log('Адрес не найден.');
            }
        })
        .catch(error => console.log('Ошибка при получении координат:', error));
}

// Запускаем инициализацию карты после загрузки страницы
window.onload = function () {
    // Инициализация карты
    initMap();
};