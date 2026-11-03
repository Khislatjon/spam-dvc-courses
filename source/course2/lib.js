// Shared engine for the SPAM DVC course. The maths follows spam.DIC.register in 2D.
var SIZE = 1024, TABLE = new Float32Array(SIZE * SIZE);
(function () {
  var w = [[.31,.12,.3],[-.17,.29,1.1],[.22,-.26,2.2],[.09,.37,.7],[.41,.05,4.1],[-.28,.2,5.2],[.13,-.33,3.3],[.36,.24,2.7],[-.1,.15,.5],[.18,.08,1.9],[-.35,-.11,.9],[.26,.34,6]];
  var two = 2 * Math.PI / SIZE;
  w = w.map(function (a) { return [Math.round(a[0] / two) * two, Math.round(a[1] / two) * two, a[2]]; });
  for (var y = 0; y < SIZE; y++) for (var x = 0; x < SIZE; x++) {
    var s = 0;
    for (var i = 0; i < w.length; i++) s += Math.sin(w[i][0] * x + w[i][1] * y + w[i][2]);
    TABLE[y * SIZE + x] = 128 + 105 * Math.tanh(s / 1.5);
  }
})();
// Linear interpolation, like SPAM's default interpolationOrder=1.
function tex(x, y) {
  var ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy, m = SIZE - 1;
  var x0 = ix & m, x1 = (ix + 1) & m, y0 = iy & m, y1 = (iy + 1) & m;
  return TABLE[y0 * SIZE + x0] * (1 - fx) * (1 - fy) + TABLE[y0 * SIZE + x1] * fx * (1 - fy) + TABLE[y1 * SIZE + x0] * (1 - fx) * fy + TABLE[y1 * SIZE + x1] * fx * fy;
}
// Bone has structure at many sizes, so add broad shapes to the fine struts for the multiscale lesson.
var BLOBS = [[-40, -30, 46, 150], [55, 25, 40, -120], [10, 70, 34, 110], [-70, 55, 30, -90], [80, -60, 38, 130], [0, -80, 28, -80]];
function rich(x, y) {
  var s = 0.32 * tex(x, y) + 88;
  for (var i = 0; i < BLOBS.length; i++) { var b = BLOBS[i], dx = (x - b[0]) / b[2], dy = (y - b[1]) / b[2]; s += b[3] * Math.exp(-(dx * dx + dy * dy)); }
  return s;
}
function shifted(t) { return function (x, y) { return tex(x - t[0], y - t[1]); }; }
// Two scores. error is SPAM's _errorCalc; zncc is the score pixel search uses.
function compare(f, g, ox, oy, h, step) {
  step = step || 1;
  var sa = 0, sb = 0, saa = 0, sbb = 0, sab = 0, sq = 0, n = 0;
  for (var y = -h; y <= h; y += step) for (var x = -h; x <= h; x += step) {
    var a = f(x, y), b = g(x + ox, y + oy), d = a - b;
    sa += a; sb += b; saa += a * a; sbb += b * b; sab += a * b; sq += d * d; n++;
  }
  var den = Math.sqrt((saa - sa * sa / n) * (sbb - sb * sb / n));
  return { error: sq / sa, zncc: den ? (sab - sa * sb / n) / den : 0 };
}
// SPAM computes the gradient once on the fixed image, so M never changes. Only A is rebuilt.
function makeOperator(f, h, step) {
  step = step || 1;
  var a = 0, b = 0, c = 0, pts = [];
  for (var y = -h; y <= h; y += step) for (var x = -h; x <= h; x += step) {
    var gx = (f(x + 1, y) - f(x - 1, y)) / 2, gy = (f(x, y + 1) - f(x, y - 1)) / 2;
    a += gx * gx; b += gx * gy; c += gy * gy;
    pts.push([x, y, gx, gy, f(x, y)]);
  }
  var det = a * c - b * b;
  return { pts: pts, a: a, b: b, c: c, det: det };
}
function iterate(op, g, u) {
  var ax = 0, ay = 0, sq = 0, sum = 0, p = op.pts;
  for (var i = 0; i < p.length; i++) {
    var q = p[i], r = q[4] - g(q[0] + u[0], q[1] + u[1]);
    ax += q[2] * r; ay += q[3] * r; sq += r * r; sum += q[4];
  }
  return { dx: (op.c * ax - op.b * ay) / op.det, dy: (op.a * ay - op.b * ax) / op.det, error: sq / sum };
}
// Follow register(): stop on a small step (status 2) or at the iteration limit (status 1).
function register(op, g, start, limit, minStep) {
  var u = start.slice(), path = [];
  limit = limit || 50; minStep = minStep || 0.001;
  for (var k = 0; k <= limit; k++) {
    var s = iterate(op, g, u), size = Math.sqrt(s.dx * s.dx + s.dy * s.dy);
    path.push({ k: k, u: u.slice(), error: s.error, step: size });
    if (k === limit) return { u: u, path: path, status: 1 };
    u = [u[0] + s.dx, u[1] + s.dy];
    if (size < minStep) return { u: u, path: path, status: 2 };
  }
}
// Average n by n pixels, like spam.DIC.binning.
function binned(f, n) {
  return function (x, y) {
    var s = 0;
    for (var j = 0; j < n; j++) for (var i = 0; i < n; i++) s += f(x * n + i, y * n + j);
    return s / (n * n);
  };
}
function pixelSearch(f, g, h, range, cStep, wStep, start) {
  var best = { score: -2, x: 0, y: 0 }, map = [];
  start = start || [0, 0];
  for (var y = -range; y <= range; y += cStep) for (var x = -range; x <= range; x += cStep) {
    var c = compare(f, g, start[0] + x, start[1] + y, h, wStep).zncc;
    map.push(c);
    if (c > best.score) best = { score: c, x: start[0] + x, y: start[1] + y };
  }
  best.map = map; return best;
}
// A made-up vertebra with a lesion. u(x, y) adds a smooth squeeze and a local collapse.
var BONE = { w: 360, h: 240 };
BONE.inside = function (x, y) {
  var a = (x - 178) / 150, b = (y - 120) / 96;
  var body = Math.pow(Math.abs(a), 3.2) + Math.pow(Math.abs(b), 3.2) <= 1;
  var lesion = (x - 322) * (x - 322) + (y - 120) * (y - 120) <= 34 * 34;
  return body && !lesion;
};
BONE.u = function (x, y) {
  var ux = (x - 180) * 0.015 + 6, uy = (y - 120) * -0.05 + 4;
  var d = ((x - 275) * (x - 275)) / (110 * 110) + ((y - 120) * (y - 120)) / (90 * 90);
  return [ux - 6 * Math.exp(-d), uy + 26 * Math.exp(-d)];
};
BONE.rawFixed = BONE.fixed = function (x, y) { return tex(x * 1.2, y * 1.2) * (BONE.inside(x, y) ? 1 : 0.12); };
BONE.rawMoved = BONE.moved = function (x, y) {
  var X = x, Y = y;
  for (var i = 0; i < 4; i++) { var u = BONE.u(X, Y); X = x - u[0]; Y = y - u[1]; }
  return BONE.rawFixed(X, Y);
};
// Lookup tables keep the whole-bone demos fast.
BONE.ready = function () {
  if (BONE.A) return; var P = 80, W = BONE.w + 2 * P, H = BONE.h + 2 * P, A = new Float32Array(W * H), B = new Float32Array(W * H);
  for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) { A[y * W + x] = BONE.rawFixed(x - P, y - P); B[y * W + x] = BONE.rawMoved(x - P, y - P); }
  function look(T) { return function (x, y) { var X = x + P, Y = y + P, i = Math.floor(X), j = Math.floor(Y); if (i < 0 || j < 0 || i >= W - 1 || j >= H - 1) return 15; var a = X - i, b = Y - j, k = j * W + i; return T[k] * (1 - a) * (1 - b) + T[k + 1] * a * (1 - b) + T[k + W] * (1 - a) * b + T[k + W + 1] * a * b; }; }
  BONE.A = A; BONE.fixed = look(A); BONE.moved = look(B);
};
if (typeof module !== "undefined") module.exports = { rich: rich, tex: tex, shifted: shifted, compare: compare, makeOperator: makeOperator, iterate: iterate, register: register, binned: binned, pixelSearch: pixelSearch, BONE: BONE };
