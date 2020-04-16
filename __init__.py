from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from anki.hooks import addHook
from anki.lang import _
from anki.notes import Note
from aqt import mw
from aqt.utils import showWarning, tooltip

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
            _("Please select exactly two notes to merge and not %s") % str(nids))
        return
    nid1, nid2 = nids
    note1 = Note(mw.col, id=nid1)
    note2 = Note(mw.col, id=nid2)
    if note1.model() != note2.model():
        showWarning(_("Please select notes of the same type to merge them"))
        return
    return mergeNotes(note1, note2)


def mergeNotes(note1, note2):
    mw.checkpoint("Merge Notes")

    model1 = note1.model()
    model2 = note2.model()
    if model1 != model2:
        showWarning(_("Please select notes of the same type to merge them"))
        return
    note = Note(mw.col, id=note1.id)
    if not getUserOption("Delete original cards", True):
        note.id = timestampID(mw.col.db, "notes", note.id)

    for i in range(len(note.fields)):
        if note1.fields[i] != note2.fields[i] or not getUserOption("When identical keep a single field", True):
            note.fields[i] += note2.fields[i]
    cards = [None] * len(model1['tmpls'])

    # Choosing which card to keep
    cards_to_delete = []
    for card1 in note1.cards():
        cards[card1.ord] = card1
    for card2 in note2.cards():
        ord = card2.ord
        card1 = cards[ord]
        if card1 is None or card1.type == CARD_NEW or card1.ivl < card2.ivl or (card1.ivl == card2.ivl and card1.factor < card2.factor):
            cards[ord] = card2
            cards_to_delete.append(card1.id)
        else:
            cards_to_delete.append(card2.id)

    # tags
    note.addTag(note2.stringTags())
    note.addTag(f"merged merged_{note1.id} merged_{note2.id}")

    if getUserOption("Delete original cards", False):
        mw.col.remNotes([note2.id])
        mw.col.remCards(cards_to_delete, notes=False)

    for card in cards:
        if card is None:
            continue
        if not getUserOption("Delete original cards", True):
            card.id = timestampID(mw.col.db, "cards", card.id)
        card.nid = note.id
        card.flush()
    note.flush()

    tooltip(_("Notes merged"))
    return note


def setupMenu(browser):
    a = QAction("Merge notes", browser)
    a.setShortcut(QKeySequence(getUserOption("Keyboard shortcut", "Ctrl+M")))
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
