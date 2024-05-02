import os
import threading
import time

# Не работает :(
# from docx import Document
# from docx.shared import Pt
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from datetime import datetime, timedelta
from data_base_control import *
import telebot
import sqlite3
import schedule
from telebot.types import InputMediaPhoto

TOKEN = 'token'
GROUP_ID = '-1002033236010'
bot = telebot.TeleBot(TOKEN)

auction_on = {}
user_lots = {}
admins_commands = {
    '1': 'cash — просмотр информации пользователя.\nwarn — выдача предупреждения пользователю.\ninactive — просмотр неактивный постов.',
    '2': 'На вашем уровне доступны все команды, которые присутствуют на уровне ниже, а также:\n\nreport — контроль и обработка входящих жалоб.\nset_balance — установить баланс пользователя.\nunpost — отмена выложенного действующего лота.',
    '3': 'У вас статус — super-admin.\nВсе команды доступны для работы.\nДля добавления новых администаторов '
         'выполняйте работу в Системе Администрирования.'}

admins_status = {
    '1': 'Приветствуем вас! Вы являетесь администратором 1 уровня.\nВаша основная задача - обеспечить порядок и безопасность в нашем приложении. Используйте доступные вам команды для управления пользователями и лотами. Следите за жалобами и обрабатывайте их справедливо.\n\nСпасибо за вашу работу!',
    '2': 'Приветствуем вас! Вы являетесь частью нашей системы поддержки.\nВаша роль - помогать пользователям решать их проблемы и отвечать на вопросы. Будьте вежливы и внимательны к каждому обращению. Спасибо за ваше терпение и профессионализм!',
    '3': 'Добро пожаловать в ряды суперадминистраторов!\n\nВаша ответственность - управлять всеми аспектами нашего приложения. Вы имеете полный доступ ко всем командам и функциям. Помогайте администраторам и системе поддержки и принимайте важные решения. Благодарим вас за ваш вклад в успех нашего приложения!'}

rules_text = ('После окончания торгов, победитель должен выйти на связь с продавцом самостоятельно в течении '
              'суток‼️\nТакже, победитель обязан выкупить лот в течении трех  дней после окончания аукциона.\n\nЧтобы '
              'узнать время окончания аукциона, нажмите на ⏰ в предложенных лотах.\nРаботают только проверенные '
              'продавцы, их отзывы суммарно достигают 10000+ на различных площадках.\nДополнительные фото по товару '
              'можно запросить у продавца лота.\n\nСлучайно сделал ставку — напиши продавцу лота. 😮\nОтправка '
              'почтой: стоимость пересылки указана под фото.\nОтправка осуществляется в течении трёх дней после '
              'оплаты.')

# Клавиатуру back в панеле администрирования
markBackAdm = telebot.types.InlineKeyboardMarkup()
backs_button = telebot.types.InlineKeyboardButton("Назад❕", callback_data='=')
markBackAdm.add(backs_button)

# Клавиатура главного меню(ЛК)
markMain = telebot.types.InlineKeyboardMarkup()
main_button = telebot.types.InlineKeyboardButton("Главное меню❕", callback_data='main')
markMain.add(main_button)


# help keyboard(ЛК)
markHELP = telebot.types.InlineKeyboardMarkup()
my_lots_button = telebot.types.InlineKeyboardButton("Мои лоты🎲", callback_data='lots')
rules_button = telebot.types.InlineKeyboardButton("Правила📝", callback_data='rules')
help_button = telebot.types.InlineKeyboardButton("Помощь📍", callback_data='help')
cash_button = telebot.types.InlineKeyboardButton("Мой аккаунт💵", callback_data='personal')


markHELP.row(my_lots_button, cash_button)
markHELP.row(rules_button, help_button)

# admins keyboard
markAdmins = telebot.types.InlineKeyboardMarkup()
commands_button = telebot.types.InlineKeyboardButton("Команды👨🏼‍💻", callback_data='commands')
status_button = telebot.types.InlineKeyboardButton("Статус👑", callback_data='status')
system_button = telebot.types.InlineKeyboardButton("Админ.система💬", callback_data='system')
markAdmins.row(commands_button, status_button)
markAdmins.add(system_button)


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['warn'])
def warning(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        bot.send_message(message.chat.id,
                         "Введите ID пользователя или перешлите его сообщение, а затем укажите причину предупреждения в формате: ID_пользователя Причина")
        bot.register_next_step_handler(message, process_warning)


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['orders_win'])
def orders_win(message):
    order_winning_names = get_winning_names_lots()

    if order_winning_names:

        markup = telebot.types.InlineKeyboardMarkup()
        for name in order_winning_names:
            button = telebot.types.InlineKeyboardButton(name[0], callback_data=f'/' + name[0])
            markup.add(button)

        bot.send_message(message.chat.id, "Выберите лот для просмотра деталей:", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "Победившие лоты отсутствуют.")


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['set_balance'])
def set_new_balance(message):
    if message.from_user.id == 626220085:
        bot.send_message(message.chat.id,
                         "Введите ID пользователя или перешлите его сообщение, а затем укажите сумму для уставноление баланса в формате: ID_пользователя Сумма")
        bot.register_next_step_handler(message, set_balance)


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['inactive'])
def inactive_auctions(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':

        result = name_inactive()
        names = [row[0] for row in result]

        keyboard = []
        for button_label in names:
            keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='5' + button_label)])
        markInactive = telebot.types.InlineKeyboardMarkup(keyboard)

        bot.send_message(message.chat.id,
                         "Выберите интересующий вас пост:", reply_markup=markInactive)


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['cash'])
def check_user_cash(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        bot.send_message(message.chat.id,
                         "Введите ID пользователя или перешлите его сообщение для просмотра баланса.")
        bot.register_next_step_handler(message, process_check_cash)


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['reports'])
def reports_check(message):
    reports = data_reports()

    if reports:
        markup = telebot.types.InlineKeyboardMarkup()
        for i, report in enumerate(reports):
            user_id, complaint = report
            button = telebot.types.InlineKeyboardButton(f"{user_id}",
                                                        callback_data=f'q{i}')
            markup.add(button)

        bot.send_message(message.chat.id,
                         "Список *жалоб* предоставлен ниже.\nДля обработки жалобы нажмите на любую из них.",
                         reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Жалобы отсутствуют.")


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['check'])
def check_auctions(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':

        results = select_all_auction()

        if results:
            keyboard = []
            lot_names = [row[0] for row in results]
            for button_label in lot_names:
                keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='9' + button_label)])

            markLots = telebot.types.InlineKeyboardMarkup(keyboard)

            bot.send_message(message.chat.id, f"Выберите лот для подтверждения и публикации:", reply_markup=markLots)
        else:
            bot.send_message(message.chat.id, "Нет доступных лотов для публикации.")


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['schedule_post'])
def schedule_post(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':

        results = select_all_auction()

        if results:
            keyboard = []
            lot_names = [row[0] for row in results]
            for button_label in lot_names:
                keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='9' + button_label)])

            markLots = telebot.types.InlineKeyboardMarkup(keyboard)

            bot.send_message(message.chat.id, f"Выберите лот для подтверждения и публикации:", reply_markup=markLots)
        else:
            bot.send_message(message.chat.id, "Нет доступных лотов для публикации.")


@bot.message_handler(commands=['unpost'])
def personal_account(message):
    bot.send_message(message.chat.id,
                     "Для остановки аукциона пришлите, пожалуйста, пост из канала.\n*Внимание!* С вашего счета будет списано 5% от конечной стоимости лота.",
                     parse_mode='Markdown')
    bot.register_next_step_handler(message, process_auction_message, message.from_user.id)


@bot.message_handler(commands=['start'])
def personal_account(message):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM personal_account WHERE user_id=?", (message.from_user.id,))
    print(message.from_user.id)
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute(
            "INSERT INTO personal_account (user_id, warn, money, successful_transactions) VALUES (?, ?, ?, ?)",
            (message.from_user.id, 0, 0, 0))
        conn.commit()

    conn.close()

    bot.send_message(message.chat.id,
                     "Добро пожаловать в ваш *личный кабинет*! 👋🏻\n\nЯ предоставлю вам информацию по выбранным лотам, помогу регулировать ход аукциона, а так же буду следить за накопленными балами.\n\nУдачных торгов!",
                     reply_markup=markHELP, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.chat.id == -1002077468713, commands=['ahelp'])
def admins_info(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать в панель *администратора*!\nДля уточнения доступных команд и вашего уровня воспользуйтесь кнопками ниже.",
                     parse_mode='Markdown', reply_markup=markAdmins)


@bot.callback_query_handler(func=lambda call: True)
def show_auction_duration(call):
    print(call.data)

    if call.data[0] == '0':

        result = get_count_auction(call.data[1:])

        if result and result[0] > 0:
            pass
        else:
            bot.answer_callback_query(call.id, "Данный лот уже недействителен.")
            return

        auction = get_auction_info(call.data[1:])

        if auction:
            user_chat_id = call.from_user.id
            send_auction_to_user(user_chat_id, auction)
            bot.answer_callback_query(call.id, "Дополнительная информация в личных сообщения.💬")

        else:
            pass


    elif call.data == 'system':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Система администрирования предназначена для контроля и управления административными функциями вашего приложения. Ниже приведены инструкции по использованию и рекомендации по повышению вашего уровня администрирования:\n\nИспользование команд: Вы можете использовать различные команды для управления пользователями, лотами, жалобами и другими административными функциями. Доступные команды зависят от вашего текущего уровня администрирования.\n\nПовышение уровня: Ваш уровень администрирования определяет доступные вам команды и функции. Чтобы повысить свой уровень, покажите свою эффективность и ответственность в выполнении административных обязанностей.\n\nРабота с жалобами: Обрабатывайте входящие жалобы от пользователей справедливо и своевременно. Это поможет поддерживать порядок и безопасность в вашем приложении.\n\nОбучение и обновление: Следите за обновлениями и новыми функциями в Системе администрирования. Постоянное обучение поможет вам эффективнее выполнять свои обязанности и повышать свой профессиональный уровень.", reply_markup=markBackAdm, parse_mode='Markdown')


    elif call.data == 'status':
        lvl = admins_coomands(call.from_user.id)
        text_lvl = admins_status.get(str(lvl[0]))
        print(text_lvl)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text_lvl, reply_markup=markBackAdm, parse_mode='Markdown')


    elif call.data == '=':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Добро пожаловать в панель *администратора*!\nДля уточнения доступных команд и вашего уровня воспользуйтесь кнопками ниже.',
                              reply_markup=markAdmins, parse_mode='Markdown')


    elif call.data == 'commands':
        lvl = admins_coomands(call.from_user.id)
        text_lvl = admins_commands.get(str(lvl[0]))
        print(text_lvl)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'На вашем уровне администрирования доступны следующие команды:\n\n{text_lvl}',
                              reply_markup=markBackAdm, parse_mode='Markdown')


    elif call.data[0] == '1':

        result = get_count_auction(call.data[1:])

        if result and result[0] > 0:
            pass
        else:
            bot.answer_callback_query(call.id, "Данный лот уже недействителен.")
            return

        bot.answer_callback_query(call.id, "Удачного торга.😎")
        user_chat_id = str(call.message.chat.id)
        if user_chat_id in auction_on.get(call.data, {}):
            current_bet = auction_on[call.data[1:]][user_chat_id]

            bot.send_message(call.message.chat.id, f"Введите ставку, которая больше текущей {current_bet}:")
            bot.register_next_step_handler(call.message, process_bet_step, call.data, current_bet)

        else:
            current_bet = max(auction_on[call.data[1:]].values())
            bot.send_message(call.message.chat.id, f"Текущая ставка *{current_bet}* BYN\nВведите вашу ставку :",
                             parse_mode='Markdown')
            bot.register_next_step_handler(call.message, process_bet_step, call.data, call.data[0])


    elif call.data[0] == '3':

        result = get_count_auction(call.data[1:])

        if result and result[0] > 0:
            pass
        else:
            bot.answer_callback_query(call.id, "Данный лот уже недействителен.")
            return

        check_status = commission_lot(call.data[1:], call.from_user.id)
        if not check_status:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='На вашем балансе недостаточно средств для реализации лота.\nПополните баланс!',
                                  reply_markup=markMain, parse_mode='Markdown')
        else:

            auction = get_auction_info(call.data[1:])
            send_auction_to_channel(auction)
            update_auctions_date(1, call.data[1:])

            bot.answer_callback_query(call.id,
                                      "Лот успешно опубликован✅\n\nС вашего счета была снята комиссия за публикацию.")


    elif call.data[0] == '4':

        bot.answer_callback_query(call.id, "Медиафайлы были высланы.📸")
        photo_id = find_photo_by_name(call.data[1:])
        bot.send_photo(call.message.chat.id, photo=photo_id)


    elif call.data[0] == '5':

        auction = get_inactive_auction_info(call.data[1:])
        start_price, end_price, seller_link, location, description, start_time, end_time, name, post = auction
        info = f"*Название:* {name}\n*Стартовая цена:* {start_price} BYN\n*Моментальная покупка:* {end_price} BYN\n*Ссылка на продавца:* {seller_link}\n*Местоположение:* {location}\n*Описание:* {description}\n\nВнимание! Проверьте нахождение фото в БД."

        markInactivePost = telebot.types.InlineKeyboardMarkup()
        main_button = telebot.types.InlineKeyboardButton("Удалить", callback_data='-' + name)
        back_button = telebot.types.InlineKeyboardButton("Назад", callback_data='inactive_back')
        post_button = telebot.types.InlineKeyboardButton("Выложить", callback_data='+' + name)
        markInactivePost.row(main_button, back_button)
        markInactivePost.add(post_button)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=info,
                              reply_markup=markInactivePost, parse_mode='Markdown')


    elif call.data[0] == '6':

        markBet = telebot.types.InlineKeyboardMarkup()
        main_button = telebot.types.InlineKeyboardButton("Главное меню❕", callback_data='main')
        back_button = telebot.types.InlineKeyboardButton("Назад", callback_data='7')

        markBet.row(main_button, back_button)
        delete_user_lots(call.from_user.id, call.data[1:])

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Лот успешно удален из истории.\n\nВы можете продолжить очищать историю, вернушись назад, либо выйти в главное меню.",
                              reply_markup=markBet)


    elif call.data[0] == '7':

        lots_user = select_lots_from_user(call.from_user.id)

        keyboard = []
        lots_list = [lot[0] for lot in lots_user]
        for button_label in lots_list:
            keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='6' + button_label)])
        markLots = telebot.types.InlineKeyboardMarkup(keyboard)
        markLots.row(telebot.types.InlineKeyboardButton("Главное меню❕", callback_data='main'),
                     telebot.types.InlineKeyboardButton("Назад", callback_data='lots'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите лот, который хотите удалить из вашей истории.", reply_markup=markLots)


    elif call.data[0] == '8':

        result = get_auction_info_unpost(call.data[1:])

        markBet = telebot.types.InlineKeyboardMarkup()
        main_button = telebot.types.InlineKeyboardButton("Главное меню❕", callback_data='main')
        back_button = telebot.types.InlineKeyboardButton("Назад", callback_data='lots')

        markBet.row(main_button, back_button)

        if result and result[0] > 0:

            result = select_lots_lot(call.from_user.id, call.data[1:])

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Лот: *{call.data[1:]}*\nВаша последняя ставка: *{result[0][0]}*\n\nУдачных торгов!",
                                  reply_markup=markBet, parse_mode='Markdown')
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Данный лот уже недействителен.\nДля удаления лота вернитесь назад.\nДля связи с тех.поддержкой вернитесь на главное меню.",
                                  reply_markup=markBet)

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lots_lot WHERE user_id = ? AND lots = ?",
                       (call.from_user.id, call.data[1:]))
        result = cursor.fetchall()
        conn.close()
        print(result)


    elif call.data[0] == '9':

        bot.answer_callback_query(call.id, text="Процесс отправки информации..")
        bot.send_message(call.message.chat.id, f"Вы выбрали лот — {call.data[1:]}. Ожидайте подгрузку информации.",
                         parse_mode='Markdown')
        process_confirm_step(call.message, call.data[1:])


    elif call.data == 'personal':

        existing_user = select_info_personal_acc(str(call.from_user.id))

        money, warn, successful_transactions = existing_user
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Информация про ваш личный аккаунт.👨🏼‍💻\n\n*‍Баланс*: {money} BYN.\n*Предупреждения*: {warn}.\n*Успешные лоты*: {successful_transactions}.\n\nПри некорректной информации просьба связаться с тех.поддержкой.',
                              reply_markup=markMain, parse_mode='Markdown')


    elif call.data[0] == 'q':

        index = int(call.data[1:])
        reports = fetch_reports()

        if 0 <= index < len(reports):

            id, user_id, report_text = reports[index]
            markReports = telebot.types.InlineKeyboardMarkup()
            main_button = telebot.types.InlineKeyboardButton("Вернуться к жалобам❕", callback_data='back_reports')
            answear_button = telebot.types.InlineKeyboardButton("Обработать⚡️",
                                                                callback_data=f'a{user_id}:{id}')

            markReports.add(main_button, answear_button)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,

                                  text=f'Жалоба от пользователя *{user_id}* :\n\n{report_text}',
                                  reply_markup=markReports, parse_mode='Markdown')


        else:
            bot.answer_callback_query(call.id, text="Жалоба не найдена.")


    elif call.data[0] == 'a':

        user_id, id_reports = call.data[1:].split(':')
        result = count_reports(id_reports)

        if result and result[0] > 0:
            pass
        else:
            bot.answer_callback_query(call.id,
                                      "Данная жалоба уже была обработана.\nВернитесь на станицу со списком жалоб.")
            return

        bot.answer_callback_query(call.id, text="Напишите ответ на жалобу.")

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT complaint FROM reports WHERE id=?", (id_reports,))
        report_text = cursor.fetchone()
        conn.close()

        bot.register_next_step_handler(call.message, lambda message: send_answer(message, user_id, report_text[0]))
        bot.send_message(call.message.chat.id, "Введите ответ на жалобу:")


    elif call.data == 'back_reports':

        reports = data_reports()

        if reports:
            markUP = telebot.types.InlineKeyboardMarkup()
            for i, report in enumerate(reports):
                print(i)
                user_id, complaint = report
                button = telebot.types.InlineKeyboardButton(f"{user_id}",
                                                            callback_data=f'q{i}')
                markUP.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Список *жалоб* предоставлен ниже.\nДля обработки жалобы нажмите на любую из них.",
                                  reply_markup=markUP, parse_mode='Markdown')

        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Жалобы отсутствуют.", parse_mode='Markdown')


    elif call.data == 'rules':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=rules_text, reply_markup=markMain)

    elif call.data == 'main':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Добро пожаловать в ваш *личный кабинет*! 👋🏻\n\nЯ предоставлю вам информацию по выбранным лотам, помогу регулировать ход аукциона, а так же буду следить за накопленными балами.\n\nУдачных торгов!",
                              reply_markup=markHELP, parse_mode='Markdown')

    elif call.data == 'info':
        bot.answer_callback_query(call.id,
                                  'После окончания торгов, победитель должен выйти на связь с продавцом самостоятельно в течение суток.\nПобедитель обязан выкупить лот в течение трех дней, после окончания аукциона.',
                                  show_alert=True)

    elif call.data == 'lots':
        user_id = str(call.from_user.id)
        result, lots_user = lots_count(user_id)

        if result[0][0] > 0:

            keyboard = []
            lots_list = [lot[0] for lot in lots_user]
            for button_label in lots_list:
                keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='8' + button_label)])
            markLots = telebot.types.InlineKeyboardMarkup(keyboard)
            markLots.row(telebot.types.InlineKeyboardButton("Главное меню❕",
                                                            callback_data='main'),
                         telebot.types.InlineKeyboardButton("Удалить лот.",
                                                            callback_data='7'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваши лоты представлены ниже.", reply_markup=markLots)

        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваши лоты отсутсвуют.\nСамое время — играть👑", reply_markup=markMain)


    elif call.data == 'post':

        markInactivePost = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton("Назад", callback_data='inactive_back')
        markInactivePost.add(back_button)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите время завершения аукциона.',
                              reply_markup=markInactivePost, parse_mode='Markdown')


    elif call.data == 'inactive_back':
        result = name_inactive()
        names = [row[0] for row in result]

        keyboard = []
        for button_label in names:
            keyboard.append([telebot.types.InlineKeyboardButton(button_label, callback_data='5' + button_label)])
        markInactive = telebot.types.InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите интересующий вас пост:",
                              reply_markup=markInactive, parse_mode='Markdown')

    elif call.data == 'winners_back':
        order_winning_names = get_winning_names_lots()

        if order_winning_names:
            markup = telebot.types.InlineKeyboardMarkup()
            for name in order_winning_names:
                button = telebot.types.InlineKeyboardButton(name[0], callback_data=f'/' + name[0])
                markup.add(button)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Выберите лот для просмотра деталей:", reply_markup=markup, )
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Заявления на передачу прав *отсутствуют*.", parse_mode='Markdown')


    elif call.data == 'help':
        bot.answer_callback_query(call.id, "Тех.поддержка AuctionBot.")
        bot.send_message(call.message.chat.id, "Наша команда поддержки готова вам помощь.\nОпишите вашу проблему:")
        bot.register_next_step_handler(call.message, process_help_description)


    elif call.data[0] == '+':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите время, в которое пост будет деактивирован.', parse_mode='Markdown')
        bot.register_next_step_handler(call.message, post_inactive_lots, call.data[1:])


    elif call.data[0] == '-':
        delete_inactive_accounts(call.data[1:])

        markInactivePost = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton("Назад", callback_data='inactive_back')
        markInactivePost.add(back_button)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Ауцион успешно удален.',
                              reply_markup=markInactivePost, parse_mode='Markdown')


    elif call.data[0] == '?':

        try:
            bot.answer_callback_query(call.id, 'Фото лота было выслано.✅')
            photo_id = find_photo_by_name(call.data[1:])
            bot.send_photo(call.message.chat.id, photo=photo_id)
        except:
            bot.answer_callback_query(call.id, 'Фото лота недоступно либо было удалено.🚫')


    elif call.data[0] == '2':

        bot.answer_callback_query(call.id, "Права на лот были успешно переданы.✅")

        markType = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton("Назад🚫", callback_data='winners_back')
        markType.add(back_button)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Вы успешно зарегистрировали передачу права на лот.\nДля просмотра других лотов вернитесь назад.",
                              reply_markup=markType, parse_mode='Markdown')

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name_lot, price_win FROM order_winning WHERE name_lot=?", (call.data[2:],))
        user_id, name_lot, price_win = list(cursor.fetchone())
        conn.close()

        # order_win(user_id, name_lot, price_win, call.data[1:2]) не работает :(


    elif call.data[0] == '/':

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name_lot, price_win FROM order_winning WHERE name_lot=?", (call.data[1:],))
        user_id, name_lot, price_win = list(cursor.fetchone())

        markType = telebot.types.InlineKeyboardMarkup()
        type_button_1 = telebot.types.InlineKeyboardButton("Ювелирный💍", callback_data='2j' + call.data[1:])
        type_button_2 = telebot.types.InlineKeyboardButton("Исторически ценный🗿", callback_data='2h' + call.data[1:])
        type_button_3 = telebot.types.InlineKeyboardButton("Стандартный📍", callback_data='2b' + call.data[1:])
        back_button = telebot.types.InlineKeyboardButton("Назад🚫", callback_data='winners_back')
        photo_button = telebot.types.InlineKeyboardButton('Фото лота📸', callback_data='?' + name_lot)

        markType.row(type_button_1, type_button_2)
        markType.add(type_button_3)
        markType.row(back_button, photo_button)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Информация по лоту:\n\nКлиент: *{user_id}*\nНазвание лота: *{name_lot}*\nЦена выигрыша: *{price_win}*\n\n\nВыберите тип лота для реализации документа.🧾\n\n*Внимание!* При выборе типа вы автоматически передаете право владения победителю.",
                              reply_markup=markType, parse_mode='Markdown')
        conn.close()



    elif call.data[0] == '*':
        auction_name, winning_bid = call.data.split(':')[1:]
        if check_order_existence(call.from_user.id, auction_name, winning_bid):
            bot.answer_callback_query(call.id, 'Этот лот уже был отправлен на проверку.📝')

        else:
            bot.answer_callback_query(call.id, 'Заявление оформлено.\nС вами свяжется администрация.👨🏼‍💻')
            insert_order(call.from_user.id, auction_name, winning_bid)


    else:

        name_lot = call.data
        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT start_time, end_time FROM auctions WHERE name=?", (name_lot,))
        row = cursor.fetchone()
        conn.close()

        if row is not None:

            start_time, end_time = row
            start_time = start_time.split('.')[0]
            end_time = end_time.split('.')[0]
            duration_text = f"Время начала: {start_time}\nВремя окончания: {end_time}"
            bot.answer_callback_query(call.id, duration_text)

        else:
            bot.answer_callback_query(call.id, "Данный лот уже недействителен.")


# Не работает :(
# def order_win(user_id, name_lot, price_win, type_of_lot):
#
#     conn = sqlite3.connect('auction_data.db')
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM order_winning WHERE user_id=? AND name_lot=?", (user_id, name_lot))
#     conn.commit()
#     conn.close()
#
#     doc = Document()
#
#     lot_types = {'j': 'Ювелирный', 'h': 'Исторечски ценный'}
#     lot_type = lot_types.get(type_of_lot, 'Стандарт')
#
#     style = doc.styles['Normal']
#     font = style.font
#     font.name = 'Times New Roman'
#     font.size = Pt(12)
#
#     title = doc.add_heading('Документ о передаче лота', level=1)
#     title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
#
#     doc.add_paragraph(f'Имя: {user_id}', style='BodyText')
#     doc.add_paragraph(f'Наименование лота: {name_lot}', style='BodyText')
#     doc.add_paragraph(f'Цена: {price_win}', style='BodyText')
#     doc.add_paragraph(f'Тип лота: {lot_type}', style='BodyText')
#
#     doc.save(f'lot_{name_lot}_document_.docx')


def commission_lot(name, user_id):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT money FROM personal_account WHERE user_id=?", (user_id,))
    money_check = cursor.fetchone()

    cursor.execute("SELECT end_price FROM auctions WHERE name=?", (name,))
    end_price = cursor.fetchone()[0]
    end_price_check = float(end_price) * 0.05

    conn.close()

    if money_check[0] < end_price_check:
        return False
    else:
        new_balance = money_check[0] - end_price_check
        update_personal_account(new_balance, user_id)
        return True


def post_inactive_lots(message, name):
    current_time = datetime.now().strftime('%H:%M')
    end_time_str = message.text

    if current_time < end_time_str < '23:59':

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inactive_auctions WHERE name=?", (name,))
        rows = get_inactive_auction_info(name)

        data_to_insert = [list(row) for row in rows]

        start_price, end_price, seller_link, location, description, start_time, end_time, name, post = data_to_insert[0]
        cursor.execute("INSERT INTO auctions (start_price, end_price, seller_link, location, description, start_time, "
                       "end_time, name, post) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (start_price, end_price,
                                                                                    seller_link, location,
                                                                                    description, current_time,
                                                                                    end_time_str, name, 0))
        conn.commit()
        conn.close()

        button = telebot.types.InlineKeyboardButton("Подтвердить.✅", callback_data="3" + name)
        keyboard = telebot.types.InlineKeyboardMarkup([[button]])
        bot.send_message(message.chat.id,
                         "Для публикации поста нажмите на кнопку ниже.\n\n*Внимание!*\nНе забудьте проверить наличие надлежащих фото для поста в БД.",
                         reply_markup=keyboard, parse_mode='Markdown')

        delete_inactive_accounts(name)

    elif end_time_str > '23:59':
        bot.send_message(message.chat.id,
                         "Время не может быть позднее 23:59. Пожалуйста, введите корректное время.")
        bot.register_next_step_handler(message, post_inactive_lots, name)

    else:
        bot.send_message(message.chat.id, 'Время введено некорректно.\nВведите значение снова.')
        bot.register_next_step_handler(message, post_inactive_lots, name)


def process_help_description(message):
    add_reports(message.from_user.id, message.text)

    bot.send_message(message.chat.id,
                     "Спасибо!\nВаша проблема была *успешно* зарегистрирована.\n\nЖалоба передана на обработку, с вами свяжится администрация.",
                     parse_mode='Markdown')


def process_bet_step(message, lot_name, current_bet):
    print(message)
    try:
        markGp = telebot.types.InlineKeyboardMarkup()
        bet_button_again = telebot.types.InlineKeyboardButton("Сделать новую ставку", callback_data=lot_name)
        markGp.add(bet_button_again)

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT start_price, end_price FROM auctions WHERE name=?", (lot_name[1:],))
        start_price_tuple, end_price = cursor.fetchone()
        conn.close()

        bet = float(message.text)
        start_price = start_price_tuple if start_price_tuple else 0.0
        current_bet = max(value for value in auction_on[lot_name[1:]].values())

        if bet > end_price:
            bot.send_message(message.chat.id,
                             f"Ваша ставка превышает конечную цену *{end_price}*.\nПожалуйста, введите корректную ставку.",
                             parse_mode='Markdown')
            bot.register_next_step_handler(message, process_bet_step, lot_name, current_bet)

        elif bet > float(current_bet):
            users_to = [user_id for user_id, user_bet in auction_on[lot_name[1:]].items() if float(user_bet) < bet]

            for user_chat_id in users_to:
                if user_chat_id != str(message.chat.id):
                    try:
                        bot.send_message(user_chat_id,
                                         f"Ваша ставка на лот '{lot_name[1:]}' была перебита.\nТекущая стоимость: *{bet}*",
                                         reply_markup=markGp, parse_mode='Markdown')
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        continue

            markup = telebot.types.InlineKeyboardMarkup()
            make_bet_button = telebot.types.InlineKeyboardButton("Новая ставка", callback_data=lot_name)
            markup.add(make_bet_button)

            conn = sqlite3.connect('auction_data.db')
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM lots_lot WHERE user_id = ? AND lots = ?",
                           (str(message.chat.id), lot_name[1:]))
            row_count = cursor.fetchone()[0]

            if row_count > 0:

                cursor.execute("UPDATE lots_lot SET end_price = ? WHERE user_id = ? AND lots = ?",
                               (bet, str(message.chat.id), lot_name[1:]))
            else:

                cursor.execute("INSERT INTO lots_lot (user_id, lots, end_price) VALUES (?, ?, ?)",
                               (str(message.chat.id), lot_name[1:], bet))

            conn.commit()

            auction_on[lot_name[1:]][str(message.chat.id)] = bet

            cursor.execute("INSERT INTO bids_history (lot_name, bidder_id, bid_amount) VALUES (?, ?, ?)",
                           (lot_name[1:], message.from_user.id, bet))
            conn.commit()
            conn.close()

            bot.send_message(message.chat.id, f"Ставка в размере *{bet}* принята.", parse_mode='Markdown',
                             reply_markup=markup)

        else:
            bot.send_message(message.chat.id,
                             f"Ставка должна быть больше текущей *{current_bet}*.\nПожалуйста, введите корректную ставку.",
                             parse_mode='Markdown')
            bot.register_next_step_handler(message, process_bet_step, lot_name, current_bet)

    except:
        bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение для ставки.")
        bot.register_next_step_handler(message, process_bet_step, lot_name, current_bet)


def process_check_cash(message):
    user_id = message.forward_from.id if message.forward_from and message.forward_from.id else message.text
    existing_user = select_info_personal_acc(user_id)
    if existing_user:
        money, warn, successful_transactions = existing_user
        text = f'Информация про аккаунт пользователя👨🏼‍💻:\n\n*‍Баланс*: {money} BYN.\n*Предупреждения*: {warn}.\n*Успешные лоты*: {successful_transactions}.'
    else:
        text = 'ID в базе данных нет.\nПроверьте правильность и пришлите снова.'
        bot.register_next_step_handler(message, process_check_cash)
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode='Markdown')


def process_warning(message):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    user_id = None
    parts = message.text.split(maxsplit=1)

    if message.forward_from and message.forward_from.id:

        user_id = message.forward_from.id
        bot.send_message(message.chat.id,
                         f"Пришлите сообщение с *причиной* предупреждения для пользователя с ID {user_id}.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, lambda msg: process_reason(msg, user_id))

    else:
        try:
            user_id_or_info = parts[0]
            if user_id_or_info.isdigit():
                user_id = int(user_id_or_info)
            else:
                bot.send_message(message.chat.id,
                                 "Некорректный формат. Введите ID пользователя или перешлите его сообщение.")
                conn.close()
                bot.register_next_step_handler(message, process_warning)
                return
            reason = parts[1]

            cursor.execute("SELECT warn FROM personal_account WHERE user_id=?", (user_id,))
            warning_count = cursor.fetchone()

            if warning_count is not None:
                warning_count = warning_count[0]
            else:
                bot.send_message(message.chat.id,
                                 f"Пользователь с ID {user_id} не существует.\nПроверьте правильно введенного ID.")
                bot.register_next_step_handler(message, process_warning)
                conn.close()
                return

            cursor.execute("UPDATE personal_account SET warn = ? WHERE user_id = ?",
                           (float(warning_count) + 1, user_id))
            conn.commit()
            bot.send_message(message.chat.id, f"Пользователь с ID {user_id} предупрежден. Причина: {reason}")
            bot.send_message(user_id, f"Вам было выдано предупреждение.\nПричина: *{reason}*", parse_mode='Markdown')
            add_warning(user_id, reason, message.from_user.id)

        except:
            bot.send_message(message.chat.id, f"Проверьте формат введенных данных.\nДалее пришлите снова.")
            bot.register_next_step_handler(message, process_warning)

    conn.close()


def set_balance(message):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    user_id = None
    parts = message.text.split(maxsplit=1)

    if message.forward_from and message.forward_from.id:
        user_id = message.forward_from.id
        bot.send_message(message.chat.id,
                         f"Пришлите новый баланс для пользователя с ID {user_id}.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, lambda msg: process_balance(msg, user_id))

    else:
        try:
            user_id_or_info = parts[0]
            if user_id_or_info.isdigit():
                user_id = int(user_id_or_info)
            else:
                bot.send_message(message.chat.id,
                                 "Некорректный формат. Введите ID пользователя или перешлите его сообщение.")
                conn.close()
                bot.register_next_step_handler(message, process_warning)
                return
            balance = parts[1]

            cursor.execute("UPDATE personal_account SET money = ? WHERE user_id = ?",
                           (float(balance), user_id))
            conn.commit()
            bot.send_message(message.chat.id, f"Баланс пользователя с ID {user_id} успешно установлен.")
            bot.send_message(user_id, f"Ваш баланс был изменен на {balance}.")

        except:
            bot.send_message(message.chat.id, f"Проверьте формат введенных данных.\nДалее пришлите снова.")
            bot.register_next_step_handler(message, process_warning)

    conn.close()


def process_balance(message, user_id):
    try:
        new_balance = float(message.text)
        update_personal_account(new_balance, user_id)

        bot.send_message(message.chat.id, f"Баланс пользователя с ID {user_id} успешно установлен.")
        bot.send_message(user_id, f"Ваш баланс был изменен на {new_balance}.")

    except:
        bot.send_message(message.chat.id, "Некорректный формат. Пожалуйста, введите число.")
        bot.register_next_step_handler(message, lambda msg: process_balance(msg, user_id))


def process_reason(message, user_id):
    reason = message.text.strip()
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT warn FROM personal_account WHERE user_id=?", (user_id,))
    warning_count = cursor.fetchone()
    try:
        if warning_count is not None:
            warning_count = warning_count[0]
        else:
            bot.send_message(message.chat.id,
                             f"Пользователь с ID {user_id} не существует.\nПроверьте наличие регистрации у пользователя и перешлите сообщение снова.")
            bot.register_next_step_handler(message, process_warning)

        cursor.execute("UPDATE personal_account SET warn = ? WHERE user_id = ?", (warning_count + 1, user_id))
        conn.commit()

        bot.send_message(message.chat.id, f"Пользователь с ID {user_id} был предупрежден. Причина: {reason}")
        add_warning(user_id, reason, message.from_user.id)
        bot.send_message(user_id, f"Вам было выдано предупреждение.\nПричина: *{reason}*", parse_mode='Markdown')
        if warning_count + 1 >= 3:
            bot.send_message(message.chat.id,
                             f"Пользователь с ID {user_id} был забанен за получение 3 предупреждений.")

        conn.close()
    except:
        pass
    conn.close()


def schedule_post_time(message):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, start_price, end_price, seller_link, location, description, start_time, end_time FROM auctions WHERE name=?",
        (message.text,))
    results = cursor.fetchall()
    conn.close()

    if results:
        current_time = datetime.now().time().strftime('%H:%M')
        max_time = '23:59'

        bot.send_message(message.chat.id,
                         f"Введите время в формате ЧЧ:ММ, не ранее {current_time} и не позднее {max_time}:")
        bot.register_next_step_handler(message, process_time, results)
    else:
        bot.send_message(message.chat.id, "Лот не найден в базе данных.")
        bot.register_next_step_handler(message, schedule_post_time)


def process_time(message, results):
    print(results)
    time_str = message.text

    current_time = datetime.now().strftime('%H:%M')
    if time_str <= current_time:
        bot.send_message(message.chat.id,
                         f"Время должно быть позже текущего времени ({current_time}). Пожалуйста, введите корректное время.")
        bot.register_next_step_handler(message, process_time, results)
    elif time_str > '23:59':
        bot.send_message(message.chat.id, "Время не может быть позднее 23:59. Пожалуйста, введите корректное время.")
        bot.register_next_step_handler(message, process_time, results)
    else:
        auction_info = results[0]
        schedule.every().day.at(time_str).do(schedule_post_group, auction_info)
        bot.send_message(message.chat.id, f"Лот {results[0]} будет опубликован в *{time_str}*.", parse_mode='Markdown')


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def schedule_post_group(auction):
    name, start_price, end_price, seller_link, location, description, start_time, end_time = auction
    info = f"*Название:* {name}\n*Стартовая цена:* {start_price} BYN\n*Моментальная покупка:* {end_price} BYN\n*Ссылка на продавца:* {seller_link}\n*Местоположение:* {location}\n*Описание:* {description}"

    markup = telebot.types.InlineKeyboardMarkup()
    duration_button = telebot.types.InlineKeyboardButton("🕔", callback_data=name)

    auction_button = telebot.types.InlineKeyboardButton("Сделать ставку📈", callback_data='0' + name)

    buy_button = telebot.types.InlineKeyboardButton("Купить сразу❗️", callback_data=start_price,
                                                    url='https://t.me/qwertyuqieiowiebot')
    markup.add(duration_button)
    markup.row(auction_button, buy_button)

    photo_id = find_photo_by_name(name)
    auction_on[name] = {f'admin': start_price}
    auction_stop_processing(name, end_time)

    bot.send_photo(GROUP_ID, photo=photo_id, caption=info, reply_markup=markup, parse_mode='Markdown')


def send_auction_info(chat_id, auction):
    start_price, end_price, seller_link, location, description, start_time, end_time, name, post = auction
    info = f"*Название:* {name}\n*Стартовая цена:* {start_price} BYN\n*Моментальная покупка:* {end_price} BYN\n*Ссылка на продавца:* {seller_link}\n*Местоположение:* {location}\n*Описание:* {description}\n\nВнимание! С вашего счета будет списано *{float(end_price) * 0.05}* за публикацию аукциона."

    photo_path = 'C:/Users/Женя/Desktop/TGBOT/'
    photo_files = [file for file in os.listdir(photo_path) if file.startswith(name)]

    markUp = telebot.types.InlineKeyboardMarkup()

    confirm_button = telebot.types.InlineKeyboardButton("Подтвердить✅", callback_data='3' + name)
    markUp.add(confirm_button)

    if len(photo_files) == 1:
        with open(os.path.join(photo_path, photo_files[0]), 'rb') as photo:
            photo_data = photo.read()
            sent_message = bot.send_photo(chat_id=chat_id, photo=photo_data, caption=info, parse_mode='Markdown',
                                          reply_markup=markUp)

    else:
        media = []
        for idx, photo_file in enumerate(photo_files):
            with open(os.path.join(photo_path, photo_file), 'rb') as photo:
                photo_data = photo.read()
                caption = info if idx == 0 else ''
                media.append(InputMediaPhoto(media=photo_data, caption=caption, parse_mode='Markdown'))

        if media:
            bot.send_media_group(chat_id=chat_id, media=media)
        else:
            bot.send_message(chat_id, "Фотографии для этого лота не найдены.")


def process_confirm_step(message, chosen_lot):
    auction = get_auction_info(chosen_lot)

    if auction:
        send_auction_info(message.chat.id, auction)
    else:
        bot.send_message(message.chat.id, "Аукцион с выбранным названием не найден.")


def find_photo_by_name(name):
    photo_path = 'C:/Users/Женя/Desktop/TGBOT/'
    for filename in os.listdir(photo_path):
        if filename.startswith(name):
            full_path = os.path.join(photo_path, filename)
            with open(full_path, 'rb') as photo_file:
                return photo_file.read()
    return None


def send_auction_to_channel(auction):
    start_price, end_price, seller_link, location, description, start_time, end_time, name, post = auction
    info = f"*Название:* {name}\n*Стартовая цена:* {start_price} BYN\n*Моментальная покупка:* {end_price} BYN\n*Ссылка на продавца:* {seller_link}\n*Местоположение:* {location}\n*Описание:* {description}"

    markup = telebot.types.InlineKeyboardMarkup()
    duration_button = telebot.types.InlineKeyboardButton("🕔", callback_data=name)
    auction_button = telebot.types.InlineKeyboardButton("Сделать ставку📈", callback_data='0' + name)
    buy_button = telebot.types.InlineKeyboardButton("Купить сразу❗️", callback_data=start_price,
                                                    url='https://t.me/qwertyuqieiowiebot')
    markup.add(duration_button)
    markup.row(auction_button, buy_button)

    photo_id = find_photo_by_name(name)
    auction_on[name] = {f'admin': start_price}
    auction_stop_processing(name, end_time)

    bot.send_photo(GROUP_ID, photo=photo_id, caption=info, reply_markup=markup, parse_mode='Markdown')


def auction_stop_processing(name, end_time):
    print(end_time)
    try:
        end_time = end_time.split()[1]
    except:
        pass

    schedule.every().day.at(end_time).do(auction_stop, name)

    schedule_thread = threading.Thread(target=run_auction_stop)
    schedule_thread.start()


def auction_stop(auction_name):
    print(auction_name)
    max_bidder_id = None
    max_bid = 0

    bids = auction_on.get(auction_name, {})

    for bidder_id, bid in bids.items():
        bid_value = float(bid)
        if bid_value > max_bid:
            max_bid = bid_value
            max_bidder_id = bidder_id

    result = get_auction_info_unpost(auction_name)
    print(result)
    if not result:
        if not max_bidder_id:
            bot.send_message(-1002077468713,
                             f'Ауционный лот *{auction_name}* был удален без каких-либо ставок от игроков.\nПересмотрите лот, либо сделай более выгодное предложение.',
                             parse_mode='Markdown')
        else:
            bot.send_message(max_bidder_id, f'К сожалению, аукцион {auction_name} был установлен либо удален.',
                             parse_mode='Markdown')
        return

    move_to_inactive_auctions(auction_name)

    try:
        if max_bidder_id:
            send_winning_message(max_bidder_id, auction_name, max_bid)

    except:
        bot.send_message(-1002077468713,
                         f'Ауционный лот *{auction_name}* был удален без каких-либо ставок от игроков.\nПересмотрите лот, либо сделай более выгодное предложение.',
                         parse_mode='Markdown')
        delete_auction_db(auction_name)


def send_winning_message(user_id, auction_name, winning_bid=None):
    markOrder = telebot.types.InlineKeyboardMarkup()
    order_button = telebot.types.InlineKeyboardButton("Оформить заявление на передачу.",
                                                      callback_data=f'*:{auction_name}:{winning_bid}')
    markOrder.add(order_button)

    message = f"Поздравляем! Вы победили на аукционе *{auction_name}* с предложением *{winning_bid}* BYN."
    bot.send_message(user_id, message, reply_markup=markOrder, parse_mode='Markdown')
    delete_auction_db(auction_name)


def run_auction_stop():
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_answer(message, user_id, report_text):
    bot.send_message(user_id, f"Ваша жалоба *{report_text}* была обработана:\n\n{message.text}", parse_mode='Markdown')
    delete_from_reports(report_text)
    bot.send_message(message.chat.id, "Ответ на жалобу был отправлен пользователю и жалоба удалена из базы данных.")


def send_auction_to_user(chat_id, auction):
    start_price, end_price, seller_link, location, description, start_time, end_time, name, post = auction
    info = f"*Название:* {name}\n*Стартовая цена:* {start_price} BYN\n*Конечная цена:* {end_price} BYN\n*Ссылка на продавца:* {seller_link}\n*Местоположение:* {location}\n*Описание:* {description}"

    markUp = telebot.types.InlineKeyboardMarkup()

    bet_button = telebot.types.InlineKeyboardButton("Сделать ставку", callback_data='1' + name)
    media_button = telebot.types.InlineKeyboardButton("Фото/видео", callback_data='4' + name)
    info_button = telebot.types.InlineKeyboardButton("❓", callback_data='info')
    time_button = telebot.types.InlineKeyboardButton("🕔", callback_data=name)
    markUp.add(time_button, info_button)
    markUp.add(bet_button, media_button)

    photo_id = find_photo_by_name(name)
    bot.send_photo(chat_id, photo=photo_id, caption=info, reply_markup=markUp, parse_mode='Markdown')


def delete_auction(auction_name, end_price, user_id, message):
    commiss = end_price * 0.05

    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT money FROM personal_account WHERE user_id=?", (user_id,))
    user_balance = cursor.fetchone()[0]
    if user_balance < commiss:
        bot.send_message(message.chat.id, 'Ваш баланс мал для уплаты комисии.\nПополните баланс.')
        return

    new_balance = user_balance - commiss

    move_to_inactive_auctions(auction_name)
    cursor.execute("UPDATE personal_account SET money=? WHERE user_id=?", (new_balance, user_id))
    cursor.execute("DELETE FROM auctions WHERE name=?", (auction_name,))
    conn.commit()
    conn.close()

    bot.delete_message(chat_id='-1002033236010', message_id=message.forward_from_message_id)
    bot.send_message('-1002077468713', f"Аукцион *{auction_name}* успешно удален с вычетом комиссии.",
                     parse_mode='Markdown')


def process_auction_message(message, user_id):
    auction_message = message.caption
    auction_lines = auction_message.strip().split('\n')

    lines = ['Название:', 'Моментальная покупка:']
    missing_lines = [line for line in lines if line not in auction_lines]
    if not missing_lines:
        bot.reply_to(message, f"123Некорректный формат поста.")
        return

    auction_name = None
    end_price = None
    for line in auction_lines:
        if 'Название:' in line:
            auction_name = line.split(': ')[1].strip()
        elif 'Моментальная покупка' in line:
            end_price = float(line.split(': ')[1].split()[0])

    if auction_name and end_price:

        conn = sqlite3.connect('auction_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM auctions WHERE name=?', (auction_name,))
        result = cursor.fetchall()
        conn.close()
        if not result:
            bot.send_message('-1002077468713',
                             "Аукцион уже *неактивен*.\nОпеределите действующий аукцион и попробуйте снова.",
                             parse_mode='Markdown')
            return

        delete_auction(auction_name, end_price, user_id, message)
    else:
        bot.send_message('-1002077468713', "Некорректный формат поста.")


run_schedule_thread = threading.Thread(target=run_schedule)
run_schedule_thread.start()

print('start')
bot.polling()
