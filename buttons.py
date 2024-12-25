from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database import User


def names(all_names):
    kb = InlineKeyboardMarkup(row_width=1)
    get_name = [InlineKeyboardButton(text=f'{name[1]}', callback_data=f'name_{name[0]}') for name in all_names]
    kb.add(*get_name)
    return kb


def phone():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    get_phone = KeyboardButton('Отправить свой номер', request_contact=True)
    kb.add(get_phone)
    return kb


def students_all_groups(groups):
    kb = InlineKeyboardMarkup(row_width=2)
    if not groups:
        kb.add(InlineKeyboardButton(text='Нет доступных групп', callback_data='none'))
        return kb
    for grp in groups:
        get_group = [
            InlineKeyboardButton(text=f'{grp["group_name"]}', callback_data=f'student_exact_group_{grp["group_id"]}')
            ]
        kb.add(*get_group)
    return kb


def all_groups(groups):
    kb = InlineKeyboardMarkup(row_width=2)
    if not groups:
        kb.add(InlineKeyboardButton(text='Нет доступных групп', callback_data='none'))
        return kb
    for grp in groups:
        get_group = [
            InlineKeyboardButton(text=f'{grp["group_name"]}', callback_data=f'exact_group_{grp["group_id"]}'),
            InlineKeyboardButton(text='❌', callback_data=f'delete_gr_{grp["group_id"]}')
        ]
        kb.add(*get_group)
    ok_bt = InlineKeyboardButton(text='Готово', callback_data=f'change_group_complete')
    kb.row(ok_bt)
    return kb


def group_members(all_names, group_id):
    kb = InlineKeyboardMarkup(row_width=1)
    for name in all_names:
        buttons = [
            InlineKeyboardButton(text='❌', callback_data=f'delete_{name}_{group_id}'),
            InlineKeyboardButton(text=f'{name}', callback_data=f'name_{name}')
        ]
        kb.row(*buttons)
    ok_bt = InlineKeyboardButton(text='Готово', callback_data='OK')
    kb.row(ok_bt)
    return kb


def student_group_members(all_names):
    kb = InlineKeyboardMarkup(row_width=1)
    for name in all_names:
        buttons = [
            InlineKeyboardButton(text=f'{name}', callback_data=f'name_{name}')
        ]
        kb.row(*buttons)
    return kb


def admin_main_menu_bt():
    kb = InlineKeyboardMarkup()
    change_pass = InlineKeyboardButton(text='Сменить свой пароль', callback_data='change_pass')
    create_new_group = InlineKeyboardButton(text='Создать новую группу', callback_data='create_new_group')
    change_group_members = InlineKeyboardButton(text='Изменить участников группы', callback_data='change_group_members')
    change_group_photo = InlineKeyboardButton(text='Изменить фото группы', callback_data='change_group_photo')
    kb.row(create_new_group)
    kb.row(change_group_members, change_group_photo)
    kb.row(change_pass)
    return kb


def all_buttons():
    gametes_num = InlineKeyboardButton(text='Расчет числа гамет', callback_data='gametes_num')
    filio_all_num = InlineKeyboardButton(text='Расчет числа гибридов', callback_data='filio_all_num')
    filio_num = InlineKeyboardButton(text='Расчет числа указанных гибридов', callback_data='filio_num')
    filio_some_num = InlineKeyboardButton(text='Расчет числа нескольких гибридов', callback_data='filio_some_num')
    segregation_fen = InlineKeyboardButton(text='Соотношение по фенотипу', callback_data='segregation_fen')
    segregation_gen = InlineKeyboardButton(text='Соотношение по генотипу', callback_data='segregation_gen')
    all_bt = gametes_num, filio_all_num, filio_num, filio_some_num, segregation_fen, segregation_gen
    return all_bt


def main_menu_bt(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start = KeyboardButton('Начать тест')
    profile = KeyboardButton('Мой профиль')
    if User.is_pro_user(user_tg_id=user_id):
        all_functions = KeyboardButton('Показать все этапы')
        kb.row(profile, start)
        kb.row(all_functions)
        return kb
    kb.row(profile, start)
    return kb


def main_menu_bt_pro():
    kb = InlineKeyboardMarkup(row_width=1)
    gametes_num = InlineKeyboardButton(text='Расчет числа гамет', callback_data='gametes_num')
    filio_all_num = InlineKeyboardButton(text='Расчет числа гибридов', callback_data='filio_all_num')
    filio_num = InlineKeyboardButton(text='Расчет числа указанных гибридов', callback_data='filio_num')
    filio_some_num = InlineKeyboardButton(text='Расчет числа нескольких гибридов', callback_data='filio_some_num')
    segregation_fen = InlineKeyboardButton(text='Соотношение по фенотипу', callback_data='segregation_fen')
    segregation_gen = InlineKeyboardButton(text='Соотношение по генотипу', callback_data='segregation_gen')
    kb.add(gametes_num, filio_all_num, filio_num, filio_some_num, segregation_fen, segregation_gen)
    return kb


def test_buttons(user, task):
    kb = InlineKeyboardMarkup(row_width=1)
    task_button = InlineKeyboardButton(text=task[0], callback_data=task[1])
    kb.add(task_button)
    return kb

