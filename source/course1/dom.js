// Small browser helpers shared by the lessons.
var $ = function (i) { return document.getElementById(i); };
function cssv(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
// Canvases can hold more pixels than logical voxels (data-s), so images stay sharp when enlarged.
function paint(c, fn) { var s = +c.dataset.s || 1, x = c.getContext("2d"), w = c.width, h = c.height, d = x.createImageData(w, h); for (var j = 0; j < h; j++) for (var i = 0; i < w; i++) { var v = fn(i / s, j / s), k = 4 * (j * w + i); d.data[k] = v[0]; d.data[k + 1] = v[1]; d.data[k + 2] = v[2]; d.data[k + 3] = 255; } x.putImageData(d, 0, 0); }
function ctxOf(c) { var s = +c.dataset.s || 1, x = c.getContext("2d"); x.setTransform(s, 0, 0, s, 0, 0); return x; }
function sheet(w, h, s) { var c = document.createElement("canvas"); c.width = w * s; c.height = h * s; c.dataset.s = s; return c; }
function gray(v) { v = Math.max(0, Math.min(255, v)); return [v, v, v]; }
var VIR = [[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]];
function viridis(t) { t = Math.max(0, Math.min(.999, t)) * 4; var k = Math.floor(t), f = t - k; return [0, 1, 2].map(function (c) { return VIR[k][c] + (VIR[k + 1][c] - VIR[k][c]) * f; }); }
function fmt(v, d) { return (v < 0 ? "−" : "") + Math.abs(v).toFixed(d === undefined ? 2 : d); }
function fitCanvas(c, h) { var r = window.devicePixelRatio || 1, w = c.clientWidth || 640; c.width = Math.round(w * r); c.height = Math.round(h * r); var x = c.getContext("2d"); x.setTransform(r, 0, 0, r, 0, 0); return { x: x, w: w, h: h }; }
function plot(c, h, series, opt) {
  opt = opt || {}; var g = fitCanvas(c, h), x = g.x, L = 46, R = 12, T = 12, B = 30, W = g.w - L - R, H = h - T - B;
  var xs = opt.x || [0, 1], ys = opt.y || [0, 1], px = function (v) { return L + (v - xs[0]) / (xs[1] - xs[0]) * W; }, py = function (v) { return T + H - (v - ys[0]) / (ys[1] - ys[0]) * H; };
  x.clearRect(0, 0, g.w, h); x.strokeStyle = cssv("--line"); x.lineWidth = 1; x.strokeRect(L, T, W, H); x.fillStyle = cssv("--muted"); x.font = "12px " + cssv("--mono");
  x.textAlign = "center"; (opt.xt || []).forEach(function (t) { x.fillText(String(t), px(t), h - 12); }); x.textAlign = "right"; (opt.yt || []).forEach(function (t) { x.fillText(String(t), L - 6, py(t) + 4); });
  series.forEach(function (s) { x.strokeStyle = s.color; x.lineWidth = s.w || 2.5; x.beginPath(); s.d.forEach(function (p, i) { var a = px(p[0]), b = py(p[1]); if (i) x.lineTo(a, b); else x.moveTo(a, b); }); x.stroke(); });
  if (opt.legend) { x.font = "600 13px " + cssv("--text"); x.textAlign = "left"; var lx = L + 12; opt.legend.forEach(function (e) { x.strokeStyle = e[0]; x.lineWidth = 3.5; x.beginPath(); x.moveTo(lx, T + 16); x.lineTo(lx + 22, T + 16); x.stroke(); x.fillStyle = cssv("--fg"); x.fillText(e[1], lx + 28, T + 20); lx += 28 + x.measureText(e[1]).width + 20; }); }
  (opt.dots || []).forEach(function (d) { x.fillStyle = d.color; x.beginPath(); x.arc(px(d.x), py(d.y), d.r || 6, 0, 7); x.fill(); });
  return { x: x, px: px, py: py };
}
