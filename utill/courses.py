import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='main.db'):
        self.db_path = db_path
        #self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем таблицу для мест
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            latitude TEXT,
            longitude TEXT
        )
        ''')

        # Создаем таблицу для курсов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            weekday TEXT,
            start_time TEXT,
            end_time TEXT,
            place_id INTEGER,
            FOREIGN KEY (place_id) REFERENCES places (id)
        )
        ''')

        # Добавляем базовые места
        places = [
            ('Дом', '22', '50'),
            ('Потемкина', '22', '50'),
            ('БФУ', '22', '50'),
            ('Максимум', '22', '50')
        ]
        cursor.executemany('INSERT OR IGNORE INTO places (name, latitude, longitude) VALUES (?, ?, ?)', places)

        # Добавляем расписание курсов
        courses_data = [
            # Понедельник
            ('Математика', 'Monday', '15:20', '17:00', 'Потемкина'),
            ('Физика', 'Monday', '18:00', '20:00', 'Дом'),
            # Вторник
            ('Яндекс Лицей', 'Tuesday', '16:30', '18:30', 'БФУ'),
            # Среда
            ('Русский язык', 'Wednesday', '16:30', '18:00', 'Дом'),
            ('Математика', 'Wednesday', '18:30', '20:00', 'Дом'),
            # Четверг
            ('Математика', 'Thursday', '15:30', '17:00', 'Потемкина'),
            ('Русский язык', 'Thursday', '18:00', '19:20', 'БФУ'),
            ('Физика', 'Thursday', '18:00', '19:30', 'Дом'),
            # Пятница
            ('Яндекс Лицей', 'Friday', '16:30', '18:30', 'БФУ'),
            # Суббота
            ('Информатика', 'Saturday', '14:00', '17:00', 'БФУ'),
            ('Математика', 'Saturday', '18:30', '19:30', 'Максимум'),
            # Воскресенье
            ('Русский язык', 'Sunday', '16:00', '18:00', 'Максимум')
        ]

        # Добавляем курсы в базу данных
        for course in courses_data:
            name, weekday, start_time, end_time, place_name = course
            cursor.execute('SELECT id FROM places WHERE name = ?', (place_name,))
            place_id = cursor.fetchone()[0]
            
            cursor.execute('''
            INSERT OR IGNORE INTO courses (name, weekday, start_time, end_time, place_id)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, weekday, start_time, end_time, place_id))

        conn.commit()
        conn.close()

    def get_courses_for_day(self, date):
        """Получение курсов на определенный день"""
        weekday = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT c.name, c.start_time, c.end_time, p.name, p.latitude, p.longitude
        FROM courses c
        JOIN places p ON c.place_id = p.id
        WHERE c.weekday = ?
        ORDER BY c.start_time
        ''', (weekday,))
        
        courses = []
        for row in cursor.fetchall():
            course_name, start_time, end_time, place_name, lat, lon = row
            
            task = {
                'название': course_name,
                'дата': date,  # Добавляем дату
                'время_начала': start_time,
                'время_окончания': end_time,
                'место': {'имя': place_name, 'широта': lat, "долгота": lon},
                'необходимый_материал': None
            }
            courses.append(task)
        
        conn.close()
        return courses

# Пример использования:
def add_static_courses(schedule, date):
    db = DatabaseManager()
    courses = db.get_courses_for_day(date)
    for course in courses:
        schedule.add_task(course)

#DatabaseManager().init_database()