"""
Создание уроков и домашних заданий
"""
from database import (
    LessonRepository, HomeworkRepository, QuestionRepository, AnswerOptionRepository
)


async def create_lessons_and_homework(created_subjects, created_courses):
    """Создание уроков и домашних заданий"""
    try:
        print("📝 Создание уроков и домашних заданий...")

        # Получаем первый курс для привязки уроков (можно изменить логику)
        if not created_courses:
            print("❌ Нет созданных курсов для привязки уроков")
            return {}

        default_course = created_courses[0]  # Используем первый курс как основной
        print(f"📚 Привязываем уроки к курсу: {default_course.name}")

        # Данные для уроков и ДЗ по предметам
        lessons_data = {
            "Python": [
                {
                    "name": "Основы Python",
                    "homework": "Основы Python",
                    "questions": [
                        {
                            "text": "Какой тип данных используется для хранения целых чисел в Python?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "int", "is_correct": True},
                                {"text": "float", "is_correct": False},
                                {"text": "str", "is_correct": False},
                                {"text": "bool", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как объявить переменную в Python?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "Просто присвоить значение: x = 5", "is_correct": True},
                                {"text": "var x = 5", "is_correct": False},
                                {"text": "int x = 5", "is_correct": False},
                                {"text": "declare x = 5", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Какой тип данных имеет значение 3.14?",
                            "microtopic": 2,  # Типы данных
                            "answers": [
                                {"text": "float", "is_correct": True},
                                {"text": "int", "is_correct": False},
                                {"text": "str", "is_correct": False},
                                {"text": "decimal", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как создать список в Python?",
                            "microtopic": 2,  # Типы данных
                            "answers": [
                                {"text": "[1, 2, 3]", "is_correct": True},
                                {"text": "{1, 2, 3}", "is_correct": False},
                                {"text": "(1, 2, 3)", "is_correct": False},
                                {"text": "list(1, 2, 3)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что такое tuple в Python?",
                            "microtopic": 2,  # Типы данных
                            "answers": [
                                {"text": "Неизменяемая последовательность", "is_correct": True},
                                {"text": "Изменяемая последовательность", "is_correct": False},
                                {"text": "Словарь", "is_correct": False},
                                {"text": "Множество", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Циклы и условия",
                    "homework": "Циклы и условия",
                    "questions": [
                        {
                            "text": "Какой оператор используется для проверки условия в Python?",
                            "microtopic": 3,  # Условия
                            "answers": [
                                {"text": "if", "is_correct": True},
                                {"text": "while", "is_correct": False},
                                {"text": "for", "is_correct": False},
                                {"text": "def", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как записать условие 'если x больше 5'?",
                            "microtopic": 3,  # Условия
                            "answers": [
                                {"text": "if x > 5:", "is_correct": True},
                                {"text": "if (x > 5)", "is_correct": False},
                                {"text": "if x > 5 then:", "is_correct": False},
                                {"text": "when x > 5:", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Какой цикл используется для перебора элементов списка?",
                            "microtopic": 4,  # Циклы
                            "answers": [
                                {"text": "for", "is_correct": True},
                                {"text": "while", "is_correct": False},
                                {"text": "do-while", "is_correct": False},
                                {"text": "foreach", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как создать цикл от 0 до 9?",
                            "microtopic": 4,  # Циклы
                            "answers": [
                                {"text": "for i in range(10):", "is_correct": True},
                                {"text": "for i in range(0, 9):", "is_correct": False},
                                {"text": "for i = 0 to 9:", "is_correct": False},
                                {"text": "while i < 10:", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что делает оператор break в цикле?",
                            "microtopic": 4,  # Циклы
                            "answers": [
                                {"text": "Прерывает выполнение цикла", "is_correct": True},
                                {"text": "Пропускает текущую итерацию", "is_correct": False},
                                {"text": "Перезапускает цикл", "is_correct": False},
                                {"text": "Ничего не делает", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Функции",
                    "homework": "Функции",
                    "questions": [
                        {
                            "text": "Какое ключевое слово используется для определения функции в Python?",
                            "microtopic": 5,  # Функции
                            "answers": [
                                {"text": "def", "is_correct": True},
                                {"text": "function", "is_correct": False},
                                {"text": "func", "is_correct": False},
                                {"text": "define", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как вернуть значение из функции?",
                            "microtopic": 5,  # Функции
                            "answers": [
                                {"text": "return значение", "is_correct": True},
                                {"text": "output значение", "is_correct": False},
                                {"text": "send значение", "is_correct": False},
                                {"text": "give значение", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что такое параметры функции?",
                            "microtopic": 5,  # Функции
                            "answers": [
                                {"text": "Переменные, которые функция принимает", "is_correct": True},
                                {"text": "Значения, которые функция возвращает", "is_correct": False},
                                {"text": "Имя функции", "is_correct": False},
                                {"text": "Тело функции", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как вызвать функцию с именем 'hello'?",
                            "microtopic": 5,  # Функции
                            "answers": [
                                {"text": "hello()", "is_correct": True},
                                {"text": "call hello()", "is_correct": False},
                                {"text": "run hello", "is_correct": False},
                                {"text": "execute hello()", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "ООП в Python",
                    "homework": "ООП в Python",
                    "questions": [
                        {
                            "text": "Какое ключевое слово используется для создания класса в Python?",
                            "microtopic": 6,  # Классы
                            "answers": [
                                {"text": "class", "is_correct": True},
                                {"text": "object", "is_correct": False},
                                {"text": "struct", "is_correct": False},
                                {"text": "type", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что такое метод __init__ в классе?",
                            "microtopic": 6,  # Классы
                            "answers": [
                                {"text": "Конструктор класса", "is_correct": True},
                                {"text": "Деструктор класса", "is_correct": False},
                                {"text": "Обычный метод", "is_correct": False},
                                {"text": "Статический метод", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как создать объект класса Car?",
                            "microtopic": 6,  # Классы
                            "answers": [
                                {"text": "my_car = Car()", "is_correct": True},
                                {"text": "my_car = new Car()", "is_correct": False},
                                {"text": "my_car = create Car()", "is_correct": False},
                                {"text": "my_car = Car.new()", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что такое self в методах класса?",
                            "microtopic": 6,  # Классы
                            "answers": [
                                {"text": "Ссылка на текущий объект", "is_correct": True},
                                {"text": "Имя класса", "is_correct": False},
                                {"text": "Статическая переменная", "is_correct": False},
                                {"text": "Глобальная переменная", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Модули и библиотеки",
                    "homework": "Модули и библиотеки",
                    "questions": [
                        {
                            "text": "Как импортировать модуль math?",
                            "microtopic": 7,  # Модули
                            "answers": [
                                {"text": "import math", "is_correct": True},
                                {"text": "include math", "is_correct": False},
                                {"text": "using math", "is_correct": False},
                                {"text": "require math", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как импортировать только функцию sqrt из модуля math?",
                            "microtopic": 7,  # Модули
                            "answers": [
                                {"text": "from math import sqrt", "is_correct": True},
                                {"text": "import sqrt from math", "is_correct": False},
                                {"text": "import math.sqrt", "is_correct": False},
                                {"text": "using math.sqrt", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что делает команда pip?",
                            "microtopic": 10,  # Библиотеки
                            "answers": [
                                {"text": "Устанавливает пакеты Python", "is_correct": True},
                                {"text": "Компилирует код", "is_correct": False},
                                {"text": "Запускает программу", "is_correct": False},
                                {"text": "Создает виртуальное окружение", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Работа с файлами",
                    "homework": "Работа с файлами",
                    "questions": [
                        {
                            "text": "Как открыть файл для чтения в Python?",
                            "microtopic": 9,  # Файлы
                            "answers": [
                                {"text": "open('file.txt', 'r')", "is_correct": True},
                                {"text": "file('file.txt', 'read')", "is_correct": False},
                                {"text": "read('file.txt')", "is_correct": False},
                                {"text": "open_file('file.txt')", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Какой режим используется для записи в файл?",
                            "microtopic": 9,  # Файлы
                            "answers": [
                                {"text": "'w'", "is_correct": True},
                                {"text": "'write'", "is_correct": False},
                                {"text": "'wr'", "is_correct": False},
                                {"text": "'output'", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Зачем нужен оператор with при работе с файлами?",
                            "microtopic": 9,  # Файлы
                            "answers": [
                                {"text": "Автоматически закрывает файл", "is_correct": True},
                                {"text": "Ускоряет чтение", "is_correct": False},
                                {"text": "Сжимает файл", "is_correct": False},
                                {"text": "Шифрует содержимое", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Обработка исключений",
                    "homework": "Обработка исключений",
                    "questions": [
                        {
                            "text": "Какой блок используется для обработки исключений?",
                            "microtopic": 8,  # Исключения
                            "answers": [
                                {"text": "try-except", "is_correct": True},
                                {"text": "catch-throw", "is_correct": False},
                                {"text": "error-handle", "is_correct": False},
                                {"text": "check-fix", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что происходит в блоке finally?",
                            "microtopic": 8,  # Исключения
                            "answers": [
                                {"text": "Код выполняется всегда", "is_correct": True},
                                {"text": "Код выполняется только при ошибке", "is_correct": False},
                                {"text": "Код выполняется только без ошибок", "is_correct": False},
                                {"text": "Код не выполняется никогда", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как вызвать исключение вручную?",
                            "microtopic": 8,  # Исключения
                            "answers": [
                                {"text": "raise Exception('сообщение')", "is_correct": True},
                                {"text": "throw Exception('сообщение')", "is_correct": False},
                                {"text": "error Exception('сообщение')", "is_correct": False},
                                {"text": "exception Exception('сообщение')", "is_correct": False}
                            ]
                        }
                    ]
                }
            ],
            "JavaScript": [
                {
                    "name": "Основы JavaScript",
                    "homework": "Основы JavaScript",
                    "questions": [
                        {
                            "text": "Как объявить переменную в JavaScript?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "let x = 5", "is_correct": True},
                                {"text": "variable x = 5", "is_correct": False},
                                {"text": "x := 5", "is_correct": False},
                                {"text": "declare x = 5", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Какой тип данных имеет значение 'Hello'?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "string", "is_correct": True},
                                {"text": "text", "is_correct": False},
                                {"text": "char", "is_correct": False},
                                {"text": "varchar", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как проверить тип переменной в JavaScript?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "typeof variable", "is_correct": True},
                                {"text": "type(variable)", "is_correct": False},
                                {"text": "variable.type", "is_correct": False},
                                {"text": "gettype(variable)", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Функции в JavaScript",
                    "homework": "Функции в JavaScript",
                    "questions": [
                        {
                            "text": "Как объявить функцию в JavaScript?",
                            "microtopic": 2,  # Функции
                            "answers": [
                                {"text": "function myFunc() {}", "is_correct": True},
                                {"text": "def myFunc():", "is_correct": False},
                                {"text": "func myFunc() {}", "is_correct": False},
                                {"text": "method myFunc() {}", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как вызвать функцию с именем 'test'?",
                            "microtopic": 2,  # Функции
                            "answers": [
                                {"text": "test()", "is_correct": True},
                                {"text": "call test()", "is_correct": False},
                                {"text": "run test", "is_correct": False},
                                {"text": "execute test()", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что такое стрелочная функция?",
                            "microtopic": 2,  # Функции
                            "answers": [
                                {"text": "() => {}", "is_correct": True},
                                {"text": "-> {}", "is_correct": False},
                                {"text": "=> {}", "is_correct": False},
                                {"text": "function() => {}", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Объекты и массивы",
                    "homework": "Объекты и массивы",
                    "questions": [
                        {
                            "text": "Как создать массив в JavaScript?",
                            "microtopic": 3,  # Объекты
                            "answers": [
                                {"text": "[1, 2, 3]", "is_correct": True},
                                {"text": "{1, 2, 3}", "is_correct": False},
                                {"text": "(1, 2, 3)", "is_correct": False},
                                {"text": "array(1, 2, 3)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как создать объект в JavaScript?",
                            "microtopic": 3,  # Объекты
                            "answers": [
                                {"text": "{name: 'John', age: 30}", "is_correct": True},
                                {"text": "[name: 'John', age: 30]", "is_correct": False},
                                {"text": "(name: 'John', age: 30)", "is_correct": False},
                                {"text": "object(name: 'John', age: 30)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как получить длину массива?",
                            "microtopic": 4,  # Массивы
                            "answers": [
                                {"text": "array.length", "is_correct": True},
                                {"text": "array.size", "is_correct": False},
                                {"text": "len(array)", "is_correct": False},
                                {"text": "array.count", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "DOM и события",
                    "homework": "DOM и события",
                    "questions": [
                        {
                            "text": "Как найти элемент по ID?",
                            "microtopic": 5,  # DOM
                            "answers": [
                                {"text": "document.getElementById('id')", "is_correct": True},
                                {"text": "document.findById('id')", "is_correct": False},
                                {"text": "document.getElement('id')", "is_correct": False},
                                {"text": "getElementById('id')", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как добавить обработчик события клика?",
                            "microtopic": 6,  # События
                            "answers": [
                                {"text": "element.addEventListener('click', function)", "is_correct": True},
                                {"text": "element.onClick(function)", "is_correct": False},
                                {"text": "element.addClick(function)", "is_correct": False},
                                {"text": "element.on('click', function)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как изменить текст элемента?",
                            "microtopic": 5,  # DOM
                            "answers": [
                                {"text": "element.textContent = 'новый текст'", "is_correct": True},
                                {"text": "element.text = 'новый текст'", "is_correct": False},
                                {"text": "element.setText('новый текст')", "is_correct": False},
                                {"text": "element.content = 'новый текст'", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Асинхронность",
                    "homework": "Промисы и async/await",
                    "questions": [
                        {
                            "text": "Что такое Promise в JavaScript?",
                            "microtopic": 7,  # Асинхронность
                            "answers": [
                                {"text": "Объект для работы с асинхронными операциями", "is_correct": True},
                                {"text": "Функция обратного вызова", "is_correct": False},
                                {"text": "Синхронная операция", "is_correct": False},
                                {"text": "Тип данных", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Как использовать async/await?",
                            "microtopic": 7,  # Асинхронность
                            "answers": [
                                {"text": "async function() { await promise }", "is_correct": True},
                                {"text": "function async() { wait promise }", "is_correct": False},
                                {"text": "async() { await promise }", "is_correct": False},
                                {"text": "function() async { await promise }", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Что делает метод fetch()?",
                            "microtopic": 9,  # Fetch
                            "answers": [
                                {"text": "Выполняет HTTP-запросы", "is_correct": True},
                                {"text": "Получает элементы DOM", "is_correct": False},
                                {"text": "Создает массивы", "is_correct": False},
                                {"text": "Обрабатывает события", "is_correct": False}
                            ]
                        }
                    ]
                }
            ],
            "Математика": [
                {
                    "name": "Алгебра",
                    "homework": "Алгебраические выражения",
                    "questions": [
                        {
                            "text": "Чему равно x² - 4x + 4?",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "(x-2)²", "is_correct": True},
                                {"text": "(x+2)²", "is_correct": False},
                                {"text": "(x-4)²", "is_correct": False},
                                {"text": "x²-4", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Решите уравнение: 2x + 5 = 11",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "x = 3", "is_correct": True},
                                {"text": "x = 8", "is_correct": False},
                                {"text": "x = 6", "is_correct": False},
                                {"text": "x = 16", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Чему равно (a + b)²?",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "a² + 2ab + b²", "is_correct": True},
                                {"text": "a² + b²", "is_correct": False},
                                {"text": "a² + ab + b²", "is_correct": False},
                                {"text": "2a² + 2b²", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Найдите корни уравнения x² - 5x + 6 = 0",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "x = 2, x = 3", "is_correct": True},
                                {"text": "x = 1, x = 6", "is_correct": False},
                                {"text": "x = -2, x = -3", "is_correct": False},
                                {"text": "x = 0, x = 5", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Упростите выражение: 3x + 2x - x",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "4x", "is_correct": True},
                                {"text": "6x", "is_correct": False},
                                {"text": "5x", "is_correct": False},
                                {"text": "2x", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Геометрия",
                    "homework": "Площади фигур",
                    "questions": [
                        {
                            "text": "Формула площади круга:",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "πr²", "is_correct": True},
                                {"text": "2πr", "is_correct": False},
                                {"text": "πr", "is_correct": False},
                                {"text": "r²", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Формула площади треугольника:",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "½ × основание × высота", "is_correct": True},
                                {"text": "основание × высота", "is_correct": False},
                                {"text": "2 × основание × высота", "is_correct": False},
                                {"text": "основание + высота", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Сумма углов треугольника равна:",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "180°", "is_correct": True},
                                {"text": "90°", "is_correct": False},
                                {"text": "360°", "is_correct": False},
                                {"text": "270°", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Формула длины окружности:",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "2πr", "is_correct": True},
                                {"text": "πr²", "is_correct": False},
                                {"text": "πr", "is_correct": False},
                                {"text": "4πr", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Теорема Пифагора: c² = ?",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "a² + b²", "is_correct": True},
                                {"text": "a + b", "is_correct": False},
                                {"text": "a² - b²", "is_correct": False},
                                {"text": "2ab", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Тригонометрия",
                    "homework": "Тригонометрические функции",
                    "questions": [
                        {
                            "text": "Чему равен sin(30°)?",
                            "microtopic": 3,  # Тригонометрия
                            "answers": [
                                {"text": "1/2", "is_correct": True},
                                {"text": "√3/2", "is_correct": False},
                                {"text": "1", "is_correct": False},
                                {"text": "√2/2", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Чему равен cos(60°)?",
                            "microtopic": 3,  # Тригонометрия
                            "answers": [
                                {"text": "1/2", "is_correct": True},
                                {"text": "√3/2", "is_correct": False},
                                {"text": "0", "is_correct": False},
                                {"text": "1", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Основное тригонометрическое тождество:",
                            "microtopic": 3,  # Тригонометрия
                            "answers": [
                                {"text": "sin²x + cos²x = 1", "is_correct": True},
                                {"text": "sin²x - cos²x = 1", "is_correct": False},
                                {"text": "sinx + cosx = 1", "is_correct": False},
                                {"text": "sinx × cosx = 1", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Логарифмы",
                    "homework": "Логарифмические функции",
                    "questions": [
                        {
                            "text": "Чему равен log₁₀(100)?",
                            "microtopic": 4,  # Логарифмы
                            "answers": [
                                {"text": "2", "is_correct": True},
                                {"text": "10", "is_correct": False},
                                {"text": "100", "is_correct": False},
                                {"text": "1", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Свойство логарифма: log(ab) = ?",
                            "microtopic": 4,  # Логарифмы
                            "answers": [
                                {"text": "log(a) + log(b)", "is_correct": True},
                                {"text": "log(a) × log(b)", "is_correct": False},
                                {"text": "log(a) - log(b)", "is_correct": False},
                                {"text": "log(a) / log(b)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Чему равен ln(e)?",
                            "microtopic": 4,  # Логарифмы
                            "answers": [
                                {"text": "1", "is_correct": True},
                                {"text": "e", "is_correct": False},
                                {"text": "0", "is_correct": False},
                                {"text": "2", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Производные",
                    "homework": "Дифференцирование",
                    "questions": [
                        {
                            "text": "Производная функции f(x) = x² равна:",
                            "microtopic": 5,  # Производные
                            "answers": [
                                {"text": "2x", "is_correct": True},
                                {"text": "x", "is_correct": False},
                                {"text": "x²", "is_correct": False},
                                {"text": "2", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Производная константы равна:",
                            "microtopic": 5,  # Производные
                            "answers": [
                                {"text": "0", "is_correct": True},
                                {"text": "1", "is_correct": False},
                                {"text": "константа", "is_correct": False},
                                {"text": "x", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Производная функции sin(x) равна:",
                            "microtopic": 5,  # Производные
                            "answers": [
                                {"text": "cos(x)", "is_correct": True},
                                {"text": "-cos(x)", "is_correct": False},
                                {"text": "sin(x)", "is_correct": False},
                                {"text": "-sin(x)", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Функции",
                    "homework": "Исследование функций",
                    "questions": [
                        {
                            "text": "Область определения функции f(x) = 1/x:",
                            "microtopic": 10,  # Функции
                            "answers": [
                                {"text": "x ≠ 0", "is_correct": True},
                                {"text": "x > 0", "is_correct": False},
                                {"text": "x ≥ 0", "is_correct": False},
                                {"text": "все действительные числа", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Функция f(x) = x² является:",
                            "microtopic": 10,  # Функции
                            "answers": [
                                {"text": "четной", "is_correct": True},
                                {"text": "нечетной", "is_correct": False},
                                {"text": "ни четной, ни нечетной", "is_correct": False},
                                {"text": "линейной", "is_correct": False}
                            ]
                        },
                        {
                            "text": "График функции y = |x| имеет вид:",
                            "microtopic": 10,  # Функции
                            "answers": [
                                {"text": "V-образной кривой", "is_correct": True},
                                {"text": "прямой линии", "is_correct": False},
                                {"text": "параболы", "is_correct": False},
                                {"text": "гиперболы", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Комбинаторика",
                    "homework": "Размещения и сочетания",
                    "questions": [
                        {
                            "text": "Формула для числа размещений без повторений:",
                            "microtopic": 7,  # Комбинаторика
                            "answers": [
                                {"text": "A(n,k) = n!/(n-k)!", "is_correct": True},
                                {"text": "A(n,k) = n!/k!", "is_correct": False},
                                {"text": "A(n,k) = n!/(k!(n-k)!)", "is_correct": False},
                                {"text": "A(n,k) = n^k", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Формула для числа сочетаний:",
                            "microtopic": 7,  # Комбинаторика
                            "answers": [
                                {"text": "C(n,k) = n!/(k!(n-k)!)", "is_correct": True},
                                {"text": "C(n,k) = n!/(n-k)!", "is_correct": False},
                                {"text": "C(n,k) = n!/k!", "is_correct": False},
                                {"text": "C(n,k) = n^k", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Вероятность",
                    "homework": "Теория вероятностей",
                    "questions": [
                        {
                            "text": "Классическое определение вероятности:",
                            "microtopic": 8,  # Вероятность
                            "answers": [
                                {"text": "P(A) = m/n", "is_correct": True},
                                {"text": "P(A) = n/m", "is_correct": False},
                                {"text": "P(A) = m×n", "is_correct": False},
                                {"text": "P(A) = m+n", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Вероятность достоверного события равна:",
                            "microtopic": 8,  # Вероятность
                            "answers": [
                                {"text": "1", "is_correct": True},
                                {"text": "0", "is_correct": False},
                                {"text": "0.5", "is_correct": False},
                                {"text": "∞", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Вероятность невозможного события равна:",
                            "microtopic": 8,  # Вероятность
                            "answers": [
                                {"text": "0", "is_correct": True},
                                {"text": "1", "is_correct": False},
                                {"text": "0.5", "is_correct": False},
                                {"text": "-1", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Интегралы",
                    "homework": "Интегрирование",
                    "questions": [
                        {
                            "text": "Интеграл от константы c равен:",
                            "microtopic": 6,  # Интегралы
                            "answers": [
                                {"text": "cx + C", "is_correct": True},
                                {"text": "c + C", "is_correct": False},
                                {"text": "c", "is_correct": False},
                                {"text": "0", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Интеграл от x равен:",
                            "microtopic": 6,  # Интегралы
                            "answers": [
                                {"text": "x²/2 + C", "is_correct": True},
                                {"text": "x + C", "is_correct": False},
                                {"text": "2x + C", "is_correct": False},
                                {"text": "x² + C", "is_correct": False}
                            ]
                        }
                    ]
                }
            ],
            "Физика": [
                {
                    "name": "Механика",
                    "homework": "Законы Ньютона",
                    "questions": [
                        {
                            "text": "Первый закон Ньютона также называется:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "Закон инерции", "is_correct": True},
                                {"text": "Закон силы", "is_correct": False},
                                {"text": "Закон действия", "is_correct": False},
                                {"text": "Закон движения", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Второй закон Ньютона записывается как:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "F = ma", "is_correct": True},
                                {"text": "F = mv", "is_correct": False},
                                {"text": "F = m/a", "is_correct": False},
                                {"text": "F = a/m", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Третий закон Ньютона гласит:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "Действие равно противодействию", "is_correct": True},
                                {"text": "Сила пропорциональна ускорению", "is_correct": False},
                                {"text": "Тело сохраняет состояние покоя", "is_correct": False},
                                {"text": "Энергия сохраняется", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Единица измерения силы в СИ:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "Ньютон (Н)", "is_correct": True},
                                {"text": "Джоуль (Дж)", "is_correct": False},
                                {"text": "Ватт (Вт)", "is_correct": False},
                                {"text": "Паскаль (Па)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Формула для расчета импульса:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "p = mv", "is_correct": True},
                                {"text": "p = ma", "is_correct": False},
                                {"text": "p = Ft", "is_correct": False},
                                {"text": "p = mv²", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Кинематика",
                    "homework": "Движение тел",
                    "questions": [
                        {
                            "text": "Формула равномерного движения:",
                            "microtopic": 9,  # Кинематика
                            "answers": [
                                {"text": "s = vt", "is_correct": True},
                                {"text": "s = at²", "is_correct": False},
                                {"text": "s = v²t", "is_correct": False},
                                {"text": "s = vt²", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Ускорение - это:",
                            "microtopic": 9,  # Кинематика
                            "answers": [
                                {"text": "Изменение скорости за единицу времени", "is_correct": True},
                                {"text": "Изменение пути за единицу времени", "is_correct": False},
                                {"text": "Произведение скорости на время", "is_correct": False},
                                {"text": "Отношение пути к времени", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Единица измерения ускорения:",
                            "microtopic": 9,  # Кинематика
                            "answers": [
                                {"text": "м/с²", "is_correct": True},
                                {"text": "м/с", "is_correct": False},
                                {"text": "м²/с", "is_correct": False},
                                {"text": "с/м", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Свободное падение характеризуется ускорением:",
                            "microtopic": 9,  # Кинематика
                            "answers": [
                                {"text": "g ≈ 9.8 м/с²", "is_correct": True},
                                {"text": "g ≈ 10 м/с", "is_correct": False},
                                {"text": "g ≈ 9.8 м/с", "is_correct": False},
                                {"text": "g ≈ 1 м/с²", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Термодинамика",
                    "homework": "Тепловые процессы",
                    "questions": [
                        {
                            "text": "Первый закон термодинамики:",
                            "microtopic": 2,  # Термодинамика
                            "answers": [
                                {"text": "ΔU = Q - A", "is_correct": True},
                                {"text": "ΔU = Q + A", "is_correct": False},
                                {"text": "ΔU = Q × A", "is_correct": False},
                                {"text": "ΔU = Q / A", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Абсолютный нуль температуры равен:",
                            "microtopic": 2,  # Термодинамика
                            "answers": [
                                {"text": "-273°C", "is_correct": True},
                                {"text": "0°C", "is_correct": False},
                                {"text": "-100°C", "is_correct": False},
                                {"text": "-373°C", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Единица измерения количества теплоты:",
                            "microtopic": 2,  # Термодинамика
                            "answers": [
                                {"text": "Джоуль (Дж)", "is_correct": True},
                                {"text": "Ньютон (Н)", "is_correct": False},
                                {"text": "Ватт (Вт)", "is_correct": False},
                                {"text": "Кельвин (К)", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Электричество",
                    "homework": "Электрические явления",
                    "questions": [
                        {
                            "text": "Закон Ома для участка цепи:",
                            "microtopic": 3,  # Электричество
                            "answers": [
                                {"text": "I = U/R", "is_correct": True},
                                {"text": "I = UR", "is_correct": False},
                                {"text": "I = R/U", "is_correct": False},
                                {"text": "I = U + R", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Единица измерения электрического сопротивления:",
                            "microtopic": 3,  # Электричество
                            "answers": [
                                {"text": "Ом (Ω)", "is_correct": True},
                                {"text": "Ампер (А)", "is_correct": False},
                                {"text": "Вольт (В)", "is_correct": False},
                                {"text": "Ватт (Вт)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Мощность электрического тока:",
                            "microtopic": 3,  # Электричество
                            "answers": [
                                {"text": "P = UI", "is_correct": True},
                                {"text": "P = U/I", "is_correct": False},
                                {"text": "P = U + I", "is_correct": False},
                                {"text": "P = U - I", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Оптика",
                    "homework": "Световые явления",
                    "questions": [
                        {
                            "text": "Скорость света в вакууме равна:",
                            "microtopic": 5,  # Оптика
                            "answers": [
                                {"text": "3×10⁸ м/с", "is_correct": True},
                                {"text": "3×10⁶ м/с", "is_correct": False},
                                {"text": "3×10¹⁰ м/с", "is_correct": False},
                                {"text": "3×10⁴ м/с", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Закон преломления света:",
                            "microtopic": 5,  # Оптика
                            "answers": [
                                {"text": "n₁sinα₁ = n₂sinα₂", "is_correct": True},
                                {"text": "n₁cosα₁ = n₂cosα₂", "is_correct": False},
                                {"text": "n₁α₁ = n₂α₂", "is_correct": False},
                                {"text": "n₁/α₁ = n₂/α₂", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Угол падения равен углу отражения - это:",
                            "microtopic": 5,  # Оптика
                            "answers": [
                                {"text": "Закон отражения", "is_correct": True},
                                {"text": "Закон преломления", "is_correct": False},
                                {"text": "Закон дисперсии", "is_correct": False},
                                {"text": "Закон интерференции", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Колебания и волны",
                    "homework": "Механические колебания",
                    "questions": [
                        {
                            "text": "Период колебаний - это:",
                            "microtopic": 7,  # Колебания
                            "answers": [
                                {"text": "Время одного полного колебания", "is_correct": True},
                                {"text": "Число колебаний в секунду", "is_correct": False},
                                {"text": "Максимальное отклонение", "is_correct": False},
                                {"text": "Скорость колебаний", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Частота колебаний измеряется в:",
                            "microtopic": 7,  # Колебания
                            "answers": [
                                {"text": "Герцах (Гц)", "is_correct": True},
                                {"text": "Секундах (с)", "is_correct": False},
                                {"text": "Метрах (м)", "is_correct": False},
                                {"text": "Радианах (рад)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Связь между периодом T и частотой f:",
                            "microtopic": 7,  # Колебания
                            "answers": [
                                {"text": "T = 1/f", "is_correct": True},
                                {"text": "T = f", "is_correct": False},
                                {"text": "T = 2πf", "is_correct": False},
                                {"text": "T = f²", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Магнетизм",
                    "homework": "Магнитные явления",
                    "questions": [
                        {
                            "text": "Сила Лоренца действует на:",
                            "microtopic": 4,  # Магнетизм
                            "answers": [
                                {"text": "Движущийся заряд в магнитном поле", "is_correct": True},
                                {"text": "Неподвижный заряд", "is_correct": False},
                                {"text": "Нейтральные частицы", "is_correct": False},
                                {"text": "Только на электроны", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Единица измерения магнитной индукции:",
                            "microtopic": 4,  # Магнетизм
                            "answers": [
                                {"text": "Тесла (Тл)", "is_correct": True},
                                {"text": "Вебер (Вб)", "is_correct": False},
                                {"text": "Генри (Гн)", "is_correct": False},
                                {"text": "Ампер (А)", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Правило левой руки определяет направление:",
                            "microtopic": 4,  # Магнетизм
                            "answers": [
                                {"text": "Силы Ампера", "is_correct": True},
                                {"text": "Магнитного поля", "is_correct": False},
                                {"text": "Электрического тока", "is_correct": False},
                                {"text": "Скорости частицы", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Атомная физика",
                    "homework": "Строение атома",
                    "questions": [
                        {
                            "text": "Модель атома Резерфорда называется:",
                            "microtopic": 6,  # Атомная физика
                            "answers": [
                                {"text": "Планетарная модель", "is_correct": True},
                                {"text": "Модель пудинга", "is_correct": False},
                                {"text": "Квантовая модель", "is_correct": False},
                                {"text": "Волновая модель", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Постоянная Планка равна:",
                            "microtopic": 6,  # Атомная физика
                            "answers": [
                                {"text": "6.63×10⁻³⁴ Дж·с", "is_correct": True},
                                {"text": "6.63×10⁻²⁴ Дж·с", "is_correct": False},
                                {"text": "6.63×10⁻¹⁴ Дж·с", "is_correct": False},
                                {"text": "6.63×10⁻⁴ Дж·с", "is_correct": False}
                            ]
                        },
                        {
                            "text": "Энергия фотона определяется формулой:",
                            "microtopic": 6,  # Атомная физика
                            "answers": [
                                {"text": "E = hf", "is_correct": True},
                                {"text": "E = mc²", "is_correct": False},
                                {"text": "E = mv²/2", "is_correct": False},
                                {"text": "E = mgh", "is_correct": False}
                            ]
                        }
                    ]
                }
            ]
        }

        # Создаем уроки и ДЗ
        for subject_name, lessons in lessons_data.items():
            if subject_name not in created_subjects:
                continue
                
            subject = created_subjects[subject_name]
            print(f"   📚 Создание уроков для предмета '{subject_name}'...")
            
            for lesson_data in lessons:
                try:
                    # Создаем урок
                    lesson = await LessonRepository.create(
                        name=lesson_data["name"],
                        subject_id=subject.id,
                        course_id=default_course.id
                    )
                    print(f"      ✅ Урок '{lesson.name}' создан (ID: {lesson.id})")
                except ValueError as e:
                    # Урок уже существует, получаем его
                    existing_lessons = await LessonRepository.get_by_subject(subject.id)
                    lesson = next((l for l in existing_lessons if l.name == lesson_data["name"]), None)
                    if lesson:
                        print(f"      ⚠️ Урок '{lesson.name}' уже существует (ID: {lesson.id})")
                    else:
                        print(f"      ❌ Ошибка при создании урока: {e}")
                        continue

                try:
                    # Создаем домашнее задание
                    homework = await HomeworkRepository.create(
                        name=lesson_data["homework"],
                        subject_id=subject.id,
                        lesson_id=lesson.id
                    )
                    print(f"      ✅ ДЗ '{homework.name}' создано (ID: {homework.id})")
                except ValueError as e:
                    # ДЗ уже существует, получаем его
                    existing_homeworks = await HomeworkRepository.get_by_lesson(lesson.id)
                    homework = next((hw for hw in existing_homeworks if hw.name == lesson_data["homework"]), None)
                    if homework:
                        print(f"      ⚠️ ДЗ '{homework.name}' уже существует (ID: {homework.id})")
                    else:
                        print(f"      ❌ Ошибка при получении ДЗ: {e}")
                        continue

                # Проверяем, есть ли уже вопросы для этого ДЗ
                existing_questions = await QuestionRepository.get_by_homework(homework.id)
                if existing_questions:
                    print(f"         ⚠️ Вопросы для ДЗ '{homework.name}' уже существуют ({len(existing_questions)} шт.)")
                    continue

                # Создаем вопросы для ДЗ
                for question_data in lesson_data["questions"]:
                    question = await QuestionRepository.create(
                        homework_id=homework.id,
                        subject_id=subject.id,
                        text=question_data["text"],
                        microtopic_number=question_data["microtopic"],
                        time_limit=30  # 30 секунд на вопрос
                    )
                    print(f"         ✅ Вопрос создан (ID: {question.id})")

                    # Создаем варианты ответов
                    for answer_data in question_data["answers"]:
                        answer = await AnswerOptionRepository.create(
                            question_id=question.id,
                            text=answer_data["text"],
                            is_correct=answer_data["is_correct"]
                        )
                        print(f"            ✅ Вариант ответа создан (ID: {answer.id})")

        # Создаем дополнительные ДЗ для демонстрации
        print("   📝 Создание дополнительных ДЗ...")
        
        additional_homework = [
            {
                "subject": "Python",
                "lesson_name": "Работа с данными",
                "homework_name": "Структуры данных",
                "questions": [
                    {
                        "text": "Какой метод используется для добавления элемента в список?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "append()", "is_correct": True},
                            {"text": "add()", "is_correct": False},
                            {"text": "insert()", "is_correct": False},
                            {"text": "push()", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Как получить длину списка в Python?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "len(list)", "is_correct": True},
                            {"text": "list.length", "is_correct": False},
                            {"text": "list.size()", "is_correct": False},
                            {"text": "count(list)", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Как создать словарь в Python?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "{'key': 'value'}", "is_correct": True},
                            {"text": "['key': 'value']", "is_correct": False},
                            {"text": "('key': 'value')", "is_correct": False},
                            {"text": "dict('key': 'value')", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Как получить значение из словаря по ключу?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "dict['key']", "is_correct": True},
                            {"text": "dict.key", "is_correct": False},
                            {"text": "dict(key)", "is_correct": False},
                            {"text": "get dict['key']", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Что такое множество (set) в Python?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "Коллекция уникальных элементов", "is_correct": True},
                            {"text": "Упорядоченная последовательность", "is_correct": False},
                            {"text": "Пары ключ-значение", "is_correct": False},
                            {"text": "Неизменяемый список", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "subject": "Python",
                "lesson_name": "Продвинутые темы",
                "homework_name": "Генераторы и декораторы",
                "questions": [
                    {
                        "text": "Что такое list comprehension?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "Способ создания списков в одну строку", "is_correct": True},
                            {"text": "Метод сортировки списков", "is_correct": False},
                            {"text": "Функция для объединения списков", "is_correct": False},
                            {"text": "Способ удаления элементов", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Синтаксис list comprehension:",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "[x for x in iterable]", "is_correct": True},
                            {"text": "{x for x in iterable}", "is_correct": False},
                            {"text": "(x for x in iterable)", "is_correct": False},
                            {"text": "list(x for x in iterable)", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Что делает ключевое слово yield?",
                        "microtopic": 5,  # Функции
                        "answers": [
                            {"text": "Создает генератор", "is_correct": True},
                            {"text": "Возвращает значение", "is_correct": False},
                            {"text": "Останавливает функцию", "is_correct": False},
                            {"text": "Создает исключение", "is_correct": False}
                        ]
                    }
                ]
            }
        ]

        for hw_data in additional_homework:
            subject_name = hw_data["subject"]
            if subject_name not in created_subjects:
                continue
                
            subject = created_subjects[subject_name]
            
            try:
                # Создаем урок
                lesson = await LessonRepository.create(
                    name=hw_data["lesson_name"],
                    subject_id=subject.id,
                    course_id=default_course.id
                )
            except ValueError:
                # Урок уже существует, получаем его
                existing_lessons = await LessonRepository.get_by_subject(subject.id)
                lesson = next((l for l in existing_lessons if l.name == hw_data["lesson_name"]), None)
                if not lesson:
                    continue

            try:
                # Создаем ДЗ
                homework = await HomeworkRepository.create(
                    name=hw_data["homework_name"],
                    subject_id=subject.id,
                    lesson_id=lesson.id
                )
                print(f"      ✅ Дополнительное ДЗ '{homework.name}' создано (ID: {homework.id})")
            except ValueError:
                # ДЗ уже существует, получаем его
                existing_homeworks = await HomeworkRepository.get_by_lesson(lesson.id)
                homework = next((hw for hw in existing_homeworks if hw.name == hw_data["homework_name"]), None)
                if homework:
                    print(f"      ⚠️ ДЗ '{homework.name}' уже существует (ID: {homework.id})")
                else:
                    print(f"      ❌ Не удалось найти ДЗ '{hw_data['homework_name']}'")
                    continue

            # Проверяем, есть ли уже вопросы для этого ДЗ
            existing_questions = await QuestionRepository.get_by_homework(homework.id)
            if existing_questions:
                print(f"         ⚠️ Вопросы для ДЗ '{homework.name}' уже существуют ({len(existing_questions)} шт.)")
                continue

            # Создаем вопросы
            for question_data in hw_data["questions"]:
                question = await QuestionRepository.create(
                    homework_id=homework.id,
                    subject_id=subject.id,
                    text=question_data["text"],
                    microtopic_number=question_data["microtopic"],
                    time_limit=20  # 20 секунд на вопрос
                )

                # Создаем варианты ответов
                for answer_data in question_data["answers"]:
                    await AnswerOptionRepository.create(
                        question_id=question.id,
                        text=answer_data["text"],
                        is_correct=answer_data["is_correct"]
                    )

        print(f"📝 Создание уроков и домашних заданий завершено!")

    except Exception as e:
        print(f"❌ Ошибка при создании уроков и ДЗ: {e}")
