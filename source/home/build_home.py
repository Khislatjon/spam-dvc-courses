import json, re, sys
from pathlib import Path
PUB = "--pub" in sys.argv
css = Path("../course2/style.css").read_text() + """
.courses { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }
.courses > * { min-width: 0; }
.course { background: var(--panel); border: 2px solid var(--line); border-radius: 18px; padding: 20px; display: grid; gap: 12px; align-content: start; }
.course .num { background: none; padding: 0; font-family: var(--head); font-size: 15px; color: var(--coral); font-weight: 700; }
.course h2 { font-size: 30px; }
.course ol { margin: 0; padding-left: 22px; display: grid; gap: 3px; font-size: 15.5px; color: var(--muted); }
.course .facts { display: flex; flex-wrap: wrap; gap: 8px; }
.course .facts span { background: var(--soft); border-radius: 999px; padding: 3px 11px; font-size: 13.5px; font-weight: 700; }
a.start { display: inline-block; justify-self: start; background: var(--blue); color: var(--panel); text-decoration: none; font-weight: 800; border-radius: 12px; padding: 10px 18px; font-size: 17px; }
a.start:hover { filter: brightness(1.08); }
a.start:focus-visible { outline: 3px solid var(--sun); outline-offset: 3px; }
"""
VOX = re.search(r"VOX = '(.*?)'\n", Path("../course2/build.py").read_text()).group(1)
links = {"c1": "https://claude.ai/artifact/8ZuF9Yy25nJZu4TwzsiL8a", "c2": "https://claude.ai/artifact/XPwgTQj1o6zpE1aY9kBnyQ"} if PUB else {"c1": "1%20How%20SPAM%20DVC%20Works/START%20HERE.html", "c2": "2%20SPAM%20Commands/START%20HERE.html"}
body = f'''<header>
  <div class="ep">Free hands-on courses</div>
  <h1>SPAM DVC Courses</h1>
  <p class="lede">Learn how digital volume correlation tracks movement inside 3D scans, and how to run it yourself with SPAM.</p>
</header>
<div class="vox">{VOX}<div class="say"><span class="who">Vox says</span>Hi, I'm Vox! New to DVC? Start with Course 1, which builds the ideas with games and labs. Already know how it works? Jump straight to Course 2 and learn the commands. You can come back here from any lesson.</div></div>
<div class="courses">
  <section class="course" aria-labelledby="c1">
    <div class="num">Course 1 &middot; the ideas</div>
    <h2 id="c1">How SPAM DVC Works</h2>
    <p>From a squeezed block of jelly to a full displacement field. No maths background needed, and every idea comes with a lab you can play with.</p>
    <div class="facts"><span>8 lessons</span><span>About 90 minutes</span><span>2 videos</span></div>
    <ol>
      <li>The Sticker Game</li><li>Scoring a Match</li><li>Phi, the Instruction Card</li><li>The Hiker in the Fog</li><li>The Blurry Glasses</li><li>The Army of Windows</li><li>The Treasure Search</li><li>The Whole Film</li>
    </ol>
    <a class="start" href="{links["c1"]}">Start Course 1 &rarr;</a>
  </section>
  <section class="course" aria-labelledby="c2">
    <div class="num">Course 2 &middot; the commands</div>
    <h2 id="c2">SPAM Commands</h2>
    <p>Learn every key flag from real SPAM runs on a test sample where the true answer is known, then build your own commands.</p>
    <div class="facts"><span>7 lessons</span><span>About 75 minutes</span><span>Command builder</span></div>
    <ol>
      <li>Reading a Command</li><li>Registration Flags</li><li>Local DVC Flags</li><li>Mask Flags</li><li>Speed Flags</li><li>Pixel Search Flags</li><li>Build Your Own Run</li>
    </ol>
    <a class="start" href="{links["c2"]}">Start Course 2 &rarr;</a>
  </section>
</div>
<section>
  <h2>How these courses work</h2>
  <ul class="keys">
    <li><b>Vox</b> explains each idea in everyday words.</li>
    <li><b>Labs</b> let you try it, with numbers calculated live or taken from real SPAM runs.</li>
    <li><b>Real SPAM</b> boxes show where each idea lives in SPAM's own code.</li>
    <li>Every lesson links back here, so you can switch courses at any time.</li>
  </ul>
</section>
<div class="real"><div class="t">Real SPAM &middot; credits</div><div>SPAM (Software for Practical Analysis of Materials) is open-source software by its own developers. If you use it, please cite Stamati et al., <i>spam: Software for Practical Analysis of Materials</i>, Journal of Open Source Software, 2020. These courses are independent, and are not made by or endorsed by the SPAM team. They were written using SPAM 0.8.1.4. Check the official documentation for anything important.</div></div>'''
t = f'<title>SPAM DVC Courses</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700&family=Nunito:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">\n<style>\n{css}</style>\n<main>\n{body}\n</main>\n'
t = t.encode("ascii", "xmlcharrefreplace").decode(); out = Path("dist"); out.mkdir(exist_ok=True); (out / ("home_pub.html" if PUB else "home.html")).write_text(t); print("home", PUB, len(t))
