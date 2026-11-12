#!/usr/bin/env python3
"""make_book.py: turn a Google Docs epub export into a clean epub plus a free-preview page for the website.

Usage (from Terminal):
    python3 make_book.py "My Story.epub" --title "My Story" --author "John Azmuth" --year 2026 --cover cover.jpg

Writes a folder (named after the story) containing:
    <Title-Author>.epub   the full book. Lock this with encrypt-epub-book.html before uploading.
    chapter-1.html        the free preview the website shows. Upload it as-is.

Text is copied exactly from your manuscript; only structure and styling are rebuilt.
The manuscript must mark each chapter with a line like  ***1   ***2  ...  (see the guide).
Needs only Python 3 (no installs). Making a cover automatically also needs Pillow (pip3 install pillow).
"""
import argparse
import html
import re
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ap = argparse.ArgumentParser(description='Build a clean epub and preview page from a Google Docs epub export.')
ap.add_argument('source', help='the epub you downloaded from Google Docs (or its .xhtml file)')
ap.add_argument('--title', required=True, help='book title, e.g. "Hole Attic"')
ap.add_argument('--author', default='John Azmuth', help='author name (default: John Azmuth)')
ap.add_argument('--year', default=str(datetime.now().year), help='copyright year printed on the cover')
ap.add_argument('--cover', help='cover image (.jpg). If left out, a simple cover is made for you')
ap.add_argument('--subtitle', default='A Novel', help='small line above the title on a made cover (default: A Novel)')
ap.add_argument('--out', help='output folder (default: a new folder named after the title)')
ARGS = ap.parse_args()

TITLE, AUTHOR = ARGS.title.strip(), ARGS.author.strip()
FILE_AS = (AUTHOR.rsplit(' ', 1)[1] + ', ' + AUTHOR.rsplit(' ', 1)[0]) if ' ' in AUTHOR else AUTHOR
RIGHTS = f'Copyright © {ARGS.year} {AUTHOR}. All rights reserved.'
SLUG = re.sub(r'[^A-Za-z0-9]+', '-', f'{TITLE} {AUTHOR}').strip('-')
OUT = Path(ARGS.out) if ARGS.out else Path(re.sub(r'[^A-Za-z0-9]+', '-', TITLE).strip('-').lower())
OUT.mkdir(parents=True, exist_ok=True)


def find_source(path):
    """Accept the epub from Google Docs, or the xhtml inside it."""
    path = Path(path)
    if not path.exists():
        sys.exit(f'I can\'t find the file "{path}". Check the name, and run this from the folder that holds it.')
    if path.suffix.lower() != '.epub':
        return path
    tmp = Path(tempfile.mkdtemp(prefix='makebook-'))
    with zipfile.ZipFile(path) as z:
        cands = [i for i in z.infolist() if i.filename.lower().endswith(('.xhtml', '.html')) and 'nav' not in i.filename.lower()]
        if not cands:
            sys.exit('That epub has no story text in it. Download it again from Google Docs (File > Download > EPUB).')
        big = max(cands, key=lambda i: i.file_size)
        target = tmp / 'story.xhtml'
        target.write_bytes(z.read(big))
    return target


def make_cover(dest):
    """A simple dark cover with title, author and the copyright line, drawn with Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit('No cover image given, and Pillow is not installed to make one. Either add  --cover your-cover.jpg  '
                 'or run  pip3 install pillow  once and try again.')
    W, H = 1600, 2400
    bg, ink, accent, soft = (29, 26, 23), (244, 239, 230), (166, 63, 34), (201, 188, 174)
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([108, 108, W - 108, H - 108], outline=accent, width=6)

    def font(size, bold=False):
        names = (['Georgia Bold.ttf', 'Georgia.ttf', 'Times New Roman Bold.ttf', 'DejaVuSerif-Bold.ttf', 'LiberationSerif-Bold.ttf']
                 if bold else ['Arial.ttf', 'Helvetica.ttc', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'])
        for n in names:
            for base in ('', '/System/Library/Fonts/Supplemental/', '/Library/Fonts/', '/System/Library/Fonts/',
                         '/usr/share/fonts/truetype/dejavu/', 'C:/Windows/Fonts/'):
                try:
                    return ImageFont.truetype(base + n, size)
                except OSError:
                    pass
        return ImageFont.load_default(size)

    def centered(text, y, fnt, fill, spacing=0):
        w = d.textlength(text, font=fnt) + spacing * max(len(text) - 1, 0)
        x = (W - w) / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill)
            x += d.textlength(ch, font=fnt) + spacing

    centered(ARGS.subtitle.upper(), 260, font(44), (217, 164, 143), 14)
    words, lines, cur = TITLE.split(), [], ''
    for w in words:  # wrap the title to fit the cover
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font(260, True)) > W - 340 and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    size = 260 if len(lines) <= 3 else 190
    y = 760 if len(lines) <= 2 else 560
    for ln in lines:
        centered(ln, y, font(size, True), ink)
        y += int(size * 1.08)
    d.rectangle([W / 2 - 130, y + 50, W / 2 + 130, y + 60], fill=accent)
    centered(AUTHOR.upper(), 1990, font(70), ink, 14)
    centered(RIGHTS, 2110, font(38), soft, 1)
    img.save(dest, 'JPEG', quality=90)


# Google Docs renumbers its CSS classes (c1, c2 ...) on every export, so roles are worked out
# from what each class DOES (indent, alignment, italic, bold), never from its number.
SCRIPT_ROLES, ITALIC, BOLD = {}, set(), set()


def _pt(decl, prop):
    m = re.search(r'(?:^|;)' + prop + r':([\d.]+)pt', decl)
    return float(m.group(1)) if m else None


def classify_styles(css):
    for m in re.finditer(r'\.(c\d+)\{([^}]*)\}', css):
        name, d = m.group(1), m.group(2)
        ml, mr, pt = _pt(d, 'margin-left'), _pt(d, 'margin-right'), _pt(d, 'padding-top')
        right = 'text-align:right' in d
        if 'font-style:italic' in d:
            ITALIC.add(name)
        if re.search(r'font-weight:700', d):
            BOLD.add(name)
        if ml is None:
            continue
        if abs(ml - 194.4) < 1:
            SCRIPT_ROLES[name] = 'cue'
        elif abs(ml - 151.2) < 1:
            SCRIPT_ROLES[name] = 'paren'
        elif abs(ml - 108) < 1 and mr is not None and abs(mr - 108) < 1:
            SCRIPT_ROLES[name] = 'dial'
        elif abs(ml - 36) < 1 and right:
            SCRIPT_ROLES[name] = 'trans'
        elif abs(ml - 36) < 1 and pt is not None and pt >= 20:
            SCRIPT_ROLES[name] = 'slug'
        elif abs(ml - 36) < 1:
            SCRIPT_ROLES[name] = 'action'


def read_paragraphs(path):
    s = path.read_text(encoding='utf-8')
    classify_styles(s.split('</style>')[0])
    body = s[s.find('<body'):]
    paras = []
    for m in re.finditer(r'<p class="([^"]*)"[^>]*>(.*?)</p>', body, flags=re.S):
        classes = m.group(1).split()
        runs = []
        for sm in re.finditer(r'<span class="([^"]*)">(.*?)</span>', m.group(2), flags=re.S):
            cl = set(sm.group(1).split())
            text = html.unescape(sm.group(2)).replace(' ', ' ')
            text = re.sub(r'[ \t\r\n]+', ' ', text)
            runs.append((text, bool(cl & ITALIC), bool(cl & BOLD)))
        paras.append((classes, runs))
    return paras


def runs_to_html(runs):
    """Join runs (dropping doubled spaces at joins) and wrap italic/bold."""
    merged = []
    for text, it, bd in runs:
        if not text:
            continue
        if merged and merged[-1][0].endswith(' ') and text.startswith(' '):
            text = text.lstrip(' ')
            if not text:
                continue
        if merged and merged[-1][1:] == (it, bd):
            merged[-1] = (merged[-1][0] + text, it, bd)
        else:
            merged.append((text, it, bd))
    if not merged:
        return '', ''
    merged[0] = (merged[0][0].lstrip(' '), *merged[0][1:])
    merged[-1] = (merged[-1][0].rstrip(' '), *merged[-1][1:])
    out, plain = [], []
    for text, it, bd in merged:
        if not text:
            continue
        h = escape(text)
        if it:
            h = f'<i>{h}</i>'
        if bd:
            h = f'<b>{h}</b>'
        out.append(h)
        plain.append(text)
    return ''.join(out), ''.join(plain)


def build_chapters(paras):
    """Returns (chapters, plain_text_lines). chapters = [(number, [html blocks])]."""
    chapters, current, script = [], None, []
    plain_all = []

    def flush_script():
        nonlocal script
        if script:
            current[1].append('<div class="script">\n' + '\n'.join(script) + '\n</div>')
            script = []

    started = False
    for classes, runs in paras:
        role_class = next((c for c in classes if c in SCRIPT_ROLES), None)
        h, plain = runs_to_html(runs)
        if not plain:
            continue
        m = re.fullmatch(r'\*{2,}\s*(\d+)', plain)
        if m:
            if current is not None:
                flush_script()
            current = (int(m.group(1)), [])
            chapters.append(current)
            started = True
            continue
        if not started:
            continue  # title and author lines before chapter 1 are rebuilt below
        plain_all.append(plain)
        if role_class:
            script.append(f'<p class="sp-{SCRIPT_ROLES[role_class]}">{h}</p>')
        else:
            flush_script()
            if plain == 'END':
                current[1].append('<p class="end">END</p>')
            else:
                current[1].append(f'<p>{h}</p>')
    if current is not None:
        flush_script()
    return chapters, plain_all


XHTML_HEAD = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
              '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
              'lang="en" xml:lang="en">\n<head>\n<meta charset="utf-8"/>\n<title>{title}</title>\n'
              '<link rel="stylesheet" type="text/css" href="book.css"/>\n</head>\n<body{cls}>\n')
XHTML_FOOT = '</body>\n</html>\n'


def page(title, inner, cls=''):
    c = f' class="{cls}"' if cls else ''
    return XHTML_HEAD.format(title=escape(title), cls=c) + inner + XHTML_FOOT


CSS = """\
/* Reflowable: no fixed page size, no fixed body font, so readers can pick their own text size. */
body { margin: 0; line-height: 1.5; }
p { margin: 0 0 0.9em; text-align: left; orphans: 2; widows: 2; }
h1, h2 { font-weight: bold; }

/* No forced page break before a chapter: each chapter is its own file, so readers already start it on a new page.
   Forcing one here made some apps (Apple Books) show a blank page before every chapter. */
h2.chapter { text-align: center; font-size: 1.35em; margin: 1.6em 0 1.4em; page-break-after: avoid; break-after: avoid; }
p.end { text-align: center; margin-top: 2.5em; font-weight: bold; letter-spacing: 0.15em; }

/* Cover: one image, scaled to fit the page without spilling onto a second one */
body.cover { text-align: center; margin: 0; padding: 0; }
body.cover div { margin: 0; padding: 0; }
body.cover img { max-width: 100%; max-height: 100%; }

/* Screenplay passages: Courier, a tinted panel and the standard script layout, so they read as a script.
   All indents are percentages of the panel width, so they hold up on a phone. */
.script {
  font-family: "Courier New", Courier, "Liberation Mono", monospace;
  font-size: 0.9em;
  line-height: 1.35;
  background-color: rgba(127, 127, 127, 0.12);
  border-left: 0.25em solid rgba(127, 127, 127, 0.55);
  padding: 0.9em 0.9em 0.2em 0.9em;
  margin: 1.6em 0;
}
.script p { margin: 0 0 0.9em; font-family: "Courier New", Courier, "Liberation Mono", monospace; }
.script .sp-slug { font-weight: bold; margin-top: 1.1em; page-break-after: avoid; break-after: avoid; }
.script .sp-slug:first-child { margin-top: 0; }
.script .sp-cue { margin: 0 0 0 36%; page-break-after: avoid; break-after: avoid; }
.script .sp-paren { margin: 0 15% 0 26%; page-break-after: avoid; break-after: avoid; }
.script .sp-dial { margin: 0 8% 0.9em 16%; }
.script .sp-trans { text-align: right; margin-top: 1.1em; }
"""


def container_xml():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles>\n    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
            '  </rootfiles>\n</container>\n')


def write_epub(path, chapters, book_id):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    files = {}
    files['OEBPS/book.css'] = CSS
    files['OEBPS/cover.xhtml'] = page(TITLE, f'<div><img src="cover.jpg" alt="{escape(TITLE)} by {escape(AUTHOR)}"/></div>\n', 'cover')
    # No separate title or copyright page: the cover image carries the title, author and copyright line,
    # so the story starts on the page right after the cover.
    toc_items, manifest_ch, spine_ch, ncx_points = [], [], [], []
    for n, blocks in chapters:
        fid = f'ch{n:02d}'
        label = f'Chapter {n}'
        inner = f'<h2 class="chapter" id="{fid}">{label}</h2>\n' + '\n'.join(blocks) + '\n'
        files[f'OEBPS/{fid}.xhtml'] = page(f'{TITLE}: {label}', inner)
        toc_items.append(f'      <li><a href="{fid}.xhtml">{label}</a></li>')
        manifest_ch.append(f'    <item id="{fid}" href="{fid}.xhtml" media-type="application/xhtml+xml"/>')
        spine_ch.append(f'    <itemref idref="{fid}"/>')
        ncx_points.append((fid, label))
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">\n'
           '<head><meta charset="utf-8"/><title>Contents</title></head>\n<body>\n'
           '  <nav epub:type="toc" id="toc">\n    <h1>Contents</h1>\n    <ol>\n'
           + '\n'.join(toc_items) + '\n    </ol>\n  </nav>\n'
           '  <nav epub:type="landmarks" hidden="hidden">\n    <ol>\n'
           '      <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>\n'
           f'      <li><a epub:type="bodymatter" href="{ncx_points[0][0]}.xhtml">Start reading</a></li>\n'
           '    </ol>\n  </nav>\n</body>\n</html>\n')
    files['OEBPS/nav.xhtml'] = nav
    # Older readers use the NCX contents list.
    play = 1
    ncx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">',
           f'  <head><meta name="dtb:uid" content="urn:uuid:{book_id}"/><meta name="dtb:depth" content="1"/>'
           '<meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>',
           f'  <docTitle><text>{escape(TITLE)}</text></docTitle>', '  <navMap>']
    for fid, label in ncx_points:
        ncx.append(f'    <navPoint id="np-{fid}" playOrder="{play}"><navLabel><text>{label}</text></navLabel><content src="{fid}.xhtml"/></navPoint>')
        play += 1
    ncx += ['  </navMap>', '</ncx>', '']
    files['OEBPS/toc.ncx'] = '\n'.join(ncx)
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">urn:uuid:{book_id}</dc:identifier>
    <dc:title>{escape(TITLE)}</dc:title>
    <dc:creator id="creator">{escape(AUTHOR)}</dc:creator>
    <meta refines="#creator" property="file-as">{escape(FILE_AS)}</meta>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
    <dc:language>en</dc:language>
    <dc:date>{now[:10]}</dc:date>
    <dc:rights>{escape(RIGHTS)}</dc:rights>
    <meta property="dcterms:modified">{now}</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="book.css" media-type="text/css"/>
    <item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
{chr(10).join(manifest_ch)}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover" linear="yes"/>
{chr(10).join(spine_ch)}
  </spine>
</package>
"""
    files['OEBPS/content.opf'] = opf
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', container_xml(), compress_type=zipfile.ZIP_DEFLATED)
        for name, data in files.items():
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/cover.jpg', COVER_BYTES, compress_type=zipfile.ZIP_STORED)


def main():
    src = find_source(ARGS.source)
    paras = read_paragraphs(src)
    chapters, plain = build_chapters(paras)
    if not chapters:
        sys.exit('No chapters found. Each chapter must start with a line like  ***1  (see the guide, step 1).')
    nums = [n for n, _ in chapters]
    if nums != list(range(1, len(nums) + 1)):
        sys.exit(f'Chapter markers are out of order or missing a number: {nums}. They must run ***1, ***2, ***3 ... with none skipped.')
    cover = OUT / 'cover.jpg'
    if ARGS.cover:
        cover_bytes = Path(ARGS.cover).read_bytes()
        if cover_bytes[:3] != b'\xff\xd8\xff':
            sys.exit('The cover must be a .jpg file.')
    else:
        make_cover(cover)
        cover_bytes = cover.read_bytes()
    global COVER_BYTES
    COVER_BYTES = cover_bytes
    full_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'https://author-page.inkmotion.art/' + SLUG.lower()))
    epub = OUT / f'{SLUG}.epub'
    write_epub(epub, chapters, full_id)
    n1, blocks1 = chapters[0]
    pv = OUT / 'chapter-1.html'
    pv.write_text(f'<h2 class="chapter">Chapter {n1}</h2>\n' + '\n'.join(blocks1) + '\n', encoding='utf-8')
    words = sum(len(p.split()) for p in plain)
    x = [z for _, bl in chapters for z in bl]
    panels = [str(n) for n, bl in chapters if any(b.startswith('<div class="script">') for b in bl)]
    ital = sum(b.count('<i>') for _, bl in chapters for b in bl)
    pw = sum(len(re.sub('<[^>]+>', '', b).split()) for b in blocks1)
    print(f'Built "{TITLE}" by {AUTHOR}')
    print(f'  chapters: {len(chapters)}   paragraphs: {len(plain)}   words: {words}')
    print(f'  chapters with a screenplay section: {", ".join(panels) if panels else "none"}')
    print(f'  italic passages: {ital}   preview (Chapter 1): {pw} words')
    print(f'  copyright line on cover: {RIGHTS}')
    print(f'Files are in the folder "{OUT}":')
    print(f'  {epub.name}  ({epub.stat().st_size // 1024} KB)  -> lock this, then upload the .enc')
    print(f'  chapter-1.html  -> upload as the free preview')
    print('Open the epub in Apple Books to look it over before you publish.')


main()
