# From the Anki tutorial, https://addon-docs.ankiweb.net/a-basic-addon.html
# A Basic Add-on for quick testing.
#

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of Qt GUI library
from aqt.qt import *


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
def test_func() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    card_count = mw.col.cardCount()
    # show a message box
    showInfo("Card count: %d" % card_count)


# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, test_func)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
