import shutil, subprocess
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
rng = np.random.default_rng(7); N = 230; W, H = 1.15, 1.5
P = np.c_[rng.uniform(-W + .05, W - .05, N), rng.uniform(.05, H - .05, N)]
cols = np.array(["#ff4d6d", "#ffb703", "#06a77d", "#118ab2", "#8338ec", "#fb5607"])[rng.integers(0, 6, N)]
C0 = np.array([-.55, 1.12]); R = .24; GROUP = (np.abs(P - C0) < R - .02).all(1)
def squash(p, s):
    p = np.atleast_2d(p); x, z = p.T; t = z / H
    return np.c_[x * (1 + .3 * s * (1 - (2 * t - 1) ** 2)), z * (1 - .3 * s)]
def outline(s):
    t = np.linspace(0, 1, 50); e = np.r_[np.c_[-W + 2 * W * t, 0 * t], np.c_[W + 0 * t, H * t], np.c_[W - 2 * W * t, H + 0 * t], np.c_[-W + 0 * t, H - H * t]]
    return squash(e, s)
BG = "#fdf3e7"; INK = "#3b2740"
def scene(s, cap, sub, mode=0, flash=0):
    f = plt.figure(figsize=(9.6, 5.4), facecolor=BG); a = f.add_axes([0, 0, 1, 1]); a.set_xlim(-2.67, 2.67); a.set_ylim(-.32, 2.68); a.set_aspect("equal"); a.axis("off")
    a.add_patch(Rectangle((-2, -.1), 4, .1, color="#b08968"))
    a.add_patch(Polygon(outline(s), closed=True, fc="#f9b4c3", ec="#d6577b", lw=2.5, alpha=.65))
    Q = squash(P, s); a.scatter(Q[:, 0], Q[:, 1], s=46, c=cols, edgecolors="white", linewidths=.5, zorder=3)
    top = H * (1 - .3 * s); a.add_patch(Rectangle((-1.5, top + .01), 3, .14, fc="#6c7a89", ec="#39424e", lw=1.5, zorder=5))
    if mode:
        g = squash(P[GROUP], s); c1 = squash(C0, s)[0]
        if mode > 1:
            a.add_patch(Rectangle(C0 - R, 2 * R, 2 * R, fill=False, ec="#118ab2", lw=3, ls=(0, (4, 3)), zorder=7)); a.scatter(P[GROUP, 0], P[GROUP, 1], s=28, c="#118ab2", edgecolors="white", linewidths=.4, zorder=7)
        a.add_patch(Rectangle(c1 - R, 2 * R, 2 * R, fill=False, ec="#d90429", lw=3.5, zorder=8)); a.scatter(g[:, 0], g[:, 1], s=70, c="#d90429", edgecolors="white", linewidths=.6, zorder=8)
        if mode > 1: a.add_patch(FancyArrowPatch(C0, c1, arrowstyle="-|>", mutation_scale=24, lw=4, color=INK, zorder=9, shrinkA=0, shrinkB=0))
    a.text(0, 2.42, cap, ha="center", fontsize=25, weight="bold", color=INK); a.text(0, 2.17, sub, ha="center", fontsize=15, color=INK)
    if flash: f.patches.append(Rectangle((0, 0), 1, 1, transform=f.transFigure, fc="white", alpha=flash))
    return f
tmp = Path("jf"); shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(); n = 0
def save(f, r=1):
    global n
    for _ in range(r): f.savefig(tmp / f"{n:05d}.png", dpi=100); n += 1
    plt.close(f)
save(scene(0, "A block of jelly", "It's full of tiny sprinkles, scattered at random."), 26)
for fl in (.9, .6, .3): save(scene(0, "Click! First 3D photo", "This is the unloaded scan.", flash=fl))
save(scene(0, "Click! First 3D photo", "This is the unloaded scan."), 18)
for s in (1 - np.cos(np.linspace(0, np.pi, 30))) / 2: save(scene(s, "Now squeeze it", "The sprinkles move with the jelly."))
for fl in (.9, .6, .3): save(scene(1, "Click! Second 3D photo", "This is the loaded scan.", flash=fl))
save(scene(1, "Click! Second 3D photo", "This is the loaded scan."), 18)
save(scene(1, "Find one little group", "This red group of sprinkles has a pattern we can recognise.", 1), 28)
save(scene(1, "Where did it start?", "The blue box shows where the same group was before squeezing.", 2), 28)
save(scene(1, "That arrow is the displacement", "Do this for every little group, and you've mapped the whole movement.", 2), 44)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", str(tmp / "%05d.png"), "-c:v", "h264_videotoolbox", "-pix_fmt", "yuv420p", "-b:v", "700k", "-movflags", "+faststart", "media/jelly.mp4"], check=True)
shutil.rmtree(tmp); print(n / 12, "s", GROUP.sum())
