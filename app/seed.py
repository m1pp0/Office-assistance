from datetime import date
from app.database import engine, Base, SessionLocal
from app.models import Team, User, Desk, Room, Booking, ResourceType, BookingStatus


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Team).first():
            print("База данных уже содержит данные. Пропуск сидирования.")
            return

        print("Начало наполнения базы данных...")

        teams_data = ["Backend Team", "Frontend Team", "Design & Product"]
        teams = [Team(name=name) for name in teams_data]
        db.add_all(teams)
        db.commit()

        for team in teams: db.refresh(team)

        users_data = [
            ("Алексей Смирнов", "alex@company.com", teams[0].id),
            ("Михаил Иванов", "mikhail@company.com", teams[0].id),
            ("Дмитрий Васильев", "dmitry@company.com", teams[0].id),
            ("Сергей Морозов", "sergey@company.com", teams[0].id),
            ("Илья Кузнецов", "ilya@company.com", teams[0].id),
            ("Екатерина Попова", "ekaterina@company.com", teams[1].id),
            ("Анна Соколова", "anna@company.com", teams[1].id),
            ("Павел Новиков", "pavel@company.com", teams[1].id),
            ("Максим Федоров", "maxim@company.com", teams[1].id),
            ("Ольга Волкова", "olga@company.com", teams[1].id),
            ("Мария Лебедева", "maria@company.com", teams[2].id),
            ("Елена Козлова", "elena@company.com", teams[2].id),
            ("Артем Степанов", "artem@company.com", teams[2].id),
            ("Ксения Павлова", "ksenia@company.com", teams[2].id),
            ("Роман Орлов", "roman@company.com", teams[2].id),
        ]

        users = [
            User(
                full_name=name,
                email=email,
                team_id=t_id,
                hashed_password="tipo_password"
            )
            for name, email, t_id in users_data
        ]
        db.add_all(users)
        db.commit()

        for user in users: db.refresh(user)

        desks = []
        # Зона A: 10 столов
        for i in range(1, 11): desks.append(Desk(code=f"A-{i}", zone="Зона OpenSpace A"))
        # Зона B: 10 столов
        for i in range(1, 11): desks.append(Desk(code=f"B-{i}", zone="Зона OpenSpace B"))
        db.add_all(desks)
        db.commit()

        for desk in desks: db.refresh(desk)

        rooms = [
            Room(name="Переговорная 'Меркурий'", capacity=4),
            Room(name="Переговорная 'Марс'", capacity=6),
            Room(name="Конференц-зал 'Юпитер'", capacity=12),
        ]
        db.add_all(rooms)
        db.commit()

        for room in rooms: db.refresh(room)

        today = date.today()
        sample_bookings = [
            Booking(
                user_id=users[0].id,
                resource_type=ResourceType.DESK,
                resource_id=desks[0].id,
                booking_date=today,
                status=BookingStatus.CONFIRMED
            ),
            Booking(
                user_id=users[1].id,
                resource_type=ResourceType.DESK,
                resource_id=desks[1].id,
                booking_date=today,
                status=BookingStatus.CONFIRMED
            ),
            Booking(
                user_id=users[5].id,
                resource_type=ResourceType.DESK,
                resource_id=desks[10].id,
                booking_date=today,
                status=BookingStatus.CONFIRMED
            ),
            Booking(
                user_id=users[10].id,
                resource_type=ResourceType.ROOM,
                resource_id=rooms[1].id,
                booking_date=today,
                status=BookingStatus.PENDING
            ),
        ]
        db.add_all(sample_bookings)
        db.commit()

        print("База данных успешно заполнена тестовыми данными!")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при сидировании данных: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()