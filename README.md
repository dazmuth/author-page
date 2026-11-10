# azmuth.inkmotion.art

John Azmuth's writing page. It shows a short bio, a Chapter 1 preview of the novel *Hole Attic* in a scrolling reader, and a way for readers to request a code that unlocks the full novel and the PDF download.

This is a separate GitHub repo from `inkmotion-art`. The main site (inkmotion.art) lives in that other repo.

## Files

```
index.html                      the whole page (bio, reader, forms)
books/
  hole-attic-chapter-1.pdf      public preview, anyone can read it
  hole-attic.enc                the full novel, locked (unreadable without the code)
README.md                       this file
```

Kept on your own computer, NOT in this repo:
- `encrypt-book.html` (the tool that locks a PDF)
- the original full-novel PDF (keep it in a private repo or a private folder)

## Go live (one time)

##1. Create a new **public** GitHub repo (for example `azmuth-site`) Upload `index.html`, `README.md`, and the `books` folder.
1. Create a new **public** GitHub repo ('author-page'). Upload `index.html`, `README.md`, and the `books` folder.
2. In GoDaddy DNS for inkmotion.art, add one record. Leave all existing records alone.
   - Type: CNAME
   - Name: `azmuth`
   - Value: `dazmuth.github.io`
3. In the new repo: Settings, then Pages. Deploy from branch `main`, folder `/ (root)`. Under Custom domain, enter `azmuth.inkmotion.art` and save.
4. Wait for the DNS check to pass (up to an hour), then tick **Enforce HTTPS**.

Your inkmotion.art domain is already verified on your GitHub account, which should cover subdomains like this one.

## Put in the real book

The files in `books/` are placeholders. The placeholder `.enc` opens with the code `DEMO-1234-ABCD-5678`. Use it to try the page, then replace it.

1. Open `encrypt-book.html` in Chrome (double-click it).
2. Choose the full novel PDF. Click **Generate a new code**. Click **Lock and download**.
3. Save the code in a password manager. It can't be recovered.
4. Upload the new `hole-attic.enc` into `books/`, replacing the old one.
5. Replace `books/hole-attic-chapter-1.pdf` with your real Chapter 1 PDF, keeping the same file name. Set the PDF's Title in its properties first so browser tabs don't say "Untitled".

Never upload the original full PDF to this repo. GitHub keeps deleted files in its history, and this repo is public.

To change the code later, lock the book again and upload the new `.enc`. The old code stops working once the new file is live. Readers who saved the old code get cleared automatically and are asked for the new one.

## Sending a reader their code

Requests arrive in the Formspree dashboard (source: `azmuth-code-request`). Reply from your own email. A link with the code in it unlocks the book with one click:

```
Hi, thanks for reading Hole Attic. Here is your code:

XXXX-XXXX-XXXX-XXXX

Or just click: https://azmuth.inkmotion.art/?code=XXXX-XXXX-XXXX-XXXX

Enjoy the story.
John
```

## Editing the page

- **Bio:** in `index.html`, find the comment `PLACEHOLDER BIO` and replace the five sentences below it.
- **Book name or file names:** edit the `BOOK` block near the top of the script at the bottom of `index.html`.
- **Formspree form:** both forms on the site post to `https://formspree.io/f/xvzynkqe`. The hidden `source` field tells you which page a signup came from.

## How the lock works

The full novel is encrypted (AES-256) before it goes on GitHub. Anyone can download the `.enc` file, but it is unreadable without the code. When a reader types the code, their browser unlocks the file, shows it in the reader, and offers the download. Nothing is sent to a server.

## Limits to know about

- A code can be passed along by the reader who got it. If one leaks, lock the book again with a new code.
- Pages are drawn as images, so readers can't select or copy text. Chapter 1 is public by design, so anyone can find and download that file.
- Formspree's free plan allows 50 submissions a month across all your forms. Check the dashboard if signups seem to stop.
- The reader loads its PDF engine (pdf.js, version 3.11.174) from the jsDelivr CDN. If that ever fails, the page falls back to a link to Chapter 1.

*Built with Claude, November 2026.*
