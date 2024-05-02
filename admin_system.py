import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton


class AdminsTeam(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Администраторы")
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "User ID", "Level"])
        self.load()
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.deleteButton = QPushButton("Удалить")
        self.deleteButton.clicked.connect(self.deleteSelectedItem)
        layout.addWidget(self.deleteButton)
        self.setLayout(layout)
        self.setFixedSize(800, 500)

    def load(self):
        conn = sqlite3.connect("auction_data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, user_id, lvl FROM admins_team")
        data = cursor.fetchall()

        self.tableWidget.setRowCount(len(data))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_num, col_num, item)

        conn.close()

    def deleteSelectedItem(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            admin_id = self.tableWidget.item(selected_row, 0).text()
            self.process_of_delete(admin_id)

    def process_of_delete(self, admin_id):
        conn = sqlite3.connect("auction_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins_team WHERE id=?", (admin_id,))
        conn.commit()
        conn.close()

        self.load()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dialog = AdminsTeam()
    dialog.exec_()
    sys.exit(app.exec_())
