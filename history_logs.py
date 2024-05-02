import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton


class Historylogs(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История торгов")
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Bid ID", "Lot Name", "Bidder ID", "Bid Amount", "Bid Time"])
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

        cursor.execute("SELECT bid_id, lot_name, bidder_id, bid_amount, bid_timestamp FROM bids_history")
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
            bid_id = self.tableWidget.item(selected_row,
                                           0).text()
            self.process_of_delete(bid_id)


    def process_of_delete(self, bid_id):
        conn = sqlite3.connect("auction_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bids_history WHERE bid_id=?", (bid_id,))
        conn.commit()
        conn.close()

        self.load()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dialog = Historylogs()
    dialog.exec_()
    sys.exit(app.exec_())
