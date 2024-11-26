import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
from utill.schedule import Schedule
from utill.eljur import School_Schedule
from utill.courses import DatabaseManager, add_static_courses


# Инициализацияя классов

# Create FastAPI instance
app = FastAPI()
schedule = Schedule()
db = DatabaseManager()
school_schedule = School_Schedule("Piskapopka", "piska123")

abspath = os.path.dirname(os.path.abspath(__file__))
print(abspath)
school = ""
allx = ""


def init():
    global school
    global allx
    try:
        school_schedule.login()
        school_schedule.get_schedule()
        days_info = school_schedule.get_days_info()
        print("\nИнформация о учебных днях:")
        for day_info in days_info:
            task = {
                'название': 'Уроки',
                'дата': day_info['дата'],
                'время_начала': day_info['время_начала_уроков'],
                'время_окончания': day_info['время_окончания_уроков'],
                'место': {'имя':'Школа','широта':"54.70857", "долгота":"20.53007"},
                'необходимый_материал': None
            }
            schedule.add_task(task)
            
            # Добавляем курсы
            courses = db.get_courses_for_day(day_info['дата'])
            #print(len(courses))
            for course in courses:
                schedule.add_task(course)

    finally:
        school_schedule.close()

        # Выводим расписание
        schedule.print_schedule()
        print('\n')
        school_schedule.print_schedule()
        school = school_schedule.get_rschedule()
        allx = schedule.get_raw_schedule()


init()


# Route for /schedule endpoint
@app.get("/schedule")
async def get_schedule():
    x = []
    today = datetime.now()
    day_name = today.strftime("%A")
    for day, schedule in allx:
        if day == day_name:
            x.append({"string":f"{day}:"})
            for task in schedule:
                x.append({"string":f"{task['время_начала']} - {task['время_окончания']}: {task['название']} " + f"@ {task['место']['имя']}"})
                if 'предупреждение' in task and task['предупреждение']:
                    x.append({"string":f"⚠️ {task['предупреждение']}"})
            x.append({"string":f"---"})
    return x

# Route for /school endpoint
@app.get("/school")
async def get_school():
    x = []
    # Get current date and time
    now = datetime.now()
    day_index = now.weekday()
    if day_index < len(school):
        today = school[day_index]
        for lesson in today.lessons:
            x.append({"string": f"{lesson.name}: {lesson.start_time} - {lesson.end_time} \n - {lesson.task}"})
    else:
        x.append({"string": "No schedule available for today"})
    return x

# Optional: Add a root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

# To run this program:
# 1. Save it as main.py
# 2. Install FastAPI and uvicorn: pip install fastapi uvicorn
# 3. Run: uvicorn main:app --reload