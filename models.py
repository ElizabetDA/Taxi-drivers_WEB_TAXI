from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import pytz
import hashlib
import math

db = SQLAlchemy()


class User(db.Model):
    """Модель пользователя."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    trips = db.relationship("Trip", backref="user", lazy="dynamic")

    def __repr__(self):
        """Возвращает строковое представление объекта User."""
        return f"User {self.email}"

    def changePassword(self, password):
        """Изменяет пароль пользователя.

        Args:
            password (str): Новый пароль.

        Returns:
            None
        """
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def checkPassword(self, password):
        """Проверяет правильность введенного пароля.

        Args:
            password (str): Введенный пароль.

        Returns:
            bool: True, если пароль верен, False в противном случае.
        """
        return self.password_hash == hashlib.sha256(
            password.encode()).hexdigest()


class Trip(db.Model):
    """Модель поездки."""

    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"),
                          nullable=True)
    pickup_location = db.Column(db.String(200), nullable=False)
    dropoff_location = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(pytz.timezone("Europe/Moscow")),
    )
    end_time = db.Column(db.DateTime, nullable=True)
    fare = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="В ожидании")
    len_way = db.Column(db.String(50), nullable=False)
    rate = db.Column(db.String(100))
    driving_score = db.Column(db.Integer)
    driving_comfort = db.Column(db.Integer)
    driving_polite = db.Column(db.Integer)
    driving_sum = db.Column(db.Float)

    def changeStatus(self, status):
        """Изменяет статус поездки.

        Args:
            status (str): Новый статус поездки.

        Returns:
            None
        """
        self.status = status

    def changeScore(self, driving_score, driving_comfort, driving_polite):
        """Изменяет оценки водителя.

        Args:
            driving_score (int): Оценка стиля вождения.
            driving_comfort (int): Оценка комфорта.
            driving_polite (int): Оценка вежливости.

        Returns:
            None
        """
        self.driving_score = driving_score
        self.driving_comfort = driving_comfort
        self.driving_polite = driving_polite
        self.driving_sum = round(
            (driving_score + driving_comfort + driving_polite) / 3, 2
        )

    def chandeDriverId(self, driver_id):
        """Изменяет ID водителя, обслуживающего поездку.

        Args:
            driver_id (int): ID водителя.

        Returns:
            None
        """
        self.driver_id = driver_id

    def __repr__(self):
        """Возвращает строковое представление объекта Trip."""
        return (
            f"Trip {self.id} - User: {self.user.username},"
            f"Driver: {self.driver.name if self.driver else None}, \
                Status: {self.status}"
        )

    @staticmethod
    def calculateFare(lenWay, rate):
        """Вычисляет стоимость поездки.

        Args:
            lenWay (int): Длина маршрута в метрах.
            rate (str): Тариф.

        Returns:
            int: Стоимость поездки.
        """
        fix = 0
        if rate == "Экономный":
            fix = 50
        elif rate == "Стандартный":
            fix = 100
        elif rate == "Премиум":
            fix = 200
        return math.ceil(lenWay * 0.02 + fix)

    def setCompleted(self):
        """Устанавливает статус поездки как "Завершена"."""
        self.status = "Завершена"
        self.end_time = datetime.now(pytz.timezone("Europe/Moscow"))

    def set_payment_method(self, payment_method):
        """Устанавливает способ оплаты.

        Args:
            payment_method (str): Способ оплаты.

        Returns:
            None
        """
        self.payment_method = payment_method


class Driver(db.Model):
    """Модель водителя."""

    __tablename__ = "drivers"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    availability = db.Column(db.String(100), nullable=False,
                             default="Свободен")
    location = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    trips = db.relationship("Trip", backref="driver", lazy="dynamic")
    rate = db.Column(db.String(100))
    raiting = db.Column(db.Float)

    def updateRaiting(self):
        """Обновляет рейтинг водителя.

        Args:

        Returns:
            None
        """
        self.raiting = round(
            db.session.query(func.avg(Trip.driving_sum))
            .filter(Trip.driver_id == self.id)
            .scalar(),
            2,
        )

    def changeAvailability(self, availability):
        """Изменяет статус доступности водителя.

        Args:
            availability (str): Новый статус доступности.

        Returns:
            None
        """

        self.availability = availability

    def addMoneyForTrip(self, fare):
        """Добавляет деньги на баланс водителя.

        Args:
            fare (int): Стоимость поездки.

        Returns:
            None
        """

        self.balance += fare

    def __repr__(self):
        """Возвращает строковое представление объекта Driver."""

        return f"Driver {self.name}, Car {self.car_model}, \
    Phone: {self.phone_number}"

    def checkPassword(self, password):
        """Проверяет правильность введенного пароля.

        Args:
            password (str): Введенный пароль.

        Returns:
            bool: True, если пароль верен, False в противном случае.
        """
        return self.password_hash == hashlib.sha256(
            password.encode()).hexdigest()
