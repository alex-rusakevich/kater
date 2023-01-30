from PyQt6.QtWidgets import QMessageBox


def panic(title, msg):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(title)
    msg.setInformativeText(msg)
    msg.setWindowTitle("Error")
    msg.exec_()

    raise Exception(f'{title}\n{msg}')
