import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDateTimeEdit, QMessageBox
from datetime import datetime, timedelta


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 500)

        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(10)

        self.start_price_label = QtWidgets.QLabel(Dialog)
        self.start_price_label.setObjectName("start_price_label")
        self.gridLayout.addWidget(self.start_price_label, 0, 0, 1, 1)
        self.start_price_edit = QtWidgets.QLineEdit(Dialog)
        self.start_price_edit.setObjectName("start_price_edit")
        self.gridLayout.addWidget(self.start_price_edit, 0, 1, 1, 1)

        self.name_label = QtWidgets.QLabel(Dialog)
        self.name_label.setObjectName("name_label")
        self.gridLayout.addWidget(self.name_label, 1, 0, 1, 1)
        self.name_edit = QtWidgets.QLineEdit(Dialog)
        self.name_edit.setObjectName("name_edit")
        self.gridLayout.addWidget(self.name_edit, 1, 1, 1, 1)

        self.end_price_label = QtWidgets.QLabel(Dialog)
        self.end_price_label.setObjectName("end_price_label")
        self.gridLayout.addWidget(self.end_price_label, 2, 0, 1, 1)
        self.end_price_edit = QtWidgets.QLineEdit(Dialog)
        self.end_price_edit.setObjectName("end_price_edit")
        self.gridLayout.addWidget(self.end_price_edit, 2, 1, 1, 1)

        self.seller_link_label = QtWidgets.QLabel(Dialog)
        self.seller_link_label.setObjectName("seller_link_label")
        self.gridLayout.addWidget(self.seller_link_label, 3, 0, 1, 1)
        self.seller_link_edit = QtWidgets.QLineEdit(Dialog)
        self.seller_link_edit.setObjectName("seller_link_edit")
        self.gridLayout.addWidget(self.seller_link_edit, 3, 1, 1, 1)

        self.location_label = QtWidgets.QLabel(Dialog)
        self.location_label.setObjectName("location_label")
        self.gridLayout.addWidget(self.location_label, 4, 0, 1, 1)
        self.location_edit = QtWidgets.QLineEdit(Dialog)
        self.location_edit.setObjectName("location_edit")
        self.gridLayout.addWidget(self.location_edit, 4, 1, 1, 1)

        self.description_label = QtWidgets.QLabel(Dialog)
        self.description_label.setObjectName("description_label")
        self.gridLayout.addWidget(self.description_label, 5, 0, 1, 1)
        self.description_edit = QtWidgets.QLineEdit(Dialog)
        self.description_edit.setObjectName("description_edit")
        self.gridLayout.addWidget(self.description_edit, 5, 1, 1, 1)

        self.start_time_label = QtWidgets.QLabel(Dialog)
        self.start_time_label.setObjectName("start_time_label")
        self.gridLayout.addWidget(self.start_time_label, 6, 0, 1, 1)
        self.start_time_edit = QtWidgets.QDateTimeEdit(Dialog)
        self.start_time_edit.setObjectName("start_time_edit")
        self.gridLayout.addWidget(self.start_time_edit, 6, 1, 1, 1)

        self.end_time_label = QtWidgets.QLabel(Dialog)
        self.end_time_label.setObjectName("end_time_label")
        self.gridLayout.addWidget(self.end_time_label, 7, 0, 1, 1)
        self.end_time_edit = QtWidgets.QDateTimeEdit(Dialog)
        self.end_time_edit.setObjectName("end_time_edit")
        self.gridLayout.addWidget(self.end_time_edit, 7, 1, 1, 1)

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 8, 0, 1, 2)
        self.pushButton.clicked.connect(self.submit_data)
        self.pushButton.setMinimumSize(100, 30)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        now = datetime.now() + timedelta(hours=1)
        self.start_time_edit.setDateTime(now)
        self.end_time_edit.setDateTime(now)


    def submit_data(self):
        print('hello')
        start_price = self.start_price_edit.text()
        name = self.name_edit.text()
        end_price = self.end_price_edit.text()
        seller_link = self.seller_link_edit.text()
        location = self.location_edit.text()
        description = self.description_edit.text()
        start_time = self.start_time_edit.dateTime().toPyDateTime()
        end_time = self.end_time_edit.dateTime().toPyDateTime()

        connection = sqlite3.connect("auction_data.db")
        cursor = connection.cursor()

        cursor.execute("INSERT INTO auctions (start_price, end_price, seller_link, location, description, start_time, end_time, name, post) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (start_price, end_price, seller_link, location, description, start_time, end_time, name, 0))
        connection.commit()
        connection.close()


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.start_price_label.setText(_translate("Dialog", "Старт. цена:"))
        self.name_label.setText(_translate("Dialog", "Название:"))
        self.end_price_label.setText(_translate("Dialog", "Кон.цена:"))
        self.seller_link_label.setText(_translate("Dialog", "Ссылка:"))
        self.location_label.setText(_translate("Dialog", "Геолокация:"))
        self.description_label.setText(_translate("Dialog", "Описание:"))
        self.start_time_label.setText(_translate("Dialog", "Время старта:"))
        self.end_time_label.setText(_translate("Dialog", "Время окончания:"))
        self.pushButton.setText(_translate("Dialog", "Принять"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())