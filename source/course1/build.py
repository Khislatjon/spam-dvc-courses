import base64, json, re, sys
from pathlib import Path
L = [("0", "index", "SPAM DVC Course", ""),
     ("1", "1_sticker_game", "The Sticker Game", "What DVC measures"),
     ("2", "2_scoring_a_match", "Scoring a Match", "Error and correlation"),
     ("3", "3_phi_instruction_card", "Phi, the Instruction Card", "The 12 numbers SPAM finds"),
     ("4", "4_the_hiker", "The Hiker in the Fog", "How SPAM improves a guess"),
     ("5", "5_blurry_glasses", "The Blurry Glasses", "Binning and registration"),
     ("6", "6_army_of_windows", "The Army of Windows", "Nodes, windows and masks"),
     ("7", "7_treasure_search", "The Treasure Search", "Pixel search and false matches"),
     ("8", "8_whole_film", "The Whole Film", "Everything together, and a final quiz")]
PUBLIC = "--public" in sys.argv
uf = Path("urls_public.json" if PUBLIC else "urls.json")
urls = json.loads(uf.read_text()) if uf.exists() and "--pub" in sys.argv else {}
out = Path(("public_" if PUBLIC else "") + ("dist_pub" if "--pub" in sys.argv else "dist")); out.mkdir(exist_ok=True)
LES = "lessons"
css, lib, dom = (Path(f).read_text() for f in ("style.css", "lib.js", "dom.js"))
lib = lib[:lib.index('if (typeof module')]
VOX = '<svg viewBox="0 0 74 74" aria-hidden="true"><path d="M37 6 67 21 37 36 7 21Z" fill="#ffd166"/><path d="M7 21 37 36V68L7 53Z" fill="#f4a72c"/><path d="M67 21 37 36V68L67 53Z" fill="#e58a1f"/><circle cx="19" cy="38" r="5.5" fill="#fff"/><circle cx="30" cy="44" r="5.5" fill="#fff"/><circle cx="20" cy="38.5" r="2.6" fill="#1d2b4a"/><circle cx="31" cy="44.5" r="2.6" fill="#1d2b4a"/><path d="M18 50q6 6 12 5" fill="none" stroke="#1d2b4a" stroke-width="2.4" stroke-linecap="round"/><circle cx="52" cy="40" r="8" fill="none" stroke="#1d2b4a" stroke-width="3"/><path d="M47 47l-6 8" stroke="#1d2b4a" stroke-width="3.5" stroke-linecap="round"/></svg>'
link = lambda stem: urls.get(stem, stem + ".html")
def asc(t):
    parts = re.split(r"(<script>.*?</script>)", t, flags=re.S)
    for i, p in enumerate(parts):
        if p.startswith("<script>"): parts[i] = "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) for c in p)
        else: parts[i] = p.encode("ascii", "xmlcharrefreplace").decode()
    return "".join(parts)
H = json.loads(Path("../home.json").read_text()) if Path("../home.json").exists() else {}
HOME = H.get("home", "") if "--pub" in sys.argv else "../START%20HERE.html"
C2 = H.get("course2", "") if "--pub" in sys.argv else "../2%20SPAM%20Commands/START%20HERE.html"
for i, (n, stem, title, sub) in enumerate(L):
    body = Path(f"{LES}/{stem}.html").read_text()
    body = re.sub(r"<vox>(.*?)</vox>", lambda m: f'<div class="vox">{VOX}<div class="say"><span class="who">Vox says</span>{m.group(1)}</div></div>', body, flags=re.S)
    body = re.sub(r'<real t="(.*?)">(.*?)</real>', lambda m: f'<div class="real"><div class="t">Real SPAM &middot; {m.group(1)}</div><div>{m.group(2)}</div></div>', body, flags=re.S)
    body = re.sub(r'<movie src="(.*?)" label="(.*?)"></movie>', lambda m: f'<video controls playsinline preload="metadata" aria-label="{m.group(2)}" src="data:video/mp4;base64,{base64.b64encode(Path(m.group(1)).read_bytes()).decode()}"></video>', body)
    for a, _, b, _ in []: pass
    body = re.sub(r'href="@(\w+)"', lambda m: f'href="{link(m.group(1))}"', body)
    top = bot = ""
    if not i: top = f'<nav class="top"><a href="{HOME}">&larr; All courses</a></nav>'
    if i:
        top = f'<nav class="top"><span><a href="{link("index")}">&larr; Course map</a> &middot; <a href="{HOME}">All courses</a></span><span>Lesson {n} of 8</span></nav>'
        prev = f'<a href="{link(L[i-1][1])}">&larr; {L[i-1][2]}</a>' if i > 1 else f'<a href="{link("index")}">&larr; Course map</a>'
        nxt = f'<a href="{link(L[i+1][1])}">Next: {L[i+1][2]} &rarr;</a>' if i < 8 else f'<a href="{HOME}">Finish: back to all courses &rarr;</a>'
        bot = f'<nav class="next">{prev}{nxt}</nav>'
    head = f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700&family=Nunito:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">\n<style>\n{css}</style>\n'
    body = body.replace("@@COURSE2", C2) if "body" in dir() else body
    t = head + f"<main>\n{top}\n{body}\n{bot}\n</main>\n"
    scripts = re.findall(r"<script>.*?</script>", t, flags=re.S)
    t = re.sub(r"<script>.*?</script>", "", t, flags=re.S)
    t += f"<script>\n{lib}\n{dom}\n</script>\n" + "".join(scripts)
    t = asc(t)
    assert t.isascii(); (out / f"{stem}.html").write_text(t); print(stem, round(len(t) / 1024), "KB")
