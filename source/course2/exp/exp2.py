import json, subprocess, time
from pathlib import Path
import numpy as np, pandas as pd, tifffile
from scipy import ndimage as ndi
BIN = Path("/opt/anaconda3/bin"); ref = tifffile.imread("unloaded.tif").astype(np.float32); S = ref.shape; rng = np.random.default_rng(5)
def U(Z, Y, X):
    d = ((Z - 120) / 62) ** 2 + ((Y - 150) / 58) ** 2 + ((X - 110) / 60) ** 2; b = np.exp(-d)
    return (Z - 120) * -0.02 + 3 - 3 * b, (Y - 110) * .006 + 12 + 30 * b, (X - 110) * .006 - 5 + 4 * b
z, y, x = np.mgrid[0:S[0], 0:S[1], 0:S[2]].astype(np.float32); Z, Y, X = z.copy(), y.copy(), x.copy()
for _ in range(6): a, b, c = U(Z, Y, X); Z, Y, X = z - a, y - b, x - c
d = ndi.map_coordinates(ref, [Z, Y, X], order=1, mode="nearest") + rng.normal(0, 6, S); tifffile.imwrite("loaded_h.tif", np.clip(d, 0, 255).astype(np.uint8)); del Z, Y, X, z, y, x
l = tifffile.imread("loaded_h.tif"); s = [q // 2 * 2 for q in S]; tifffile.imwrite("l2h.tif", l[:s[0], :s[1], :s[2]].reshape(s[0] // 2, 2, s[1] // 2, 2, s[2] // 2, 2).astype(np.float32).mean((1, 3, 5)).astype(np.uint8))
def run(cmd):
    t = time.time(); r = subprocess.run([str(BIN / cmd[0])] + [str(c) for c in cmd[1:]], capture_output=True, text=True); return time.time() - t, r
def score(d):
    g = d[d.returnStatus > 0]; tu = np.array(U(g.Zpos.values, g.Ypos.values, g.Xpos.values)).T; e = np.sqrt(((g[["Zdisp", "Ydisp", "Xdisp"]].values - tu) ** 2).sum(1)); return dict(tried=int((d.returnStatus > -5).sum()), conv=int((d.returnStatus == 2).sum()), limit=int((d.returnStatus == 1).sum()), rms=round(float(np.sqrt((e ** 2).mean())), 2), wrong=int((e > 2).sum()), its=int(d.iterations.sum()))
R = {}; t, r = run(["spam-reg", "unloaded.tif", "loaded_h.tif", "-mf1", "mask.tif", "-bb", 4, "-be", 2, "-od", ".", "-pre", "hreg"]); q = pd.read_csv("hreg-registration.tsv", sep="\t").iloc[0]; R["reg"] = dict(status=int(q.returnStatus), Y=round(float(q.Ydisp), 1), time=round(t, 1)); print(R["reg"], flush=True)
pf = "hreg-registration.tsv"; dv = lambda pre, *a: run(["spam-ldic", "unloaded.tif", "loaded_h.tif", "-mf1", "mask.tif", "-mc", .5, *a, "-ns", 50, "-hws", 25, "-glt", 5, "-np", 4, "-od", ".", "-pre", pre])
t, r = dv("hno", "-pf", pf); o = score(pd.read_csv("hno-ldic.tsv", sep="\t")); o.update(name="No search", time=round(t, 1), positions=0, t_search=0); R["none"] = o; print(o, flush=True)
R["ps"] = []
for name, sr in (("Too small", (-3, 3, -3, 3, -3, 3)), ("About right", (-5, 5, -18, 18, -5, 5)), ("Too wide", (-40, 40, -40, 40, -40, 40))):
    p = f"h{sr[1]}"; t, r = run(["spam-pixelSearch", "u2.tif", "l2h.tif", "-mf1", "m2.tif", "-mc", .5, "-pf", pf, "-pfb", .5, "-sr", *sr, "-ns", 25, "-hws", 12, "-glt", 5, "-np", 4, "-od", ".", "-pre", p]); t2, r2 = dv(p + "d", "-pf", p + "-pixelSearch.tsv", "-pfb", 2); o = score(pd.read_csv(p + "d-ldic.tsv", sep="\t")); o.update(name=name, sr=sr, t_search=round(t, 1), t_dvc=round(t2, 1), positions=(sr[1] - sr[0] + 1) * (sr[3] - sr[2] + 1) * (sr[5] - sr[4] + 1)); R["ps"].append(o); print(o, flush=True)
t2, r2 = dv("hbad", "-pf", "h18-pixelSearch.tsv"); o = score(pd.read_csv("hbad-ldic.tsv", sep="\t")); o.update(time=round(t2, 1)); R["forgot_pfb"] = o; print("forgot", o, flush=True)
for g in (5, 60, 100):
    t, r = run(["spam-ldic", "unloaded.tif", "loaded.tif", "-pf", "reg_4_2-registration.tsv", "-glt", g, "-ns", 50, "-hws", 25, "-np", 4, "-od", ".", "-pre", f"glt{g}"]); dd = pd.read_csv(f"glt{g}-ldic.tsv", sep="\t"); R[f"glt{g}"] = dict(tried=int((dd.returnStatus > -5).sum()), conv=int((dd.returnStatus == 2).sum()), time=round(t, 1)); print(g, R[f"glt{g}"], flush=True)
json.dump(R, open("results2.json", "w"), indent=1, default=str); print("DONE")
