import sqlite3


def fetch_reports():
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, complaint FROM reports")
    reports = cursor.fetchall()
    conn.close()
    return reports


def count_reports(id_reports):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reports WHERE id=?", (id_reports,))
    result = cursor.fetchone()
    conn.close()
    return result


def name_inactive():
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inactive_auctions")
    result = cursor.fetchall()
    conn.close()
    return result


def data_reports():
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, complaint FROM reports")
    reports = cursor.fetchall()
    conn.close()
    return reports


def delete_auction_db(auction_name):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM auctions WHERE name=?", (auction_name,))
    conn.commit()
    conn.close()


def move_to_inactive_auctions(auction_name):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM auctions WHERE name=?', (auction_name,))
    result = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM inactive_auctions WHERE name=?', (auction_name,))
    check = cursor.fetchall()

    if check[0][0] == 0:
        result_list = [list(row) for row in result]
        cursor.execute(
            'INSERT INTO inactive_auctions (start_price, end_price, seller_link, location, description, name, post) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (result_list[0][1], result_list[0][2], result_list[0][3], result_list[0][4], result_list[0][5],
             result_list[0][8], 0))
        conn.commit()
        conn.close()


def get_auction_info(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auctions WHERE name=?", (arg,))
    auction = cursor.fetchone()[1:]
    conn.close()
    return auction


def get_auction_info_unpost(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auctions WHERE name=?", (arg,))
    auction = cursor.fetchone()
    conn.close()
    return auction


def get_count_auction(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auctions WHERE name=?", (arg,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_inactive_auction_info(auction_name):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inactive_auctions WHERE name=?", (auction_name,))
    auction = cursor.fetchone()
    conn.close()
    return auction


def update_personal_account(arg1, arg2):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE personal_account SET money = ? WHERE user_id = ?", (arg1, arg2))
    conn.commit()
    conn.close()


def select_all_auction():
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, start_price, end_price, seller_link, location, description, start_time, end_time FROM auctions WHERE post=?",
        (0,))
    results = cursor.fetchall()
    conn.close()
    return results


def select_info_personal_acc(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT money, warn, successful_transactions FROM personal_account WHERE user_id=?",
                   (arg,))

    existing_user = cursor.fetchone()
    conn.close()
    return existing_user


def select_lots_lot(arg1, arg2):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT end_price FROM lots_lot WHERE user_id = ? AND lots = ?",
                   (arg1, arg2))
    result = cursor.fetchall()
    conn.close()
    return result


def select_lots_from_user(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT lots FROM lots_lot WHERE user_id=?', (arg,))
    lots_user = cursor.fetchall()
    conn.close()
    return lots_user


def delete_user_lots(arg1, arg2):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lots_lot WHERE user_id=? AND lots=?', (arg1, arg2))
    conn.commit()
    conn.close()


def check_auction_active(auction_name):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auctions WHERE name=?", (auction_name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def lots_count(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(lots) FROM lots_lot WHERE user_id=?', (arg,))
    result = cursor.fetchall()
    cursor.execute('SELECT lots FROM lots_lot WHERE user_id=?', (arg,))
    lots_user = cursor.fetchall()
    conn.close()
    return result , lots_user


def get_winning_names_lots():
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name_lot FROM order_winning")
    order_winning_names = cursor.fetchall()
    conn.close()
    return order_winning_names


def delete_inactive_accounts(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inactive_auctions WHERE name=?", (arg,))
    conn.commit()
    conn.close()


def add_reports(arg1, arg2):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (user_id, complaint) VALUES (?, ?)", (arg1, arg2))
    conn.commit()
    conn.close()


def get_lot_prices(arg1):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT start_price, end_price FROM auctions WHERE name=?", (arg1,))
    start_price, end_price = cursor.fetchone()
    print(start_price, end_price)
    conn.close()
    return start_price, end_price


def delete_from_reports(arg):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE complaint=?", (arg,))
    conn.commit()
    conn.close()


def check_order_existence(arg1, arg2, arg3):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM order_winning WHERE user_id=? AND name_lot=? AND price_win=?",
                   (arg1, arg2, arg3))
    order_count = cursor.fetchone()[0]
    conn.close()
    return order_count > 0


def insert_order(arg1, arg2, arg3):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO order_winning (user_id, name_lot, price_win) VALUES (?, ?, ?)",
                   (arg1, arg2, arg3))
    cursor.execute(
        "UPDATE personal_account SET successful_transactions = successful_transactions + 1 WHERE user_id = ?",
        (arg1,))
    conn.commit()
    conn.close()


def add_warning(user_id, reason, admin_id):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO warning_list (user_id, reason, admin_id) VALUES (?, ?, ?) ''', (user_id, reason, admin_id))
    conn.commit()
    conn.close()


def admins_coomands(user_id):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    select_query = "SELECT lvl FROM admins_team WHERE user_id = ?"
    cursor.execute(select_query, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_auctions_date(arg1, arg2):
    conn = sqlite3.connect('auction_data.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE auctions SET post = ? WHERE name = ?", (arg1, arg2))
    conn.commit()
    conn.close()
