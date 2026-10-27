# -*- coding: utf-8 -*-
"""案例流程每步示意图的公共样式与工具：全部用合成数据实际计算后绘制。"""
import io, re, os, math
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

INK, JADE, CLAY, BLUE, RED = '#212837', '#2f7d6b', '#b26a39', '#41699b', '#b05a51'
GREY, LGREY, MUTE = '#8a8a8a', '#d9d9d9', '#4a4a4a'
SAND, MOSS = '#d8c89a', '#9fb19c'
FONT = "'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif"
W_IN, H_IN = 6.0, 2.85          # 432×205 pt；页面上按 600px 宽显示，字号约放大 1.39 倍

mpl.rcParams.update({
    'svg.fonttype': 'none', 'svg.hashsalt': 'petro-steps',
    'font.family': 'sans-serif', 'font.sans-serif': ['Noto Sans CJK SC', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': 10, 'axes.titlesize': 10.5, 'axes.labelsize': 9.8,
    'xtick.labelsize': 9.3, 'ytick.labelsize': 9.3, 'legend.fontsize': 9.3,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#6b6b6b', 'axes.linewidth': .8,
    'xtick.color': '#3d3d3d', 'ytick.color': '#3d3d3d', 'xtick.major.size': 3, 'ytick.major.size': 3,
    'xtick.major.width': .8, 'ytick.major.width': .8,
    'axes.labelcolor': '#2f2f2f', 'text.color': INK, 'axes.titlecolor': INK,
    'axes.titlepad': 6, 'axes.titlelocation': 'left', 'axes.titleweight': 'bold',
    'legend.frameon': False, 'figure.facecolor': 'none', 'axes.facecolor': 'none',
    'savefig.facecolor': 'none', 'lines.linewidth': 1.8, 'hatch.linewidth': .6,
})

SEIS = LinearSegmentedColormap.from_list('seis', ['#262626', '#6f6f6f', '#c4c4c0', '#f7f7f3'])
PROB = LinearSegmentedColormap.from_list('prob', [(0.69, 0.35, 0.32, 0), (0.69, 0.35, 0.32, .95)])

def fig(ncols=2, widths=None, wspace=.32, **kw):
    f = plt.figure(figsize=(W_IN, H_IN))
    gs = f.add_gridspec(1, ncols, width_ratios=widths, wspace=wspace, left=kw.get('left', .085), right=kw.get('right', .985),
                        top=kw.get('top', .86), bottom=kw.get('bottom', .17))
    polar = kw.get('polar', ())
    return f, [f.add_subplot(gs[0, i], projection='polar' if i in polar else None) for i in range(ncols)]

def rose(ax, angles, weights=None, color=JADE, nb=18, half=True, alpha=.85, rmax=None, labels=True):
    """走向玫瑰图（0–180° 对称），angles 以度计、自北顺时针"""
    a = np.mod(angles, 180)
    h, e = np.histogram(a, bins=nb, range=(0, 180), weights=weights)
    h = h / h.max()
    w = np.deg2rad(180 / nb)
    for off in (0, 180):
        ax.bar(np.deg2rad(e[:-1] + off) + w / 2, h, width=w * .92, color=color, alpha=alpha, lw=0)
    ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
    ax.set_yticks([]); ax.set_ylim(0, rmax or 1.05)
    ax.set_xticks(np.deg2rad([0, 45, 90, 135]), ['N', '45°', 'E', '135°'] if labels else [] )
    ax.tick_params(axis='x', pad=-2, labelsize=8.6, colors='#555')
    ax.spines['polar'].set_color('#9a9a9a'); ax.spines['polar'].set_linewidth(.7)
    ax.grid(color='#d5d5d5', lw=.6)
    return h

def title(ax, kind, text):
    """kind: 'do' 做法（绿）/ 'trap' 常见问题（红）/ 其他直接写标题"""
    tag, col = {'do': ('做法', JADE), 'trap': ('常见问题', RED), 'check': ('检验', BLUE)}.get(kind, (kind, INK))
    t1 = ax.text(-.08 if ax.name == 'polar' else 0, 1.13 if ax.name == 'polar' else 1.04, tag, transform=ax.transAxes, color=col, fontsize=10.5, fontweight='bold', va='bottom')
    if text: ax.annotate(' ' + text, xy=(1, 0), xycoords=t1, va='bottom', ha='left', fontsize=10.5, color=INK)

def img_axes(ax):
    for s in ax.spines.values(): s.set_visible(True); s.set_color('#9a9a9a'); s.set_linewidth(.7)
    ax.set_xticks([]); ax.set_yticks([])

def note(ax, x, y, text, color=INK, size=9.5, ha='left', va='center', bold=False, box=False, **kw):
    bb = dict(boxstyle='round,pad=.25', fc='white', ec='none', alpha=.85) if box else None
    return ax.text(x, y, text, color=color, fontsize=size, ha=ha, va=va, fontweight='bold' if bold else 'normal', bbox=bb, **kw)

def save(f, path):
    buf = io.StringIO()
    f.savefig(buf, format='svg', metadata={'Date': None, 'Creator': None})
    plt.close(f)
    s = buf.getvalue()
    s = s[s.index('<svg'):]
    s = re.sub(r'font-family:[^;"]*', 'font-family: ' + FONT, s)
    s = re.sub(r'<metadata>.*?</metadata>', '', s, flags=re.S)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(s)
    return len(s)

# ---------------------------------------------------------------- 合成地震剖面
def ricker(f, dt=.002, n=None):
    n = n or int(.128 / dt)
    t = (np.arange(n) - n // 2) * dt
    a = (np.pi * f * t) ** 2
    return (1 - 2 * a) * np.exp(-a)

def reflectivity(n, rng, sparsity=.12):
    r = rng.normal(0, 1, n) * (rng.random(n) < sparsity)
    return r

def section(nx=220, nt=140, faults=(), fold=6., seed=1, f=45, noise=.04, unconf=None, mask_w=1.3):
    """faults: [(x_top, slope_dx_per_t, throw)]；返回 (振幅剖面[nt,nx], 断层掩膜[nt,nx])"""
    rng = np.random.default_rng(seed)
    r = reflectivity(nt * 3, rng)
    tt, xx = np.mgrid[0:nt, 0:nx].astype(float)
    tau = tt - fold * np.sin(xx / nx * 2.2 + .4) - .04 * xx
    mask = np.zeros((nt, nx), bool)
    for x0, sl, th in faults:
        xf = x0 + sl * tt
        tau = tau - th * (xx > xf)
        mask |= np.abs(xx - xf) < mask_w
    if unconf is not None:
        # 不整合面以上地层水平、以下倾斜（削截）
        above = tt < unconf
        tau = np.where(above, tt, tau + .12 * xx)
    w = ricker(f, n=48)
    tr = np.convolve(r, w, 'same')
    amp = np.interp(tau + nt, np.arange(len(tr)), tr)
    amp /= np.abs(amp).max() + 1e-9
    amp += rng.normal(0, noise, amp.shape)
    return amp, mask

# ---------------------------------------------------------------- 平面图工具
def field(shape, sigma, seed=0):
    """平滑随机场，归一化到 0–1"""
    from scipy import ndimage
    g = ndimage.gaussian_filter(np.random.default_rng(seed).normal(size=shape), sigma)
    g -= g.min(); return g / (g.max() + 1e-12)

def map_axes(ax, xlim=None, ylim=None, km=None):
    """平面图：保留细边框，去掉刻度；km=(x,y,len) 画比例尺"""
    img_axes(ax)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    ax.set_aspect('equal', adjustable='box')
    if km:
        x, y, L = km
        ax.plot([x, x + L], [y, y], color=INK, lw=2, solid_capstyle='butt')
        ax.text(x + L / 2, y, '%g km' % km[3] if len(km) > 3 else '', ha='center', va='bottom', fontsize=8.8, color=INK)

def pct(v, d=0): return ('%.' + str(d) + 'f%%') % (v * 100)
