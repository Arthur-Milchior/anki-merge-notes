# Merging notes
## Rationale
At one point, for some complex reason, I had related notes and I
wanted to merge them. This did make sens because their was no filled
filled in both notes, and no card type generated for both notes.

This add-on does just this. In the browser, you select two notes with
the same note type, and it merges them.

## Description
Let's say you want to merge notes N1 and N2. There is no way to states
which one is N1 and which one is N2.

If N1 and N2 have distinct tip, an error message is shown. Otherwise,
both notes become a single notes N. Each fields of N is the
concatenation of the same fields in N1 and N2.

For each card type CT, N has a card of type CT which is a copy of the
card of type CT of N1 or of N2, the choice is made such that the card
with the greatest interval is chosen. In case of equal interval, the
greatest easiness is used.

N has the tags of both notes, plus the tags merged mergedNID1 and
mergedNID2 with NIDi being the id of note i.

## Warning
A card of N may be suspended, etc... if the card fo the
same type in N1 or N2 is suspended. Same thing occurs with flagged cards.

## Configuration
None. Hire me if you want me to add more options.
## Version 2.0
None

## TODO

## Links, licence and credits

Key         |Value
------------|-------------------------------------------------------------------
Copyright   | Arthur Milchior <arthur@milchior.fr>
Based on    | Anki code by Damien Elmes <anki@ichi2.net>
License     | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Source in   | https://github.com/Arthur-Milchior/anki-merge-notes
Addon number| [???????](https://ankiweb.net/shared/info/1482505492)
Support me on| [![Ko-fi](https://ko-fi.com/img/Kofi_Logo_Blue.svg)](Ko-fi.com/arthurmilchior) or [![Patreon](http://www.milchior.fr/patreon.png)](https://www.patreon.com/bePatron?u=146206)
