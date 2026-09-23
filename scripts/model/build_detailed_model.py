"""Build the detailed DPV yacht model.

Reads the original model (scripts/model/source/dpv-luxury-yacht.glb) and writes
public/models/dpv-luxury-yacht-detailed.glb with:
  - a twin V12 engine room (engines, gearboxes, shafts, exhaust, fuel tanks)
  - electrical systems (generator, batteries, switchboard, inverters, cable trays, lights)
  - navigation equipment (helm displays, radar, satcom, antennas)
  - interior joinery and upholstery (cabins, bulkheads, stairs, galley, tables)
  - hull hardware (swim ladder, anchor and chain)
  - a fix that seats the propellers on their pod drives and makes them counter-rotate

Every added part is fitted to the measured hull shape and checked to sit inside it.
Coordinates are in the model root's local space: bow +x, starboard +z, up +y, metres.

Usage (from the project root):
    pip install -r scripts/model/requirements.txt
    python3 scripts/model/build_detailed_model.py
"""
import os, struct, json, math
from collections import OrderedDict
import numpy as np
from geom import *

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(HERE, 'source', 'dpv-luxury-yacht.glb')
OUT = os.path.join(ROOT, 'public', 'models', 'dpv-luxury-yacht-detailed.glb')

raw = open(SRC, 'rb').read()
jlen = struct.unpack('<I', raw[12:16])[0]
J = json.loads(raw[20:20 + jlen])
blen = struct.unpack('<I', raw[20 + jlen:24 + jlen])[0]
BIN = bytearray(raw[28 + jlen:28 + jlen + blen])

def accessor(i):
    a = J['accessors'][i]; bv = J['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a['componentType']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    arr = np.frombuffer(bytes(BIN), dtype=dt, count=a['count'] * n, offset=off)
    return arr.reshape(-1, n) if n > 1 else arr

def node_verts(name):
    return np.vstack([np.array(accessor(J['meshes'][nd['mesh']]['primitives'][0]['attributes']['POSITION']), float)
                      for nd in J['nodes'] if nd.get('name') == name and 'mesh' in nd])

HB = node_verts('hull_bottom_stbd'); HT = node_verts('hull_topside_stbd')
HULL = np.vstack([HB, HT]); ROOF = node_verts('house_roof'); ARCH = node_verts('radar_arch'); DECK = node_verts('main_deck')

def half_beam(x, y):
    for rx, ry in [(0.3, 0.1), (0.45, 0.16), (0.8, 0.3)]:
        s = HULL[(np.abs(HULL[:, 0] - x) < rx) & (np.abs(HULL[:, 1] - y) < ry)]
        if len(s) > 2:
            w = np.exp(-((s[:, 0] - x) / rx) ** 2 - ((s[:, 1] - y) / ry) ** 2)
            # upper envelope, lightly smoothed
            top = np.sort(s[:, 2])[-max(1, len(s) // 6):]
            return float(top.mean())
    return 0.0

def hull_y(x, z):
    """Height of the inside of the hull bottom at station x, offset z."""
    z = abs(z)
    for rx, rz in [(0.3, 0.1), (0.5, 0.2), (0.9, 0.35)]:
        s = HB[(np.abs(HB[:, 0] - x) < rx) & (np.abs(HB[:, 2] - z) < rz)]
        if len(s): return float(s[:, 1].min())
    return float(HB[np.abs(HB[:, 0] - x) < 0.5][:, 1].min())

def keel(x):
    return float(HULL[np.abs(HULL[:, 0] - x) < 0.4][:, 1].min())

def deck_min(x):
    return float(DECK[np.abs(DECK[:, 0] - x) < 0.4][:, 1].min())

def surface_top(verts, x, z, r=0.25):
    s = verts[(np.abs(verts[:, 0] - x) < r) & (np.abs(verts[:, 2] - z) < r)]
    return float(s[:, 1].max())

def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]

MATS = {
    'engine_grey':   dict(c='#4B545D', m=0.5, r=0.4),
    'engine_dark':   dict(c='#2E3439', m=0.45, r=0.45),
    'engine_red':    dict(c='#BA2127', m=0.3, r=0.3),
    'aluminium':     dict(c='#C7CED5', m=0.85, r=0.3),
    'cast_iron':     dict(c='#5E656B', m=0.7, r=0.6),
    'rubber_black':  dict(c='#1A1E22', m=0.0, r=0.75),
    'tank_alu':      dict(c='#B3BCC5', m=0.75, r=0.42),
    'genset_white':  dict(c='#F0F3F5', m=0.1, r=0.35),
    'dpv_blue_sys':  dict(c='#195C8F', m=0.25, r=0.35),
    'battery_black': dict(c='#262C32', m=0.1, r=0.55),
    'panel_white':   dict(c='#E8ECF0', m=0.15, r=0.4),
    'breaker_black': dict(c='#2A2F35', m=0.1, r=0.45),
    'screen_glow':   dict(c='#0D2740', m=0.1, r=0.08, e='#2A78B8'),
    'glass_dark':    dict(c='#0B0F14', m=0.2, r=0.05),
    'led_white':     dict(c='#FFFFFF', m=0.0, r=0.2, e='#FFFFFF'),
    'led_underwater':dict(c='#CFEAFF', m=0.0, r=0.2, e='#8FD0FF'),
    'nav_red':       dict(c='#BA2127', m=0.0, r=0.2, e='#BA2127'),
    'nav_green':     dict(c='#1E9E58', m=0.0, r=0.2, e='#1E9E58'),
    'teak':          dict(c='#8B5A36', m=0.0, r=0.5),
    'teak_caulk':    dict(c='#2B2622', m=0.0, r=0.7),
    'oak_light':     dict(c='#CDAC84', m=0.0, r=0.45),
    'walnut':        dict(c='#6B4A33', m=0.0, r=0.4),
    'fabric_cream':  dict(c='#EAE4D9', m=0.0, r=0.85),
    'fabric_white':  dict(c='#F6F4F0', m=0.0, r=0.8),
    'fabric_blue':   dict(c='#195C8F', m=0.0, r=0.85),
    'counter_black': dict(c='#23282D', m=0.25, r=0.2),
    'stainless_sys': dict(c='#D6DBE0', m=0.95, r=0.16),
    'brass':         dict(c='#C9A45C', m=0.9, r=0.3),
    'cable_blue':    dict(c='#195C8F', m=0.0, r=0.6),
    'cable_red':     dict(c='#BA2127', m=0.0, r=0.6),
    'cable_black':   dict(c='#1C2024', m=0.0, r=0.6),
    'fibreglass':    dict(c='#DDE4E9', m=0.0, r=0.6),
    'copper':        dict(c='#B8743F', m=0.9, r=0.35),
    'gauge_face':    dict(c='#F7F7F5', m=0.0, r=0.4),
}

PARTS = []
INT, EXT = 'systems_internal', 'details_external'
def add(name, group, mesh, mat):
    PARTS.append((name, group, mesh, mat))

# ============================================================== ENGINE ROOM: twin V12 diesels
YC = -0.05          # crankshaft height
X_FLY, X_FRONT = -12.85, -10.45

def bank(zc, sgn):
    """One cylinder bank built upright, then tilted 45 degrees outboard (sgn = +1 stbd side of the vee)."""
    out = []
    pv = (0, YC, zc)
    def tilt(m): return rotate(m, (1, 0, 0), 45 * sgn, pv)
    out.append(('eng_block', tilt(rbox((-12.72, YC + 0.28, zc - 0.2), (-10.58, YC + 0.58, zc + 0.2), 0.03)), 'engine_grey'))
    for i in range(6):
        x0 = -12.64 + i * 0.335
        out.append(('eng_block', tilt(rbox((x0, YC + 0.58, zc - 0.19), (x0 + 0.31, YC + 0.71, zc + 0.19), 0.02)), 'engine_grey'))
        out.append(('eng_valvecover', tilt(rbox((x0 + 0.025, YC + 0.71, zc - 0.155), (x0 + 0.285, YC + 0.79, zc + 0.155), 0.03)), 'engine_red'))
        # injector cap and cover bolts
        out.append(('eng_valvecover', tilt(lathe([(0, 0), (0.035, 0), (0.035, 0.035), (0.028, 0.045), (0, 0.045)], (x0 + 0.155, YC + 0.79, zc), (0, 1, 0), 18)), 'aluminium'))
        for bx in (x0 + 0.05, x0 + 0.26):
            for bz in (-0.12, 0.12):
                out.append(('eng_valvecover', tilt(cyl((bx, YC + 0.79, zc + bz), (bx, YC + 0.805, zc + bz), 0.012, 8)), 'aluminium'))
        # exhaust port stub from head to manifold (outboard face of the bank)
        out.append(('eng_exhaust', tilt(sweep([(x0 + 0.155, YC + 0.64, zc + 0.19), (x0 + 0.155, YC + 0.63, zc + 0.26), (x0 + 0.155, YC + 0.6, zc + 0.3)], 0.035, seg=12)), 'cast_iron'))
    # water-jacketed exhaust manifold along the outboard side
    out.append(('eng_exhaust', tilt(sweep([(-12.66, YC + 0.6, zc + 0.31), (-10.5, YC + 0.6, zc + 0.31)], 0.07, seg=20)), 'cast_iron'))
    for i in range(7):
        x = -12.66 + i * 0.36
        out.append(('eng_exhaust', tilt(torus((x, YC + 0.6, zc + 0.31), (1, 0, 0), 0.07, 0.012, 20, 6)), 'cast_iron'))
    manifold_end = rot_pt((-10.5, YC + 0.6, zc + 0.31), (1, 0, 0), 45 * sgn, pv)
    return out, manifold_end

def engine(zc):
    """Starboard engine at +zc; port engine is its mirror."""
    P = []
    s = 1  # outboard direction for the starboard engine
    # crankcase with ribs
    P.append(('eng_block', rbox((-12.75, -0.48, zc - 0.36), (-10.55, 0.22, zc + 0.36), 0.04), 'engine_grey'))
    for i in range(7):
        x = -12.6 + i * 0.33
        for sz in (-1, 1):
            P.append(('eng_block', rbox((x - 0.025, -0.45, zc + sz * 0.36 - 0.02), (x + 0.025, 0.12, zc + sz * 0.36 + 0.02), 0.01, 2), 'engine_grey'))
    # oil sump, tapering toward the keel
    P.append(('eng_block', prism([(0.34, -0.48), (0.28, -0.74), (0.24, -0.8), (-0.24, -0.8), (-0.28, -0.74), (-0.34, -0.48)],
                                 'x', -12.55, -10.7), 'engine_dark'))
    P[-1] = (P[-1][0], translate(P[-1][1], (0, 0, zc)), P[-1][2])
    P.append(('eng_block', cyl((-10.9, -0.8, zc + 0.1), (-10.9, -0.84, zc + 0.1), 0.03, 12), 'aluminium'))  # drain plug
    # banks
    for sg in (-1, 1):
        b, mend = bank(zc, sg)
        P += b
        if sg == 1: mend_out = mend
        else: mend_in = mend
    # valley cover and charge-air cooler on top of the vee
    P.append(('eng_block', prism([(0.1, 0.18), (0.24, 0.38), (-0.24, 0.38), (-0.1, 0.18)], 'x', -12.6, -10.62), 'engine_dark'))
    P[-1] = (P[-1][0], translate(P[-1][1], (0, 0, zc)), P[-1][2])
    P.append(('eng_intercooler', rbox((-12.45, 0.38, zc - 0.24), (-10.95, 0.66, zc + 0.24), 0.05), 'aluminium'))
    for i in range(9):
        x = -12.3 + i * 0.16
        P.append(('eng_intercooler', rbox((x - 0.02, 0.66, zc - 0.2), (x + 0.02, 0.68, zc + 0.2), 0.008, 2), 'aluminium'))
    P.append(('eng_intercooler', rbox((-10.98, 0.36, zc - 0.26), (-10.85, 0.7, zc + 0.26), 0.04), 'dpv_blue_sys'))
    P.append(('eng_intercooler', rbox((-12.55, 0.36, zc - 0.26), (-12.42, 0.7, zc + 0.26), 0.04), 'dpv_blue_sys'))
    # twin turbochargers at the free end, axis fore-aft
    turbos = []
    for sg in (-1, 1):
        tz = zc + sg * 0.34; p0 = np.array([-10.55, 0.68, tz])
        prof = [(0, 0), (0.07, 0), (0.07, 0.01), (0.13, 0.03), (0.14, 0.08), (0.12, 0.14), (0.06, 0.15),
                (0.06, 0.24), (0.13, 0.25), (0.155, 0.3), (0.14, 0.35), (0.09, 0.36), (0.08, 0.42), (0.085, 0.42), (0.085, 0.44), (0, 0.44)]
        P.append(('eng_turbo', lathe(prof, p0, (1, 0, 0), 28), 'cast_iron'))
        P.append(('eng_turbo', torus(p0 + [0.075, 0, 0], (1, 0, 0), 0.13, 0.055, 28, 12), 'cast_iron'))
        P.append(('eng_turbo', torus(p0 + [0.3, 0, 0], (1, 0, 0), 0.15, 0.06, 28, 12), 'aluminium'))
        P.append(('eng_turbo', lathe([(0.06, 0), (0.06, 0.1)], p0 + [0.14, 0, 0], (1, 0, 0), 20), 'stainless_sys'))
        # pleated air filter, DPV blue, with chrome end cap
        fp = []
        for k in range(15):
            r = 0.135 if k % 2 == 0 else 0.118
            fp += [(r, 0.04 + k * 0.02)]
        filt = [(0.08, 0), (0.12, 0.0), (0.135, 0.02)] + fp + [(0.135, 0.34), (0.1, 0.36), (0, 0.365)]
        P.append(('eng_airfilter', lathe(filt, p0 + [0.44, 0, 0], (1, 0, 0), 32), 'dpv_blue_sys'))
        P.append(('eng_airfilter', lathe([(0.125, 0), (0.14, 0.005), (0.14, 0.03), (0.1, 0.045), (0, 0.05)], p0 + [0.76, 0, 0], (1, 0, 0), 32), 'stainless_sys'))
        # compressor outlet to the charge-air cooler
        P.append(('eng_intercooler', sweep([p0 + [0.3, 0.2, 0], p0 + [0.25, 0.3, -sg * 0.1], (-10.75, 0.9, zc), (-11.0, 0.72, zc)], 0.05, seg=16), 'aluminium'))
        turbos.append((sg, p0))
    # manifolds to turbine inlets
    for sg, p0 in turbos:
        mend = mend_out if sg == 1 else mend_in
        P.append(('eng_exhaust', sweep([mend, mend + [0.05, 0.0, 0], p0 + [0.06, -0.14, sg * 0.04], p0 + [0.07, -0.08, 0]], 0.065, seg=18), 'cast_iron'))
    # turbine outlets rise, merge and run aft to the water-lift muffler
    outer = next(p for sg, p in turbos if sg == 1); inner = next(p for sg, p in turbos if sg == -1)
    P.append(('eng_exhaust', sweep([outer + [0.07, 0.12, 0], outer + [0.06, 0.32, 0.02], outer + [-0.2, 0.44, 0.1], (-11.2, 1.08, zc + 0.52)], 0.075, seg=20), 'stainless_sys'))
    P.append(('eng_exhaust', sweep([inner + [0.07, 0.12, 0], inner + [0.06, 0.4, 0.0], inner + [-0.25, 0.55, 0.3], (-11.2, 1.08, zc + 0.52)], 0.075, seg=20), 'stainless_sys'))
    P.append(('eng_exhaust', lathe([(0.075, 0), (0.12, 0.08), (0.12, 0.25), (0.1, 0.33), (0.1, 0.33)], (-11.1, 1.08, zc + 0.52), (-1, 0, 0), 24), 'stainless_sys'))
    for x in (-11.28, -11.36):
        P.append(('eng_exhaust', torus((x, 1.08, zc + 0.52), (1, 0, 0), 0.12, 0.015, 24, 6), 'stainless_sys'))
    P.append(('eng_exhaust', sweep([(-11.43, 1.08, zc + 0.52), (-11.8, 1.1, zc + 0.62), (-12.2, 1.05, zc + 0.72)], 0.1, seg=20), 'rubber_black'))
    mu = [(0, 0), (0.1, 0), (0.1, 0.03), (0.2, 0.08), (0.22, 0.14), (0.22, 0.62), (0.2, 0.68), (0.1, 0.73), (0.1, 0.76), (0, 0.76)]
    P.append(('eng_muffler', lathe(mu, (-12.18, 1.02, zc + 0.74), (-1, 0, 0), 32), 'rubber_black'))
    for x in (-12.42, -12.7):
        P.append(('eng_muffler', torus((x, 1.02, zc + 0.74), (1, 0, 0), 0.222, 0.012, 32, 6), 'stainless_sys'))
    P.append(('eng_exhaust', sweep([(-12.94, 1.02, zc + 0.74), (-13.4, 1.05, zc + 0.78), (-14.0, 0.85, 1.95), (-14.45, 0.62, 2.0)], 0.1, seg=20), 'rubber_black'))
    # front end: timing cover, damper, pulleys, belt, alternator, raw-water pump
    P.append(('eng_frontend', rbox((-10.55, -0.55, zc - 0.4), (-10.44, 0.42, zc + 0.4), 0.04), 'engine_grey'))
    grooves = [(0.19, 0)] + [(0.19 if k % 2 == 0 else 0.175, 0.01 + k * 0.012) for k in range(7)] + [(0.19, 0.09), (0.19, 0.09), (0, 0.095)]
    P.append(('eng_frontend', lathe([(0, 0), (0.19, 0)] + grooves, (-10.44, -0.25, zc), (1, 0, 0), 36), 'cast_iron'))
    P.append(('eng_frontend', lathe([(0, 0), (0.1, 0), (0.1, 0), (0.1, 0.05), (0.09, 0.055), (0.1, 0.06), (0.1, 0.09), (0, 0.09)], (-10.44, 0.18, zc), (1, 0, 0), 28), 'aluminium'))
    P.append(('eng_frontend', lathe([(0, 0), (0.06, 0), (0.06, 0.07), (0, 0.07)], (-10.44, -0.02, zc - 0.25), (1, 0, 0), 20), 'aluminium'))
    alt = [(0, 0), (0.1, 0)] + [(0.1 if k % 2 == 0 else 0.092, 0.015 + k * 0.018) for k in range(9)] + [(0.1, 0.18), (0.06, 0.2), (0.06, 0.2), (0.06, 0.26), (0, 0.26)]
    P.append(('eng_frontend', lathe(alt, (-10.62, 0.12, zc + 0.3), (1, 0, 0), 28), 'aluminium'))
    P.append(('eng_frontend', rbox((-10.6, 0.02, zc + 0.3 - 0.03), (-10.55, 0.06, zc + 0.3 + 0.03), 0.01, 2), 'cable_red'))
    # belt path = convex hull around the pulleys, as a real drive belt wraps them
    pulleys = [(-0.25, 0.0, 0.18), (0.18, 0.0, 0.095), (-0.02, -0.25, 0.058), (0.12, 0.3, 0.058)]
    pts = [(yy + (r + 0.006) * math.cos(a), dz + (r + 0.006) * math.sin(a)) for yy, dz, r in pulleys for a in np.linspace(0, 2 * np.pi, 48, endpoint=False)]
    pts = sorted(set(pts))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    hull2 = lo[:-1] + up[:-1]
    P.append(('eng_frontend', sweep([(-10.395, yy, zc + dz) for yy, dz in hull2], rect_profile(0.01, 0.028), closed=True, smooth_path=False, twist_up=(1, 0, 0)), 'rubber_black'))
    P.append(('eng_frontend', lathe([(0, 0), (0.08, 0), (0.08, 0.14), (0.05, 0.16), (0, 0.16)], (-10.44, -0.4, zc + 0.3), (1, 0, 0), 24), 'dpv_blue_sys'))
    # heat exchanger and expansion tank
    hx = [(0, 0), (0.08, 0), (0.08, 0.02), (0.11, 0.02), (0.11, 0.06), (0.1, 0.07), (0.1, 1.33), (0.11, 1.34), (0.11, 1.38), (0.08, 1.38), (0.08, 1.4), (0, 1.4)]
    P.append(('eng_heatex', lathe(hx, (-12.25, -0.18, zc + 0.5), (1, 0, 0), 28), 'copper'))
    P.append(('eng_heatex', sweep([(-10.85, -0.18, zc + 0.5), (-10.6, -0.3, zc + 0.46), (-10.46, -0.4, zc + 0.36)], 0.035, seg=12), 'rubber_black'))
    P.append(('eng_heatex', rbox((-10.9, 0.2, zc + 0.36), (-10.62, 0.42, zc + 0.56), 0.04), 'aluminium'))
    P.append(('eng_heatex', lathe([(0, 0), (0.045, 0), (0.045, 0.03), (0.05, 0.035), (0.05, 0.05), (0, 0.055)], (-10.76, 0.42, zc + 0.46), (0, 1, 0), 18), 'dpv_blue_sys'))
    # oil filters and ECU on the inboard side
    for x in (-11.35, -11.1):
        P.append(('eng_oilfilter', lathe([(0, 0), (0.055, 0), (0.065, 0.01), (0.065, 0.2), (0.058, 0.215), (0, 0.22)], (x, -0.15, zc - 0.44), (0, -1, 0), 24), 'dpv_blue_sys'))
    P.append(('eng_oilfilter', rbox((-11.45, -0.18, zc - 0.44), (-11.0, -0.1, zc - 0.36), 0.015), 'engine_grey'))
    P.append(('eng_ecu', rbox((-12.3, -0.25, zc - 0.43), (-11.7, 0.12, zc - 0.37), 0.02), 'breaker_black'))
    for k in range(6):
        P.append(('eng_ecu', rbox((-12.26 + k * 0.1, -0.22, zc - 0.44), (-12.2 + k * 0.1, 0.09, zc - 0.43), 0.005, 1), 'engine_dark'))
    P.append(('eng_ecu', sweep([(-11.9, 0.12, zc - 0.4), (-11.8, 0.3, zc - 0.36), (-11.3, 0.3, zc - 0.25)], 0.018, seg=10), 'cable_black'))
    # feet and resilient mounts on the bearers
    for x in (-12.45, -10.8):
        for sz in (-1, 1):
            P.append(('eng_mount', rbox((x - 0.1, -0.42, zc + sz * 0.34 - 0.02), (x + 0.1, -0.34, zc + sz * 0.5), 0.015), 'engine_grey'))
            P.append(('eng_mount', lathe([(0, 0), (0.1, 0), (0.1, 0.02), (0.075, 0.03), (0.06, 0.08), (0.05, 0.1), (0, 0.1)], (x, -0.55, zc + sz * 0.45), (0, 1, 0), 20), 'rubber_black'))
    # flywheel housing, gearbox, coupling, shaft and seal
    P.append(('eng_flywheel', lathe([(0, 0), (0.42, 0), (0.42, 0.04), (0.39, 0.06), (0.36, 0.22), (0.3, 0.26), (0, 0.26)], (X_FLY + 0.1, -0.12, zc), (-1, 0, 0), 40), 'engine_grey'))
    P.append(('eng_gearbox', rbox((-13.55, -0.55, zc - 0.3), (-13.0, 0.12, zc + 0.3), 0.05), 'dpv_blue_sys'))
    P.append(('eng_gearbox', rbox((-13.5, 0.12, zc - 0.18), (-13.1, 0.18, zc + 0.18), 0.02), 'engine_dark'))
    P.append(('eng_gearbox', lathe([(0, 0), (0.05, 0), (0.05, 0.4), (0, 0.4)], (-13.48, 0.2, zc + 0.2), (1, 0, 0), 16), 'copper'))
    P.append(('eng_gearbox', lathe([(0, 0), (0.16, 0), (0.16, 0.05), (0.1, 0.06), (0.1, 0.1), (0.14, 0.1), (0.14, 0.14), (0, 0.14)], (-13.55, -0.35, zc), (-1, 0, 0), 28), 'stainless_sys'))
    shaft_a = np.array([-13.69, -0.38, zc]); shaft_b = np.array([-14.4, -0.8, zc])
    P.append(('eng_shaft', cyl(shaft_a, shaft_b, 0.055, 20), 'stainless_sys'))
    d = shaft_b - shaft_a
    P.append(('eng_shaft', lathe([(0.06, 0), (0.1, 0.01), (0.1, 0.12), (0.075, 0.2), (0.06, 0.22)], shaft_a + d * 0.55, d, 24), 'rubber_black'))
    P.append(('eng_shaft', lathe([(0.075, 0), (0.075, 0.01), (0.075, 0.06)], shaft_a + d * 0.55 + d / np.linalg.norm(d) * 0.04, d, 24), 'stainless_sys'))
    # sea strainer and seacock
    sx, sz_ = -9.95, zc - 0.05
    P.append(('eng_seacock', lathe([(0, 0), (0.06, 0), (0.06, 0.05), (0.04, 0.06), (0.04, 0.1), (0.09, 0.12), (0.09, 0.34), (0.1, 0.35), (0.1, 0.39), (0, 0.4)],
                                   (sx, hull_y(sx, sz_) + 0.02, sz_), (0, 1, 0), 24), 'aluminium'))
    P.append(('eng_seacock', cyl((sx, hull_y(sx, sz_) + 0.37, sz_), (sx, hull_y(sx, sz_) + 0.43, sz_), 0.06, 20), 'dpv_blue_sys'))
    P.append(('eng_seacock', sweep([(sx, hull_y(sx, sz_) + 0.28, sz_ + 0.09), (sx - 0.03, -0.3, sz_ + 0.2), (-10.2, -0.36, zc + 0.3), (-10.26, -0.4, zc + 0.3)], 0.028, seg=12), 'rubber_black'))
    return P

ENG_ZC = 1.15
stbd = engine(ENG_ZC)
for name, m, mat in stbd:
    add(f'{name}_stbd', INT, m, mat)
    add(f'{name}_port', INT, mirror_z(m), mat)

# engine bearers follow the hull bottom
for sz in (-1, 1):
    for dz in (-0.45, 0.45):
        z = sz * (ENG_ZC + dz)
        xs = np.linspace(-9.6, -13.3, 16)
        poly = [(-13.3, -0.55), (-9.6, -0.55)] + [(x, hull_y(x, z) + 0.03) for x in xs]
        poly[2] = (-9.6, max(poly[2][1], -0.95)); poly[-1] = (-13.3, poly[-1][1])
        m = prism(poly, 'z', z - 0.045, z + 0.045)
        add(f'hull_str_bearer_{"stbd" if sz > 0 else "port"}', INT, m, 'fibreglass')

# ============================================================== FUEL TANKS (hull-following, both sides)
def fuel_tank():
    xs = np.linspace(-7.45, -5.15, 13)
    top = 0.8; zin = 0.46
    inner_rows, curve_rows, top_rows = [], [], []
    for x in xs:
        yb = hull_y(x, zin) + 0.07
        ys = np.linspace(yb, top, 16)
        curve = [(x, y, max(zin + 0.04, half_beam(x, y) - 0.07)) for y in ys]
        curve[0] = (x, yb, zin + 0.04)
        inner_rows.append([(x, top, zin), (x, yb + 0.03, zin)])
        curve_rows.append(curve)
        top_rows.append([(x, top, curve[-1][2]), (x, top, zin)])
    # soften the inner-bottom corner by joining the inner face to the curve start
    for r_in, c in zip(inner_rows, curve_rows):
        r_in.append(c[0])
    tank = merge(loft(inner_rows), loft(curve_rows), loft(top_rows))
    for rows_idx in (0, -1):
        ring = [inner_rows[rows_idx][0], inner_rows[rows_idx][1]] + curve_rows[rows_idx] + [top_rows[rows_idx][0]]
        cen = np.mean(ring, 0); cp = np.vstack([cen, ring]); ci = []
        for j in range(len(ring)): ci += [0, 1 + j, 1 + (j + 1) % len(ring)]
        ci = np.array(ci); tank = merge(tank, M(cp, np.tile(smooth_normals(cp, ci)[0], (len(cp), 1)), ci))
    parts = [(tank, 'tank_alu')]
    # inspection hatches with bolt rings
    for x in (-6.95, -5.7):
        zc = 1.35
        parts.append((lathe([(0, 0), (0.17, 0), (0.17, 0.02), (0.15, 0.03), (0, 0.03)], (x, top, zc), (0, 1, 0), 32), 'aluminium'))
        for k in range(10):
            a = 2 * np.pi * k / 10
            parts.append((cyl((x + 0.145 * np.cos(a), top + 0.03, zc + 0.145 * np.sin(a)), (x + 0.145 * np.cos(a), top + 0.045, zc + 0.145 * np.sin(a)), 0.01, 6), 'stainless_sys'))
    # fill, vent and pickup fittings
    for x, r in ((-6.35, 0.045), (-6.15, 0.025), (-5.45, 0.03)):
        parts.append((lathe([(0, 0), (r * 1.4, 0), (r * 1.4, 0.03), (r, 0.04), (r, 0.12), (r * 1.2, 0.13), (r * 1.2, 0.16), (0, 0.16)], (x, top, 2.2), (0, 1, 0), 18), 'brass'))
    # sight gauge on the inner face
    parts.append((cyl((-6.0, -0.4, zin - 0.03), (-6.0, 0.7, zin - 0.03), 0.018, 10), 'glass_dark'))
    for y in (-0.4, 0.7):
        parts.append((rbox((-6.04, y - 0.03, zin - 0.06), (-5.96, y + 0.03, zin), 0.01, 2), 'brass'))
    # hold-down straps
    for x in (-7.1, -6.3, -5.5):
        pts = [(x, top + 0.012, zin)] + [(x, top + 0.012, z) for z in np.linspace(zin + 0.1, half_beam(x, top) - 0.1, 4)]
        parts.append((sweep(pts, rect_profile(0.012, 0.07), step=0.1, smooth_path=False, twist_up=(0, 1, 0)), 'rubber_black'))
    return parts

for m, mat in fuel_tank():
    add('eng_tank_stbd', INT, m, mat)
    add('eng_tank_port', INT, mirror_z(m), mat)
for sz in (-1, 1):
    add(f'eng_fuelline_{"stbd" if sz > 0 else "port"}', INT,
        sweep([(-7.3, -0.3, sz * 0.5), (-7.8, 0.4, sz * 0.6), (-9.2, 1.18, sz * 0.75), (-10.6, 1.18, sz * 0.95), (-10.9, 0.5, sz * 0.9)], 0.02, seg=10), 'cable_red')

# ============================================================== ELECTRICAL
# generator in its sound shield
gx0, gx1 = -9.45, -7.95
add('elec_genset', INT, rbox((gx0, -0.72, -0.42), (gx1, 0.1, 0.42), 0.06), 'genset_white')
add('elec_genset', INT, rbox((gx0 - 0.005, -0.3, -0.425), (gx1 + 0.005, -0.22, 0.425), 0.03), 'dpv_blue_sys')
for sz in (-1, 1):
    for r in range(3):
        for c in range(5):
            x = gx0 + 0.3 + c * 0.2; y = -0.62 + r * 0.1
            add('elec_genset', INT, rbox((x, y, sz * 0.425 - 0.004), (x + 0.15, y + 0.03, sz * 0.425 + 0.004), 0.006, 1), 'breaker_black')
add('elec_genset', INT, rbox((gx1 - 0.01, -0.15, -0.28), (gx1 + 0.01, 0.05, 0.28), 0.02), 'breaker_black')
add('elec_genset', INT, rbox((gx1 + 0.005, -0.08, -0.12), (gx1 + 0.012, 0.02, 0.05), 0.005, 1), 'screen_glow')
for z in (0.12, 0.2):
    add('elec_genset', INT, cyl((gx1 + 0.01, -0.03, z), (gx1 + 0.03, -0.03, z), 0.018, 12), 'engine_red' if z < 0.15 else 'cable_blue')
for x in (gx0 + 0.25, gx1 - 0.25):
    add('elec_genset', INT, torus((x, 0.14, 0), (0, 0, 1), 0.04, 0.01, 16, 6, arc=(0, np.pi)), 'stainless_sys')
for sz in (-1, 1):
    add('elec_genset', INT, rbox((gx0 - 0.05, -0.84, sz * 0.36 - 0.04), (gx1 + 0.05, -0.76, sz * 0.36 + 0.04), 0.01), 'engine_grey')
    for x in (gx0 + 0.1, gx1 - 0.1):
        add('elec_genset', INT, lathe([(0, 0), (0.06, 0), (0.06, 0.02), (0.04, 0.05), (0, 0.05)], (x, -0.76, sz * 0.36), (0, 1, 0), 16), 'rubber_black')
add('elec_genset', INT, sweep([(gx0 + 0.1, 0.0, 0.42), (gx0 + 0.05, 0.25, 0.7), (-9.2, 0.4, 2.4), (-9.0, 0.35, half_beam(-9.0, 0.35) - 0.12)], 0.05, seg=16), 'rubber_black')

# battery bank between the gearboxes
add('elec_battery', INT, rbox((-14.02, -0.68, -0.62), (-13.04, -0.6, 0.62), 0.015), 'fibreglass')
for sz in (-1, 1):
    add('elec_battery', INT, rbox((-14.02, -0.6, sz * 0.62 - 0.02), (-13.04, -0.52, sz * 0.62), 0.005, 1), 'fibreglass')
for i in range(3):
    for j in range(2):
        x0 = -13.97 + i * 0.31; z0 = -0.56 + j * 0.58
        add('elec_battery', INT, rbox((x0, -0.6, z0), (x0 + 0.27, -0.33, z0 + 0.52), 0.012), 'battery_black')
        add('elec_battery', INT, rbox((x0 - 0.004, -0.34, z0 - 0.004), (x0 + 0.274, -0.3, z0 + 0.524), 0.01), 'breaker_black')
        for tz, mat in ((z0 + 0.08, 'cable_red'), (z0 + 0.44, 'breaker_black')):
            add('elec_battery', INT, lathe([(0, 0), (0.028, 0), (0.028, 0.02), (0.018, 0.022), (0.016, 0.05), (0, 0.05)], (x0 + 0.08, -0.3, tz), (0, 1, 0), 14), 'brass')
            add('elec_battery', INT, rbox((x0 + 0.05, -0.28, tz - 0.035), (x0 + 0.11, -0.25, tz + 0.035), 0.01, 2), mat)
        add('elec_battery', INT, torus((x0 + 0.2, -0.3, z0 + 0.26), (0, 0, 1), 0.05, 0.008, 14, 6, arc=(0, np.pi)), 'breaker_black')
for tz, mat in ((0.08, 'copper'), (0.44, 'copper')):
    for base in (-0.56, 0.02):
        add('elec_battery', INT, rbox((-13.92, -0.255, base + tz - 0.015), (-13.24, -0.245, base + tz + 0.015), 0.004, 1), mat)
add('elec_battery', INT, rbox((-13.0, -0.4, -0.25), (-12.95, 0.1, 0.25), 0.01), 'panel_white')
for z in (-0.12, 0.12):
    add('elec_battery', INT, lathe([(0, 0), (0.07, 0), (0.07, 0.02), (0.05, 0.03), (0.05, 0.05), (0, 0.05)], (-12.95, -0.1, z), (1, 0, 0), 20), 'breaker_black')
    add('elec_battery', INT, rbox((-12.9, -0.12, z - 0.015), (-12.86, -0.08, z + 0.015), 0.005, 1), 'engine_red')

# main switchboard cabinet between the fuel tanks
sx0, sx1 = -6.55, -6.2
add('elec_switchboard', INT, rbox((sx0, -0.7, -0.32), (sx1, 1.15, 0.32), 0.02), 'panel_white')
for (a, b) in [((sx1, -0.7, -0.32), (sx1 + 0.02, 1.15, -0.28)), ((sx1, -0.7, 0.28), (sx1 + 0.02, 1.15, 0.32)),
               ((sx1, 1.11, -0.32), (sx1 + 0.02, 1.15, 0.32)), ((sx1, -0.7, -0.32), (sx1 + 0.02, -0.66, 0.32))]:
    add('elec_switchboard', INT, rbox(a, b, 0.006, 1), 'dpv_blue_sys')
for r in range(5):
    y = 0.62 - r * 0.17
    add('elec_switchboard', INT, rbox((sx1, y - 0.07, -0.25), (sx1 + 0.012, y + 0.07, 0.25), 0.004, 1), 'breaker_black')
    for c in range(8):
        z = -0.21 + c * 0.06
        add('elec_switchboard', INT, box((sx1 + 0.012, y - 0.05, z - 0.022), (sx1 + 0.035, y + 0.05, z + 0.022)), 'panel_white')
        add('elec_switchboard', INT, box((sx1 + 0.035, y - 0.005 + (0.02 if (r + c) % 3 else -0.02), z - 0.008), (sx1 + 0.05, y + 0.005 + (0.02 if (r + c) % 3 else -0.02), z + 0.008)),
            'engine_red' if c == 0 else 'breaker_black')
for k, z in enumerate((-0.17, 0.0, 0.17)):
    add('elec_switchboard', INT, lathe([(0, 0), (0.065, 0), (0.07, 0.005), (0.07, 0.02), (0.06, 0.022)], (sx1, 0.92, z), (1, 0, 0), 28), 'breaker_black')
    add('elec_switchboard', INT, disc((sx1 + 0.02, 0.92, z), (1, 0, 0), 0.058, 28), 'gauge_face')
    ndl = rotate(box((sx1 + 0.022, 0.92, z - 0.003), (sx1 + 0.025, 0.97, z + 0.003)), (1, 0, 0), -30 + k * 30, (sx1, 0.92, z))
    add('elec_switchboard', INT, ndl, 'engine_red')
add('elec_switchboard', INT, rbox((sx1, -0.5, -0.2), (sx1 + 0.012, -0.22, 0.2), 0.01), 'glass_dark')
add('elec_switchboard', INT, rbox((sx1 + 0.012, -0.48, -0.18), (sx1 + 0.014, -0.24, 0.18), 0.005, 1), 'screen_glow')
add('elec_switchboard', INT, lathe([(0, 0), (0.06, 0), (0.06, 0.02), (0.02, 0.025), (0.02, 0.06), (0, 0.06)], (sx1, -0.6, 0.0), (1, 0, 0), 24), 'breaker_black')
# inverter chargers with fin heat sinks on the forward bulkhead
for sz in (-1, 1):
    z = sz * 1.6
    add('elec_inverter', INT, rbox((-4.97, 0.15, z - 0.3), (-4.8, 0.95, z + 0.3), 0.03), 'panel_white')
    add('elec_inverter', INT, rbox((-4.81, 0.62, z - 0.2), (-4.79, 0.84, z + 0.2), 0.01), 'screen_glow')
    for k in range(9):
        zz = z - 0.24 + k * 0.06
        add('elec_inverter', INT, box((-4.8, 0.2, zz - 0.006), (-4.76, 0.55, zz + 0.006)), 'aluminium')
# ladder cable trays with cable bundles
def tray(path, width=0.2):
    parts = []
    for off in (-width / 2, width / 2):
        pts = [np.asarray(p) + [0, 0, off] for p in path]
        parts.append((sweep(pts, rect_profile(0.012, 0.05), smooth_path=False, twist_up=(0, 1, 0)), 'aluminium'))
    for a, b in zip(path[:-1], path[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float); L = np.linalg.norm(b - a)
        for t in np.arange(0.1, L, 0.3):
            p = a + (b - a) * t / L
            parts.append((box(p + [-0.01, -0.028, -width / 2], p + [0.01, -0.02, width / 2]), 'aluminium'))
    for k, (dz, mat) in enumerate(((-0.05, 'cable_red'), (0.0, 'cable_blue'), (0.05, 'cable_black'))):
        parts.append((sweep([np.asarray(p) + [0, -0.005, dz] for p in path], 0.016, seg=8, smooth_path=False), mat))
    return parts
for m, mat in tray([(-13.0, 1.2, 0.0), (-6.4, 1.2, 0.0)]):
    add('elec_tray', INT, m, mat)
for m, mat in tray([(-6.4, 1.26, 0.0), (-4.95, 1.26, 0.0)], 0.16):
    add('elec_tray', INT, m, mat)
add('elec_cable', INT, sweep([(-13.3, -0.25, -0.45), (-13.25, 0.6, -0.3), (-13.1, 1.18, -0.05)], 0.025, seg=10), 'cable_red')
add('elec_cable', INT, sweep([(-13.3, -0.25, 0.45), (-13.25, 0.6, 0.3), (-13.1, 1.18, 0.05)], 0.025, seg=10), 'cable_black')
add('elec_cable', INT, sweep([(-6.4, 1.18, 0.0), (-6.4, 1.15, 0.0)], 0.03, seg=10), 'cable_blue')
add('elec_cable', INT, sweep([(-8.7, 0.1, 0.0), (-8.7, 0.7, 0.0), (-8.6, 1.17, 0.0)], 0.022, seg=10), 'cable_blue')
add('elec_cable', EXT, sweep([(-4.9, 1.3, 0.1), (-2.0, 1.36, 0.6), (1.5, 1.38, 0.9), (2.9, 1.45, 0.9), (3.0, 1.7, 0.9)], 0.028, seg=10), 'cable_blue')
# shore power, underwater lights, navigation lights, searchlight, courtesy LEDs (exterior)
add('elec_shorepower', EXT, lathe([(0, 0), (0.1, 0), (0.1, 0.015), (0.075, 0.03), (0.075, 0.07), (0.06, 0.08), (0, 0.08)], (-14.5, 1.1, -1.2), (-1, 0, 0), 28), 'stainless_sys')
add('elec_shorepower', EXT, disc((-14.58, 1.1, -1.2), (-1, 0, 0), 0.058, 28), 'dpv_blue_sys')
for z in (-2.1, -0.55, 0.55, 2.1):
    add('elec_led_underwater', EXT, lathe([(0, 0), (0.1, 0), (0.1, 0.01), (0.085, 0.025), (0, 0.03)], (-14.49, -0.35, z), (-1, 0, 0), 28), 'stainless_sys')
    add('elec_led_underwater', EXT, disc((-14.522, -0.35, z), (-1, 0, 0), 0.07, 28), 'led_underwater')
for z, mat in [(-2.86, 'nav_red'), (2.86, 'nav_green')]:
    s = 1 if z > 0 else -1
    add('elec_navlight', EXT, rbox((-2.25, 2.5, z - 0.04), (-1.92, 2.64, z + 0.04), 0.02), 'breaker_black')
    add('elec_navlight', EXT, rbox((-1.95, 2.52, z - 0.035 + s * 0.005), (-1.9, 2.62, z + 0.035 + s * 0.005), 0.02), mat)
add('elec_navlight', EXT, lathe([(0, 0), (0.05, 0), (0.05, 0.03), (0.04, 0.06), (0, 0.065)], (-14.5, 1.42, 0), (-1, 0, 0), 20), 'led_white')
arch_top = surface_top(ARCH, -2.05, 0.9)
add('elec_navlight', EXT, lathe([(0, 0), (0.05, 0), (0.05, 0.02), (0.02, 0.03), (0.02, 0.14), (0, 0.14)], (-2.05, arch_top - 0.02, 0.9), (0, 1, 0), 16), 'breaker_black')
add('elec_navlight', EXT, lathe([(0.03, 0), (0.045, 0.02), (0.045, 0.08), (0.035, 0.1), (0, 0.105)], (-2.05, arch_top + 0.12, 0.9), (0, 1, 0), 20), 'led_white')
rx = 7.6; rtop = surface_top(ROOF, rx, 0)
add('elec_searchlight', EXT, lathe([(0, 0), (0.12, 0), (0.12, 0.02), (0.07, 0.05), (0.05, 0.14), (0, 0.14)], (rx, rtop - 0.01, 0), (0, 1, 0), 24), 'breaker_black')
add('elec_searchlight', EXT, lathe([(0, 0), (0.08, 0), (0.11, 0.05), (0.12, 0.2), (0.125, 0.24), (0.11, 0.25), (0, 0.25)], (rx - 0.12, rtop + 0.25, 0), (1, 0, 0), 28), 'aluminium')
add('elec_searchlight', EXT, disc((rx + 0.125, rtop + 0.25, 0), (1, 0, 0), 0.1, 28), 'led_white')
add('elec_searchlight', EXT, torus((rx, rtop + 0.17, 0), (0, 0, 1), 0.13, 0.015, 20, 8, arc=(0, np.pi)), 'breaker_black')
for z in (-2.92, 2.92):
    add('elec_led_strip', EXT, rbox((-13.4, 1.55, z - 0.012), (-1.8, 1.575, z + 0.012), 0.008, 1), 'led_white')

# ============================================================== NAVIGATION AND COMMUNICATION
dash_y = 2.34
for z0, z1 in [(-0.48, 0.1), (0.14, 0.72)]:
    zc = (z0 + z1) / 2; w = z1 - z0; h = w * 0.64
    parts = [rbox((3.3, dash_y + 0.05, z0), (3.37, dash_y + 0.05 + h, z1), 0.02),
             rbox((3.29, dash_y + 0.07, z0 + 0.02), (3.3, dash_y + 0.03 + h, z1 - 0.02), 0.004, 1)]
    for p, mat in zip(parts, ('breaker_black', 'screen_glow')):
        add('nav_mfd', EXT, rotate(p, (0, 0, 1), -16, (3.34, dash_y, zc)), mat)
    add('nav_mfd', EXT, rbox((3.34, dash_y, zc - 0.08), (3.4, dash_y + 0.07, zc + 0.08), 0.01), 'breaker_black')
for z in (0.9, 0.99):
    add('nav_throttle', EXT, rbox((3.08, dash_y, z - 0.035), (3.22, dash_y + 0.06, z + 0.035), 0.02), 'breaker_black')
    add('nav_throttle', EXT, sweep([(3.15, dash_y + 0.05, z), (3.1, dash_y + 0.15, z), (3.03, dash_y + 0.22, z)], 0.013, seg=8), 'stainless_sys')
    add('nav_throttle', EXT, ellipsoid((3.02, dash_y + 0.23, z), (0.035, 0.03, 0.035), 16, 10), 'engine_red')
add('nav_joystick', EXT, lathe([(0, 0), (0.07, 0), (0.07, 0.02), (0.05, 0.03), (0.02, 0.04), (0.015, 0.13), (0.03, 0.15), (0.032, 0.18), (0.02, 0.2), (0, 0.2)], (3.1, dash_y, -0.75), (0, 1, 0), 20), 'breaker_black')
add('nav_joystick', EXT, disc((3.1, dash_y + 0.2, -0.75), (0, 1, 0), 0.018, 16), 'dpv_blue_sys')
add('nav_compass', EXT, lathe([(0, 0), (0.08, 0), (0.08, 0.02), (0.075, 0.025), (0.07, 0.06), (0.05, 0.09), (0, 0.1)], (3.2, dash_y, -0.95), (0, 1, 0), 28), 'glass_dark')
add('nav_compass', EXT, torus((3.2, dash_y + 0.02, -0.95), (0, 1, 0), 0.08, 0.008, 28, 6), 'stainless_sys')
# satcom radomes, GPS, VHF and an open-array radar on the arch
for z in (-1.35, 1.35):
    top = surface_top(ARCH, -2.1, z, 0.3)
    add('nav_satcom', EXT, lathe([(0, 0), (0.18, 0), (0.18, 0.02), (0.12, 0.04), (0.1, 0.12), (0.2, 0.13), (0.2, 0.14), (0, 0.14)], (-2.1, top - 0.02, z), (0, 1, 0), 32), 'panel_white')
    dome = [(0.26, 0)] + [(0.26 * math.cos(a) ** 0.8, 0.02 + 0.34 * math.sin(a)) for a in np.linspace(0, np.pi / 2, 12)]
    add('nav_satcom', EXT, lathe([(0.27, 0), (0.27, 0.02)] + dome[1:], (-2.1, top + 0.12, z), (0, 1, 0), 36), 'genset_white')
top = surface_top(ARCH, -2.1, -0.55, 0.3)
add('nav_gps', EXT, lathe([(0, 0), (0.02, 0), (0.02, 0.08), (0.06, 0.09), (0.065, 0.11), (0.05, 0.13), (0, 0.135)], (-2.1, top - 0.01, -0.55), (0, 1, 0), 24), 'genset_white')
top = surface_top(ARCH, -2.35, 1.2, 0.3)
add('nav_antenna', EXT, lathe([(0, 0), (0.04, 0), (0.04, 0.06), (0.025, 0.08), (0.02, 0.16), (0.015, 0.16), (0.012, 1.2), (0.008, 2.0), (0.004, 2.05), (0, 2.06)], (-2.45, top - 0.02, 1.2), (0, 1, 0), 12), 'genset_white')
dome_top = 3.375 + 0.3
add('nav_radar', EXT, lathe([(0, 0), (0.15, 0), (0.15, 0.02), (0.13, 0.03), (0.12, 0.16), (0.08, 0.2), (0, 0.2)], (-2.36, dome_top - 0.03, 0), (0, 1, 0), 28), 'genset_white')
rows = []
for zz in np.linspace(-1.0, 1.0, 21):
    t = 1 - (abs(zz) / 1.0) ** 6
    hw, hh = 0.07 * (0.6 + 0.4 * t), 0.09 * (0.7 + 0.3 * t)
    rows.append([(-2.36 + hw * math.cos(a), dome_top + 0.28 + hh * math.sin(a), zz) for a in np.linspace(0, 2 * np.pi, 20, endpoint=False)])
add('nav_radar', EXT, loft(rows, close=True, caps=True), 'genset_white')
add('nav_radar', EXT, cyl((-2.36, dome_top + 0.17, 0), (-2.36, dome_top + 0.2, 0), 0.06, 16), 'breaker_black')
# electronics rack under the helm
add('nav_blackbox', INT, rbox((2.7, -0.45, 0.3), (3.2, 0.52, 1.0), 0.015), 'breaker_black')
for k in range(4):
    y0 = 0.33 - k * 0.22
    add('nav_blackbox', INT, rbox((2.685, y0, 0.36), (2.7, y0 + 0.16, 0.94), 0.01), 'engine_dark')
    add('nav_blackbox', INT, box((2.68, y0 + 0.11, 0.4), (2.685, y0 + 0.13, 0.5)), 'screen_glow')

# ============================================================== INTERIOR JOINERY AND UPHOLSTERY
SOLE_Y = -0.55
xs = np.arange(-4.85, 7.31, 0.3)
edge = [half_beam(x, SOLE_Y - 0.06) - 0.1 for x in xs]
sole_poly = [(x, e) for x, e in zip(xs, edge)] + [(x, -e) for x, e in zip(xs[::-1], edge[::-1])]
add('int_sole', INT, prism(sole_poly, 'y', SOLE_Y - 0.04, SOLE_Y), 'teak')
for zl in np.arange(-2.8, 2.81, 0.14):  # caulking seams clipped to the sole outline
    inside = [x for x, e in zip(xs, edge) if abs(zl) < e - 0.02]
    if len(inside) > 1:
        add('int_sole', INT, box((inside[0], SOLE_Y, zl - 0.004), (inside[-1], SOLE_Y + 0.002, zl + 0.004)), 'teak_caulk')

def bulkhead(x, doors):
    """Joinery bulkhead that follows the hull section, with door openings [(z0, z1)]."""
    top = deck_min(x) - 0.06
    zmax_fn = lambda y: half_beam(x, y) - 0.08
    breaks = sorted([z for d in doors for z in d])
    edges = [-10] + breaks + [10]
    parts = []
    for a, b in zip(edges[:-1], edges[1:]):
        is_door = any(abs(a - d0) < 1e-6 and abs(b - d1) < 1e-6 for d0, d1 in doors)
        y0 = SOLE_Y + 1.95 if is_door else SOLE_Y
        if y0 >= top: continue
        ys = np.linspace(y0, top, 10)
        if a == -10 and b == 10:
            poly = [(zmax_fn(y), y) for y in ys] + [(-zmax_fn(y), y) for y in ys[::-1]]
        elif a == -10:
            poly = [(-zmax_fn(y), y) for y in ys[::-1]] + [(b, y0), (b, top)]
            poly = [(-zmax_fn(top), top)] + [(-zmax_fn(y), y) for y in ys[::-1]][1:] + [(b, y0), (b, top)]
        elif b == 10:
            poly = [(a, top), (a, y0)] + [(zmax_fn(y), y) for y in ys]
        else:
            poly = [(a, y0), (b, y0), (b, top), (a, top)]
        parts.append(prism(poly, 'x', x - 0.025, x + 0.025))
    add('int_bulkhead', INT, merge(*parts), 'oak_light')
    for z0, z1 in doors:
        yt = SOLE_Y + 1.95
        frame = [rbox((x - 0.04, SOLE_Y, z0 - 0.05), (x + 0.04, yt + 0.05, z0), 0.01),
                 rbox((x - 0.04, SOLE_Y, z1), (x + 0.04, yt + 0.05, z1 + 0.05), 0.01),
                 rbox((x - 0.04, yt, z0 - 0.05), (x + 0.04, yt + 0.05, z1 + 0.05), 0.01)]
        add('int_door', INT, merge(*frame), 'walnut')
        leaf = rbox((x - 0.018, SOLE_Y + 0.01, z0 + 0.005), (x + 0.018, yt - 0.01, z1 - 0.005), 0.01)
        leaf = rotate(leaf, (0, 1, 0), 70, (x, 0, z0))
        add('int_door', INT, leaf, 'oak_light')
        hz = z1 - 0.07
        hp = rot_pt((x + 0.03, SOLE_Y + 1.0, hz), (0, 1, 0), 70, (x, 0, z0))
        add('int_door', INT, lathe([(0, 0), (0.02, 0), (0.02, 0.05), (0, 0.05)], hp, rotmat((0, 1, 0), 70) @ np.array([1, 0, 0]), 12), 'stainless_sys')

bulkhead(-4.9, [])
bulkhead(-0.95, [(-0.35, 0.35)])
bulkhead(4.35, [(-0.35, 0.3)])

def bed(x0, x1, z0, z1, head='aft', pillow_mat='fabric_blue'):
    H = SOLE_Y
    add('int_bed', INT, rbox((x0 + 0.04, H, z0 + 0.04), (x1 - 0.04, H + 0.33, z1 - 0.04), 0.02), 'walnut')
    for zz in (z0 + 0.04, z1 - 0.04):  # drawer fronts
        for k in range(2):
            xa = x0 + 0.25 + k * (x1 - x0 - 0.5) / 2
            xb = xa + (x1 - x0 - 0.6) / 2
            add('int_bed', INT, rbox((xa, H + 0.06, zz - 0.012), (xb, H + 0.27, zz + 0.012), 0.008, 2), 'oak_light')
            add('int_bed', INT, rbox(((xa + xb) / 2 - 0.08, H + 0.22, zz - 0.02), ((xa + xb) / 2 + 0.08, H + 0.235, zz + 0.02), 0.005, 1), 'stainless_sys')
    add('int_bed', INT, rbox((x0, H + 0.33, z0), (x1, H + 0.36, z1), 0.012), 'oak_light')
    add('int_bed', INT, rbox((x0 + 0.02, H + 0.36, z0 + 0.02), (x1 - 0.02, H + 0.58, z1 - 0.02), 0.07, 3), 'fabric_white')
    fx = x1 - 0.55 if head == 'aft' else x0 + 0.02
    add('int_bed', INT, rbox((fx, H + 0.56, z0 - 0.01), (fx + 0.5, H + 0.61, z1 + 0.01), 0.025, 3), 'fabric_blue')
    hx = x0 - 0.12 if head == 'aft' else x1 + 0.02
    add('int_headboard', INT, rbox((hx, H, z0 - 0.1), (hx + 0.1, H + 1.2, z1 + 0.1), 0.02), 'walnut')
    ncol = max(3, int((z1 - z0) / 0.3))
    for k in range(ncol):
        za = z0 - 0.06 + k * (z1 - z0 + 0.12) / ncol; zb = za + (z1 - z0 + 0.12) / ncol - 0.012
        add('int_headboard', INT, rbox((hx + 0.1, H + 0.45, za), (hx + 0.16, H + 1.14, zb), 0.03, 3), 'fabric_cream')
    n = 2 if (z1 - z0) > 1.0 else 1
    for k in range(n):
        zc = z0 + (z1 - z0) * (k + 0.5) / n; hw = min(0.34, (z1 - z0) / n / 2 - 0.05)
        px = x0 + 0.28 if head == 'aft' else x1 - 0.28
        add('int_pillow', INT, rbox((px - 0.14, H + 0.58, zc - hw), (px + 0.14, H + 0.74, zc + hw), 0.07, 3), 'fabric_white')
        add('int_pillow', INT, rotate(rbox((px + 0.02, H + 0.6, zc - hw * 0.6), (px + 0.2, H + 0.75, zc + hw * 0.6), 0.06, 3), (0, 0, 1), -35, (px + 0.1, H + 0.6, zc)), pillow_mat)

def nightstand(x0, z, lamp=True):
    H = SOLE_Y
    add('int_nightstand', INT, rbox((x0, H, z - 0.22), (x0 + 0.42, H + 0.5, z + 0.22), 0.015), 'walnut')
    add('int_nightstand', INT, rbox((x0 + 0.42, H + 0.28, z - 0.2), (x0 + 0.43, H + 0.46, z + 0.2), 0.006, 1), 'oak_light')
    add('int_nightstand', INT, rbox((x0 + 0.43, H + 0.36, z - 0.06), (x0 + 0.44, H + 0.375, z + 0.06), 0.004, 1), 'stainless_sys')
    if lamp:
        add('int_lamp', INT, lathe([(0, 0), (0.06, 0), (0.06, 0.02), (0.012, 0.03), (0.012, 0.3), (0, 0.3)], (x0 + 0.21, H + 0.5, z), (0, 1, 0), 18), 'stainless_sys')
        add('int_lamp', INT, lathe([(0.1, 0), (0.07, 0.18), (0.07, 0.18), (0, 0.18)], (x0 + 0.21, H + 0.72, z), (0, 1, 0), 24), 'fabric_cream')

def wardrobe(x0, x1, z0, z1, y1, face):
    H = SOLE_Y
    add('int_wardrobe', INT, rbox((x0, H, z0), (x1, y1, z1), 0.015), 'oak_light')
    n = max(1, int(round((x1 - x0) / 0.5)))
    fz = z0 if face < 0 else z1
    for k in range(n):
        xa = x0 + 0.02 + k * (x1 - x0 - 0.04) / n; xb = xa + (x1 - x0 - 0.04) / n - 0.01
        add('int_wardrobe', INT, rbox((xa, H + 0.08, fz - 0.012), (xb, y1 - 0.04, fz + 0.012), 0.008, 2), 'walnut')
        hx = xb - 0.05 if k % 2 == 0 else xa + 0.05
        add('int_wardrobe', INT, rbox((hx - 0.008, H + 0.9, fz + face * 0.012), (hx + 0.008, H + 1.2, fz + face * 0.03), 0.004, 1), 'stainless_sys')

# master stateroom (full beam amidships)
bed(-3.5, -1.55, -0.95, 0.95, 'aft')
for z in (-1.32, 1.32): nightstand(-3.62, z)
wardrobe(-4.6, -1.5, -2.85, -2.35, 1.2, 1)
wardrobe(-4.6, -2.7, 2.35, 2.85, 1.2, -1)
add('int_sofa', INT, rbox((-2.5, SOLE_Y, 2.0), (-1.3, SOLE_Y + 0.42, 2.6), 0.03), 'walnut')
add('int_sofa', INT, rbox((-2.48, SOLE_Y + 0.42, 2.02), (-1.32, SOLE_Y + 0.56, 2.56), 0.05, 3), 'fabric_cream')
add('int_sofa', INT, rbox((-2.48, SOLE_Y + 0.5, 2.44), (-1.32, SOLE_Y + 0.95, 2.58), 0.05, 3), 'fabric_cream')
for zc in (-0.4, 0.4):
    add('int_pillow', INT, rbox((-3.0 + zc, SOLE_Y + 0.55, 2.3), (-2.62 + zc, SOLE_Y + 0.85, 2.44), 0.06, 3), 'fabric_blue') if False else None
# starboard guest (double) and port guest (single)
bed(-0.3, 1.65, 0.5, 1.9, 'aft')
nightstand(-0.42, 2.1, lamp=True)
bed(1.55, 3.4, -2.0, -1.2, 'aft', pillow_mat='fabric_cream')
wardrobe(1.9, 2.8, 1.72, 2.08, 1.0, -1)
# forward VIP
bed(5.05, 6.9, -0.72, 0.72, 'aft')
wardrobe(4.45, 4.95, -1.35, -0.9, 1.1, 1)
# companionway stairs from the saloon, with stringers and handrail
tread_pts = []
for k in range(7):
    x = -0.55 + k * 0.26; y = 1.43 - (k + 1) * 0.285
    add('int_stairs', INT, rbox((x, y - 0.045, -2.02), (x + 0.3, y, -1.38), 0.012), 'teak')
    add('int_stairs', INT, box((x + 0.28, y - 0.002, -1.99), (x + 0.3, y + 0.001, -1.41)), 'teak_caulk')
    tread_pts.append((x + 0.15, y))
for z in (-2.06, -1.34):
    sp = [(-0.62, 1.45), (-0.45, 1.45), (1.45, SOLE_Y + 0.1), (1.45, SOLE_Y), (1.25, SOLE_Y), (-0.62, 1.2)]
    add('int_stairs', INT, prism(sp, 'z', z - 0.02, z + 0.02), 'walnut')
rail = [(-0.5, 2.3, -1.3), (-0.3, 2.3, -1.3), (1.4, 0.35, -1.3), (1.55, 0.35, -1.3)]
add('int_stairs', INT, sweep(rail, 0.022, seg=12, smooth_path=True, step=0.05), 'stainless_sys')
for (x, y) in (tread_pts[0], tread_pts[3], tread_pts[6]):
    add('int_stairs', INT, cyl((x, y, -1.3), (x, y + 0.85 if y > 1.0 else y + 0.87, -1.3), 0.014, 10), 'stainless_sys')

# saloon dining table, galley and cockpit table (visible through the glazing)
def table(cx, cz, top_y, rx, rz, mat_top='teak'):
    top = lathe([(0, 0), (0.97, 0), (1.0, 0.01), (1.0, 0.035), (0.97, 0.045), (0, 0.045)], (0, 0, 0), (0, 1, 0), 48)
    top = scale(top, (rx, 1, rz)); top = translate(top, (cx, top_y - 0.045, cz))
    add('int_table', EXT, top, mat_top)
    add('int_table', EXT, lathe([(0, 0), (0.22, 0), (0.22, 0.012), (0.08, 0.03), (0.045, 0.06), (0.045, top_y - 1.52), (0.09, top_y - 1.5), (0.09, top_y - 1.47), (0, top_y - 1.47)],
                                (cx, 1.47, cz), (0, 1, 0), 28), 'stainless_sys')
table(1.4, 0.55, 2.05, 0.82, 0.36)
table(-5.3, 0.0, 2.1, 0.78, 0.5)
# galley
gz0, gz1 = -2.15, -1.6
add('int_galley', EXT, rbox((0.2, 1.47, gz0), (2.6, 2.3, gz1), 0.015), 'oak_light')
for k in range(4):
    xa = 0.24 + k * 0.59
    add('int_galley', EXT, rbox((xa, 1.55, gz1 - 0.005), (xa + 0.56, 2.24, gz1 + 0.012), 0.008, 2), 'walnut')
    add('int_galley', EXT, rbox((xa + 0.2, 2.17, gz1 + 0.012), (xa + 0.36, 2.185, gz1 + 0.03), 0.004, 1), 'stainless_sys')
add('int_galley', EXT, rbox((0.16, 2.3, gz0 - 0.02), (2.64, 2.35, gz1 + 0.04), 0.012), 'counter_black')
add('int_galley', EXT, rbox((0.5, 2.24, -2.02), (0.98, 2.352, -1.72), 0.03), 'stainless_sys')
add('int_galley', EXT, lathe([(0, 0), (0.03, 0), (0.03, 0.02), (0.018, 0.03), (0.018, 0.1), (0, 0.1)], (0.74, 2.35, -2.08), (0, 1, 0), 16), 'stainless_sys')
add('int_galley', EXT, sweep([(0.74, 2.44, -2.08), (0.74, 2.62, -2.08), (0.74, 2.64, -1.98), (0.74, 2.56, -1.9)], 0.014, seg=10), 'stainless_sys')
add('int_galley', EXT, rbox((1.45, 2.35, -2.06), (2.2, 2.356, -1.66), 0.004, 1), 'glass_dark')
for cx, cz, r in ((1.65, -1.95, 0.1), (2.0, -1.78, 0.08), (1.65, -1.76, 0.07), (2.0, -1.97, 0.09)):
    add('int_galley', EXT, torus((cx, 2.357, cz), (0, 1, 0), r, 0.003, 32, 4), 'panel_white')
add('int_galley', EXT, rbox((2.68, 1.47, gz0), (3.08, 2.62, gz1), 0.02), 'stainless_sys')
add('int_galley', EXT, rbox((2.7, 1.5, gz1), (3.06, 2.6, gz1 + 0.01), 0.01), 'stainless_sys')
add('int_galley', EXT, rbox((3.0, 1.9, gz1 + 0.01), (3.02, 2.4, gz1 + 0.04), 0.006, 1), 'breaker_black')

# ============================================================== HULL HARDWARE (exterior)
for z in (-0.18, 0.18):
    add('hw_ladder', EXT, sweep([(-15.7, 0.44, z), (-15.82, 0.38, z), (-15.86, 0.2, z), (-15.86, -0.78, z)], 0.02, seg=10), 'stainless_sys')
    add('hw_ladder', EXT, lathe([(0, 0), (0.035, 0), (0.035, 0.02), (0, 0.025)], (-15.7, 0.44, z), (0, 1, 0), 14), 'stainless_sys')
for k in range(4):
    y = 0.05 - k * 0.25
    add('hw_ladder', EXT, rbox((-15.9, y - 0.012, -0.18), (-15.8, y + 0.012, 0.18), 0.01), 'stainless_sys')
    add('hw_ladder', EXT, rbox((-15.9, y + 0.012, -0.16), (-15.8, y + 0.016, 0.16), 0.004, 1), 'rubber_black')
# delta-style anchor in the bow roller, with chain to the locker
ax, ay = 14.42, 2.18
shank = [(ax - 0.05, ay + 0.05), (ax + 0.02, ay + 0.05), (ax + 0.12, ay - 0.55), (ax + 0.04, ay - 0.57)]
add('hw_anchor', EXT, prism(shank, 'z', -0.022, 0.022), 'stainless_sys')
for sg in (-1, 1):
    fl = [(0, 0), (0.1, 0.06), (0.22, 0.02), (0.0, -0.3)]
    rows = []
    for t in np.linspace(0, 1, 6):
        z = sg * 0.28 * t
        rows.append([(ax + 0.08 + px * (1 - 0.6 * t), ay - 0.57 + py * (1 - 0.6 * t) - 0.04 * t, z) for px, py in fl])
    add('hw_anchor', EXT, loft(rows, close=True, caps=True), 'stainless_sys')
add('hw_anchor', EXT, torus((ax - 0.03, ay + 0.08, 0), (0, 0, 1), 0.035, 0.01, 16, 6), 'stainless_sys')
for k in range(7):
    p = np.array([ax - 0.12 - k * 0.075, ay + 0.1 + 0.02 * np.sin(k), 0.0])
    axis = (0, 1, 0) if k % 2 == 0 else (0, 0, 1)
    add('hw_chain', EXT, scale(torus(p, axis, 0.03, 0.008, 16, 6), (1.35, 1, 1), p), 'stainless_sys')

# ============================================================== propeller alignment fix
# Each nacelle is tilted ~5.7 degrees (its matrix); the propellers were placed level and 0.2 m low.
# Seat each hub on its nacelle's tail, on the same axis, and mirror the starboard propeller so the
# pair counter-rotates (outward turning), as on a real twin installation.
for i, nd in enumerate(J['nodes']):
    if nd.get('name') != 'propeller': continue
    zc = nd['matrix'][14]
    nac = next(n for n in J['nodes'] if n.get('name') == 'drive_nacelle' and abs(n['matrix'][14] - zc) < 1e-6)
    m = nac['matrix']; ax = np.array([m[0], m[1], m[2]])          # nacelle local +x in parent space
    org = np.array([m[12], m[13], m[14]])
    hub0 = org + ax * -0.92                                           # tail of the nacelle (radius 0.22)
    c0 = np.array([ax[1] * -1, ax[0], 0.0]) * -1                      # blade reference axis, perpendicular in the xy plane
    c1 = -ax                                                          # hub axis points aft along the nacelle
    c0 = np.cross(c1, [0, 0, 1]); c0 /= np.linalg.norm(c0)
    c2 = np.cross(c0, c1)
    if zc > 0: c2 = -c2                                               # starboard: mirrored blades
    nd['matrix'] = [*c0, 0, *c1, 0, *c2, 0, *hub0, 1]

# ============================================================== validate and write
bad = []
for name, grp, m, mat in PARTS:
    if grp != INT or name.startswith('elec_cable'): continue
    if name == 'int_stairs' and m['p'][:, 1].max() > 1.9: continue  # handrail rises into the saloon by design
    P = m['p'][::5]
    for p in P:
        x, y, z = p
        if y > deck_min(x) + 0.03: bad.append((name, 'above deck', np.round(p, 2))); break
        if y < keel(x) + 0.01: bad.append((name, 'below keel', np.round(p, 2))); break
        hb = half_beam(x, y)
        if hb and abs(z) > hb + 0.01: bad.append((name, f'outside beam {hb:.2f}', np.round(p, 2))); break
print('validation issues:', len(bad))
for b in bad[:30]: print('  ', b)

def align4(b):
    while len(b) % 4: b.append(0)

mat_index = {}
for name, spec in MATS.items():
    mat = {'name': name, 'doubleSided': True,
           'pbrMetallicRoughness': {'baseColorFactor': lin(spec['c']) + [1.0], 'metallicFactor': spec['m'], 'roughnessFactor': spec['r']}}
    if 'e' in spec: mat['emissiveFactor'] = lin(spec['e'])
    mat_index[name] = len(J['materials']); J['materials'].append(mat)

root = next(i for i, n in enumerate(J['nodes']) if n.get('name') == 'dpv_luxury_yacht')
groups = {}
for g in (INT, EXT):
    groups[g] = len(J['nodes']); J['nodes'].append({'name': g, 'children': []})
    J['nodes'][root]['children'].append(groups[g])

bucket = OrderedDict()
for name, grp, m, mat in PARTS:
    bucket.setdefault((name, grp), OrderedDict()).setdefault(mat, []).append(m)

def add_accessor(arr, comp, typ, target, minmax=False):
    align4(BIN); off = len(BIN); data = arr.tobytes(); BIN.extend(data)
    J['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data), 'target': target})
    acc = {'bufferView': len(J['bufferViews']) - 1, 'componentType': comp, 'count': len(arr), 'type': typ}
    if minmax: acc['min'] = arr.min(0).tolist(); acc['max'] = arr.max(0).tolist()
    J['accessors'].append(acc); return len(J['accessors']) - 1

tris = verts = 0
for (name, grp), bymat in bucket.items():
    prims = []
    for mat, ms in bymat.items():
        m = merge(*ms)
        pos = m['p'].astype(np.float32)
        nrm = (m['n'] / (np.linalg.norm(m['n'], axis=1, keepdims=True) + 1e-9)).astype(np.float32)
        idx = m['i'].astype(np.uint16) if len(pos) < 65535 else m['i'].astype(np.uint32)
        prims.append({'attributes': {'POSITION': add_accessor(pos, 5126, 'VEC3', 34962, True), 'NORMAL': add_accessor(nrm, 5126, 'VEC3', 34962)},
                      'indices': add_accessor(idx, 5123 if idx.dtype == np.uint16 else 5125, 'SCALAR', 34963), 'material': mat_index[mat]})
        tris += len(m['i']) // 3; verts += len(pos)
    J['meshes'].append({'name': name, 'primitives': prims})
    J['nodes'].append({'name': name, 'mesh': len(J['meshes']) - 1})
    J['nodes'][groups[grp]]['children'].append(len(J['nodes']) - 1)

align4(BIN)
J['buffers'][0]['byteLength'] = len(BIN)
js = json.dumps(J, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
glb = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(BIN))
glb += struct.pack('<I4s', len(js), b'JSON') + js + struct.pack('<I4s', len(BIN), b'BIN\x00') + bytes(BIN)
open(OUT, 'wb').write(glb)
print(f'nodes {len(bucket)}, +{tris} tris, +{verts} verts, file {len(glb)/1e6:.2f} MB')
