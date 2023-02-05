from PyQt6.QtWidgets import QMessageBox, QWidget, QScrollArea, QVBoxLayout


def panic(title: str, msg_text: str):
    """
    Show error message window and raise exception

    :param title: exception title
    :param msg_text: exception message
    """

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(title)
    msg.setInformativeText(msg_text)
    msg.setWindowTitle("Error")
    msg.exec_()

    raise Exception(f'{title}\n{msg}')


def show_log(title: str, msg_text: str):
    """
    Show log message window

    :param title: log title
    :param msg_text: log message
    """

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(title)
    msg.setInformativeText(msg_text)
    msg.setWindowTitle("Information")
    msg.exec_()
