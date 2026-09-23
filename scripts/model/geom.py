import math
import numpy as np

def M(p, n, i):
    return {'p': np.asarray(p, float).reshape(-1, 3), 'n': np.asarray(n, float).reshape(-1, 3), 'i': np.asarray(i, np.int64).ravel()}

def merge(*ms):
    ms = [m for m in ms if m is not None and len(m['i'])]
    P, N, I, off = [], [], [], 0
    for m in ms:
        P.append(m['p']); N.append(m['n']); I.append(m['i'] + off); off += len(m['p'])
    return M(np.vstack(P), np.vstack(N), np.concatenate(I))

def smooth_normals(P, I):
    N = np.zeros_like(P); t = I.reshape(-1, 3)
    fn = np.cross(P[t[:, 1]] - P[t[:, 0]], P[t[:, 2]] - P[t[:, 0]])
    for k in range(3): np.add.at(N, t[:, k], fn)
    ln = np.linalg.norm(N, axis=1, keepdims=True); ln[ln == 0] = 1
    return N / ln

def fix_winding(m):
    """Make triangle winding agree with the supplied vertex normals."""
    t = m['i'].reshape(-1, 3); P = m['p']
    fn = np.cross(P[t[:, 1]] - P[t[:, 0]], P[t[:, 2]] - P[t[:, 0]])
    vn = m['n'][t].sum(1)
    flip = (fn * vn).sum(1) < 0
    t = t.copy(); t[flip] = t[flip][:, ::-1]
    return M(P, m['n'], t.ravel())

def basis(d):
    d = np.asarray(d, float); d = d / np.linalg.norm(d)
    a = np.array([0, 1, 0]) if abs(d[1]) < 0.9 else np.array([1, 0, 0])
    u = np.cross(d, a); u /= np.linalg.norm(u); v = np.cross(d, u)
    return d, u, v

# ------------------------------------------------------------------ transforms
def rotmat(axis, deg):
    a = math.radians(deg); ax = np.asarray(axis, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K

def rotate(m, axis, deg, pivot):
    R = rotmat(axis, deg); pv = np.asarray(pivot, float)
    return M((m['p'] - pv) @ R.T + pv, m['n'] @ R.T, m['i'])

def rot_pt(p, axis, deg, pivot):
    R = rotmat(axis, deg); pv = np.asarray(pivot, float)
    return (np.asarray(p, float) - pv) @ R.T + pv

def translate(m, t):
    return M(m['p'] + np.asarray(t, float), m['n'], m['i'])

def scale(m, s, pivot=(0, 0, 0)):
    s = np.asarray(s, float); pv = np.asarray(pivot, float)
    n = m['n'] / s; n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    return M((m['p'] - pv) * s + pv, n, m['i'])

def mirror_z(m):
    p = m['p'].copy(); n = m['n'].copy(); p[:, 2] *= -1; n[:, 2] *= -1
    return M(p, n, m['i'])

# ------------------------------------------------------------------ primitives
def box(mn, mx):
    (x0, y0, z0), (x1, y1, z1) = mn, mx
    F = [([1, 0, 0], [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
         ([-1, 0, 0], [(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)]),
         ([0, 1, 0], [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)]),
         ([0, -1, 0], [(x0, y0, z1), (x0, y0, z0), (x1, y0, z0), (x1, y0, z1)]),
         ([0, 0, 1], [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
         ([0, 0, -1], [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)])]
    P, N, I = [], [], []
    for k, (n, q) in enumerate(F):
        P += q; N += [n] * 4; b = 4 * k; I += [b, b + 1, b + 2, b, b + 2, b + 3]
    return M(P, N, I)

def rbox(mn, mx, r, k=2):
    """Box with rounded edges and corners of radius r."""
    k = min(k, 3)
    mn, mx = np.asarray(mn, float), np.asarray(mx, float)
    c = (mn + mx) / 2; h = (mx - mn) / 2
    r = min(r, h.min() * 0.98)
    if r <= 1e-4: return box(mn, mx)
    a = np.linspace(0, np.pi / 2, k + 1)
    def coords(hh):
        return np.concatenate([-(hh - r) - r * np.sin(a[::-1]), (hh - r) + r * np.sin(a)])
    cs = [coords(h[0]), coords(h[1]), coords(h[2])]
    P, N, I = [], [], []
    inner = h - r
    for ax in range(3):
        b, cc = [i for i in range(3) if i != ax]
        for s in (-1, 1):
            base = len(P); nb, nc = len(cs[b]), len(cs[cc])
            for i in range(nb):
                for j in range(nc):
                    q = np.zeros(3); q[ax] = s * h[ax]; q[b] = cs[b][i]; q[cc] = cs[cc][j]
                    inn = np.clip(q, -inner, inner); d = q - inn; n = d / np.linalg.norm(d)
                    P.append(c + inn + n * r); N.append(n)
            for i in range(nb - 1):
                for j in range(nc - 1):
                    v0 = base + i * nc + j
                    I += [v0, v0 + 1, v0 + nc + 1, v0, v0 + nc + 1, v0 + nc]
    return fix_winding(M(P, N, I))

def lathe(profile, p0, axis, seg=32, arc=None):
    """Revolve a (radius, distance-along-axis) profile. Repeat a point to get a crisp edge."""
    seg = max(8, int(seg * 0.75))
    d, u, v = basis(axis); p0 = np.asarray(p0, float)
    n = len(profile); a0, a1 = (0, 2 * np.pi) if arc is None else arc
    full = arc is None
    cols = seg if full else seg + 1
    ang = np.linspace(a0, a1, cols, endpoint=not full)
    P = []
    for r, t in profile:
        for a in ang:
            P.append(p0 + d * t + r * (np.cos(a) * u + np.sin(a) * v))
    P = np.array(P); I = []
    for i in range(n - 1):
        for j in range(cols if full else cols - 1):
            a = i * cols + j; b = i * cols + (j + 1) % cols
            I += [a, b, b + cols, a, b + cols, a + cols]
    I = np.array(I)
    return M(P, smooth_normals(P, I), I)

def disc(center, axis, r, seg=32):
    return lathe([(0, 0), (r, 0)], center, axis, seg)

def cyl(p1, p2, r, seg=24, caps=True):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float); L = np.linalg.norm(p2 - p1)
    prof = [(0, 0), (r, 0), (r, 0), (r, L), (r, L), (0, L)] if caps else [(r, 0), (r, L)]
    return lathe(prof, p1, p2 - p1, seg)

def ellipsoid(c, r, seg=24, rings=14, half=False):
    c = np.asarray(c, float); r = np.asarray(r, float) if np.ndim(r) else np.array([r, r, r], float)
    P, N, I = [], [], []
    top = rings // 2 if half else rings
    for i in range(top + 1):
        th = np.pi / 2 - np.pi * i / rings
        for k in range(seg + 1):
            ph = 2 * np.pi * k / seg
            n = np.array([np.cos(th) * np.cos(ph), np.sin(th), np.cos(th) * np.sin(ph)])
            P.append(c + n * r); nn = n / r; N.append(nn / np.linalg.norm(nn))
    for i in range(top):
        for k in range(seg):
            a = i * (seg + 1) + k; b = a + seg + 1
            I += [a, a + 1, b, a + 1, b + 1, b]
    return fix_winding(M(P, N, I))

def torus(c, axis, R, r, seg=32, tube=12, arc=(0, 2 * np.pi)):
    seg = max(8, int(seg * 0.75)); tube = max(4, int(tube * 0.75))
    c = np.asarray(c, float); d, u, v = basis(axis)
    full = abs(arc[1] - arc[0] - 2 * np.pi) < 1e-6
    P, N, I = [], [], []
    for i in range(seg + 1):
        a = arc[0] + (arc[1] - arc[0]) * i / seg; ca = np.cos(a) * u + np.sin(a) * v
        for k in range(tube + 1):
            b = 2 * np.pi * k / tube; n = np.cos(b) * ca + np.sin(b) * d
            P.append(c + R * ca + r * n); N.append(n)
    for i in range(seg):
        for k in range(tube):
            a = i * (tube + 1) + k; b = a + tube + 1
            I += [a, b, a + 1, a + 1, b, b + 1]
    return fix_winding(M(P, N, I))

# ------------------------------------------------------------------ paths and sweeps
def catmull(ctrl, closed=False, step=0.04):
    P = [np.asarray(p, float) for p in ctrl]
    if len(P) == 2 and not closed:
        L = np.linalg.norm(P[1] - P[0]); n = max(2, int(L / step) + 1)
        return np.array([P[0] + (P[1] - P[0]) * t for t in np.linspace(0, 1, n)])
    pts = P + P[:3] if closed else [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    rng = range(len(P)) if closed else range(len(P) - 1)
    for i in rng:
        p0, p1, p2, p3 = (pts[i], pts[i + 1], pts[i + 2], pts[i + 3]) if not closed else (pts[i - 1 if i else len(P) - 1], pts[i], pts[i + 1], pts[i + 2])
        L = np.linalg.norm(p2 - p1); n = max(2, int(L / step))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed: out.append(P[-1])
    return np.array(out)

def sweep(ctrl, shape, closed=False, step=0.06, seg=16, caps=True, smooth_path=True, twist_up=None):
    seg = max(6, int(seg * 0.75))
    """Sweep a circle (shape=radius) or 2D profile [(a,b),...] along a path."""
    path = catmull(ctrl, closed, step) if smooth_path else np.array([np.asarray(p, float) for p in ctrl])
    n = len(path)
    T = np.zeros_like(path)
    for i in range(n):
        a = path[(i - 1) % n] if (closed or i > 0) else path[i]
        b = path[(i + 1) % n] if (closed or i < n - 1) else path[i]
        T[i] = b - a
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    up = np.asarray(twist_up, float) if twist_up is not None else None
    Nv = np.zeros_like(path)
    if up is not None:
        for i in range(n):
            x = np.cross(T[i], up); x /= np.linalg.norm(x); Nv[i] = x
    else:
        _, u0, _ = basis(T[0]); Nv[0] = u0
        for i in range(1, n):
            v = np.cross(T[i - 1], T[i]); s = np.linalg.norm(v)
            if s < 1e-8: Nv[i] = Nv[i - 1]; continue
            ang = math.degrees(math.atan2(s, np.dot(T[i - 1], T[i])))
            Nv[i] = rotmat(v / s, ang) @ Nv[i - 1]
    B = np.cross(T, Nv)
    if np.isscalar(shape):
        prof = [(shape * math.cos(a), shape * math.sin(a)) for a in np.linspace(0, 2 * np.pi, seg, endpoint=False)]
    else:
        prof = shape
    m = len(prof)
    P = np.array([path[i] + a * Nv[i] + b * B[i] for i in range(n) for a, b in prof])
    I = []
    rows = n if closed else n - 1
    for i in range(rows):
        i2 = (i + 1) % n
        for j in range(m):
            j2 = (j + 1) % m
            a, b, c, d = i * m + j, i * m + j2, i2 * m + j2, i2 * m + j
            I += [a, b, c, a, c, d]
    I = np.array(I)
    parts = [M(P, smooth_normals(P, I), I)]
    if caps and not closed:
        for i, sgn in ((0, -1), (n - 1, 1)):
            ring = P[i * m:(i + 1) * m]; cen = ring.mean(0)
            cp = np.vstack([cen, ring]); ci = []
            for j in range(m): ci += [0, 1 + j, 1 + (j + 1) % m]
            parts.append(fix_winding(M(cp, np.tile(T[i] * sgn, (m + 1, 1)), ci)))
    return merge(*parts)

def rect_profile(w, h, crisp=True):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    if not crisp: return pts
    out = []
    for p in pts: out += [p, p]
    return out

def loft(rows, close=False, caps=False):
    """Surface through rows of points (each row same length)."""
    R = [np.asarray(r, float) for r in rows]; n, m = len(R), len(R[0])
    P = np.vstack(R); I = []
    cols = m if close else m - 1
    for i in range(n - 1):
        for j in range(cols):
            j2 = (j + 1) % m
            a, b, c, d = i * m + j, i * m + j2, (i + 1) * m + j2, (i + 1) * m + j
            I += [a, b, c, a, c, d]
    I = np.array(I)
    parts = [M(P, smooth_normals(P, I), I)]
    if caps:
        for r, sgn in ((R[0], -1), (R[-1], 1)):
            cen = r.mean(0); cp = np.vstack([cen, r]); ci = []
            for j in range(m): ci += [0, 1 + j, 1 + (j + 1) % m]
            ci = np.array(ci); nrm = smooth_normals(cp, ci)[0]
            parts.append(M(cp, np.tile(nrm, (m + 1, 1)), ci))
    return merge(*parts)

def prism(poly, axis, a0, a1):
    """Extrude a 2D polygon. axis 'x': (z,y); 'y': (x,z); 'z': (x,y)."""
    poly = np.asarray(poly, float); n = len(poly)
    def P3(q, a):
        return {'x': (a, q[1], q[0]), 'y': (q[0], a, q[1]), 'z': (q[0], q[1], a)}[axis]
    rows = []
    for a in (a0, a1): rows.append([P3(q, a) for q in poly])
    # sides with crisp edges: duplicate each vertex
    parts = []
    for k in range(n):
        q0, q1 = poly[k], poly[(k + 1) % n]
        quad = np.array([P3(q0, a0), P3(q1, a0), P3(q1, a1), P3(q0, a1)])
        I = np.array([0, 1, 2, 0, 2, 3]); nr = smooth_normals(quad, I)
        parts.append(M(quad, nr, I))
    for a in (a0, a1):
        ring = np.array([P3(q, a) for q in poly]); cen = ring.mean(0)
        cp = np.vstack([cen, ring]); ci = []
        for j in range(n): ci += [0, 1 + j, 1 + (j + 1) % n]
        ci = np.array(ci); nrm = smooth_normals(cp, ci)[0]
        parts.append(M(cp, np.tile(nrm, (n + 1, 1)), ci))
    m = merge(*parts)
    # orient normals outward relative to the solid's centroid
    cen = m['p'].mean(0); t = m['i'].reshape(-1, 3)
    fc = m['p'][t].mean(1); fn = m['n'][t[:, 0]]
    out = ((fc - cen) * fn).sum(1) < 0
    nn = m['n'].copy()
    for f in np.where(out)[0]:
        nn[t[f]] = -m['n'][t[f]]
    return fix_winding(M(m['p'], nn, m['i']))
