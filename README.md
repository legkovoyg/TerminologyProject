---

# Terminology Project

---

## 1. Описание проекта

- Сервис предназначен для решения тестового задания - разработать сервис терминологии и REST API к нему.
- Описание проекта (README.md) создано с использованием ChatGPT.
- В проекте не используется Docker, Redis, Postgres ввиду требований ТЗ.

---

## 2. Проблема

Существует множество сервисов, обменивающихся электронными документами в формате JSON. Помимо структуры документа необходимо прийти к общему соглашению об использовании кодов для представления данных (например, специальностей медработников, диагнозов и т.д.). Независимый сервис терминологии позволяет централизованно хранить и обновлять справочники, что повышает согласованность данных между системами.

---

## 3. Требования

### 3.1. Технологии

- **Язык:** Python 3.12.7
- **Фреймворк:** Django 5.1.6
- **REST API:** Django REST Framework (DRF)
- **Документация API:** drf-yasg (Swagger)
- **База данных:** SQLite
- **Управление зависимостями:** Poetry

### 3.2. Объекты и ограничения

#### Справочник (RefBook)
- **Поля:**  
  - Код (string, максимум 100 символов, обязательно)
  - Наименование (string, максимум 300 символов, обязательно)
  - Описание (текст произвольной длины)

- **Ограничения:**  
  - Не может быть двух справочников с одинаковым кодом.

#### Версия справочника (RefBookVersion)
- **Поля:**  
  - Справочник (ForeignKey, обязательно)
  - Версия (string, максимум 50 символов, обязательно)
  - Дата начала действия версии (дата)

- **Ограничения:**  
  - Не может быть более одной версии для одного справочника с одинаковой датой начала действия.
  - Не может существовать две версии с одинаковым набором «справочник + версия».

#### Элемент справочника (RefBookElement)
- **Поля:**  
  - Версия справочника (ForeignKey, обязательно)
  - Код элемента (string, максимум 100 символов, обязательно)
  - Значение элемента (string, максимум 300 символов, обязательно)

- **Ограничения:**  
  - В пределах одной версии справочника не может быть элементов с одинаковым кодом.

---

## 4. Административная панель

Админка предоставляет возможность:
- Добавления, изменения и удаления справочников. При редактировании справочника отображается список его версий с возможностью редактирования.
- Отображения в списке справочников следующих полей:
  - Идентификатор
  - Код
  - Наименование
  - Текущая версия
  - Дата начала действия версии
- Редактирования версий справочников с возможностью добавления элементов для каждой версии.
- Редактирования элементов справочника.

Интерфейс админки полностью на русском языке.

---

## 5. API

API сервиса предоставляет следующие методы:

### 5.1. Получение списка справочников

- **Метод:** GET  
- **URL:** `/api/refbooks/`  
- **Параметры запроса:**  
  - `date` (опционально, формат: ГГГГ-ММ-ДД) – если указан, возвращаются только те справочники, у которых есть версия с датой начала действия, не превышающей указанную.
- **Формат ответа:**

  ```json
  {
      "refbooks": [
          {
              "id": "1",
              "code": "MS1",
              "name": "Специальности медработников"
          },
          {
              "id": "2",
              "code": "ICD-10",
              "name": "МКБ-10"
          }
      ]
  }
  ```

### 5.2. Получение элементов заданного справочника

- **Метод:** GET  
- **URL:** `/api/refbooks/<id>/elements`  
- **Параметры запроса:**  
  - `version` (опционально) – номер версии. Если не указан, возвращаются элементы текущей версии (версия, дата начала которой — самая поздняя, но не позже текущей даты).
- **Формат ответа:**

  ```json
  {
      "elements": [
          {
              "code": "J00",
              "value": "Острый насморк"
          },
          {
              "code": "J01",
              "value": "Некоторое заболевание"
          }
      ]
  }
  ```

### 5.3. Валидация элемента справочника

- **Метод:** GET  
- **URL:** `/api/refbooks/<id>/check_element`  
- **Параметры запроса:**  
  - `code` (обязательный) – код элемента.
  - `value` (обязательный) – значение элемента.
  - `version` (опционально) – номер версии. Если не указан, проверяются элементы текущей версии.
- **Формат ответа:**

  ```json
  {
      "result": true
  }
  ```

  Если элемент с указанными данными найден, возвращается `true`, иначе — `false`.

---

## 6. Тестирование

Для API написаны тесты, которые проверяют:
- Получение списка справочников.
- Фильтрацию справочников по дате.
- Получение элементов справочника (с указанием и без указания версии).
- Валидацию существования элемента по заданным параметрам.
- 
Чтобы запустить тесты, выполните в корневой папке проекта команду:

```bash
python manage.py test
```

---

## 7. Документация API

Документация для API генерируется с помощью Swagger (drf-yasg). Все методы, параметры запроса и примеры ответов подробно описаны с помощью декоратора `@swagger_auto_schema`.

Чтобы запустить сервер и просмотреть Swagger UI, выполните:

```bash
python manage.py runserver
```

и перейдите по адресу:  
```
http://127.0.0.1:8000/swagger/
```

---

## 8. Запуск проекта

1. **Установка зависимостей:**

   Проект использует Poetry для управления зависимостями. Для установки заполните .env файл, созданный по .env_template и выполните:

   ```bash
   poetry install
   ```

2. **Применение миграций:**

   ```bash
   python manage.py migrate
   ```

3. **Запуск сервера:**

   ```bash
   python manage.py runserver
   ```

---

## 9. Дополнительная информация

- **Язык интерфейса админки:** русский.
- **База данных:** SQLite.
- **Тестовое задание:** Проект разработан согласно тестовому заданию, описанному в документе ТЗ.
- **SuperUser:** test - test.

