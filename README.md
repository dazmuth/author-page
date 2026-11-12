# author-page.inkmotion.art

John Azmuth's writing page. It shows a short bio, then Chapter 1 of the novel *Hole Attic* as normal text right on the page (nothing to download). Readers can request a code that unlocks the whole novel in the same reader and adds a download of the e-book (an epub file).

This is a separate GitHub repo from `inkmotion-art`. The main site (inkmotion.art) lives in that other repo.

## Files

```
index.html                      the whole page (bio, photo, reader, forms)
avatar-blackbar-square.webp     photo beside the bio (542 KB, what the page actually loads)
avatar-blackbar-square.png      same photo, 3 MB, only a fallback for very old browsers
books/
  chapter-1.html                free preview, shown directly on the page
  hole-attic.enc                the full novel (the epub), locked: unreadable without the code
README.md                       this file
```

Kept on your own computer, NOT in this repo:
- `encrypt-book.html` (the tool that locks the epub)
- `Hole-Attic-John-Azmuth.epub` (the unlocked original; keep it in a private folder)

**Important:** if the repo still has an older `books/hole-attic.enc` or any `.pdf` in `books/`, they are from the old PDF version. Replace the `.enc` with a freshly locked epub (steps below) and delete the PDFs.

## Go live (one time)

1. Create a new **public** GitHub repo (for example `azmuth-site`). Upload `index.html`, `README.md`, the avatar files, and the `books` folder.
2. In GoDaddy DNS for inkmotion.art, add one record. Leave all existing records alone.
   - Type: CNAME
   - Name: `author-page`
   - Value: `dazmuth.github.io`
3. In the new repo: Settings, then Pages. Deploy from branch `main`, folder `/ (root)`. Under Custom domain, enter `author-page.inkmotion.art` and save.
4. Wait for the DNS check to pass (up to an hour), then tick **Enforce HTTPS**. Unlocking only works over https.

## Put in the real book

1. Open `encrypt-book.html` in Chrome (double-click it).
2. Choose `Hole-Attic-John-Azmuth.epub`. Type your existing code, or click **Generate a new code**. Click **Lock and download**. (The tool refuses PDFs.)
3. Save the code in a password manager. It can't be recovered.
4. Upload the new `hole-attic.enc` into `books/`, replacing the old one. Upload `chapter-1.html` into `books/` too.

Never upload the unlocked epub to this repo. GitHub keeps deleted files in its history, and this repo is public.

To change the code later, lock the book again and upload the new `.enc`. The old code stops working once the new file is live. Readers who saved the old code get cleared automatically and are asked for the new one.

## If you edit the story

Chapter 1 and the epub are built from the Google Doc. After editing the Doc, download it from Google Docs as an epub (or "Web page (.html, zipped)") and ask Claude to rebuild: that produces a new epub and a new `chapter-1.html`. Then lock the new epub (above) and upload both files.

## Sending a reader their code

Requests arrive in the Formspree dashboard (source: `azmuth-code-request`). Reply from your own email. A link with the code in it unlocks the book with one click:

```
Hi, thanks for reading Hole Attic. Here is your code:

XXXX-XXXX-XXXX-XXXX

Or just click: https://author-page.inkmotion.art/?code=XXXX-XXXX-XXXX-XXXX

Enjoy the story.
John
```

## Editing the page

- **Bio:** in `index.html`, find `<p class="bio">` and replace the text inside it.
- **Photo:** the photo sits beside the bio and is stretched to match the bio's height. To swap it, upload a new image with the same file name (keep it square). On phones the photo moves above the text.
- **"Get a code to read the rest" button:** scrolls to the request form, flashes it, and puts the cursor in the email box.
- **Reader text size and Dark/Light:** readers set these themselves; the page remembers their choice on their device.
- **Book name or file names:** edit the `BOOK` block near the top of the script at the bottom of `index.html`.
- **Formspree form:** both forms on the site post to `https://formspree.io/f/xvzynkqe`. The hidden `source` field tells you which page a signup came from.

## How the lock works

The full novel (the epub) is encrypted (AES-256) before it goes on GitHub. Anyone can download the `.enc` file, but it is unreadable without the code. When a reader types the code, their browser unlocks the file, shows the story in the reader one chapter at a time, and offers the epub download. Nothing is sent to a server.

## Limits to know about

- A code can be passed along by the reader who got it. If one leaks, lock the book again with a new code.
- Chapter 1 is public by design, and an unlocked reader can copy text. The epub download is yours to give away once someone has a code.
- Formspree's free plan allows 50 submissions a month across all your forms. Check the dashboard if signups seem to stop.
- The reader loads its unzip tool (JSZip 3.10.1) from the jsDelivr CDN, pinned with an integrity hash. If that fails, the reader says so and the preview still works.

*Built with Claude, November 2026.*
