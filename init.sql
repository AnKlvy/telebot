-- Создание таблиц для телеграм бота

-- Таблица курсов
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица предметов
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица групп
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, subject_id)
);

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'curator', 'teacher', 'student')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица студентов (расширенная информация)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    tariff VARCHAR(50),
    points INTEGER DEFAULT 0,
    level VARCHAR(50) DEFAULT 'Новичок',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица кураторов
CREATE TABLE IF NOT EXISTS curators (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица преподавателей
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица менеджеров
CREATE TABLE IF NOT EXISTS managers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица уроков
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица микротем
CREATE TABLE IF NOT EXISTS microtopics (
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица вопросов
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    microtopic_id INTEGER REFERENCES microtopics(id) ON DELETE CASCADE,
    question_type VARCHAR(20) DEFAULT 'homework' CHECK (question_type IN ('homework', 'test')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица тестов месяца
CREATE TABLE IF NOT EXISTS month_tests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    microtopic_numbers INTEGER[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица бонусных заданий
CREATE TABLE IF NOT EXISTS bonus_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка начальных данных
INSERT INTO courses (name, description) VALUES 
    ('ЕНТ', 'Единое национальное тестирование'),
    ('IT', 'Информационные технологии')
ON CONFLICT (name) DO NOTHING;

INSERT INTO subjects (name, course_id) VALUES 
    ('Математика', 1),
    ('Физика', 1),
    ('История Казахстана', 1),
    ('Химия', 1),
    ('Биология', 1),
    ('Python', 2),
    ('JavaScript', 2),
    ('Java', 2)
ON CONFLICT (name) DO NOTHING;

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_subjects_course_id ON subjects(course_id);
CREATE INDEX IF NOT EXISTS idx_groups_subject_id ON groups(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_microtopic_id ON questions(microtopic_id);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
