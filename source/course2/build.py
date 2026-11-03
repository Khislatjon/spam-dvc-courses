import json, re, sys
from pathlib import Path
L = [("0", "index", "SPAM Commands Course", ""), ("1", "1_reading_a_command", "Reading a Command", ""), ("2", "2_spam_reg", "Registration Flags", ""), ("3", "3_spam_ldic", "Local DVC Flags", ""), ("4", "4_masks", "Mask Flags", ""), ("5", "5_speed", "Speed Flags", ""), ("6", "6_pixel_search", "Pixel Search Flags", ""), ("7", "7_your_own_run", "Build Your Own Run", "")]
PUB = "--pub" in sys.argv; urls = json.loads(Path("urls.json").read_text()) if PUB and Path("urls.json").exists() else {}
out = Path("dist"); out.mkdir(exist_ok=True)
css, dom = Path("style.css").read_text(), Path("dom.js").read_text()
R = json.load(open("exp/results.json")); R2 = json.load(open("exp/results2.json")) if Path("exp/results2.json").exists() else {}
VOX = '<svg viewBox="0 0 74 74" aria-hidden="true"><path d="M37 6 67 21 37 36 7 21Z" fill="#ffd166"/><path d="M7 21 37 36V68L7 53Z" fill="#f4a72c"/><path d="M67 21 37 36V68L67 53Z" fill="#e58a1f"/><circle cx="19" cy="38" r="5.5" fill="#fff"/><circle cx="30" cy="44" r="5.5" fill="#fff"/><circle cx="20" cy="38.5" r="2.6" fill="#1d2b4a"/><circle cx="31" cy="44.5" r="2.6" fill="#1d2b4a"/><path d="M18 50q6 6 12 5" fill="none" stroke="#1d2b4a" stroke-width="2.4" stroke-linecap="round"/><circle cx="52" cy="40" r="8" fill="none" stroke="#1d2b4a" stroke-width="3"/><path d="M47 47l-6 8" stroke="#1d2b4a" stroke-width="3.5" stroke-linecap="round"/></svg>'
link = lambda s: urls.get(s, s + ".html")
def asc(t):
    parts = re.split(r"(<script>.*?</script>)", t, flags=re.S)
    for i, p in enumerate(parts):
        parts[i] = "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) for c in p) if p.startswith("<script>") else p.encode("ascii", "xmlcharrefreplace").decode()
    return "".join(parts)
DATA = "var REG=" + json.dumps(R["reg"]) + ";var GRID=" + json.dumps(R["grid"]) + ";var NOPF=" + json.dumps(R["no_pf"]) + ";var MASK=" + json.dumps(R["mask"]) + ";var NP=" + json.dumps(R["np"]) + ";var NODEMAP=" + Path("exp/nodemap.json").read_text() + ";var DATA0=" + json.dumps(R2["none"]) + ";var DATA1=" + json.dumps(R2["ps"]) + ";"
H = json.loads(Path("../home.json").read_text()) if Path("../home.json").exists() else {}
HOME = H.get("home", "") if "--pub" in sys.argv else "../START%20HERE.html"
C2 = H.get("course2", "") if "--pub" in sys.argv else "../2%20SPAM%20Commands/START%20HERE.html"
for i, (n, stem, title, _) in enumerate(L):
    b = Path(f"lessons/{stem}.html").read_text()
    b = re.sub(r"<vox>(.*?)</vox>", lambda m: f'<div class="vox">{VOX}<div class="say"><span class="who">Vox says</span>{m.group(1)}</div></div>', b, flags=re.S)
    b = re.sub(r'<real t="(.*?)">(.*?)</real>', lambda m: f'<div class="real"><div class="t">Real SPAM &middot; {m.group(1)}</div><div>{m.group(2)}</div></div>', b, flags=re.S)
    b = re.sub(r'href="@(\w+)"', lambda m: f'href="{link(m.group(1))}"', b)
    top = bot = ""
    if not i: top = f'<nav class="top"><a href="{HOME}">&larr; All courses</a></nav>'
    if i:
        top = f'<nav class="top"><span><a href="{link("index")}">&larr; Course map</a> &middot; <a href="{HOME}">All courses</a></span><span>Lesson {n} of 7</span></nav>'
        prev = f'<a href="{link(L[i-1][1])}">&larr; {L[i-1][2]}</a>' if i > 1 else f'<a href="{link("index")}">&larr; Course map</a>'
        nxt = f'<a href="{link(L[i+1][1])}">Next: {L[i+1][2]} &rarr;</a>' if i < 7 else f'<a href="{HOME}">Finish: back to all courses &rarr;</a>'
        bot = f'<nav class="next">{prev}{nxt}</nav>'
    head = f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700&family=Nunito:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">\n<style>\n{css}</style>\n'
    t = head + f"<main>\n{top}\n{b}\n{bot}\n</main>\n"
    sc = re.findall(r"<script>.*?</script>", t, flags=re.S); t = re.sub(r"<script>.*?</script>", "", t, flags=re.S)
    t = asc(t + f"<script>\n{dom}\n{DATA}\n</script>\n" + "".join(sc)); assert t.isascii(); (out / f"{stem}.html").write_text(t); print(stem, round(len(t) / 1024), "KB")
