from PyQt5.QtWidgets import QTextEdit, QLineEdit


def get_widget_text(widget):
    if isinstance(widget, QLineEdit):
        return widget.text()
    elif isinstance(widget, QTextEdit):
        return widget.toPlainText()
    else:
        return None


def set_widget_text(widget, text):
    if isinstance(widget, QLineEdit):
        widget.setText(text)
    elif isinstance(widget, QTextEdit):
        widget.setPlainText(text)
    else:
        raise TypeError("Unsupported widget type")
