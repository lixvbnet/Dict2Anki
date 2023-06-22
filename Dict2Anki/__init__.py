try:
    from aqt import mw
    # import all of Qt GUI library
    from aqt.qt import *
    from Dict2Anki.addon.addonWindow import Windows

    def show_window():
        w = Windows()
        w.exec()

    action = QAction("Dict2Anki...", mw)
    qconnect(action.triggered, show_window)
    mw.form.menuTools.addAction(action)

except Exception as ex:
    err = ex
    # print(err)
    import os
    if os.environ.get('DEVDICT2ANKI'):
        import sys
        from Dict2Anki.addon.addonWindow import Windows
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        window = Windows()
        window.show()
        sys.exit(app.exec())
