# How to publish a story on author-page.inkmotion.art

From a Google Doc to the website, step by step. You do all of it yourself.

**What you end up with:** a free preview (Chapter 1) that anyone can read on the page, and the full book that unlocks with a code you email. Unlocked readers also get an e-book (epub) to download.

**Time:** about 15 minutes once you've done it once.

---

## The pieces (what each file is)

| File | Where it lives | What it does |
|------|----------------|--------------|
| `make_book.py` | your computer | Turns the Google Doc into a clean epub and the Chapter 1 preview |
| `encrypt-epub-book.html` | your computer | Locks the epub with a code |
| `Hole-Attic-John-Azmuth.epub` | your computer only | The unlocked book. **Never upload this to GitHub** |
| `hole-attic.enc` | GitHub, `books/` | The locked book. Safe to be public |
| `chapter-1.html` | GitHub, `books/` | The free preview |

The old PDF lock tool (`encrypt-pdf-book.html`) no longer works with the site. Keep it for history if you like.

---

## Part 1. Get your Google Doc ready (once per story)

1. **Mark each chapter** with a line on its own that reads `***1`, then `***2`, `***3` and so on. Numbers must run in order with none skipped. Even a short story needs `***1` at the top.
2. **Anything above `***1`** (title, byline, notes) is left out of the book. That's on purpose. The cover carries the title and author.
3. **Put "END"** on its own line at the very end if you want the END marker.
4. **Screenplay sections:** the script finds them by their page indents, so format them the way your Hole Attic script is formatted. The easiest way: copy a script paragraph from the Hole Attic doc, paste it into the new doc, and type over the words.
   If you set them by hand, use Courier New with these Format > Align & indent > Indentation options:

   | Part | Left | Right | Other |
   |------|------|-------|-------|
   | Scene heading (EXT./INT.) | 0.5" | none | 24 pt space before |
   | Action | 0.5" | none | |
   | Character name | 2.7" | none | |
   | Dialogue | 1.5" | 1.5" | |
   | Parenthetical | 2.1" | 1" | |
   | Transition (CUT TO:) | 0.5" | none | align right |
5. **Italics** and **bold** carry over. Other fonts and sizes are ignored on purpose, so the book fits every screen.

## Part 2. Download the epub from Google Docs

In the Google Doc: **File > Download > EPUB Publication (.epub)**. Save it somewhere easy, such as a folder called `book-work` on your Desktop.

Do this every time you change the Doc. Don't edit the epub itself.

## Part 3. Build the clean book (Terminal)

**One-time setup:** your Mac probably has Python already. Open **Terminal** (press Cmd+Space, type Terminal) and type `python3 --version`. If you see a version number you're set. If not, macOS offers to install developer tools; say yes.

Put `make_book.py` and `hole-attic-cover.jpg` in the same folder as the epub you downloaded.

In Terminal:

1. Type `cd ` (with a space after it), drag that folder from Finder into the Terminal window, press Return.
2. Run (change the file name to match yours):

```
python3 make_book.py "HoleAttic_Nov_2026.epub" --title "Hole Attic" --author "John Azmuth" --year 2015 --cover hole-attic-cover.jpg
```

For a **new story**, change the title, the year and the cover. Leave out `--cover ...` and it makes a simple dark cover for you (needs a one-time `pip3 install pillow`). Add `--subtitle "A Story"` if "A Novel" doesn't fit.

3. It makes a folder named after the title (here `hole-attic`) and prints a summary. **Read the summary:**

```
chapters: 33   paragraphs: 3923   words: 92699
chapters with a screenplay section: 18, 21, 33
italic passages: 125   preview (Chapter 1): 1039 words
```

Check that the numbers make sense. If the chapter count is wrong, a `***N` marker is missing or misspelled. If screenplay chapters are missing, the script paragraphs lost their indents. If the italic count is 0 and you have italics, tell Claude.

4. **Look at the epub.** Double-click it to open in Apple Books. Check the cover, the start of Chapter 1, and a screenplay chapter.

Inside the folder:
- `Hole-Attic-John-Azmuth.epub` is the full book.
- `chapter-1.html` is the preview.
- `cover.jpg` appears only when the tool made the cover for you.

## Part 4. Lock the book

1. Open `encrypt-epub-book.html` in Chrome (double-click it).
2. Choose **the epub that `make_book.py` made** (Part 3), not the one you downloaded from Google Docs. The tool refuses the Google one.
   The Google epub is one big unformatted document; locking it would give readers a single endless page with no chapters.
3. Type your existing code, or click **Generate a new code**. Click **Lock and download**.
4. It saves `hole-attic.enc`. Save the code in your password manager. It cannot be recovered.

**Which code?**
- Same code as before: readers who already have it keep access. Use this for typo fixes.
- New code: the old code stops working. Use this if a code leaked. You'll need to email the new code to your readers.

## Part 5. Upload to GitHub

1. Go to your author-page repo on github.com, then open the `books` folder.
2. Click **Add file > Upload files**. Drag in `hole-attic.enc`, and `chapter-1.html` **only if Chapter 1 changed**. Same names as before; GitHub replaces the old ones.
3. Click **Commit changes**.
4. Wait a minute or two for the site to update.

**Never upload** the unlocked `.epub` or the cover. GitHub keeps every file it has ever seen, even deleted ones.

## Part 6. Check it worked

1. Open https://author-page.inkmotion.art in a **private window** (so you see what a new reader sees). If the page looks stale, hard-refresh with Cmd+Shift+R.
2. The preview should show Chapter 1 and **no** download button.
3. Enter the code. The chapter menu should list all your chapters. Open one with a screenplay and make sure it's in Courier.
4. Click **Download e-book** and confirm the file opens.

## The "Forget my code on this device" link

Below the unlocked reader, this link makes that reader's browser forget their code and go back to the preview. It doesn't change the book or the code for anyone else. It's useful on a shared or public computer.

## Sending a reader their code

Requests arrive in the Formspree dashboard. Reply from your own email with the code, or send a link that unlocks with one click:

```
https://author-page.inkmotion.art/?code=XXXX-XXXX-XXXX-XXXX
```

---

## Quick routine for edits to the existing book

1. Edit the Google Doc.
2. File > Download > EPUB.
3. Run the `make_book.py` command (Part 3).
4. Lock the new epub with the same code (Part 4).
5. Upload `hole-attic.enc`. Upload `chapter-1.html` only if Chapter 1 changed.

---

## Adding a second story

**Part 1 to Part 4 work for any story**, with its own title, cover and code. But **the website page currently has room for one book, Hole Attic.** A second story needs a new section on the page, with its own file names. That's a one-time change to `index.html`, so you'd ask Claude to add the section. After that, each story follows the same routine on its own.

Tip: when you lock a second story, name the files after it (for example `books/second-story.enc`) so they don't overwrite Hole Attic.

---

## If something goes wrong

| What you see | What to do |
|--------------|------------|
| `I can't find the file` | Check the file name, and that Terminal is in the folder (Part 3 step 1) |
| `Chapter markers are out of order` | Fix the `***N` lines in the Doc, download again |
| `No chapters found` | The Doc has no `***1` line, or Google changed the file; download again |
| Screenplay looks like normal text | Those paragraphs lost their indents; re-paste from a good script paragraph |
| Lock tool says the epub "comes straight from Google Docs" | You skipped Part 3. Run `make_book.py` and lock the epub it makes |
| The site shows one long page, "Chapter 1 of 1" | You locked the Google epub. Do Part 3, lock the new epub, upload the new `.enc` |
| The page says it couldn't open the book | Open the page over `https://`, and check the `.enc` was made from the latest epub |
| The code is rejected | The `.enc` and the code don't match. Lock again with the code you intend |
| Terminal says `python3: command not found` | Accept the macOS prompt to install developer tools, then try again |

If a check you don't understand fails, send Claude the summary Terminal printed.

---

*Built with Claude, November 2026. Tools: `make_book.py`, `encrypt-epub-book.html`.*
