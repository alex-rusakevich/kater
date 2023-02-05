from PyQt6.QtWidgets import QMessageBox


def panic(title: str, msg: str):
    """
    Show error missage window and raise exception

    :param title: exception title
    :param msg: exception message
    """

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(title)
    msg.setInformativeText(msg)
    msg.setWindowTitle("Error")
    msg.exec_()

    raise Exception(f'{title}\n{msg}')
