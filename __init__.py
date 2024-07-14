import os
import requests

DEBUG = False
try:
    rc = os.system(r'grep -E -q "^export\s+DICT2ANKI_SSL_VERIFY=0" ~/.bashrc.local.sh')
    if rc == 0:
        DEBUG = True
except Exception:
    pass

try:
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo, qconnect
    # import all of Qt GUI library
    from aqt.qt import *
    from .addon.addonWindow import Windows

    def disable_ssl_check():
        original_req = requests.Session.request

        def request(*args, **kwargs):
            kwargs['verify'] = False
            return original_req(*args, **kwargs)
        requests.Session.request = request

    if DEBUG:
        showInfo("[Dict2Anki] DEBUG=True, SSL Check is DISABLED!")
        disable_ssl_check()


    def show_window():
        w = Windows()
        w.exec()

    action = QAction("Dict2Anki...", mw)
    qconnect(action.triggered, show_window)
    mw.form.menuTools.addAction(action)

except Exception as ex:
    err = ex
    import os
    if os.environ.get('DEVDICT2ANKI'):
        import sys
        from .addon.addonWindow import Windows
        from aqt.qt import QApplication
        app = QApplication(sys.argv)
        window = Windows()
        window.show()
        sys.exit(app.exec())
