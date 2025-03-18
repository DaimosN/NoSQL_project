from pymongo import MongoClient
from faker import Faker
from random import randint, choice, sample

# Инициализация Faker
fake = Faker('ru_RU')

# Подключение к MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.university

# Очистка коллекций (опционально)
db.students.drop()
db.teachers.drop()
db.courses.drop()
db.grades.drop()
db.departments.drop()

# --------------------------------------------
# 1. Генерация факультетов
# --------------------------------------------
departments = [
    {"name": "Информационные технологии", "dean": "Иван Сидоров"},
    {"name": "Экономика", "dean": "Мария Петрова"},
    {"name": "Лингвистика", "dean": "Анна Козлова"}
]

inserted_departments = db.departments.insert_many(departments)
department_ids = inserted_departments.inserted_ids

# --------------------------------------------
# 2. Генерация преподавателей (по 3 на факультет)
# --------------------------------------------
teachers = []
for dep_id in department_ids:
    for _ in range(3):
        teacher = {
            "firstName": fake.first_name_male() if randint(0, 1) else fake.first_name_female(),
            "lastName": fake.last_name(),
            "email": fake.unique.email(),
            "departmentId": dep_id
        }
        teachers.append(teacher)

inserted_teachers = db.teachers.insert_many(teachers)
teacher_ids = inserted_teachers.inserted_ids

# --------------------------------------------
# 3. Генерация курсов (по 5 на факультет)
# --------------------------------------------
courses = []
course_names = {
    "Информационные технологии": ["Python", "Базы данных", "Web-разработка", "Алгоритмы", "ИИ"],
    "Экономика": ["Макроэкономика", "Бухучёт", "Финансы", "Маркетинг", "Статистика"],
    "Лингвистика": ["Английский", "Немецкий", "Перевод", "Фонетика", "Литература"]
}

for dep in db.departments.find():
    dep_name = dep["name"]
    for course_name in course_names[dep_name]:
        course = {
            "name": f"{course_name} ({dep_name})",
            "description": fake.sentence(),
            "credits": randint(1, 5),
            "departmentId": dep["_id"],
            "teacherIds": sample(teacher_ids, 2)  # 2 случайных преподавателя
        }
        courses.append(course)

inserted_courses = db.courses.insert_many(courses)
course_ids = inserted_courses.inserted_ids

# --------------------------------------------
# 4. Генерация студентов (по 10 на факультет)
# --------------------------------------------
students = []
for dep_id in department_ids:
    for _ in range(10):
        student = {
            "firstName": fake.first_name_male() if randint(0, 1) else fake.first_name_female(),
            "lastName": fake.last_name(),
            "email": fake.unique.email(),
            "group": f"GROUP-{dep_id}-{randint(1, 5)}",
            "departmentId": dep_id
        }
        students.append(student)

inserted_students = db.students.insert_many(students)
student_ids = inserted_students.inserted_ids

# --------------------------------------------
# 5. Генерация оценок (по 20 на студента)
# --------------------------------------------
grades = []
for student_id in student_ids:
    for _ in range(20):
        course = choice(course_ids)
        grade = {
            "studentId": student_id,
            "courseId": course,
            "grade": randint(2, 5),
            "date": fake.date_time_between(start_date='-1y', end_date='now'),
            "type": choice(["экзамен", "зачёт", "тест", "курсовая"])
        }
        grades.append(grade)

db.grades.insert_many(grades)

# --------------------------------------------
# Вывод статистики
# --------------------------------------------
print(f"[+] Departments: {db.departments.count_documents({})}")
print(f"[+] Teachers: {db.teachers.count_documents({})}")
print(f"[+] Courses: {db.courses.count_documents({})}")
print(f"[+] Students: {db.students.count_documents({})}")
print(f"[+] Grades: {db.grades.count_documents({})}")
