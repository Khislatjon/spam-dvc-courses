import pickle, numpy as np, spam.DIC
from scipy import ndimage as ndi
rng = np.random.default_rng(3); S = 200; hw = 25
v = ndi.gaussian_filter(rng.normal(size=(S, S, S)), 2.6, mode="wrap"); v = 128 + 105 * np.tanh(v / v.std() * 1.1); v = v.astype("<f4")
T = np.array([4., 26., -3.]); Phi = np.eye(4); Phi[:3, 3] = T; Phi[0, 0] = .985; Phi[1, 1] = 1.008
w = spam.DIC.applyPhi(v, Phi=Phi, interpolationOrder=1).astype("<f4") + rng.normal(0, 7, v.shape).astype("<f4")
c = np.array([S // 2] * 3); win = v[c[0]-hw:c[0]+hw+1, c[1]-hw:c[1]+hw+1, c[2]-hw:c[2]+hw+1]
def film(start, kmax):
    u0 = np.round(start).astype(int); pad = 40; lo = c + u0 - hw - pad; hi = c + u0 + hw + pad + 1
    box = w[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]; P0 = np.eye(4); P0[:3, 3] = start - u0; fr = []
    for k in range(kmax + 1):
        if k == 0: Ph, st = P0.copy(), 0
        else:
            r = spam.DIC.register(win, box, PhiInit=P0.copy(), margin=1, maxIterations=k, deltaPhiMin=.001, interpolationOrder=1, interpolator="C"); Ph, st = r["Phi"], r["returnStatus"]
        d = spam.DIC.applyPhi(box, Phi=np.linalg.inv(Ph), interpolationOrder=1); q = np.array(box.shape) // 2; s = tuple(slice(a - hw, a + hw + 1) for a in q); ww = d[s]
        e = float(((win[1:-1, 1:-1, 1:-1] - ww[1:-1, 1:-1, 1:-1]) ** 2).sum() / win[1:-1, 1:-1, 1:-1].sum())
        fr.append(dict(k=k, t=Ph[:3, 3] + u0, err=e, st=st, w=ww[:, :, hw].copy()))
        if st == 2: break
    print(start, "frames", len(fr), "err", round(fr[0]["err"], 1), "->", round(fr[-1]["err"], 1), "t", fr[-1]["t"].round(1), "st", fr[-1]["st"]); return fr
fa = film(np.array([0., 6., 0.]), 50); fb = film(np.array([4., 26., -3.]) + [.4, -.3, .2], 50)
pickle.dump(dict(fa=fa, fb=fb, win=win[:, :, hw]), open("frames_synth.pkl", "wb"))
