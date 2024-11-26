from datetime import datetime, timedelta
import openrouteservice


client = openrouteservice.Client(key='5b3ce3597851110001cf6248b406c2a4df264cdfac696101870c473c')


class Schedule:
    def __init__(self):
        self.week_schedule = {
            'Monday': [], 'Tuesday': [], 'Wednesday': [], 
            'Thursday': [], 'Friday': [], 'Saturday': [], 'Sunday': []
        }
        # Инициализация базового расписания с отдыхом
        for day in self.week_schedule:
            self.week_schedule[day] = [{
                'название': 'Отдых',
                'время_начала': '08:00',
                'время_окончания': '22:00',
                'место': {'имя':'Дом','широта':"22", "долгота":"50"}
            }]

    def time_from_a_to_b(self, place1, place2, profile="foot-walking"):
        cords = (place1, place2)
        routes = client.directions(cords, profile=profile)
        #print(int(routes['routes'][0]['summary']['duration'])/60)
        return int(routes['routes'][0]['summary']['duration'])/60

    def add_task(self, task):
        day = datetime.strptime(task['дата'], '%Y-%m-%d').strftime('%A')
        day_schedule = self.week_schedule[day]
        
        # Если день содержит только отдых
        if len(day_schedule) == 1 and day_schedule[0]['название'] == 'Отдых':
            self.initialize_day(day, task)
        else:
            self.update_day(day, task)
            
    def initialize_day(self, day, task):
        day_schedule = self.week_schedule[day]
        day_schedule.clear()
        
        # Добавляем пробуждение
        wake_time = (datetime.strptime(task['время_начала'], '%H:%M') - 
                    timedelta(hours=2)).strftime('%H:%M')
        day_schedule.append({
            'название': 'Пробуждение',
            'время_начала': wake_time,
            'время_окончания': wake_time,
            'место': {'имя':'Дом','широта':"54.699585", "долгота":"20.617323"}
        })
        
        # Добавляем перемещение к первой задаче
        travel_time = self.time_from_a_to_b((20.617323, 54.699585), (task['место']['долгота'],task['место']['широта']))
        travel_start = (datetime.strptime(task['время_начала'], '%H:%M') - 
                       timedelta(minutes=travel_time)).strftime('%H:%M')
        
        if task['место']['имя'] != 'Дом':
            day_schedule.append({
                'название': f'Перемещение из Дом в {task["место"]["имя"]}',
                'время_начала': travel_start,
                'время_окончания': task['время_начала'],
                'место': {'имя':'В пути','широта':"0", "долгота":"0"}
            })
        
        # Добавляем задачу
        day_schedule.append(task)
        
        # Добавляем возвращение домой если нужно
        if task['место']['имя'] != 'Дом':
            travel_start = datetime.strptime(task['время_окончания'], '%H:%M')
            travel_end = (travel_start + 
                         timedelta(minutes=self.time_from_a_to_b((task['место']['долгота'],task['место']['широта']), (20.617323, 54.699585)))).strftime('%H:%M')
            
            day_schedule.append({
                'название': f'Перемещение из {task["место"]["имя"]} в Дом',
                'время_начала': task['время_окончания'],
                'время_окончания': travel_end,
                'место': {'имя':'В пути','широта':"0", "долгота":"0"}
            })
            
        # Добавляем сон и отдых
        self.add_sleep_and_rest(day, task['дата'])

    def update_day(self, day, new_task):
        day_schedule = self.week_schedule[day]
        
        # Собираем все задачи (кроме служебных)
        tasks = [t for t in day_schedule if t['название'] not in 
                ['Пробуждение', 'Сон', 'Отдых'] and not t['название'].startswith('Перемещение')]
        
        # Добавляем новую задачу если её еще нет
        if not any(t['название'] == new_task['название'] and 
                t['время_начала'] == new_task['время_начала'] for t in tasks):
            tasks.append(new_task)
        
        # Сортируем задачи по времени
        tasks.sort(key=lambda x: datetime.strptime(x['время_начала'], '%H:%M'))
        
        # Очищаем день и заново его собираем
        day_schedule.clear()
        
        # Добавляем пробуждение
        wake_time = (datetime.strptime(tasks[0]['время_начала'], '%H:%M') - 
                    timedelta(hours=2)).strftime('%H:%M')
        day_schedule.append({
            'название': 'Пробуждение',
            'время_начала': wake_time,
            'время_окончания': wake_time,
            'место': {'имя':'Дом','широта':"54.699585", "долгота":"20.617323"}
        })
        
        # Добавляем задачи и перемещения между ними
        current_location = 'Дом'
        current_cords = (20.617323, 54.699585)
        for task in tasks:
            if current_location != task['место']['имя']:
                travel_time = self.time_from_a_to_b(current_cords, (task['место']['долгота'],task['место']['широта']))
                travel_start = (datetime.strptime(task['время_начала'], '%H:%M') - 
                            timedelta(minutes=travel_time)).strftime('%H:%M')
                
                # Добавляем только одно прямое перемещение
                day_schedule.append({
                    'название': f'Перемещение из {current_location} в {task["место"]["имя"]}',
                    'время_начала': travel_start,
                    'время_окончания': task['время_начала'],
                    'место': {'имя':'В пути','широта':"0", "долгота":"0"}
                })
                current_location = task['место']['имя']
                current_cords = (task['место']['долгота'],task['место']['широта'])
            
            day_schedule.append(task)
            current_cords = (task['место']['долгота'],task['место']['широта'])
        
        # Добавляем возвращение домой если нужно
        if current_location != 'Дом':
            last_task = tasks[-1]
            travel_start = datetime.strptime(last_task['время_окончания'], '%H:%M')
            travel_end = (travel_start + 
                        timedelta(minutes=self.time_from_a_to_b(current_cords, (20.617323, 54.699585)))).strftime('%H:%M')
            
            day_schedule.append({
                'название': f'Перемещение из {current_location} в Дом',
                'время_начала': last_task['время_окончания'],
                'время_окончания': travel_end,
                'место': {'имя':'В пути','широта':"0", "долгота":"0"}
            })
            
        # Добавляем сон и отдых
        self.add_sleep_and_rest(day, new_task['дата'])

    def add_sleep_and_rest(self, day, date):
        day_schedule = self.week_schedule[day]
        
        # Определяем время начала сна исходя из времени пробуждения следующего дня
        next_day = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%A')
        next_day_schedule = self.week_schedule[next_day]
        
        next_wake_time = '07:00'  # По умолчанию
        for next_task in next_day_schedule:
            if next_task['название'] == 'Пробуждение':
                next_wake_time = next_task['время_начала']
                break
        
        # Вычисляем время начала сна (9 часов до следующего пробуждения)
        next_wake = datetime.strptime(next_wake_time, '%H:%M')
        sleep_start = (next_wake - timedelta(hours=9)).strftime('%H:%M')
        
        # Добавляем отдых до начала сна
        last_event = day_schedule[-1]
        rest_start = datetime.strptime(last_event['время_окончания'], '%H:%M')
        rest_end = datetime.strptime(sleep_start, '%H:%M')
        
        if rest_start < rest_end:
            day_schedule.append({
                'название': 'Отдых',
                'время_начала': rest_start.strftime('%H:%M'),
                'время_окончания': sleep_start,
                'место': {'имя':'Дом','широта':"54.699585", "долгота":"20.617323"}
            })
        
        # Добавляем время сна
        day_schedule.append({
            'название': 'Сон',
            'время_начала': sleep_start,
            'время_окончания': '23:59',
            'место': {'имя':'Дом','широта':"54.699585", "долгота":"20.617323"},
            'предупреждение': None
        })

    def check_sleep_duration(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(len(days)):
            current_day = days[i]
            next_day = days[(i + 1) % 7]
            
            current_schedule = self.week_schedule[current_day]
            next_day_schedule = self.week_schedule[next_day]
            
            # Пропускаем дни с базовым расписанием (только отдых)
            if len(current_schedule) == 1 and current_schedule[0]['название'] == 'Отдых':
                continue
            
            # Находим время начала сна в текущем дне
            sleep_task = next(task for task in reversed(current_schedule) 
                            if task['название'] == 'Сон')
            sleep_start = datetime.strptime(sleep_task['время_начала'], '%H:%M')
            
            # Находим время пробуждения на следующий день
            next_wake_time = '07:00'  # По умолчанию
            for task in next_day_schedule:
                if task['название'] == 'Пробуждение':
                    next_wake_time = task['время_начала']
                    break
            
            next_wake = datetime.strptime(next_wake_time, '%H:%M')
            
            # Расчет продолжительности сна
            sleep_duration = 0
            if sleep_start >= next_wake:  # если время сна после времени пробуждения
                sleep_duration = 24 - (sleep_start.hour + sleep_start.minute/60) + \
                            (next_wake.hour + next_wake.minute/60)
            else:  # если время сна до времени пробуждения
                sleep_duration = (next_wake.hour + next_wake.minute/60) - \
                            (sleep_start.hour + sleep_start.minute/60)
            
            # Обновляем предупреждение в задаче сна
            sleep_task['предупреждение'] = 'Недостаточно сна!' if sleep_duration < 9 else None

    def print_schedule(self):
        for day, schedule in self.week_schedule.items():
            print(f"\n{day}:")
            for task in schedule:
                print(f"{task['время_начала']} - {task['время_окончания']}: {task['название']} "
                      f"@ {task['место']['имя']}")
                if 'предупреждение' in task and task['предупреждение']:
                    print(f"⚠️ {task['предупреждение']}")

    def get_schedule(self):

        for day, schedule in self.week_schedule.items():
            print(f"\n{day}:")
            for task in schedule:
                print(f"{task['время_начала']} - {task['время_окончания']}: {task['название']} "
                      f"@ {task['место']['имя']}")
                if 'предупреждение' in task and task['предупреждение']:
                    print(f"⚠️ {task['предупреждение']}")

    def get_raw_schedule(self):
        return self.week_schedule.items()
        























"""
class Schedule:
    def __init__(self):
        self.week_schedule = {
            'Monday': [],
            'Tuesday': [],
            'Wednesday': [],
            'Thursday': [],
            'Friday': [],
            'Saturday': [],
            'Sunday': []
        }
        # Инициализация базового расписания с отдыхом
        for day in self.week_schedule:
            self.week_schedule[day] = [{
                'название': 'Отдых',
                'время_начала': '08:00',
                'время_окончания': '22:00',
                'место': {'имя':'Дом','широта':"22", "долгота":"50"}
            }]

    def time_from_a_to_b(self, place1, place2):
        # Здесь должна быть ваша функция расчета времени перемещения
        # Для примера возвращаем 30 минут
        return 30

    
    def add_task(self, task):
        day = datetime.strptime(task['дата'], '%Y-%m-%d').strftime('%A')
        
        # Получаем текущее расписание дня
        day_schedule = self.week_schedule[day]
        
        # Если день содержит только отдых, очищаем его
        if len(day_schedule) == 1 and day_schedule[0]['название'] == 'Отдых':
            day_schedule.clear()
            
            # Добавляем пробуждение (за час до первой задачи)
            wake_time = (datetime.strptime(task['время_начала'], '%H:%M') - 
                        timedelta(hours=1)).strftime('%H:%M')
            day_schedule.append({
                'название': 'Пробуждение',
                'время_начала': wake_time,
                'время_окончания': wake_time,
                'место': {'имя':'Дом','широта':"22", "долгота":"50"}
            })
        
        # Собираем все задачи (кроме служебных)
        tasks = [t for t in day_schedule if t['название'] not in ['Пробуждение', 'Сон', 'Отдых']]
        
        # Добавляем новую задачу, если её ещё нет
        if not any(t['название'] == task['название'] and 
                t['время_начала'] == task['время_начала'] for t in tasks):
            tasks.append(task)
        
        # Сортируем задачи по времени
        tasks.sort(key=lambda x: datetime.strptime(x['время_начала'], '%H:%M'))
        
        # Очищаем расписание, оставляя только пробуждение
        day_schedule[:] = [t for t in day_schedule if t['название'] == 'Пробуждение']
        
        # Текущее местоположение начинается с дома
        current_location = 'Дом'
        
        # Добавляем задачи и перемещения
        for task in tasks:
            if current_location != task['место']['имя']:
                travel_time = self.time_from_a_to_b(current_location, task['место']['имя'])
                travel_start = (datetime.strptime(task['время_начала'], '%H:%M') - 
                            timedelta(minutes=travel_time)).strftime('%H:%M')
                
                day_schedule.append({
                    'название': f'Перемещение из {current_location } в {task["место"]["имя"]}',
                    'время_начала': travel_start,
                    'время_окончания': task['время_начала'],
                    'место': {'имя':'В пути','широта':"22", "долгота":"50"}
                })
                current_location = task['место']['имя']
            
            day_schedule.append (task)
            current_location = task['место']['имя']

        # Если последняя задача не дома, добавляем перемещение домой
        if current_location != 'Дом':
            last_task = tasks[-1]
            travel_time = self.time_from_a_to_b(current_location, 'Дом')
            travel_start = datetime.strptime(last_task['время_окончания'], '%H:%M')
            travel_end = (travel_start + timedelta(minutes=travel_time)).strftime('%H:%M')
            
            day_schedule.append({
                'название': f'Перемещение из {current_location} в Дом',
                'время_начала': last_task['время_окончания'],
                'время_окончания': travel_end,
                'место': {'имя':'В пути','широта':"22", "долгота":"50"}
            })

        # Определяем время начала сна исходя из времени пробуждения следующего дня
        next_day = (datetime.strptime(task['дата'], '%Y-%m-%d') ).strftime('%A')
        next_day_schedule = self.week_schedule[next_day]
        
        next_wake_time = '07:00'  # По умолчанию
        for next_task in next_day_schedule:
            if next_task['название'] == 'Пробуждение':
                next_wake_time = next_task['время_начала']
                break
        
        # Вычисляем время начала сна (9 часов до следующего пробуждения)
        next_wake = datetime.strptime(next_wake_time, '%H:%M')
        sleep_start = (next_wake - timedelta(hours=9)).strftime('%H:%M')
        
        # Добавляем отдых до начала сна
        last_event = day_schedule[-1]
        rest_start = datetime.strptime(last_event['время_окончания'], '%H:%M')
        rest_end = datetime.strptime(sleep_start, '%H:%M')
        
        if rest_start < rest_end:
            day_schedule.append({
                'название': 'Отдых',
                'время_начала': rest_start.strftime('%H:%M'),
                'время_окончания': sleep_start,
                'место': {'имя':'Дом','широта':"22", "долгота":"50"}
            })
        
        # Добавляем время сна
        day_schedule.append({
            'название': 'Сон',
            'время_начала': sleep_start,
            'время_окончания': '23:59',
            'место': {'имя':'Дом','широта':"22", "долгота":"50"},
            'предупреждение': None
        })
        
        # Проверяем продолжительность сна
        self.check_sleep_duration()
    

    def check_sleep_duration(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(len(days)):
            current_day = days[i]
            next_day = days[(i + 1) % 7]  # Переход на следующий день по кругу
            
            current_schedule = self.week_schedule[current_day]
            next_day_schedule = self.week_schedule[next_day]
            
            # Пропускаем дни с базовым расписанием (только отдых)
            if len(current_schedule) == 1 and current_schedule[0]['название'] == 'Отдых':
                continue
                
            # Находим время начала сна в текущем дне
            sleep_task = next(task for task in reversed(current_schedule) 
                            if task['название'] == 'Сон')
            sleep_start = datetime.strptime(sleep_task['время_начала'], '%H:%M')
            
            # Находим время пробуждения на следующий день
            next_wake_time = '08:00'  # По умолчанию
            for task in next_day_schedule:
                if task['название'] == 'Пробуждение':
                    next_wake_time = task['время_начала']
                    break
            
            next_wake = datetime.strptime(next_wake_time, '%H:%M')
            
            # Расчет продолжительности сна
            sleep_duration = 0
            if sleep_start >= next_wake:  # если время сна после времени пробуждения
                sleep_duration = 24 - (sleep_start.hour + sleep_start.minute/60) + \
                            (next_wake.hour + next_wake.minute/60)
            else:  # если время сна до времени пробуждения
                sleep_duration = (next_wake.hour + next_wake.minute/60) - \
                            (sleep_start.hour + sleep_start.minute/60)
            
            # Обновляем предупреждение в задаче сна
            sleep_task['предупреждение'] = 'Недостаточно сна!' if sleep_duration < 9 else None


    def print_schedule(self):
        for day, schedule in self.week_schedule.items():
            print(f"\n{day}:")
            for task in schedule:
                print(f"{task['время_начала']} - {task['время_окончания']}: {task['название']} "
                      f"@ {task['место']['имя']}")
                if 'предупреждение' in task and task['предупреждение']:
                    print(f"⚠️ {task['предупреждение']}")"""