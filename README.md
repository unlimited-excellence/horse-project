![contributors](https://img.shields.io/github/contributors/unlimited-excellence/horse-project) ![git-size](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unlimited-excellence/horse-project/badges/git-size.md) ![git-file-count](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unlimited-excellence/horse-project/badges/git-file-count.md) ![git-lines-of-code](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unlimited-excellence/horse-project/badges/git-lines-of-code.md)
# Детальний опис MVP проєкту HORSE

Цей документ містить детальний опис мінімально життєздатного продукту (MVP) для Telegram-бота, розробленого на Python із використанням MongoDB для зберігання даних. Мета MVP - перевірити основну ідею проєкту: нараховувати токени за розв'язані задачі на офіційних раундах Codeforces (з урахуванням складності задач) та впровадити механізм верифікації, який підтверджує, що введений Codeforces handle належить користувачу.

---

## Зміст

- [1. Загальна Ідея](#1-загальна-ідея)
- [2. Основний Функціонал](#2-основний-функціонал)
  - [2.1 Реєстрація та Підключення](#21-реєстрація-та-підключення)
  - [2.2 Синхронізація та Нарахування Токенів](#22-синхронізація-та-нарахування-токенів)
  - [2.3 Переказ Токенів](#23-переказ-токенів)
- [3. Архітектура Проєкту](#3-архітектура-проєкту)
- [4. Компоненти MVP](#4-компоненти-mvp)
  - [4.1 Telegram Бот](#41-telegram-бот)
  - [4.2 Верифікація Codeforces Handle](#42-верифікація-codeforces-handle)
  - [4.3 Нарахування Токенів за Офіційні Раунди](#43-нарахування-токенів-за-офіційні-раунди)
  - [4.4 Переказ Токенів](#44-переказ-токенів)
- [5. Потік Роботи Користувача](#5-потік-роботи-користувача)
- [6. Зберігання Даних у MongoDB](#6-зберігання-даних-у-mongodb)
- [7. Обробка Команд та Логіка Нарахування](#7-обробка-команд-та-логіка-нарахування)
- [8. Логування та Моніторинг](#8-логування-та-моніторинг)
- [9. Майбутні Розширення](#9-мабутні-розширення)
- [10. Висновок](#10-висновок)

---

## 1. Загальна Ідея

Проєкт спрямований на створення Telegram-бота, який:
- **Реєструє користувачів** та зберігає їх основну інформацію у MongoDB.
- Дозволяє користувачам **пов’язати свій акаунт Codeforces** із своїм Telegram-акаунтом за допомогою команди `/link <handle>`.
- **Верифікує Codeforces handle**: після введення handle бот генерує унікальний контрольний код, який користувач повинен опублікувати у своєму профілі Codeforces. Бот перевіряє наявність цього коду через Codeforces API, щоб підтвердити приналежність акаунта.
- **Нараховує токени** за розв'язані задачі на офіційних раундах Codeforces, причому кількість токенів залежить від складності задачі:
  - Наприклад, за легку задачу - 5 токенів, за середню - 10 токенів, за складну - 20 токенів.
- Забезпечує можливість **переказу токенів** між користувачами.

---

## 2. Основний Функціонал

### 2.1 Реєстрація та Підключення

- **Команда `/start`**  
  При першому контакті бот вітає користувача та створює запис у базі даних (якщо користувача ще немає).

- **Команда `/link <handle>`**  
  Користувач вводить свій Codeforces handle.  
  - Бот генерує унікальний контрольний код.
  - Надсилає інструкції, щоб користувач опублікував цей код у своєму профілі на Codeforces (наприклад, у розділі "About" або "Bio").
  
- **Верифікація Codeforces handle**  
  Бот періодично перевіряє наявність контрольного коду через Codeforces API. Якщо код знайдено, бот підтверджує, що handle належить користувачу, та оновлює відповідний запис у MongoDB.

### 2.2 Синхронізація та Нарахування Токенів

- **Отримання даних з офіційних раундів**  
  Бот за допомогою планувальника (наприклад, `apscheduler`) періодично опитує Codeforces API для отримання інформації про участь користувача в офіційних раундах та даних про розв'язані задачі.

- **Обчислення токенів**  
  За кожну розв'язану задачу бот визначає її складність (легка, середня, складна) та нараховує токени згідно з встановленими коефіцієнтами:
  - Наприклад: 5 токенів за легку задачу, 10 токенів за середню, 20 токенів за складну.

- **Оновлення даних**  
  Після розрахунку токенів баланс користувача оновлюється в MongoDB, а інформація про нарахування записується в історію транзакцій.

### 2.3 Переказ Токенів

- **Команда `/balance`**  
  Відображає поточний баланс токенів користувача.

- **Команда `/send @username <кількість>`**  
  Дозволяє користувачу переказувати токени іншому користувачу:
  - Перевіряється, чи достатньо токенів у відправника.
  - Баланси обох користувачів оновлюються в MongoDB.
  - Запис транзакції зберігається в окремій колекції для журналу транзакцій.

---

## 3. Архітектура Проєкту
```lua
      +-----------------+                +--------------------------------------+
      |   Telegram      | <------------> |           Логіка Бота                |
      |  (Інтерфейс)    |                | (Python, python-telegram-bot)        |
      +-----------------+                +-----------------+--------------------+
                                                   |
                                                   v
                                           +---------------+
                                           |   MongoDB     |
                                           | (База даних)  |
                                           +---------------+
                                                   |
                                                   v
                      +--------------------------------------------------+
                      |           Codeforces API (опційно)               |
                      | або механізм для імпорту даних про рейтинг       |
                      +--------------------------------------------------+
```
- **Telegram Бот**: Основний інтерфейс для взаємодії з користувачами.
- **Логіка Бота**: Реалізована на Python із використанням бібліотеки `python-telegram-bot` для обробки команд і повідомлень, а також `apscheduler` для періодичного опитування API.
- **MongoDB**: Зберігає інформацію про користувачів, баланси токенів, контрольні коди та історію транзакцій.
- **Codeforces API**: Отримує дані про участь у офіційних раундах, розв’язані задачі та для перевірки наявності контрольних кодів.

---

## 4. Компоненти MVP

### 4.1 Telegram Бот

- **Основні Команди**:  
  `/start`, `/link <handle>`, `/balance`, `/send @username <кількість>`, `/rating` (опційно для перегляду останніх результатів).
  
- **Обробка Повідомлень**:  
  Використання бібліотеки `python-telegram-bot` для керування взаємодією з користувачами.

- **Планувальник Завдань**:  
  Інтеграція з `apscheduler` для періодичного опитування Codeforces API.

### 4.2 Верифікація Codeforces Handle

- **Генерація Контрольного Коду**:  
  При отриманні команди `/link <handle>`, бот генерує унікальний контрольний код для користувача.

- **Інструкції для Верифікації**:  
  Бот надсилає повідомлення з інструкціями, як опублікувати контрольний код у профілі Codeforces.

- **Перевірка через API**:  
  Бот періодично перевіряє через Codeforces API, чи з'явився контрольний код у профілі користувача, та оновлює статус верифікації.

### 4.3 Нарахування Токенів за Офіційні Раунди

- **Опитування Codeforces API**:  
  Бот отримує дані про офіційні раунди та розв’язані задачі користувача.

- **Логіка Розрахунку**:  
  Визначення складності кожної задачі та нарахування токенів згідно з коефіцієнтами:
  - Наприклад, легка - 5 токенів, середня - 10 токенів, складна - 20 токенів.

- **Оновлення Балансу**:  
  Новий баланс токенів записується у базі даних, а транзакції фіксуються в окремій колекції.

### 4.4 Переказ Токенів

- **Команда `/balance`**:  
  Перегляд поточного балансу користувача.

- **Команда `/send @username <кількість>`**:  
  Обробка переказу токенів між користувачами з валідацією (перевірка достатності коштів) та оновленням даних у MongoDB.

---

## 5. Потік Роботи Користувача

1. **Запуск Бота**  
   Користувач запускає бота командою `/start`, отримує привітальне повідомлення та інструкції.

2. **Прив’язка Codeforces**  
   - Команда: `/link <handle>`  
   - Бот генерує контрольний код і надсилає інструкції щодо його публікації в профілі Codeforces.

3. **Верифікація**  
   - Бот опитує Codeforces API для перевірки наявності контрольного коду.
   - Після успішної перевірки запис у базі даних оновлюється: handle верифіковано.

4. **Нарахування Токенів**  
   - Після участі у офіційних раундах Codeforces бот отримує інформацію про розв'язані задачі.
   - За кожну задачу токени нараховуються залежно від її складності.
   - Баланс користувача оновлюється, а транзакції фіксуються.

5. **Переказ Токенів**  
   - Команда `/balance` відображає поточний баланс.
   - Команда `/send @username <кількість>` дозволяє переказувати токени між користувачами.

---

## 6. Зберігання Даних у MongoDB

- **Колекція "users"**:  
  Зберігає дані користувача:
  ```json
  {
    "_id": "<telegram_user_id>",
    "codeforces_handle": "tourist",
    "verified": true,
    "rating": 3500,
    "tokens": 500,
    "control_code": "ABC123XYZ",  // унікальний код для верифікації
    "registered_at": "2025-01-01T12:00:00Z"
  }

- **Колекція "transactions"**:
  Записує історію переказів токенів:
  ```json
  {
    "from": "<telegram_user_id>",
    "to": "<telegram_user_id>",
    "amount": 50,
    "timestamp": "2025-01-02T15:30:00Z"
  }

---

## 7. Обробка Команд та Логіка Нарахування

### Обробка Команд
- Використання бібліотеки `python-telegram-bot` для обробки команд (`/start`, `/link`, `/balance`, `/send`).

### Планувальник Завдань
- Інтеграція з `apscheduler` для періодичного опитування Codeforces API.

### Функції Нарахування Токенів
- Отримання даних про офіційні раунди та розв’язані задачі.
- Визначення складності задач.
- Розрахунок кількості токенів згідно з заданими коефіцієнтами.
- Оновлення балансу користувача та запис транзакцій у MongoDB.

---

## 8. Логування та Моніторинг

### Логування Подій
- Реєстрація всіх ключових подій: реєстрації, верифікації, нарахування токенів, перекази.

### Використання Стандартного Логування Python
- Відстеження помилок та стану роботи бота.

### Моніторинг
- (Опційно) інтеграція з сервісами моніторингу для аналізу продуктивності та стабільності MVP.

---

## 9. Майбутні Розширення

### Покращення Валідації
- Розширення процесу верифікації Codeforces handle із додатковими кроками або перевірками.

### Додаткові Команди
- Реалізація додаткових функцій для покращення взаємодії з користувачами.

### Інтеграція з Іншими Платформами
- Додавання підтримки для AtCoder, LeetCode тощо.

### Розширена Аналітика
- Відстеження активності користувачів, статистики змагань та інших метрик.

### Контейнеризація
- Створення Dockerfile для зручного розгортання застосунку.

---

## 10. Висновок

MVP версія цього проєкту демонструє основний функціонал:
- Реєстрація та прив’язка акаунтів через Telegram.
- Верифікація Codeforces handle через публікацію контрольного коду.
- Нарахування токенів за розв'язані задачі на офіційних раундах згідно зі складністю задач.
- Переказ токенів між користувачами.

Це дозволяє перевірити життєздатність ідеї, зібрати відгуки та спланувати подальший розвиток платформи.
