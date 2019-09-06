from aqt import mw
from aqt.utils import showWarning
from anki.hooks import addHook
from anki.notes import Note
from anki.utils import timestampID
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def mergeNids(nids):
    if len(nids)!=2:
        showWarning(_("Please select exactly two notes to merge and not %s")% nids)
        return
    nid1, nid2 = nids
    note1 = Note(mw.col, id=nid1)
    note2 = Note(mw.col, id=nid2)
    mergeNotes(note1, note2)

def mergeNotes(note1, note2):
    model = note1.model()
    model2 = note2.model()
    if model != model2:
        showWarning(_("Please select notes of the same type to merge them"))
        return
    note = Note(mw.col, model)
    for i in range(len(note.fields)):
        note.fields[i] = note1.fields[i]+note2.fields[i]
    cards = [None] * len(model['tmpls'])

    # Choosing which card to keep
    for card in note1.cards():
        cards[card.ord] = card
    for card in note2.cards():
        ord = card.ord
        card1 = cards[ord]
        if card1 is None or card1.ivl < card.ivl or (card1.ivl == card.ivl and card1.ease < card.ease):
            cards[ord] = card

    # tags
    note.addTag(note1.stringTags())
    note.addTag(note2.stringTags())
    note.addTag(f"merged merged_{note1.id} merged_{note2.id}")

    for card in cards:
        if card is None:
            continue
        card.id = timestampID(mw.col.db, "cards")
        card.nid = note.id
        card.flush()
    note.flush()

    if getUserOption("Delete original cards", False):
        mw.col.remNotes([note1.id, note2.id])

    tooltip(_("Notes merged"))

def setupMenu(browser):
    a = QAction("Merge notes", browser)
    a.setShortcut(QKeySequence("Ctrl+Alt+M"))
    a.triggered.connect(lambda : mergeNids(browser.selectedNotes()))
    browser.form.menuEdit.addAction(a)
addHook("browser.setupMenus", setupMenu)
