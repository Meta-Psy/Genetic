import telebot
import database as db
import buttons as bt
import random
from telebot.types import Message, PhotoSize
from database import User, Admin, Group

bot = telebot.TeleBot('7475946417:AAHRiC_nf5wur28BVcVD6SlKI-lXDmlRO2U')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = User.user_log_in(user_id)
    if user:
        bot.send_message(user_id, f'Добро пожаловать в ваш личный аккаунт {user.user_name}',
                         reply_markup=bt.main_menu_bt(user_id))
    else:
        bot.send_message(user_id,
                         'Добро пожаловать в генетику! \n\n'
                         'Здесь вы сможете закрепить свои основные навыки III этапа решения генетических задач \n'
                         'Вы зашли впервые. Пройдите пожалуйста быструю регистрацию!')
        bot.send_message(user_id, 'Найдите свою группу',
                         reply_markup=bt.students_all_groups(Group.get_all_groups()))


@bot.message_handler(commands=['admin'])
def admin_log_in(message):
    admin_id = message.from_user.id
    bot.send_message(admin_id, 'Пароль: ')
    bot.register_next_step_handler(message, admin_sign_in)


@bot.message_handler(content_types=['text'])
def user_main_menu(message):
    user_id = message.from_user.id
    if message.text == 'Мой профиль':
        info = Group.get_exact_student_id(user_id)
        bot.send_message(user_id, text=info, reply_markup=bt.main_menu_bt(user_id))
    elif message.text == 'Начать тест':
        main_menu(message)
    elif message.text == 'Показать все этапы':
        if User.is_pro_user(user_id):
            bot.send_message(
                user_id,
                text=(
                    "✨ *Добро пожаловать в ПРО-режим!* 🚀\n\n"
                    "💼 *Все доступные функции:* 📋\n\n"
                    "1. 📊 *Расчёт числа гамет* —\n"
                    "   _Определите количество возможных гамет организма._ 🧬\n\n"
                    "2. 🧬 *Расчёт числа гибридов* —\n"
                    "   _Вычислите общее количество гибридов при скрещивании._ 🔢\n\n"
                    "3. 🔍 *Расчёт числа указанных гибридов* —\n"
                    "   _Найдите точное количество гибридов с заданным генотипом._ 🎯\n\n"
                    "4. 🧩 *Расчёт числа нескольких гибридов* —\n"
                    "   _Рассчитайте гибриды с особыми признаками._ 📈\n\n"
                    "5. 🔬 *Соотношение по фенотипу* —\n"
                    "   _Определите фенотипические соотношения потомков._ 📊\n\n"
                    "6. 📊 *Соотношение по генотипу* —\n"
                    "   _Рассчитайте генотипические соотношения наследования._ 🧬\n\n"
                    "🌟 *Используйте доступные инструменты и станьте экспертом!* 🎓"
                ),
                reply_markup=bt.main_menu_bt_pro(),
                parse_mode="Markdown"
            )
        elif not User.is_pro_user(user_id):
            bot.send_message(user_id, 'Не жульничать!')


@bot.callback_query_handler(lambda call: call.data in ['gametes_num', 'filio_all_num',
                                                       'filio_num', 'filio_some_num',
                                                       'segregation_fen', 'segregation_gen',
                                                       'change_pass', 'create_new_group',
                                                       'change_group_members', 'change_group_photo',
                                                       'del_group', 'upgrade_all_pro'])
def all_calls(call):
    user_id = call.message.chat.id
    if call.data == 'gametes_num':
        bot.delete_message(user_id, call.message.message_id)
        parent, hetero = db.random_parent()
        bot.send_message(
            user_id,
            text=(
                "📊 *Задача:*\n\n"
                "Каково *количество гамет* организма с генотипом:\n"
                f"`{parent}`\n\n"
                "_\\(Отправьте ответ в виде числа\\.\\)_ 🔢"
            ),
            parse_mode="MarkdownV2"
        )

        # Регистрация следующего шага
        bot.register_next_step_handler(
            call.message,
            lambda msg: gametes_num(msg, hetero)
        )
    elif call.data == 'filio_all_num':
        bot.delete_message(user_id, call.message.message_id)
        parent_1, hetero_1, parent_2, hetero_2, number = db.random_parents(6, 8)
        answer = (2**hetero_1) * (2**hetero_2)
        bot.send_message(
            user_id,
            text=(
                "📊 *Задача:*\n\n"
                "Каково *количество гибридов \\(детей\\)*, полученных при скрещивании:\n\n"
                f"♀️ *{parent_1}* \n"
                f"♂️ *{parent_2}* \n\n"
                "_\\(Отправьте ответ в виде числа\\.\\)_ 🔢"  # Экранированы скобки и точка
            ),
            parse_mode="MarkdownV2")
        bot.register_next_step_handler(call.message, lambda msg: filio_all_num(msg, answer))
    elif call.data == 'filio_num':
        bot.delete_message(user_id, call.message.message_id)
        answer, filio, parent_1, parent_2 = db.filio_nums()
        bot.send_message(user_id, text=(
            "📊 *Задача:*\n\n"
            "При скрещивании:\n\n"
            f"♀️ *{parent_1}* \n"
            f"♂️ *{parent_2}* \n\n"
            "Найдите *количество детей* с генотипом:\n"
            f"`{filio}`"
        ), parse_mode="MarkdownV2")
        bot.register_next_step_handler(call.message, lambda msg: filio_num(msg, answer))
    elif call.data == 'filio_some_num':
        bot.delete_message(user_id, call.message.message_id)
        random_filio_some_num = random.choice(
            ['дети со всеми гомозиготными признаками', 'дети со всеми гетерозиготными признаками'])
        if random_filio_some_num == 'дети со всеми гомозиготными признаками':
            result, parent_1, parent_2 = db.test4_1()
            bot.send_message(user_id, text=(
                "📊 *Задача:*\n\n"
                "При скрещивании:\n\n"
                f"♀️ *{parent_1}* \n"
                f"♂️ *{parent_2}* \n\n"
                "Найдите *количество всех детей*, соответствующих условию:\n"
                f"*{random_filio_some_num}*"
            ), parse_mode="MarkdownV2")
            bot.register_next_step_handler(call.message, lambda msg: filio_some_nums(msg, result, random_filio_some_num))
        elif random_filio_some_num == 'дети со всеми гетерозиготными признаками':
            result, parent_1, parent_2 = db.test4_2()
            bot.send_message(user_id, text=(
                "📊 *Задача:*\n\n"
                "При скрещивании:\n\n"
                f"♀️ *{parent_1}* \n"
                f"♂️ *{parent_2}* \n\n"
                "Найдите *количество всех детей*, соответствующих условию:\n"
                f"*{random_filio_some_num}*"
            ), parse_mode="MarkdownV2")
            bot.register_next_step_handler(call.message,
                                           lambda msg: filio_some_nums(msg, result, random_filio_some_num))
    elif call.data == 'segregation_fen':
        bot.delete_message(user_id, call.message.message_id)
        parent_1, parent_2, *result = db.segregation_fen()
        bot.send_message(user_id, text=(
            "📊 *Задача:*\n\n"
            "При скрещивании:\n\n"
            f"♀️ *{parent_1}* \n"
            f"♂️ *{parent_2}* \n\n"
            "Найдите *соотношение всех фенотипов* данных организмов\\.\n\n"
            "📊 *Ответ напишите в формате:* `9\\:3\\:3\\:1`"
        ), parse_mode="MarkdownV2")
        bot.register_next_step_handler(call.message, lambda msg: segregation_fen(msg, result))
    elif call.data == 'segregation_gen':
        bot.delete_message(user_id, call.message.message_id)
        parent_1, parent_2, result = db.segregation_gen()
        bot.send_message(user_id, text=(
            "📊 *Задача:*\n\n"
            "При скрещивании:\n\n"
            f"♀️ *{parent_1}* \n"
            f"♂️ *{parent_2}* \n\n"
            "Найдите *соотношение всех генотипов* данных организмов\\.\n\n"
            "📊 *Ответ напишите в формате:* `1\\:2\\:1\\:2\\:4\\:2\\:1\\:2\\:1`"
        ), parse_mode="MarkdownV2")
        bot.register_next_step_handler(call.message, lambda msg: segregation_gen(msg, result))
    elif call.data == 'change_pass':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Введите ваш старый пароль: ')
        bot.register_next_step_handler(call.message, admin_change_password)
    elif call.data == 'create_new_group':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Введите имя вашей новой группы: ')
        bot.register_next_step_handler(call.message, get_group_name)
    elif call.data == 'upgrade_all_pro':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Успешно обновлено')
        Admin.upgrade_all_pro_status()
    elif call.data == 'del_group':
        bot.delete_message(user_id, call.message.message_id)
        groups = Group.get_all_groups()
        bot.send_message(call.message.chat.id, 'Выберите группу, которую вы бы хотели удалить: ',
                         reply_markup=bt.all_groups(groups))
    elif call.data == 'change_group_members':
        bot.delete_message(user_id, call.message.message_id)
        groups = Group.get_all_groups()
        bot.send_message(call.message.chat.id, "Нажмите на название группы, которую вы бы хотели изменить: ",
                         reply_markup=bt.all_groups(groups))
    elif call.data == 'change_group_complete':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Изменения успешно сохранены. \n'
                                  'Чтобы вы хотели сделать еще?', reply_markup=bt.admin_main_menu_bt())
    elif call.data == 'OK':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Изменения успешно сохранены. \n'
                                  'Чтобы вы хотели сделать еще?', reply_markup=bt.admin_main_menu_bt())
    elif call.data == 'change_group_photo':
        bot.delete_message(user_id, call.message.message_id)



@bot.callback_query_handler(lambda call: 'delete_gr_' in call.data)
def delete_groups(call):
    user_id = call.message.chat.id
    group_id = int(call.data.replace('delete_gr_', ''))
    Admin.delete_group(group_id)
    groups = Group.get_all_groups()
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=bt.all_groups(groups)
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        bot.send_message(call.message.chat.id, 'Список групп обновлен.', reply_markup=bt.all_groups(groups))


@bot.callback_query_handler(lambda call: 'student_exact_group_' in call.data)
def student_add(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    group_id = int(call.data.replace('student_exact_group_', ''))
    all_members = Group.get_all_students(group_id)
    print(all_members)
    bot.send_message(user_id, 'Найдите себя', reply_markup=bt.student_group_members(all_members))


@bot.callback_query_handler(lambda call: 'exact_group_' in call.data)
def change_members(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    group_id = int(call.data.replace('exact_group_', ''))
    all_members = Group.get_all_students(group_id)
    bot.send_message(user_id, 'Напишите имя студентов которых вы бы хотели добавить через запятую, '
                              'либо удалите через "❌" тех, '
                              'кого нужно исключить из группы. \n'
                              'Если некого добавлять, нажмите "Готово"', reply_markup=bt.group_members(all_members, group_id))
    bot.register_next_step_handler(call.message, add_members, group_id)


def add_members(message, group_id):
    user_id = message.from_user.id
    new_members = [name.strip() for name in message.text.split(',')]
    current_members = Group.get_all_students(group_id) or []
    merge_students = list(set(current_members + new_members))
    Admin.change_group_members(group_id, merge_students)
    bot.send_message(
        user_id,
        '📋 *Список участников обновлён!* 🎉\n\n'
        '📝 *Текущий список участников группы:*\n'
        f"`{', '.join(merge_students)}`\n\n"
        'Хотите добавить или удалить ещё участников? Выберите действие ниже:',
        parse_mode='Markdown',
        reply_markup=bt.group_members(merge_students, group_id)  # Обновлённые кнопки
    )


@bot.callback_query_handler(lambda call: 'delete_' in call.data)
def delete_member(call):
    user_id = call.message.chat.id

    # Извлекаем имя студента и group_id из callback_data
    data = call.data.replace('delete_', '').split('_')
    student_name = '_'.join(data[:-1]).strip()  # Вдруг в имени есть подчеркивания
    group_id = int(data[-1])  # Последний элемент — group_id

    # Удаляем сообщение с кнопками
    bot.delete_message(user_id, call.message.message_id)

    # Ищем студента в базе данных
    student = db.get_exact_student(student_name)
    if not student:
        bot.send_message(user_id, f'❌ Пользователь "{student_name}" не найден в группе!')
        return

    # Удаляем студента из группы
    Admin.remove_student_from_group(group_id, student['user_id'])

    # Получаем обновлённый список студентов
    all_students = Group.get_all_students(group_id)
    bot.send_message(
        user_id,
        f"✅ Участник '{student_name}' успешно удалён из группы!\n\n"
        "📋 Обновлённый список участников:",
        reply_markup=bt.group_members(all_students, group_id)
    )

@bot.callback_query_handler(lambda call: call.data.startswith('group_') and call.data.replace('group_', '').isdigit())
def groups_call_data(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)

    # Преобразуем group_id в число
    group_id = int(call.data.replace('group_', ''))
    group_info = Group.get_exact_group(group_id)

    # Проверяем наличие информации о группе
    if group_info and group_info['group_photo']:
        with open('group_photo.jpg', 'wb') as file:
            file.write(group_info['group_photo'])
        with open('group_photo.jpg', 'rb') as photo:
            bot.send_photo(
                user_id,
                photo=photo,
                caption=f"Группа: {group_info['group_name']}\nСтуденты: {', '.join(group_info['all_students'])}"
            )
    else:
        bot.send_message(
            user_id,
            f"Группа: {group_info['group_name']}\nСтуденты: {', '.join(group_info['all_students'])}"
        )


@bot.callback_query_handler(lambda call: call.data == 'change_group_complete')
def handle_change_complete(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    bot.send_message(user_id, "Изменения успешно сохранены!")


def admin_sign_in(message):
    admin_id = message.from_user.id
    password = message.text
    admin = Admin.admin_log_in(admin_id, password)
    if admin:
        bot.send_message(admin_id, f'Добро пожаловать в администраторский аккаунт {admin.admin_name}',
                         reply_markup=bt.admin_main_menu_bt())
    else:
        bot.send_message(admin_id, f'Пароль неверный, попробуйте еще раз!')
        bot.register_next_step_handler(message, admin_sign_in)


@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    user_id = message.from_user.id
    photo: PhotoSize = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    photo_path = f'{user_id}_photo.jpg'
    with open(photo_path, 'wb') as file:
        file.write(downloaded_file)
    with open(photo_path, 'rb') as file:
        photo_data = file.read()
    User.change_photo(user_id, photo_data)
    bot.send_message(user_id, "Ваше фото успешно сохранено в базе данных!")


def get_name(message, group_id):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Найдите себя:', reply_markup=bt.names(Group.get_all_students(group_id)))


@bot.callback_query_handler(lambda call: 'name_' in call.data)
def name_call_data(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    user_name = call.data.replace('name_', '')
    bot.send_message(user_id, 'Теперь отправьте номер при помощи кнопки в вашем меню 📋.', reply_markup=bt.phone())
    bot.register_next_step_handler(call.message, get_number, user_name)


def get_number(message, user_name):
    user_id = message.from_user.id
    if message.contact:
        user_number = message.contact.phone_number
        bot.send_message(user_id, 'Отлично. Ваш номер телефона сохранен')
        user = User.user_sign_in(user_id, user_name, user_number)
        if user:
            bot.send_message(user_id, 'Поздравляю! Вы успешно зарегистрированы. '
                                      'Пора проверить ваши генетические навыки', reply_markup=bt.main_menu_bt(user_id))
        else:
            bot.send_message(user_id, 'Ошибка регистрации. Обратитесь к Алексею Николаевичу')
        student_info = db.get_exact_student(user_name)
        if student_info:
            if student_info['user_photo']:
                with open('temp_photo.jpg', 'wb') as file:
                    file.write(student_info['user_photo'])
                with open('temp_photo.jpg', 'rb') as photo:
                    bot.send_photo(user_id, photo=photo, caption=(
                        f"Имя: {student_info['user_name']}\n"
                        f"Номер: {student_info['user_number']}\n"
                        f"Pro статус: {'Да' if student_info['pro_status'] else 'Нет'}\n"
                        f"Пройдено экзаменов: {student_info['exam_pass']}"
                    ))
            else:
                bot.send_message(user_id, (
                    f"Имя: {student_info['user_name']}\n"
                    f"Номер: {student_info['user_number']}\n"
                    f"Pro статус: {'Да' if student_info['pro_status'] else 'Нет'}\n"
                    f"Пройдено экзаменов: {student_info['exam_pass']}"
                ))
        else:
            bot.send_message(user_id, "Пользователь не найден.")
    else:
        bot.send_message(user_id, 'Отправьте, пожалуйста, номер при помощи кнопки в вашем меню 📋.',
                         reply_markup=bt.phone())
        bot.register_next_step_handler(message, get_number, user_name)


def admin_change_password(message):
    admin_id = message.from_user.id
    password = message.text
    admin = Admin.admin_log_in(admin_id, password)
    if admin:
        bot.send_message(admin_id, 'Введите пароль на который вы хотели бы заменить свой старый: ')
        bot.register_next_step_handler(message, admin_change_password_complete, admin)
    else:
        bot.send_message(admin_id, 'Возникли проблемы с авторизацией. Попробуйте авторизоваться снова.\n'
                                   'Введите ваш старый пароль.')
        bot.register_next_step_handler(message, admin_log_in)


def admin_change_password_complete(message, admin):
    admin_id = message.from_user.id
    new_password = message.text
    Admin.change_password(admin, new_password)
    bot.send_message(admin_id, 'Поздравляем, ваш пароль успешно изменен!')


def get_group_name(message):
    admin_id = message.from_user.id
    group_name = message.text.strip()
    if group_name:
        bot.send_message(
            admin_id,
            text=(
                "📝 *Шаг 1 из 2:* Создание группы.\n\n"
                f"✅ *Название группы:* `{group_name}` добавлено! 🏫\n\n"
                "👥 *Теперь добавьте список студентов:* \n"
                "_Введите их имена через запятую._"
            ),
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, get_all_students, group_name)


def get_all_students(message, group_name):
    admin_id = message.from_user.id
    student_list = [name.strip() for name in message.text.strip().split(',')]
    if not student_list or student_list == ['']:
        bot.send_message(
            admin_id,
            text="❌ *Ошибка:* Список студентов пустой! 😞\n\nВведите данные ещё раз.",
            parse_mode="Markdown"
        )
        return

    # Создаем группу
    group = Admin.create_new_group(group_name, student_list)

    # Успешное создание
    if group:
        bot.send_message(
            admin_id,
            text=(
                f"🎉 *Группа создана!* 🏫\n\n"
                f"📚 *Название группы:* `{group_name}`\n"
                f"👥 *Список студентов:* {', '.join(student_list)}\n\n"
                "💼 *Что бы вы хотели сделать дальше?*"
            ),
            parse_mode="Markdown",
            reply_markup=bt.admin_main_menu_bt()
        )
    # Ошибка создания
    else:
        bot.send_message(
            admin_id,
            text="❌ *Ошибка при создании группы!* 😞\n\nПопробуйте ещё раз.",
            parse_mode="Markdown"
        )


def main_menu(message):
    user_id = message.from_user.id
    user = User.user_log_in(user_id)
    bot.send_message(
        user_id,
        text=
            "🚀 *Начнем тренировку первого этапа!* 🧬\n\n"
            "📌 *Тема:* _Расчёт числа гамет._ 🔢\n"
            "🎓 Готовы? Тогда начнём!",
        parse_mode="Markdown",
        reply_markup=bt.test_buttons(user, ('Расчет числа гамет', 'gametes_num'))
    )


def gametes_num(message, hetero, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы

    try:
        # Проверка ответа
        if int(user_answer) == 2 ** hetero:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                    "✅ *Правильно!* 🎉\n\n"
                    f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            bot.send_message(
                user_id,
                text=
                    f"❌ *Неправильно!*\n\n"
                    f"✅ *Правильный ответ:* *{2 ** hetero}* 🎯\n\n"
                    "📊 *Совет по решению задачи:*\n"
                    "1. *Посчитайте количество гетерозигот.* 🧬\n"
                    "2. *Возведите 2 в их степень.* ✖️\n\n"
                    "_Попробуйте ещё раз!_ 🔄",
                parse_mode="Markdown"
            )

        # Следующий вопрос
        if count < 5:
            parent, hetero = db.random_parent()
            bot.send_message(
                user_id,
                text=
                    "📊 *Задача:*\n\n"
                    "Каково *количество гамет* организма с генотипом:\n"
                    f"`{parent}`\n\n"
                    "_(Отправьте ответ в виде числа.)_ 🔢\n\n"
                    f"➡️ *Переходим к вопросу {count + 1} из 5.*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(
                message,
                lambda msg: gametes_num(msg, hetero, count + 1, correct_answer)
            )
        else:
            # Завершение теста
            bot.send_message(
                user_id,
                text=
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* *{correct_answer}* *правильных ответов из 5.*",
                parse_mode="Markdown"
            )
            user = User.user_log_in(user_id)

            # Переход к следующему этапу
            if correct_answer == 5:
                bot.send_message(
                    user_id,
                    text=
                        "🌟 *Поздравляем!* 🎉\n\n"
                        "Вы набрали *максимальный балл!* 🏆\n"
                        "Переходите к *следующему этапу.* 🚀",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(user, ('Расчет количества всех детей', 'filio_all_num')))
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(user, ('Расчет числа гамет', 'gametes_num'))
                )
    except ValueError:
        bot.send_message(
            user_id,
            text="❌ *Ошибка ввода!* 😞\n\nПожалуйста, введите число! 🔢",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, lambda msg: gametes_num(msg, hetero, count, correct_answer))


def filio_all_num(message, answer, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы
    print(user_answer)

    try:
        # Проверка правильного ответа
        if int(user_answer) == answer:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                        "✅ *Правильно!* 🎉\n\n"
                        f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            bot.send_message(
                user_id,
                text=
                    f"❌ *Неправильно!*\n\n"
                    f"✅ *Правильный ответ:* `{answer}` 🎯\n\n"
                    "📊 *Совет по решению задачи:*\n"
                    "1. *Посчитайте количество гетерозигот каждого из родителей.* 👩‍🔬👨‍🔬\n"
                    "2. *Возведите 2 в степень количества этих гетерозигот.* ✖️\n\n"
                    "_Попробуйте ещё раз!_ 🔄",
                parse_mode="Markdown"
            )

        # Переход к следующему вопросу
        if count < 5:
            # Генерация новых данных для вопроса
            parent_1, hetero_1, parent_2, hetero_2, number = db.random_parents(6, 8)
            answer = (2 ** hetero_1) * (2 ** hetero_2)

            bot.send_message(
                user_id,
                text=
                    "📊 *Задача:*\n\n"
                    "Каково *количество гибридов (детей)*, полученных при скрещивании:\n\n"
                    f"♀️ *{parent_1}* \n"
                    f"♂️ *{parent_2}* \n\n"
                    "_(Отправьте ответ в виде числа.)_ 🔢",
                parse_mode="Markdown"
            )

            bot.register_next_step_handler(
                message,
                lambda msg: filio_all_num(msg, answer, count + 1, correct_answer)
            )

        # Завершение теста
        else:
            bot.send_message(
                user_id,
                text=
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* `{correct_answer}` *правильных ответов из 5.*",
                parse_mode="Markdown"
            )

            user = User.user_log_in(user_id)

            # Проверка на максимальный балл
            if correct_answer == 5:
                bot.send_message(
                    user_id,
                    text=
                        "🌟 *Поздравляем!* 🎉\n\n"
                        "Вы набрали *максимальный балл!* 🏆\n"
                        "Переходите к *следующему этапу.* 🚀",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расчет количества конкретных детей', 'filio_num')
                    )
                )
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расчет количества всех детей', 'filio_all_num')
                    )
                )
    except ValueError:
        # Обработка некорректного ввода
        bot.send_message(
            user_id,
            text="❌ *Ошибка ввода!* 😞\n\nПожалуйста, введите число! 🔢",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            message,
            lambda msg: filio_all_num(msg, answer, count, correct_answer)
        )


def filio_num(message, answer, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы

    try:
        # Проверка ответа
        if int(user_answer) == answer:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                        "✅ *Правильно!* 🎉\n\n"
                        f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            # Неправильный ответ
            bot.send_message(
                user_id,
                text=
                    f"❌ *Неправильно!* 😞\n\n"
                    f"✅ *Правильный ответ:* `{answer}` 🎯\n\n"
                    "📊 *Рекомендация по расчёту:*\n"
                    "1. *Найдите такие пары признаков, которые являются гетерозиготами у обоих родителей и ребенка одновременно.* 🧬\n"
                    "2. *Перемножьте 2 саму на себя столько же раз, сколько нашли таких совпадений.* ✖️\n\n"
                    "📌 *Пример:*\n\n"
                    "_Родители:_ *АаBb × AaBb*\n\n"
                    "_Ребенок:_ *Aabb*\n\n"
                    "- У всех троих гетерозигота совпадает только по признаку А.*\n"
                    "- Расчет: 2 детей*\n\n"
                    "_Попробуйте ещё раз!_ 🔄",
                parse_mode="Markdown"
            )

        # Переход к следующему вопросу
        if count < 5:
            # Генерация новых данных
            filio_real_num, filio, parent_1, parent_2 = db.filio_nums()
            bot.send_message(
                user_id,
                text=
                    "📊 *Задача:*\n\n"
                    "При скрещивании:\n\n"
                    f"♀️ *{parent_1}* \n"
                    f"♂️ *{parent_2}* \n\n"
                    f"Найдите количество детей с генотипом:\n"
                    f"`{filio}`",
                parse_mode="Markdown"
            )

            # Рекурсивный вызов для следующего вопроса
            bot.register_next_step_handler(
                message,
                lambda msg: filio_num(msg, filio_real_num, count + 1, correct_answer)
            )
        else:
            # Завершение теста
            bot.send_message(
                user_id,
                text=
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* `{correct_answer}` *правильных ответов из 5.*",
                parse_mode="Markdown"
            )

            user = User.user_log_in(user_id)

            # Проверка на максимальный балл
            if correct_answer == 5:
                bot.send_message(
                    user_id,
                    text=
                        "🌟 *Поздравляем!* 🎉\n\n"
                        "Вы набрали *максимальный балл!* 🏆\n"
                        "Переходите к *следующему этапу.* 🚀",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расчёт количества нескольких конкретных детей', 'filio_some_num')
                    )
                )
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расчёт количества конкретных детей', 'filio_num')
                    )
                )
    except ValueError:
        # Обработка ошибок при некорректном вводе
        bot.send_message(
            user_id,
            text="❌ *Ошибка ввода!* 😞\n\nПожалуйста, введите число! 🔢",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            message,
            lambda msg: filio_num(msg, answer, count, correct_answer)
        )


def filio_some_nums(message, result, random_filio_some_num, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы
    try:
        if int(user_answer) == result:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                        "✅ *Правильно!* 🎉\n\n"
                        f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            bot.send_message(
                user_id,
                text=
                    f"❌ *Неправильно!* 😞\n\n"
                    f"✅ *Правильный ответ:* `{result}` 🎯\n\n"
                    "📊 *Совет по анализу признаков:*\n"
                    "1. *Рассматривайте каждую пару признаков отдельно.* 🧬\n"
                    "2. *Проверьте возможность гомо- или гетерозиготы:* 🧐\n"
                    "   - Если в каждой паре возможна комбинация, переходите к следующему шагу.\n\n"
                    "3. *Проверьте законы Менделя:*\n"
                    "   - *2-й закон Менделя:*\n"
                    "     - Ищите признаки, где возможны гомо- и гетерозиготы. *Ставьте 2.*\n"
                    "   - *1-й закон Менделя:*\n"
                    "     - Если все потомки — гетерозиготы, *ставьте 0.*\n\n"
                    "📌 *Пример:*\n\n"
                    "_Родители:_ *АаBB × Аавв*\n\n"
                    "- *Признак A:*  Возможна гомо- и гетерозигота (Аа). *Ставим 2.*\n"
                    "- *Признак B:*  Все потомки — гетерозиготы (Bb). *Ставим 0.*\n\n"
                    "*Результат:* Ответ = _2 × 0 = 0 детей_ 🔢",
                parse_mode="Markdown")
        if count < 5:
            random_filio_some_num = random.choice(
                ['дети со всеми гомозиготными признаками', 'дети со всеми гетерозиготными признаками']
            )

            # Генерация данных в зависимости от условия
            if random_filio_some_num == 'дети со всеми гомозиготными признаками':
                result, parent_1, parent_2 = db.test4_1()
            else:
                result, parent_1, parent_2 = db.test4_2()

            # Новый вопрос
            bot.send_message(
                user_id,
                text=
                    "📊 *Задача:*\n\n"
                    "При скрещивании:\n\n"
                    f"♀️ *{parent_1}* \n"
                    f"♂️ *{parent_2}* \n\n"
                    f"Найдите количество всех детей, соответствующих условию:\n"
                    f"*{random_filio_some_num}*",
                parse_mode="Markdown"
            )

            # Переход к следующему вопросу
            bot.register_next_step_handler(
                message,
                lambda msg: filio_some_nums(
                    msg, result, random_filio_some_num, count + 1, correct_answer
                )
            )
        else:
            # Завершение теста
            bot.send_message(
                user_id,
                text=
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* `{correct_answer}` *правильных ответов из 5.*",
                parse_mode="Markdown"
            )

            user = User.user_log_in(user_id)

            # Проверка на максимальный результат
            if correct_answer == 5:
                bot.send_message(
                    user_id,
                    text=
                        "🌟 *Поздравляем!* 🎉\n\n"
                        "Вы набрали *максимальный балл!* 🏆\n"
                        "Переходите к *следующему этапу.* 🚀",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расщепление по фенотипу', 'segregation_fen')
                    )
                )
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    parse_mode="Markdown",
                    reply_markup=bt.test_buttons(
                        user, ('Расчет количества нескольких конкретных детей', 'filio_some_num')
                    )
                )
    except ValueError:
        # Ошибка при вводе неверных данных
        bot.send_message(
            user_id,
            text=
                "❌ *Ошибка ввода!* 😞\n\n"
                "Пожалуйста, введите число! 🔢",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            message,
            lambda msg: filio_some_nums(
                msg, result, random_filio_some_num, count, correct_answer
            )
        )


def segregation_fen(message, result, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы
    formatted_result = ':'.join(result) if isinstance(result, list) else result
    try:
        # Проверка правильности ответа
        if user_answer == formatted_result:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                        "✅ *Правильно!* 🎉\n\n"
                        f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            # Сообщение с подсказкой
            bot.send_message(
                user_id,
                text=
                    f"❌ *Неправильно!* 😞\n\n"
                    f"✅ *Правильный ответ:* `{formatted_result}` 🎯\n\n"
                    "📝 *Совет по решению задачи:*\n"
                    "1. Возьмите *ручку и тетрадь*. ✏️📒\n"
                    "2. *Распишите полный математический метод:*\n"
                    "   - Выбирайте по *1 паре признаков* из каждого столбика. 🧬\n"
                    "   - При совмещении всех выбранных пар *перемножьте числа* слева от каждой пары. ✖️\n"
                    "3. *Переберите все возможные сочетания.* 🔄\n\n"
                    "📊 *Ответ укажите в формате:* `9:3:3:1`",
                parse_mode="Markdown"
            )

        # Переход к следующему вопросу
        if int(count) < 5:
            parent_1, parent_2, result = db.segregation_fen()
            bot.send_message(
                user_id,
                text=(
                    "📊 *Задача:*\n\n"
                    "При скрещивании:\n\n"
                    f"♀️ *{parent_1}* \n"
                    f"♂️ *{parent_2}* \n\n"
                    "Найдите *соотношение всех фенотипов* данных организмов.\n\n"
                    "📊 *Ответ укажите в формате:* `9:3:3:1`"),
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(
                message,
                lambda msg: segregation_fen(msg, result, count + 1, correct_answer)
            )
        else:
            # Завершение теста
            bot.send_message(
                user_id,
                text=(
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* `{correct_answer}` *правильных ответов из 5.*"),
                parse_mode="Markdown"
            )

            # Проверка результатов и переход к следующему этапу
            user = User.user_log_in(user_id)
            if correct_answer == 5:
                bot.send_message(
                    user_id,
                    text=
                        "🌟 *Поздравляем!* 🎉\n\n"
                        "Вы набрали *максимальный балл!* 🏆\n"
                        "Переходите к *следующему этапу.* 🚀",
                    reply_markup=bt.test_buttons(
                        user, ('Расщепление по генотипу', 'segregation_gen')
                    ),
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    reply_markup=bt.test_buttons(
                        user, ('Расщепление по фенотипу', 'segregation_fen')
                    ),
                    parse_mode="Markdown"
                )

    # Обработка ошибок ввода
    except ValueError:
        bot.send_message(
            user_id,
            text=(
                "❌ *Ошибка ввода\\!* 😞\n\n"
                "Пожалуйста, введите ответ в формате *9\\:3\\:3\\:1* 🔢"),
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            message,
            lambda msg: segregation_fen(msg, result, count, correct_answer)
        )


def segregation_gen(message, result, count=1, correct_answer=0):
    user_id = message.from_user.id
    user_answer = message.text.strip()  # Убираем лишние пробелы

    try:
        # Проверка ответа
        if user_answer == result:
            correct_answer += 1
            if count < 5:
                bot.send_message(
                    user_id,
                    text=
                        "✅ *Правильно!* 🎉\n\n"
                        f"📊 *Переходим к вопросу {count + 1} из 5.*",
                    parse_mode="Markdown"
                )
            else:
                pass
        else:
            # Сообщение с подсказкой
            bot.send_message(
                user_id,
                text=(
                    f"❌ *Неправильно!* 😞\n\n"
                    f"✅ *Правильный ответ:* `{result}` 🎯\n\n"
                    "📝 *Совет по решению задачи:*\n"
                    "1\\. Возьмите *ручку и тетрадь* ✏️📒\n"
                    "2\\. *Распишите все возможные сочетания аллелей по генотипам* 🧬\n"
                    "3\\. *Подсчитайте количество различных комбинаций* 🔄\n\n"
                    "📊 *Ответ укажите в формате:* `1:2:1:2:4:2:1:2:1`"),
                parse_mode="Markdown"
            )

        # Переход к следующему вопросу
        if count < 5:
            parent_1, parent_2, result = db.segregation_gen()
            bot.send_message(
                user_id,
                text=(
                    "📊 *Задача:*\n\n"
                    "При скрещивании:\n\n"
                    f"♀️ *{parent_1}* \n"
                    f"♂️ *{parent_2}* \n\n"
                    "Найдите *соотношение всех генотипов* данных организмов.\n\n"
                    "📊 *Ответ укажите в формате:* `1:2:1:2:4:2:1:2:1`"),
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(
                message,
                lambda msg: segregation_gen(msg, result, count + 1, correct_answer)
            )
        else:
            # Завершение теста
            bot.send_message(
                user_id,
                text=
                    "🎉 *Тест завершён!* 🎓\n\n"
                    f"📊 *Ваш результат:* `{correct_answer}` *правильных ответов из 5.*",
                parse_mode="Markdown"
            )

            # Проверка результатов и переход к следующему этапу
            user = User.user_log_in(user_id)
            if correct_answer == 5:
                if User.is_pro_user(user_id):
                    bot.send_message(
                        user_id,
                        "🎉 *Поздравляем!* 🏆\n\n"
                        "Вы сделали ещё один шаг к званию *великого математика-генетика*! 🧬📚\n"
                        "Продолжайте в том же духе, и скоро Алексей Николаевич будет бояться вас! 💥"
                    )
                    User.increase_exam_pass(user_id)
                else:
                    bot.send_message(user_id, text=(
                            "🌟 *Поздравляем!* 🎉\n\n"
                            "Вы набрали *максимальный балл\\!* 🏆\n"
                            "А также вы полностью прошли экзамен по *математическому методу*\n"
                            "и стали *профессиональным математическим методологом!* 🚀"),
                        reply_markup=bt.main_menu_bt(user_id),
                        parse_mode="Markdown"
                    )
                    User.activate_pro_status(user_id)
                    User.increase_exam_pass(user_id)
                    bot.send_message(user_id, 'Вы приобретаете статус профессионального пользователя!\n'
                                              'Теперь вам доступны все функции сразу: ',
                                     reply_markup=bt.main_menu_bt_pro())
            else:
                bot.send_message(
                    user_id,
                    text=
                        "❌ *Этап не пройден.* 😞\n\n"
                        "Попробуйте ещё раз! 🔄\n"
                        "Нажмите кнопку ниже, чтобы *начать заново.* ⬇️",
                    reply_markup=bt.test_buttons(
                        user, ('Расщепление по генотипу', 'segregation_gen')
                    ),
                    parse_mode="Markdown"
                )

    # Обработка ошибок ввода
    except ValueError:
        bot.send_message(
            user_id,
            text=(
                "❌ *Ошибка ввода!* 😞\n\n"
                "Пожалуйста, введите ответ в формате *1:2:1:2:4:2:1:2:1* 🔢"),
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            message,
            lambda msg: segregation_gen(msg, result, count, correct_answer)
        )


bot.infinity_polling(timeout=999, long_polling_timeout=5)
