import pickle, subprocess, shutil, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = pickle.load(open("frames_synth.pkl", "rb")); ref = D["win"]; BG = "#10151f"; FG = "#eef2f8"; AC = "#ffd166"; GOOD = "#59d6a4"; BAD = "#ff7a59"
plt.rcParams.update({"font.size": 13, "font.family": "DejaVu Sans", "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG, "axes.edgecolor": "#55607a", "figure.facecolor": BG, "axes.facecolor": BG})
tmp = Path("fr"); shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(); n = [0]
def save(fig, rep=1):
    for _ in range(rep):
        fig.savefig(tmp / f"{n[0]:05d}.png", dpi=100); n[0] += 1
    plt.close(fig)
def card(title, sub, rep):
    f = plt.figure(figsize=(9.6, 5.4)); f.text(.5, .6, title, ha="center", fontsize=28, weight="bold", color=AC); f.text(.5, .42, sub, ha="center", fontsize=16, linespacing=1.5); save(f, rep)
def frames(fr, label, col, emax):
    errs = [x["err"] for x in fr]; idx = list(range(0, min(14, len(fr)))) + list(range(14, len(fr), 4))
    if idx[-1] != len(fr) - 1: idx.append(len(fr) - 1)
    for i in idx:
        x = fr[i]; f = plt.figure(figsize=(9.6, 5.4)); f.suptitle(label, fontsize=17, color=col, y=.97, weight="bold")
        gs = f.add_gridspec(2, 3, left=.05, right=.97, top=.88, bottom=.1, hspace=.45, wspace=.15, height_ratios=[1.3, 1])
        for j, (im, t, kw) in enumerate(((ref, "Unloaded window (stays still)", dict(cmap="gray", vmin=0, vmax=255)), (x["w"], "Loaded window, moved by the guess", dict(cmap="gray", vmin=0, vmax=255)), (ref - x["w"], "Difference (grey = match)", dict(cmap="gray", vmin=-160, vmax=160)))):
            a = f.add_subplot(gs[0, j]); a.imshow(im, **kw); a.set_title(t, fontsize=12); a.axis("off")
        a = f.add_subplot(gs[1, :2]); a.plot(range(i + 1), errs[:i + 1], color=col, lw=2.5, marker="o", ms=3); a.set_xlim(0, 50); a.set_ylim(0, emax); a.set_xlabel("Iteration"); a.set_ylabel("Error"); a.grid(alpha=.2)
        st = {0: "Starting", 1: "Hit the 50-iteration limit (status 1)", 2: "Converged (status 2)"}.get(x["st"], str(x["st"]))
        if x["k"] and x["st"] == 1 and i < len(fr) - 1: st = "Iterating"
        f.text(.69, .34, f"Iteration  {x['k']}", fontsize=14); f.text(.69, .27, f"Guess in y  {x['t'][1]:.1f} vx", fontsize=14); f.text(.69, .2, f"Error  {x['err']:.1f}", fontsize=14); f.text(.69, .11, st, fontsize=12.5, color=col, weight="bold")
        save(f, 18 if i == len(fr) - 1 else (4 if i < 14 else 2))
ema = max(x["err"] for x in D["fa"] + D["fb"]) * 1.1
card("Real SPAM, made-up scan", "One 51 vx window from a made-up 3D sponge. The true shift in y is 26 vx.\nThis is the real spam.DIC.register, one iteration at a time.", 40)
card("Run 1: a far first guess", "The first guess in y is 6 vx, which is 20 vx from the true match.", 30)
frames(D["fa"], "Far first guess: SPAM gets stuck", BAD, ema)
card("Run 2: a close first guess", "Same window, same scans. Only the first guess changes.", 30)
frames(D["fb"], "Close first guess: SPAM finds it", GOOD, ema)
card("Same window, two answers", "Far guess: stuck at 3.9 vx, error 60.3, 50 iterations\nClose guess: 26.0 vx, error 0.3, converged in 3 iterations", 50)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", str(tmp / "%05d.png"), "-c:v", "h264_videotoolbox", "-pix_fmt", "yuv420p", "-b:v", "550k", "-movflags", "+faststart", "media/synthetic_window_iterations.mp4"], check=True)
shutil.rmtree(tmp); print("ok")
