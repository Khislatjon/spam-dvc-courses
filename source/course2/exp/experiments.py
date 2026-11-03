import json, re, subprocess, time
from pathlib import Path
import numpy as np, pandas as pd, tifffile
from scipy import ndimage as ndi
BIN = Path("/opt/anaconda3/bin"); rng = np.random.default_rng(11); S = (240, 220, 220)
n = ndi.gaussian_filter(rng.normal(size=S), 2.4, mode="wrap"); bone = 128 + 100 * np.tanh(n / n.std() * 1.1)
broad = ndi.gaussian_filter(rng.normal(size=S), 14, mode="wrap"); bone = bone + broad / broad.std() * 22
z, y, x = np.mgrid[0:S[0], 0:S[1], 0:S[2]].astype(np.float32)
c = np.array(S) / 2; r2 = ((y - c[1]) / 92) ** 2 + ((x - c[2]) / 92) ** 2; sam = (r2 <= 1) & (np.abs(z - c[0]) <= 108)
ref = np.where(sam, bone, 22).astype(np.float32)
def U(Z, Y, X):
    d = ((Z - 120) / 42) ** 2 + ((Y - 150) / 38) ** 2 + ((X - 110) / 45) ** 2; b = np.exp(-d)
    return (Z - 120) * -0.02 + 3 - 3 * b, (Y - 110) * .006 + 16 + 16 * b, (X - 110) * .006 - 5 + 3 * b
Z, Y, X = z.copy(), y.copy(), x.copy()
for _ in range(5): a, b_, c_ = U(Z, Y, X); Z, Y, X = z - a, y - b_, x - c_
dfm = ndi.map_coordinates(ref, [Z, Y, X], order=1, mode="nearest").astype(np.float32) + rng.normal(0, 6, S).astype(np.float32)
ref = np.clip(ref + rng.normal(0, 6, S), 0, 255).astype(np.uint8); dfm = np.clip(dfm, 0, 255).astype(np.uint8)
tifffile.imwrite("unloaded.tif", ref); tifffile.imwrite("loaded.tif", dfm); tifffile.imwrite("mask.tif", sam.astype(np.uint8) * 255)
del Z, Y, X, z, y, x, n, broad, bone
R = {"shape": S}
def run(cmd):
    t = time.time(); r = subprocess.run([str(BIN / cmd[0])] + [str(c) for c in cmd[1:]], capture_output=True, text=True); return time.time() - t, r
def rd(f): return pd.read_csv(f, sep="\t")
def score(d):
    ok = d.returnStatus > -5; g = d[d.returnStatus > 0]; tu = np.array(U(g.Zpos.values, g.Ypos.values, g.Xpos.values)).T; e = np.sqrt(((g[["Zdisp", "Ydisp", "Xdisp"]].values - tu) ** 2).sum(1))
    c = (d.returnStatus == 2).values[d.returnStatus.values > 0]
    return dict(nodes=len(d), tried=int(ok.sum()), conv=int((d.returnStatus == 2).sum()), limit=int((d.returnStatus == 1).sum()), failed=int(((d.returnStatus < 0) & (d.returnStatus > -5)).sum()), skipped=int((d.returnStatus <= -5).sum()), rms=round(float(np.sqrt((e ** 2).mean())), 3) if len(e) else None, rms_conv=round(float(np.sqrt((e[c] ** 2).mean())), 3) if c.sum() else None, wrong=int((e > 2).sum()), its=int(d.iterations.sum()))
out = []
for bb, be in ((1, 1), (2, 2), (4, 2), (4, 1), (8, 2), (8, 1), (16, 2)):
    t, r = run(["spam-reg", "unloaded.tif", "loaded.tif", "-mf1", "mask.tif", "-bb", bb, "-be", be, "-od", ".", "-pre", f"reg_{bb}_{be}"]); q = rd(f"reg_{bb}_{be}-registration.tsv").iloc[0]
    u0 = np.array(U(q.Zpos, q.Ypos, q.Xpos), float); out.append(dict(bb=bb, be=be, time=round(t, 1), status=int(q.returnStatus), error=round(float(q.error), 2), iters=int(q.iterations), Y=round(float(q.Ydisp), 2), err_t=round(float(np.linalg.norm([q.Zdisp - u0[0], q.Ydisp - u0[1], q.Xdisp - u0[2]])), 2), Fzz=round(float(q.Fzz), 4))); print(out[-1], flush=True)
    if bb == 4 and be == 2: R["reg_terminal"] = r.stdout[-1400:]
R["reg"] = out; pf = "reg_4_2-registration.tsv"
print(open(pf).read()[:500], flush=True); R["reg_tsv"] = open(pf).read()
base = ["-mf1", "mask.tif", "-mc", .5, "-pf", pf, "-glt", 5, "-np", 4]
out = []
for ns in (25, 50):
    for h in (5, 10, 15, 25, 40):
        t, r = run(["spam-ldic", "unloaded.tif", "loaded.tif", *base, "-ns", ns, "-hws", h, "-od", ".", "-pre", f"g_{ns}_{h}"]); o = score(rd(f"g_{ns}_{h}-ldic.tsv")); o.update(ns=ns, hws=h, time=round(t, 1)); out.append(o); print(o, flush=True)
R["grid"] = out
t, r = run(["spam-ldic", "unloaded.tif", "loaded.tif", "-mf1", "mask.tif", "-mc", .5, "-glt", 5, "-np", 4, "-ns", 50, "-hws", 25, "-od", ".", "-pre", "nopf"]); o = score(rd("nopf-ldic.tsv")); o.update(time=round(t, 1)); R["no_pf"] = o; print("nopf", o, flush=True)
out = []
for mc in (None, 0, .25, .5, .75, 1):
    m = [] if mc is None else ["-mf1", "mask.tif", "-mc", mc]
    t, r = run(["spam-ldic", "unloaded.tif", "loaded.tif", *m, "-pf", pf, "-glt", 5, "-np", 4, "-ns", 50, "-hws", 25, "-od", ".", "-pre", f"m_{mc}"]); o = score(rd(f"m_{mc}-ldic.tsv")); o.update(mc=mc, time=round(t, 1)); out.append(o); print(o, flush=True)
R["mask"] = out
out = []
for np_ in (1, 2, 4, 6):
    t, r = run(["spam-ldic", "unloaded.tif", "loaded.tif", *["-mf1", "mask.tif", "-mc", .5, "-pf", pf, "-glt", 5], "-np", np_, "-ns", 25, "-hws", 25, "-od", ".", "-pre", f"np_{np_}"]); out.append(dict(np=np_, time=round(t, 1))); print(out[-1], flush=True)
R["np"] = out
b2 = lambda a: a[:a.shape[0] // 2 * 2, :a.shape[1] // 2 * 2, :a.shape[2] // 2 * 2].reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, a.shape[2] // 2, 2).astype(np.float32).mean((1, 3, 5))
tifffile.imwrite("u2.tif", b2(ref).astype(np.uint8)); tifffile.imwrite("l2.tif", b2(dfm).astype(np.uint8)); tifffile.imwrite("m2.tif", (b2(sam.astype(np.uint8) * 255) > 127).astype(np.uint8) * 255)
out = []
for name, sr in (("Too small", (-2, 2, -2, 2, -2, 2)), ("About right", (-6, 6, -14, 14, -6, 6)), ("Too wide", (-30, 30, -30, 30, -30, 30))):
    t, r = run(["spam-pixelSearch", "u2.tif", "l2.tif", "-mf1", "m2.tif", "-mc", .5, "-pf", pf, "-pfb", .5, "-sr", *sr, "-ns", 25, "-hws", 12, "-glt", 5, "-np", 4, "-od", ".", "-pre", f"ps_{sr[1]}"])
    if r.returncode: print(r.stderr[-400:]); 
    t2, r2 = run(["spam-ldic", "unloaded.tif", "loaded.tif", "-mf1", "mask.tif", "-mc", .5, "-pf", f"ps_{sr[1]}-pixelSearch.tsv", "-pfb", 2, "-ns", 50, "-hws", 25, "-glt", 5, "-np", 4, "-od", ".", "-pre", f"after_{sr[1]}"]); o = score(rd(f"after_{sr[1]}-ldic.tsv")); o.update(name=name, sr=sr, t_search=round(t, 1), t_dvc=round(t2, 1), positions=int((sr[1] - sr[0] + 1) * (sr[3] - sr[2] + 1) * (sr[5] - sr[4] + 1))); out.append(o); print(o, flush=True)
R["ps"] = out
R["ldic_head"] = "".join(open("g_50_25-ldic.tsv").readlines()[:3]); t, r = run(["spam-ldic", "-h"]); json.dump(R, open("results.json", "w"), indent=1, default=str); print("DONE")
