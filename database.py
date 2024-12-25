import string
import random
from itertools import islice, product
import sqlite3
import bcrypt
from math import prod
import time
import telebot
from requests.exceptions import ConnectionError


conn = sqlite3.connect('MetaPsy_biology.db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_tg_id INTEGER UNIQUE,
    user_name TEXT NOT NULL,
    user_photo BLOB,
    user_number TEXT DEFAULT '939993399',
    pro_status BOOLEAN DEFAULT 0,
    exam_pass INTEGER DEFAULT 0
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    all_students TEXT DEFAULT '',
    group_photo BLOB
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_tg_id INTEGER UNIQUE,
    admin_name TEXT NOT NULL, 
    admin_password TEXT NOT NULL
);
''')
conn.commit()
conn.close()

conn = sqlite3.connect('MetaPsy_biology.db')
cur = conn.cursor()
password = '1278'
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
try:
    cur.execute('SELECT * FROM admins WHERE admin_tg_id = ?', (71353121,))
    if not cur.fetchone():
        cur.execute('''
            INSERT INTO admins (admin_tg_id, admin_name, admin_password)
            VALUES (?, ?, ?)
        ''', (71353121, 'Алексей', hashed_password))
        conn.commit()
        print("Администратор успешно добавлен!")
    else:
        print("Администратор уже существует!")
except sqlite3.IntegrityError:
    print("Ошибка: администратор с таким Telegram ID уже существует!")
finally:
    conn.close()


def safe_send_message(bot, chat_id, text):
    retry_count = 3
    for i in range(retry_count):
        try:
            bot.send_message(chat_id, text)
            break
        except ConnectionError as e:
            print(f"Connection error: {e}. Retrying {i + 1}/{retry_count}...")
            time.sleep(2)  # Задержка перед повторной попыткой
        except Exception as e:
            print(f"Unexpected error: {e}")
            break


class User:
    def __init__(self, user_id, user_tg_id, user_name, user_photo, user_number, pro_status, exam_pass):
        self.user_id = user_id
        self.user_tg_id = user_tg_id
        self.user_name = user_name
        self.user_photo = user_photo
        self.user_number = user_number
        self.pro_status = pro_status
        self.exam_pass = exam_pass

    @staticmethod
    def user_sign_in(user_tg_id, user_name, user_number):
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM users WHERE user_name=?', (user_name,))
            result = cursor.fetchone()
            if result:
                cursor.execute('''
                    UPDATE users SET user_tg_id=?, user_number=? WHERE user_name=?
                ''', (user_tg_id, user_number, user_name))
                con.commit()
                cursor.execute('SELECT * FROM users WHERE user_name=?', (user_name,))
                user = cursor.fetchone()
                return User(
                    user_id=user[0],
                    user_tg_id=user[1],
                    user_name=user[2],
                    user_photo=user[3],
                    user_number=user[4],
                    pro_status=bool(user[5]),
                    exam_pass=int(user[6])
                )
            else:
                cursor.execute('''
                    INSERT INTO users (user_tg_id, user_name, user_number, pro_status, exam_pass)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_tg_id, user_name, user_number, 0, 0))
                con.commit()
                cursor.execute('SELECT * FROM users WHERE user_name=?', (user_name,))
                user = cursor.fetchone()
                print('Зашел новый пользователь')
                return User(
                    user_id=user[0],
                    user_tg_id=user[1],
                    user_name=user[2],
                    user_photo=user[3],
                    user_number=user[4],
                    pro_status=bool(user[5]),
                    exam_pass=int(user[6])
                )

    @staticmethod
    def user_log_in(user_id):
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE user_tg_id=?', (user_id,))
        result = cursor.fetchone()
        if result:
            user_id, user_tg_id, user_name, user_photo, user_number, user_status, exam_pass = result
            return User(user_id, user_tg_id, user_name, user_photo, user_number, user_status, exam_pass)
        else:
            print('Ошибка при регистрации')
            return None

    @staticmethod
    def change_photo(user_id, photo_path):
        with open(photo_path, 'rb') as file:
            photo_data = file.read()
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('UPDATE users SET user_photo = ? WHERE user_tg_id = ?', (photo_data, user_id))
        con.commit()
        con.close()

    @staticmethod
    def delete_account(user_id):
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE user_tg_id = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('DELETE FROM users WHERE user_tg_id = ?', (user_id,))
            con.commit()
            con.close()
            print(f'Аккаунт с user_id {user_id} успешно удалён.')
            return True
        else:
            con.close()
            print(f'Пользователь с user_id {user_id} не найден.')
            return False


    @staticmethod
    def delete_user(student_name, group_id):
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            # Получаем ID студента
            cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (student_name,))
            user = cursor.fetchone()
            if user:
                student_id = user[0]
                # Удаляем студента из группы
                cursor.execute('DELETE FROM group_members WHERE group_id = ? AND user_id = ?', (group_id, student_id))
                con.commit()

    @staticmethod
    def activate_pro_status(user_id):
        conn = sqlite3.connect('MetaPsy_biology.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_tg_id = ?', (user_id,))
        user = cur.fetchone()
        if not user:
            conn.close()
            return False
        cur.execute('UPDATE users SET pro_status = 1 WHERE user_tg_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def is_pro_user(user_tg_id):
        conn = sqlite3.connect('MetaPsy_biology.db')
        cur = conn.cursor()
        cur.execute('SELECT pro_status FROM users WHERE user_tg_id = ?', (user_tg_id,))
        result = cur.fetchone()
        conn.close()
        if result and result[0] == 1:
            return True
        return False

    @staticmethod
    def increase_exam_pass(user_tg_id: int):
        """
        Увеличивает количество сданных экзаменов для пользователя.
        :param user_tg_id: Телеграм ID пользователя.
        """
        try:
            conn = sqlite3.connect('MetaPsy_biology.db')
            cur = conn.cursor()
            cur.execute('''
                UPDATE users
                SET exam_pass = exam_pass + 1
                WHERE user_tg_id = ?
            ''', (user_tg_id,))
            conn.commit()
            conn.close()
            print(f"Количество сданных экзаменов для пользователя {user_tg_id} увеличено.")
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")


def get_exact_student(user_name):
    with sqlite3.connect('MetaPsy_biology.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE user_name = ?', (user_name,))
        user = cursor.fetchone()
    if user:
        print(f"Найден пользователь: {user[2]}")
        return {
            'user_id': user[0],
            'user_tg_id': user[1],
            'user_name': user[2],
            'user_photo': user[3],
            'user_number': user[4],
            'pro_status': bool(user[5]),
            'exam_pass': int(user[6])
        }
    else:
        print(f"Пользователь '{user_name}' не найден!")
        return None


class Admin:
    def __init__(self, admin_id, admin_tg_id, admin_name, admin_password):
        self.admin_id = admin_id
        self.admin_tg_id = admin_tg_id
        self.admin_name = admin_name
        self.admin_password = admin_password

    @staticmethod
    def admin_sign_in(admin_tg_id, admin_name, admin_password):
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('SELECT * FROM admins WHERE admin_tg_id = ?', (admin_tg_id,))
        hashed_password_l = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO admins (admin_tg_id, admin_name, admin_password)
            VALUES (?, ?, ?)''', (admin_tg_id, admin_name, hashed_password_l))
        con.commit()
        con.close()
        print('Администратор успешно добавлен.')
        return True

    @staticmethod
    def admin_log_in(admin_tg_id, admin_password):
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('SELECT * FROM admins WHERE admin_tg_id = ?', (admin_tg_id,))
        admin = cursor.fetchone()
        con.close()
        if admin:
            hashed_password = admin[3]
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            try:
                if bcrypt.checkpw(admin_password.encode('utf-8'), hashed_password):
                    print('Успешный вход!')
                    return Admin(*admin)
                else:
                    print('Неверный пароль!')
                    return None
            except ValueError as e:
                print(f'Ошибка хэша: {e}')
                return None
        else:
            print('Администратор не найден!')
            return None

    def change_password(self, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('UPDATE admins SET admin_password = ? WHERE admin_tg_id = ?',
                       (hashed_password, self.admin_tg_id))
        con.commit()
        con.close()
        print('Пароль успешно изменён!')

    @staticmethod
    def create_new_group(group_name, all_students, group_photo=None):
        if isinstance(all_students, str):
            all_students_list = [name.strip() for name in all_students.split(',')]
        else:
            all_students_list = [name.strip() for name in all_students]
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                INSERT INTO groups (group_name, group_photo)
                VALUES (?, ?)
            ''', (group_name, group_photo))
            group_id = cursor.lastrowid  # ID группы
            for user_name in all_students_list:
                user_name = user_name.strip()
                cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,))
                user = cursor.fetchone()
                if not user:
                    cursor.execute('''
                        INSERT INTO users (user_tg_id, user_name, user_number, pro_status, exam_pass)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (None, user_name, '939993399', 0, 0))
                    user_id = cursor.lastrowid
                else:
                    user_id = user[0]
                cursor.execute('''
                    INSERT INTO group_members (group_id, user_id)
                    VALUES (?, ?)
                ''', (group_id, user_id))

            con.commit()
        print(f'Группа "{group_name}" успешно создана!')
        return True

    @staticmethod
    def change_group_members(group_id, merge_students):
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()

            # Очистка текущих записей о членах группы
            cursor.execute('DELETE FROM group_members WHERE group_id = ?', (group_id,))

            # Добавляем новых студентов в group_members
            for student_name in merge_students:
                # Получаем ID студента по имени
                cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (student_name,))
                user_id = cursor.fetchone()

                # Если студента нет в users — добавляем его
                if not user_id:
                    cursor.execute('INSERT INTO users (user_name) VALUES (?)', (student_name,))
                    user_id = cursor.lastrowid
                else:
                    user_id = user_id[0]

                # Добавляем студента в группу
                cursor.execute('INSERT INTO group_members (group_id, user_id) VALUES (?, ?)', (group_id, user_id))

            con.commit()
            print(f'Список участников группы {group_id} обновлён!')

    @staticmethod
    def change_group_photo(group_id, photo_path):
        with open(photo_path, 'rb') as file:
            photo_data = file.read()
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('UPDATE groups SET group_photo = ? WHERE group_id = ?', (photo_data, group_id))
        con.commit()
        con.close()
        print(f'Фото группы {group_id} обновлено!')

    @staticmethod
    def delete_group(group_id):
        con = sqlite3.connect('MetaPsy_biology.db')
        cursor = con.cursor()
        cursor.execute('DELETE FROM groups WHERE group_id = ?', (group_id,))
        con.commit()
        con.close()


    @staticmethod
    def remove_student_from_group(group_id, user_id):
        """Удаляет студента из группы по group_id и user_id."""
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()

            # Удаляем запись из таблицы group_members
            cursor.execute('''
                DELETE FROM group_members
                WHERE group_id = ? AND user_id = ?
            ''', (group_id, user_id))

            # Обновляем поле all_students в таблице groups
            cursor.execute('''
                SELECT u.user_name
                FROM group_members gm
                JOIN users u ON gm.user_id = u.user_id
                WHERE gm.group_id = ?
            ''', (group_id,))
            updated_students = [row[0] for row in cursor.fetchall()]
            updated_students_str = ', '.join(updated_students)

            cursor.execute('''
                UPDATE groups
                SET all_students = ?
                WHERE group_id = ?
            ''', (updated_students_str, group_id))

            con.commit()
            print(f'Пользователь {user_id} удалён из группы {group_id}.')

class Group:
    def __init__(self, group_id, group_name, all_students, group_photo):
        self.group_id = group_id
        self.group_name = group_name
        self.all_students = all_students
        self.group_photo = group_photo

    @staticmethod
    def get_all_students(group_id):
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT u.user_name 
                FROM group_members gm
                JOIN users u ON gm.user_id = u.user_id
                WHERE gm.group_id = ?
            ''', (group_id,))
            members = [row[0] for row in cursor.fetchall()]
            return members

    @staticmethod
    def get_exact_student(user_name):
        user_name = user_name.strip()  # Убираем пробелы
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM users WHERE user_name = ?', (user_name,))
            user = cursor.fetchone()

        if user:
            print(f"Найден пользователь: {user[2]}")
            return {
                'user_id': user[0],
                'user_tg_id': user[1],
                'user_name': user[2],
                'user_photo': user[3],
                'user_number': user[4],
                'pro_status': bool(user[5]),
                'exam_pass': int(user[6])
            }
        else:
            print(f"Пользователь '{user_name}' не найден!")
            return None

    @staticmethod
    def get_all_groups():
        try:
            with sqlite3.connect('MetaPsy_biology.db') as con:
                cursor = con.cursor()
                cursor.execute('SELECT * FROM groups')
                results = cursor.fetchall()
                groups = []
                for row in results:
                    groups.append({
                        'group_id': row[0],
                        'group_name': row[1],
                        'all_students': row[2].split(',') if row[2] else []
                    })
                return groups if groups else []
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о группах: {e}")
            return []

    @staticmethod
    def get_exact_student_id(user_id):
        try:
            with sqlite3.connect('MetaPsy_biology.db') as con:
                cursor = con.cursor()
                cursor.execute('SELECT * FROM users WHERE user_tg_id = ?', (user_id,))
                result = cursor.fetchone()

                if result:
                    info = {
                        'user_id': result[0],
                        'tg_id': result[1],
                        'name': result[2],
                        'photo': result[3],
                        'phone': result[4],
                        'pro_status': 'Да' if result[5] else 'Нет',
                        'exam_pass': result[6]
                    }

                    # Проверка наличия фото
                    if info['photo']:
                        try:
                            # Сохраняем фото
                            with open(f"user_{info['user_id']}_photo.jpg", 'wb') as file:
                                file.write(info['photo'])
                            photo_status = f"Есть фото (user_{info['user_id']}_photo.jpg)"
                        except Exception as e:
                            photo_status = f"Ошибка при сохранении фото: {e}"
                    else:
                        photo_status = 'Фото отсутствует'

                    # Формируем результат
                    student_info = (
                        f"👤 Имя: {info['name']}\n"
                        f"📞 Номер телефона: {info['phone']}\n"
                        f"⭐ Pro-статус: {info['pro_status']}\n"
                        f"📚 Сдано экзаменов: {info['exam_pass']}\n"
                        f"📷 Фото: {photo_status}"
                    )
                    return student_info
                else:
                    return "Пользователь не найден!"
        except sqlite3.Error as e:
            return e

    @staticmethod
    def get_exact_group(group_id):
        # Подключаемся к базе данных
        with sqlite3.connect('MetaPsy_biology.db') as con:
            cursor = con.cursor()
            # Получаем данные группы по ID
            cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
            group = cursor.fetchone()

        # Если группа найдена
        if group:
            # Формируем информацию о группе
            group_info = {
                'group_id': group[0],
                'group_name': group[1],
                'all_students': group[2].split(',') if group[2] else [],  # Список студентов
                'group_photo': group[3]  # Фото (если есть)
            }

            # Проверка наличия фото
            photo_status = 'Есть фото' if group_info['group_photo'] else 'Фото отсутствует'

            # Формируем текстовый вывод
            group_text = (
                    f"🏫 *Группа:* {group_info['group_name']}\n"
                    f"👥 *Участников:* {len(group_info['all_students'])}\n"
                    f"📸 *Фото:* {photo_status}\n\n"
                    f"📋 *Список участников:*\n" +
                    '\n'.join([f"- {student}" for student in group_info['all_students']])
            )

            return group_info, group_text
        else:
            return None, "❌ *Группа не найдена!*"

def convert_to_binary(filename):
    with open(filename, 'rb') as file:
        return file.read()


def random_parent():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    number = random.randint(6, 12)
    parent = list()
    hetero = 0
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent.append(pair)
        if pair[0] != pair[1]:
            hetero += 1
    parent_str = ''.join(parent)
    return parent_str, hetero


def random_parents(n, m):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    number = random.randint(n, m)
    parent_1 = list()
    hetero_1 = 0
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_1.append(pair)
        if pair[0] != pair[1]:
            hetero_1 += 1
    parent_str_1 = ''.join(parent_1)
    parent_2 = list()
    hetero_2 = 0
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_2.append(pair)
        if pair[0] != pair[1]:
            hetero_2 += 1
    parent_str_2 = ''.join(parent_2)
    return parent_str_1, hetero_1, parent_str_2, hetero_2, number


def random_parent_for_filio():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    number = random.randint(6, 10)
    parent_1 = list()
    parent_pairs_1 = list()
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_1.append(pair)
        parent_pairs_1.append(pair)
    parent_str_1 = ''.join(parent_1)
    parent_2 = list()
    parent_pairs_2 = list()
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_2.append(pair)
        parent_pairs_2.append(pair)
    parent_str_2 = ''.join(parent_2)
    return parent_str_1, parent_pairs_1, parent_str_2, parent_pairs_2


def random_filio():
    # Генерация родителей
    parent_str_1, parent_pairs_1, parent_str_2, parent_pairs_2 = random_parent_for_filio()

    # Генерация потомков
    filio_1 = []
    filio_2 = []

    # Создаём генотип потомков для каждого родителя
    for pair in parent_pairs_1:
        if pair[0] == pair[1]:  # Гомозигота (AA или aa)
            filio_1.append(pair[0])
        else:  # Гетерозигота (Aa или aA)
            filio_1.append(random.choice(pair))

    for pair in parent_pairs_2:
        if pair[0] == pair[1]:  # Гомозигота
            filio_2.append(pair[0])
        else:  # Гетерозигота
            filio_2.append(random.choice(pair))

    # Формирование потомков
    result = []
    hetero_filio = []

    for ch1, ch2 in zip(filio_1, filio_2):
        # Сохраняем порядок символов в парах
        pair = ''.join(sorted([ch1, ch2]))
        result.append(pair)

        # Определяем гетерозиготы
        if pair[0] != pair[1]:  # Aa
            hetero_filio.append(pair)

    return ''.join(result), hetero_filio, parent_str_1, parent_str_2


def filio_nums():
    filio, hetero_filio, parent_1, parent_2 = random_filio()
    count = 0
    print(hetero_filio)
    for pair in hetero_filio:
        if str(pair) in parent_1 and str(pair) in parent_2:
            print(pair)
            count += 1
        else:
            pass
    answer = 2**count
    return answer, filio, parent_1, parent_2


def split_into_pairs(s):
    return [s[i:i+2] for i in range(0, len(s), 2)]


def all_filio():
    parent_str_1, hetero_1, parent_str_2, hetero_2, number = random_parents(2, 4)
    parent_pairs_1 = split_into_pairs(parent_str_1)
    parent_pairs_2 = split_into_pairs(parent_str_2)
    parent_code_1 = []
    parent_code_2 = []
    for ch1, ch2 in parent_pairs_1:
        if ch1.islower():
            parent_code_1.append(1)
        elif ch1.isupper() and ch2.islower():
            parent_code_1.append(2)
        elif ch1.isupper() and ch2.isupper():
            parent_code_1.append(3)
    for ch1, ch2 in parent_pairs_2:
        if ch1.islower():
            parent_code_2.append(1)
        elif ch1.isupper() and ch2.islower():
            parent_code_2.append(2)
        elif ch1.isupper() and ch2.isupper():
            parent_code_2.append(3)
    return parent_code_1, parent_code_2, parent_str_1, parent_str_2, number


def test4_1():
    parent_code_1, parent_code_2, parent_str_1, parent_str_2, number = all_filio()
    result = 1
    for i in range(0, number):
        if parent_code_1[i] == 1 and parent_code_2[i] == 1:
            result *= 1
        elif parent_code_1[i] == 3 and parent_code_2[i] == 3:
            result *= 1
        elif parent_code_1[i] == 1 and parent_code_2[i] == 3:
            result *= 0
        elif parent_code_1[i] == 3 and parent_code_2[i] == 1:
            result *= 0
        elif parent_code_1[i] == 2 and parent_code_2[i] == 2:
            result *= 2
        elif parent_code_1[i] == 2 and parent_code_2[i] == 1:
            result *= 1
        elif parent_code_1[i] == 2 and parent_code_2[i] == 3:
            result *= 1
        elif parent_code_1[i] == 1 and parent_code_2[i] == 2:
            result *= 1
        elif parent_code_1[i] == 3 and parent_code_2[i] == 2:
            result *= 1
    return result, parent_str_1, parent_str_2


def test4_2():
    parent_code_1, parent_code_2, parent_str_1, parent_str_2, number = all_filio()
    result = 1
    for i in range(0, number):
        if parent_code_1[i] == 1 and parent_code_2[i] == 1:
            result *= 0
        elif parent_code_1[i] == 3 and parent_code_2[i] == 3:
            result *= 0
        elif parent_code_1[i] == 1 and parent_code_2[i] == 3:
            result *= 1
        elif parent_code_1[i] == 3 and parent_code_2[i] == 1:
            result *= 1
        elif parent_code_1[i] == 2 and parent_code_2[i] == 2:
            result *= 2
        elif parent_code_1[i] == 2 and parent_code_2[i] == 1:
            result *= 1
        elif parent_code_1[i] == 2 and parent_code_2[i] == 3:
            result *= 1
        elif parent_code_1[i] == 1 and parent_code_2[i] == 2:
            result *= 1
        elif parent_code_1[i] == 3 and parent_code_2[i] == 2:
            result *= 1

    return result, parent_str_1, parent_str_2


def create_pre_fen():
    parent_str_1, hetero_1, parent_str_2, hetero_2, number = random_parents(2, 3)
    parent_1_pairs = split_into_pairs(parent_str_1)
    parent_2_pairs = split_into_pairs(parent_str_2)
    pre_answer = list()
    for pair_parent_1, pair_parent_2 in islice(zip(parent_1_pairs, parent_2_pairs), number):
        # Гетерозигота с гетерозиготой (Аа х Аа)
        if pair_parent_1 == pair_parent_2 and pair_parent_1[0] != pair_parent_1[1]:
            pre_answer.append([3, 1])
        # Гомозиготы с гомозиготами (АА х АА или АА х аа или аа х АА или аа х аа)
        elif pair_parent_1[0] == pair_parent_1[1] and pair_parent_2[0] == pair_parent_2[1]:
            pre_answer.append([1])
        # Гомозиготы с гетерозиготами (АА х Аа)
        elif pair_parent_1[0] == pair_parent_1[1] and pair_parent_2[0] != pair_parent_2[1] and str(pair_parent_1) == str(pair_parent_1).upper():
            print(str(pair_parent_1), str(pair_parent_2).upper())
            pre_answer.append([1])
            # Гомозиготы с гетерозиготами (Аa х АA)
        elif pair_parent_2[0] == pair_parent_2[1] and pair_parent_1[0] != pair_parent_1[1] and str(pair_parent_2) == str(pair_parent_2).upper():
            pre_answer.append([1])
        # Гомозиготы с гетерозиготами (аа х Аа или Аа х аа)
        else:
            pre_answer.append([1, 1])
    return parent_str_1, parent_str_2, pre_answer


def create_pre_gen():
    parent_str_1, hetero_1, parent_str_2, hetero_2, number = random_parents(2, 3)
    parent_1_pairs = split_into_pairs(parent_str_1)
    parent_2_pairs = split_into_pairs(parent_str_2)
    pre_answer = list()
    for pair_parent_1, pair_parent_2 in islice(zip(parent_1_pairs, parent_2_pairs), number):
        # Гетерозигота с гетерозиготой (Аа х Аа)
        if pair_parent_1 == pair_parent_2 and pair_parent_1[0] != pair_parent_1[1]:
            pre_answer.append([1, 2, 1])
        # Гомозиготы с гомозиготами (АА х АА или АА х аа или аа х АА или аа х аа)
        elif pair_parent_1[0] == pair_parent_1[1] and pair_parent_2[0] == pair_parent_2[1]:
            pre_answer.append([1])
        # Гомозиготы с гетерозиготами (АА х Аа или аа х Аа или Аа х АА или Аа х аа)
        else:
            pre_answer.append([1, 1])
    return parent_str_1, parent_str_2, pre_answer


def segregation_fen():
    parent_str_1, parent_str_2, pre_answer = create_pre_fen()
    combinations = product(*pre_answer)
    results = [prod(comb) for comb in combinations]
    result = ':'.join(map(str, results))
    print(result)
    return parent_str_1, parent_str_2, result


def segregation_gen():
    parent_str_1, parent_str_2, pre_answer = create_pre_gen()
    combinations = product(*pre_answer)
    results = [prod(comb) for comb in combinations]
    result = ':'.join(map(str, results))
    print(parent_str_1, parent_str_2)
    print(pre_answer)
    print(result)
    return parent_str_1, parent_str_2, result


segregation_fen()
