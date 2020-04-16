from aqt import mw
from aqt.utils import showWarning, tooltip
from anki.hooks import addHook
from anki.notes import Note
from anki.lang import _
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .config import getUserOption
from .consts import *


def onMerge(browser):
    note = mergeNids(browser.selectedNotes())
    cards = note.cards()
    browser.search()
    browser.model.selectedCards = {card.id: True for card in cards}
    #browser.model.focusedCard = cards[0].id
    browser.model.restoreSelection()


def mergeNids(nids):
    if len(nids) != 2:
        showWarning(
            _("Please select exactly two notes to merge and not %s") % nids)
        return
    nid1, nid2 = nids
    note1 = Note(mw.col, id=nid1)
    note2 = Note(mw.col, id=nid2)
    model = note1.model()
    model2 = note2.model()
    if model != model2:
        showWarning(_("Please select notes of the same type to merge them"))
        return
    return mergeNotes(note1, note2)


def mergeNotes(note1, note2):
    mw.checkpoint("Merge Notes")

    model = note1.model()
    model2 = note2.model()
    if model != model2:
        showWarning(_("Please select notes of the same type to merge them"))
        return
    note = Note(mw.col, id=note1.id)
    if not getUserOption("Delete original cards", True):
        note.id = timestampID(mw.col.db, "notes", note.id)

    for i in range(len(note.fields)):
        field1 = note1.fields[i]
        field2 = note2.fields[i]
        if field1 != field2 or not getUserOption("When identical keep a single field", True):
            note.fields[i] += field2
    cards = [None] * len(model['tmpls'])

    # Choosing which card to keep
    for card in note1.cards():
        cards[card.ord] = card
    for card in note2.cards():
        ord = card.ord
        card1 = cards[ord]
        if card1 is None or card1.type == CARD_NEW or card1.ivl < card.ivl or (card1.ivl == card.ivl and card1.factor < card.factor):
            cards[ord] = card

    # tags
    note.addTag(note2.stringTags())
    note.addTag(f"merged merged_{note1.id} merged_{note2.id}")

    for card in cards:
        if card is None:
            continue
        if not getUserOption("Delete original cards", True):
            card.id = timestampID(mw.col.db, "cards", card.id)
        card.nid = note.id
        card.flush()
    note.flush()

    if getUserOption("Delete original cards", False):
        mw.col.remNotes([note2.id])

    tooltip(_("Notes merged"))
    return note


def setupMenu(browser):
    a = QAction("Merge notes", browser)
    a.setShortcut(QKeySequence("Ctrl+Alt+M"))
    a.triggered.connect(lambda: onMerge(browser))
    browser.form.menuEdit.addAction(a)


addHook("browser.setupMenus", setupMenu)


def timestampID(db, table, t=None):
    "Return a non-conflicting timestamp for table."
    # be careful not to create multiple objects without flushing them, or they
    # may share an ID.
    t = t or intTime(1000)
    while db.scalar("select id from %s where id = ?" % table, t):
        t += 1
    return t
