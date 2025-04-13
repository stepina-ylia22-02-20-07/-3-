import sqlite3
import json

# Подключение к базе данных
conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id)
)
''')

# Загрузка данных из JSON
with open('questions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for item in data:
    # Проверка, существует ли вопрос
    cursor.execute('''
    SELECT id FROM questions
    WHERE theme = ? AND question_text = ? AND correct_answer = ?
    ''', (item['theme'], item['question'], item['correct_answer']))
    existing_question = cursor.fetchone()

    if not existing_question:
        # Добавление вопроса, если его нет в базе данных
        cursor.execute('''
        INSERT INTO questions (theme, question_text, correct_answer)
        VALUES (?, ?, ?)
        ''', (item['theme'], item['question'], item['correct_answer']))

        # Получение ID последнего добавленного вопроса
        question_id = cursor.lastrowid

        # Добавление вариантов ответов
        for option in item['options']:
            cursor.execute('''
            INSERT INTO options (question_id, option_text)
            VALUES (?, ?)
            ''', (question_id, option))
    else:
        print(f"Вопрос уже существует: {item['question']}")

# Сохранение изменений
conn.commit()
conn.close()