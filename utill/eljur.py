import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import List, Dict
from datetime import datetime

class Lesson:
    def __init__(self, name, start_time, end_time, task="Без задания"):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.task = task

    def __str__(self):
        return f"- {self.name}: {self.start_time}-{self.end_time}\n  {self.task}"

class SchoolDay:
    def __init__(self, date, weekday):
        self.weekday = weekday
        # Преобразование даты из формата "DD.MM" в "YYYY-MM-DD"
        day, month = date.split('.')
        current_year = datetime.now().year
        self.date = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        self.lessons = []
        self.start_time = None
        self.end_time = None

    def add_lesson(self, lesson):
        self.lessons.append(lesson)
        self._update_time_bounds()

    def _update_time_bounds(self):
        if self.lessons:
            self.start_time = self.lessons[0].start_time
            self.end_time = self.lessons[-1].end_time

    def get_schedule(self):
        return "\n".join(str(lesson) for lesson in self.lessons)

    def __str__(self):
        return f"{self.weekday}, {self.date}\n{self.get_schedule()}"
    
    def to_dict(self) -> Dict:
        return {
            "день": self.weekday,
            "дата": self.date,
            "время_начала_уроков": self.start_time,
            "время_окончания_уроков": self.end_time
        }

class School_Schedule:
    def __init__(self, username, password):
        self.driver = webdriver.Firefox()
        self.username = username
        self.password = password
        self.school_days = []

    def login(self):
        self.driver.get("https://keo.gov39.ru/authorize")
        time.sleep(3)
        box = self.driver.find_elements(By.TAG_NAME, "input")
        box[0].send_keys(self.username)
        box[1].send_keys(self.password)
        login_button = self.driver.find_element(
            By.TAG_NAME, "button"
        )
        login_button.click()
        time.sleep(3)

    def get_schedule(self):
        self.driver.get("https://keo.gov39.ru/journal-app/u.36774/week.0")
        time.sleep(3)
        days = self.driver.find_elements(By.CLASS_NAME, "dnevnik-day")

        for day in days:
            day_info = day.find_element(By.CLASS_NAME, "dnevnik-day__title").text.split(", ")
            school_day = SchoolDay(date=day_info[1], weekday=day_info[0])

            lessons = day.find_element(By.CLASS_NAME, "dnevnik-day__lessons")
            lessons = lessons.find_elements(By.CLASS_NAME, "dnevnik-lesson")

            for lesson in lessons:
                name = lesson.find_element(By.CLASS_NAME, "js-rt_licey-dnevnik-subject").text
                times = lesson.find_element(By.CLASS_NAME, "dnevnik-lesson__time").text.split("–")
                
                try:
                    task = lesson.find_element(By.CLASS_NAME, "dnevnik-lesson__task").text
                except:
                    task = "Без задания"

                school_day.add_lesson(Lesson(name, times[0], times[1], task))

            self.school_days.append(school_day)

    def get_days_info(self) -> List[Dict]:
        """Возвращает массив словарей с информацией о каждом учебном дне"""
        return [day.to_dict() for day in self.school_days]

    def print_schedule(self):
        for day in self.school_days:
            print(day)
            print()

    def get_rschedule(self):
        return self.school_days

    def close(self):
        self.driver.quit()

