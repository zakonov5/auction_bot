import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QMessageBox


class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить пользователя")

        self.user_id_label = QLabel("User ID:")
        self.user_id_edit = QLineEdit()

        self.warn_label = QLabel("Warn:")
        self.warn_edit = QLineEdit()

        self.money_label = QLabel("Money:")
        self.money_edit = QLineEdit()

        self.successful_transactions_label = QLabel("Successful Transactions:")
        self.successful_transactions_edit = QLineEdit()

        self.addButton = QPushButton("Добавить")
        self.cancelButton = QPushButton("Отмена")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.cancelButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.user_id_label)
        mainLayout.addWidget(self.user_id_edit)
        mainLayout.addWidget(self.warn_label)
        mainLayout.addWidget(self.warn_edit)
        mainLayout.addWidget(self.money_label)
        mainLayout.addWidget(self.money_edit)
        mainLayout.addWidget(self.successful_transactions_label)
        mainLayout.addWidget(self.successful_transactions_edit)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.addButton.clicked.connect(self.add_user)
        self.cancelButton.clicked.connect(self.reject)

    def add_user(self):
        user_id = self.user_id_edit.text()
        warn = self.warn_edit.text()
        money = self.money_edit.text()
        successful_transactions = self.successful_transactions_edit.text()

        if not user_id or not warn or not money or not successful_transactions:
            QMessageBox.warning(self, "sos", "заполните все поля.")
            return

        try:
            warn = int(warn)
            money = float(money)
            successful_transactions = int(successful_transactions)
        except ValueError:
            QMessageBox.warning(self, "sos", "проверьте введенные данные.")
            return

        conn = sqlite3.connect("auction_data.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO personal_account (user_id, warn, money, successful_transactions) VALUES (?, ?, ?, ?)",
                       (user_id, warn, money, successful_transactions))
        conn.commit()
        conn.close()

        self.accept()


class Users_BD(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("БД пользователей")

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "user_id", "warn", "money", "successful_transactions"])

        self.addButton = QPushButton("Добавить")
        self.deleteButton = QPushButton("Удалить")

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.deleteButton)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.tableWidget)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.addButton.clicked.connect(self.add_user)
        self.deleteButton.clicked.connect(self.delete_user)

        self.load()
        self.setFixedSize(800, 500)

    def load(self):
        conn = sqlite3.connect("auction_data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, user_id, warn, money, successful_transactions FROM personal_account")
        data = cursor.fetchall()

        self.tableWidget.setRowCount(len(data))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_num, col_num, item)

        conn.close()

    def add_user(self):
        dialog = AddUserDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load()

    def delete_user(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            user_id = self.tableWidget.item(selected_row, 1).text()
            conn = sqlite3.connect("auction_data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM personal_account WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self.tableWidget.removeRow(selected_row)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dialog = Users_BD()
    dialog.exec_()
    sys.exit(app.exec_())
