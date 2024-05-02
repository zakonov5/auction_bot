import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy, \
    QDialog
from history_logs import Historylogs
from post_loading import Ui_Dialog
from users_logs import Users_BD
from admin_system import AdminsTeam


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления ботом")
        self.resize(800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        layout.addStretch()
        self.button_published = QPushButton("Публикация поста")
        self.button_published.setFixedSize(200, 50)
        self.button_published.clicked.connect(self.open_window)

        layout.addWidget(self.button_published)

        self.button_logs = QPushButton("История торгов")
        self.button_logs.clicked.connect(self.open_history_logs)
        self.button_logs.setFixedSize(200, 50)
        layout.addWidget(self.button_logs)

        self.button_userlogs = QPushButton("БД пользователей")
        self.button_userlogs.setFixedSize(200, 50)
        self.button_userlogs.clicked.connect(self.open_users_bd)
        layout.addWidget(self.button_userlogs)

        self.button_admin = QPushButton("Admins System")
        self.button_admin.setFixedSize(200, 50)
        self.button_admin.clicked.connect(self.admin_system)
        layout.addWidget(self.button_admin)
        layout.addStretch()

    def open_history_logs(self):
        self.post_loading = Historylogs()
        self.post_loading.show()

    def open_window(self):
        self.dialog = QDialog()
        self.ui_dialog = Ui_Dialog()
        self.ui_dialog.setupUi(self.dialog)
        self.dialog.show()

    def open_users_bd(self):
        self.users_logs = Users_BD()
        self.users_logs.show()


    def admin_system(self):
        self.admin_system = AdminsTeam()
        self.admin_system.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
