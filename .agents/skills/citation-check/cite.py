#!/usr/bin/env python3
"""Checks the report's citations against the cited sources. Changes nothing.

Usage, from anywhere in the repo:
  cite.py list [FILE...]            each citation in the report (or in FILEs), resolved to its source's pages; exits 1 on a FAIL
  cite.py text KEY [LOCATOR]        prints the cited chapter or section of KEY's source, or all of it
  cite.py quote KEY LOCATOR QUOTE   exits 0 if QUOTE is verbatim in that text; otherwise says where in the source it is
  cite.py --self-test
"""
import functools, html, os, re, subprocess, sys, unicodedata
from collections import namedtuple
from pathlib import Path

# outline: (depth, title, first page) per entry, in order. HTML has a page per line.
Source = namedtuple('Source', 'name unit outline pages')
NUMBER = re.compile(r'(?:chapter\s+)?(\d+(?:\.\d+)*)\.?(?=[\s:]|$)', re.I)
LOCATOR = re.compile(r'(?:chs?|secs?)\.\s*(\d+(?:\.\d+)*)(?:\s*[–-]\s*(\d+(?:\.\d+)*))?')
CITATION = re.compile(r'\[([^\[\]]*@[^\[\]]*)\]')


class Fail(Exception):
    pass


def run(*cmd, data=None):
    try:
        return subprocess.run(cmd, input=data, capture_output=True, text=True, errors='replace', check=True).stdout
    except subprocess.CalledProcessError as e:
        raise Fail(f'{cmd[0]} failed: {e.stderr.strip()}')


def git_path(arg):
    return Path(run('git', 'rev-parse', '--path-format=absolute', arg).strip())


@functools.cache
def bib():
    """Each entry of report/references.bib as {field: value}, by key."""
    text = Path('report/references.bib').read_text()
    return {m[1]: dict(re.findall(r'^\s*(\w+)\s*=\s*\{(.*)\},?$', m[2], re.M))
            for m in re.finditer(r'^@\w+\{([^,\s]+),(.*?)^\}', text, re.M | re.S)}


@functools.cache
def front_digits(pdf):
    """The digits on the PDF's first 20 pages, where a book prints its ISBN."""
    return re.sub(r'\D', '', run('pdftotext', '-l', '20', str(pdf), '-'))


@functools.cache
def source(key):
    """KEY's source: the PDF in docs/books that prints the entry's ISBN, or the page at the entry's url."""
    entry = bib().get(key)
    if entry is None:
        raise Fail(f'{key} is not in report/references.bib')
    if 'isbn' in entry:
        # docs/books is untracked, so a worktree has none: read the main checkout's.
        books = git_path('--git-common-dir').parent / 'docs/books'
        isbn = re.sub(r'\D', '', entry['isbn'])
        pdf = next((p for p in sorted(books.glob('*.pdf')) if isbn in front_digits(p)), None)
        if pdf is None:
            raise Fail(f'no PDF in {books} prints ISBN {entry["isbn"]}')
        xml = run('pdftohtml', '-xml', '-i', '-q', '-stdout', '-f', '1', '-l', '1', str(pdf))
        outline, depth = [], 0
        for m in re.finditer(r'<(/?)outline>|<item page="(\d+)">(.*?)</item>', xml):
            if m[2]:
                outline.append((depth, html.unescape(m[3]), int(m[2])))
            else:
                depth += -1 if m[1] else 1
        return Source(pdf.name, 'PDF pp.', outline, run('pdftotext', str(pdf), '-').split('\f')[:-1])
    if 'url' in entry:
        md = run('pandoc', '-f', 'html', '-t', 'markdown_strict-raw_html', '--wrap=none', data=run('curl', '-fsSL', entry['url']))
        lines = [re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line) for line in md.splitlines()]
        outline = [(len(m[1]), m[2], i) for i, line in enumerate(lines, 1) if (m := re.match(r'(#+) (.*)', line))]
        return Source(entry['url'], 'lines', outline, lines)
    raise Fail(f'{key} has neither an isbn nor a url in report/references.bib')


def number(title):
    m = NUMBER.match(title)
    return m and m[1]


def span(outline, n, end, exact):
    """First and last page of the outline entry numbered N, subsections included; END is the source's last page.
    EXACT when each entry starts its own page, as each line of HTML does."""
    found = [i for i, (_, title, _) in enumerate(outline) if number(title) == n]
    if not found:
        raise Fail(f'the source has no chapter or section {n}')
    i = min(found, key=lambda i: outline[i][0])  # a chapter, not a numbered list inside one
    depth, _, first = outline[i]
    for d, title, page in outline[i + 1:]:
        m = number(title)
        if d < depth or d == depth and m and not (m + '.').startswith(n + '.'):
            # A chapter starts on a new page; a section may start on the page where the one before it ends.
            # shortcut: so a section's range ends on the next one's first page, and a passage from there passes; cut at its heading if that misleads.
            return first, page - 1 if exact or '.' not in (m or '') else page
    return first, end


def locate(key, locator=''):
    """KEY's source, and the first and last page LOCATOR cites: all of it when there is no locator."""
    src = source(key)
    if not locator:
        return src, 1, len(src.pages)
    m = LOCATOR.fullmatch(locator.strip())
    if not m:
        raise Fail(f'cite.py reads only ch., chs., sec. and secs.; find "{locator}" in `cite.py text {key}`')
    exact, end = src.unit == 'lines', len(src.pages)
    return src, span(src.outline, m[1], end, exact)[0], span(src.outline, m[2] or m[1], end, exact)[1]


def norm(text):
    """TEXT without case, punctuation or spacing, so a passage matches across line breaks and hyphenation."""
    return re.sub(r'[\W_]', '', unicodedata.normalize('NFKC', text).casefold())


def where(src, passage):
    """The page that holds PASSAGE, with the outline entries it sits under, or None."""
    page = next((p for p, text in enumerate(src.pages, 1) if norm(passage) in norm(text)), None)
    if page is None:
        return None
    path = {}
    for d, title, first in src.outline:
        if first > page:
            break
        path = {k: v for k, v in path.items() if k < d} | {d: title}
    return f'{src.unit} {page}: ' + ' > '.join(path.values())


def citations(line):
    """(key, locator, claim) for each citation on LINE; the claim is its sentence up to the citation."""
    for m in CITATION.finditer(line):
        claim = re.split(r'(?<=[.!?])\s+', line[:m.start()])[-1].strip()
        for part in m[1].split(';'):
            if c := re.search(r'(?<!\w)-?@([^\s,;]+?)(?:\s*,\s*(.*?))?\s*$', part):
                yield c[1], c[2] or '', claim


def report_files():
    """The report's files, in the order report/pandoc.yaml builds them."""
    return [Path('report', f) for f in re.findall(r'\$\{\.\}/(\S+\.md)', Path('report/pandoc.yaml').read_text())]


def main(cmd='', *args):
    if cmd == '--self-test':
        return self_test()
    os.chdir(git_path('--show-toplevel'))
    if cmd == 'list':
        status = 0
        for path in [Path(a) for a in args] or report_files():
            for no, line in enumerate(path.read_text().splitlines(), 1):
                for key, locator, claim in citations(line):
                    cited = f'{path}:{no}: [@{key}' + (f', {locator}]' if locator else ']')
                    try:
                        src, first, last = locate(key, locator)
                        print(f'{cited} -> {src.name}, {src.unit} {first}-{last}\n    {claim}')
                    except Fail as e:
                        print(f'FAIL {cited}: {e}')
                        status = 1
        return status
    if cmd == 'text' and 1 <= len(args) <= 2:
        src, first, last = locate(*args)
        print('\n'.join(src.pages[first - 1:last]))
        return 0
    if cmd == 'quote' and len(args) == 3:
        key, locator, passage = args
        src, first, last = locate(key, locator)
        cited = f'{src.name}, {src.unit} {first}-{last}'
        if len(norm(passage)) < 30:
            raise Fail('quote at least a sentence')
        if norm(passage) in norm('\n'.join(src.pages[first - 1:last])):
            print(f'OK: in {cited}')
            return 0
        found = where(src, passage)
        print(f'FAIL: not in {cited}; ' + (f'it is on {found}' if found else 'nor on any one page of the source'))
        return 1
    print(__doc__)
    return 2


def self_test():
    assert list(citations('First. Then a claim [@a, ch. 2; see @b-c].')) == [('a', 'ch. 2', 'Then a claim'), ('b-c', '', 'Then a claim')]
    assert not list(citations('Mail [me@x.org] about Table \\ref{tab:x}.'))
    flat = [(1, '2 Decomposition', 10), (1, '2.1 What', 10), (1, '2.1.1 Why', 11), (1, '2.2 Defining', 14),
            (1, 'Summary', 20), (1, '3 IPC', 22)]
    assert span(flat, '2', 99, False) == (10, 21)
    assert span(flat, '2.1', 99, False) == (10, 14)
    assert span(flat, '3', 99, False) == (22, 99)
    nested = [(1, 'PART I', 1), (2, 'CHAPTER 1: Essential', 2), (3, 'Defined', 3), (2, 'CHAPTER 2: Customer', 9),
              (3, 'A template', 10), (4, '1. Introduction', 10), (1, 'PART II', 20)]
    assert span(nested, '1', 99, False) == (2, 8)
    assert span(nested, '2', 99, False) == (9, 19)
    page = [(2, '13.2. Isolation \\#', 44), (3, 'Important', 60), (3, '13.2.1. Read Committed', 128),
            (3, '13.2.2. Repeatable Read', 166), (2, 'Submit correction', 273)]
    assert span(page, '13.2.1', 300, True) == (128, 165)
    assert span(page, '13.2.2', 300, True) == (166, 272)
    try:
        span(flat, '4', 99, False)
        raise AssertionError('a missing section resolved')
    except Fail:
        pass
    assert LOCATOR.fullmatch('secs. 2.2.2–2.2.4').groups() == ('2.2.2', '2.2.4')
    assert norm('Plan to re-\nsolve all “TBDs” ﬁrst') == norm('plan to resolve all TBDs first')
    src = Source('book', 'PDF pp.', nested, ['', 'Essential text', 'Defined: plan to resolve all TBDs first'])
    assert where(src, 'plan to resolve all TBDs first') == 'PDF pp. 3: PART I > CHAPTER 1: Essential > Defined'
    print('self-test ok')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(*sys.argv[1:]))
    except Fail as e:
        sys.exit(f'FAIL: {e}')
