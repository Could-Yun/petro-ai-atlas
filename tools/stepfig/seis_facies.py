# -*- coding: utf-8 -*-
"""地震相智能分类：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from scipy.cluster.vq import kmeans2
from common import *

FC = ['#d9b86a', '#9fb19c', '#c98f6a', '#8fa3b8', '#b7a7c9']
FN = ['河道', '分流间湾', '前缘砂', '前三角洲', '湖相泥']

def _wedge(nx=240, nt=140, seed=2):
    rng = np.random.default_rng(seed)
    x = np.arange(nx)[None, :].astype(float); t = np.arange(nt)[:, None].astype(float)
    top = 30 + .17 * x + 3 * np.sin(x / 40); bot = 60 + .30 * x + 3 * np.sin(x / 33)
    G = np.where(t < top, t - top + 100, np.where(t < bot, 100 + 40 * (t - top) / (bot - top), 140 + (t - bot)))
    r = reflectivity(400, rng, .2)
    tr = np.convolve(r, ricker(45, n=48), 'same')
    amp = np.interp(G + 60, np.arange(400), tr); amp /= np.abs(amp).max()
    return amp + rng.normal(0, .03, amp.shape), top, bot, (t >= top) & (t < bot)

def s1():
    amp, top, bot, inside = _wedge()
    nx = amp.shape[1]; x = np.arange(nx)
    prop = top[0] + .5 * (bot[0] - top[0])
    flat = np.full(nx, 48.)
    share_p = inside[np.clip(prop, 0, 139).astype(int), x].mean()
    share_f = inside[flat.astype(int), x].mean()
    f, (a1, a2) = fig(2, wspace=.05, top=.84, bottom=.15, left=.015, right=.985)
    for ax, line, k, t_, sh in [(a1, prop, 'do', '沿层取切片', share_p), (a2, flat, 'trap', '等时切片穿层', share_f)]:
        ax.imshow(amp, cmap=SEIS, vmin=-.8, vmax=.8, aspect='auto', interpolation='bilinear')
        ax.fill_between(x, top[0], bot[0], color=JADE, alpha=.08, lw=0)
        ax.plot(x, top[0], color=BLUE, lw=1.5); ax.plot(x, bot[0], color=BLUE, lw=1.5)
        c = JADE if k == 'do' else RED
        ax.plot(x, line, color=c, lw=2.4)
        img_axes(ax); ax.set_xlim(0, nx - 1); ax.set_ylim(amp.shape[0] - 1, 0); title(ax, k, t_)
        note(ax, .5, -.04, '切片上 %s 的样点来自目的层' % pct(sh), c, 9.2, 'center', 'top', True, transform=ax.transAxes)
    note(a1, 6, top[0][0] - 3, '顶', BLUE, 9, 'left', 'bottom', True); note(a1, 6, bot[0][0] + 3, '底', BLUE, 9, 'left', 'top', True)
    return f

def _tile(kind, n=40, seed=0):
    rng = np.random.default_rng(seed)
    t, x = np.mgrid[0:n, 0:n].astype(float)
    if kind == 0:   # 河道：透镜状、杂乱充填
        G = t + 6 * np.exp(-((x - 20) / 9) ** 2) * (t > 14); amp = np.sin(G / 1.6) * (1 - .6 * (np.abs(x - 20) < 9) * (t > 14) * rng.random((n, n)))
    elif kind == 1: amp = np.sin(t / 1.8) * (.45 + .25 * rng.random((n, n))) * (rng.random((1, n)) > .25)
    elif kind == 2: amp = np.sin(t / 1.7 + .5 * np.sin(x / 15))
    elif kind == 3: G = t - .6 * x * (t / n) ; amp = np.sin((t - .45 * x * np.tanh((t - 20) / 8)) / 1.7)
    else: amp = .35 * np.sin(t / 1.6 + .2 * np.sin(x / 10))
    return ndimage.gaussian_filter(amp, .6) + rng.normal(0, .06, (n, n))

def _features(seed=3, n=90):
    rng = np.random.default_rng(seed)
    cen = np.array([[.35, .75], [.45, .32], [.85, .82], [.62, .55], [.88, .25]])     # 连续性, 振幅
    X = np.vstack([rng.normal(c, .055, (n, 2)) for c in cen]); y = np.repeat(np.arange(5), n)
    return X, y, cen

def s2():
    f = plt.figure(figsize=(W_IN, H_IN))
    gs = f.add_gridspec(2, 6, width_ratios=[1, 1, 1, .2, 2.3, .02], hspace=.55, wspace=.12, left=.02, right=.98, top=.84, bottom=.17)
    pos = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    for k, (r, c) in enumerate(pos):
        ax = f.add_subplot(gs[r, c]); ax.imshow(_tile(k, seed=k), cmap=SEIS, vmin=-1, vmax=1, aspect='auto'); img_axes(ax)
        for s in ax.spines.values(): s.set_color(FC[k]); s.set_linewidth(2.2)
        note(ax, .5, -.06, FN[k], INK, 9, 'center', 'top', True, transform=ax.transAxes)
        if k == 0: title(ax, 'do', '5 类相带的典型剖面')
    ax = f.add_subplot(gs[1, 2]); ax.axis('off')
    note(ax, .05, .55, '每类配\n典型剖面\n和井点', MUTE, 8.8, 'left', 'center', transform=ax.transAxes)
    a2 = f.add_subplot(gs[:, 4])
    X, y, cen = _features()
    rng = np.random.default_rng(4)
    tr = (cen[2] + cen[3]) / 2 + rng.normal(0, .07, (70, 2))
    for k in range(5): a2.scatter(*X[y == k].T, s=7, color=FC[k], lw=0, alpha=.9)
    a2.scatter(*tr.T, s=14, facecolor='none', edgecolor=RED, lw=.9)
    d = ((tr[:, None, :] - cen[None]) ** 2).sum(-1); near = d.argmin(1)
    for k in range(5): note(a2, cen[k][0], cen[k][1] + .1, FN[k], INK, 8.8, 'center', 'bottom')
    note(a2, 1.04, .6, '红圈：过渡相\n%s 归入前缘砂\n%s 归入前三角洲' % (pct((near == 2).mean()), pct((near == 3).mean())), RED, 8.8, 'left', 'center')
    a2.set_xlim(.15, 1.6); a2.set_ylim(.05, 1.02); a2.set_xlabel('同相轴连续性'); a2.set_ylabel('振幅')
    title(a2, 'trap', '“过渡相”分不清')
    return f

def s3():
    X, y, cen = _features(seed=5)
    f = plt.figure(figsize=(W_IN, H_IN))
    gs = f.add_gridspec(1, 3, width_ratios=[1.25, .62, .62], wspace=.36, left=.085, right=.985, top=.78, bottom=.27)
    a1 = f.add_subplot(gs[0])
    runs = [kmeans2(X, 5, minit='++', seed=sd)[1] for sd in (0, 3)]
    mk = ['o', 's', '^', 'D', 'v']
    for k in range(5): a1.scatter(*X[runs[0] == k].T, s=10, marker=mk[k], facecolor='none', edgecolor=INK, lw=.6)
    for k in range(5):
        m = X[runs[0] == k].mean(0); note(a1, m[0] + .07, m[1] + .08, '簇 %d' % (k + 1), INK, 9, 'center', 'center', True, box=True)
    a1.set_xlim(.15, 1.1); a1.set_ylim(.05, 1.05); a1.set_xlabel('同相轴连续性'); a1.set_ylabel('振幅')
    title(a1, 'do', '无监督聚类：自然分成 5 组')
    short = ['河道', '间湾', '前缘', '前三', '湖泥']
    for j, lab in enumerate(runs):
        ax = f.add_subplot(gs[1 + j])
        ct = np.array([[((lab == k) & (y == c)).sum() for c in range(5)] for k in range(5)], float)
        ax.imshow(ct / ct.sum(1, keepdims=True), cmap=LinearSegmentedColormap.from_list('h', ['#f6f6f2', JADE]), vmin=0, vmax=1, aspect='auto')
        ax.set_yticks(range(5), ['簇%d' % (k + 1) for k in range(5)], fontsize=8.6); ax.set_xticks(range(5), short, fontsize=8.2, rotation=90)
        ax.tick_params(length=0)
        for sp in ax.spines.values(): sp.set_visible(False)
        c2 = ct[1].argmax(); ax.add_patch(mpl.patches.Rectangle((c2 - .5, .5), 1, 1, fill=False, ec=RED, lw=1.8))
        note(ax, .5, 1.03, ['第一次运行', '换随机种子'][j], MUTE, 9, 'center', 'bottom', transform=ax.transAxes)
        note(ax, .5, -.33, '簇2 = %s' % FN[c2], RED, 9.2, 'center', 'top', True, transform=ax.transAxes)
    t1 = f.axes[1].text(-.38, 1.14, '常见问题', transform=f.axes[1].transAxes, color=RED, fontsize=10.5, fontweight='bold', va='bottom')
    f.axes[1].annotate(' 编号本身没有地质含义', xy=(1, 0), xycoords=t1, va='bottom', fontsize=10.5, color=INK)
    return f

def s4():
    n1, n2 = 110, 150
    g = np.stack([field((n1, n2), 10, s) for s in range(5)]); truth = g.argmax(0)
    rng = np.random.default_rng(2)
    raw = truth.copy(); m = rng.random(truth.shape) < .16; raw[m] = rng.integers(0, 5, m.sum())
    cnt = np.stack([ndimage.uniform_filter((raw == c).astype(float), 5) for c in range(5)]); sm = cnt.argmax(0)
    f = plt.figure(figsize=(W_IN, H_IN))
    gs = f.add_gridspec(1, 4, width_ratios=[1, 1, .38, 1.3], wspace=.1, left=.015, right=.985, top=.84, bottom=.2)
    cm = ListedColormap(FC)
    for j, (img, t_) in enumerate([(raw, '分类结果'), (sm, '井点赋义 + 去碎斑')]):
        ax = f.add_subplot(gs[j]); ax.imshow(img, cmap=cm, vmin=0, vmax=4, aspect='auto', interpolation='nearest'); img_axes(ax)
        title(ax, '数据' if j == 0 else 'do', t_)
        if j:
            wl = rng.uniform([8, 8], [n2 - 8, n1 - 8], (12, 2))
            for x, y in wl: ax.plot(x, y, 'o', ms=5, mfc='white', mec=INK, mew=1.2)
            note(ax, .5, -.04, '圆点：标定用的井', MUTE, 8.8, 'center', 'top', transform=ax.transAxes)
        else: note(ax, .5, -.04, '碎斑 %s' % pct(m.mean()), MUTE, 8.8, 'center', 'top', transform=ax.transAxes)
    a3 = f.add_subplot(gs[3])
    p = .7; ns = np.arange(1, 11)
    from math import comb
    def pc(n):
        s = sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n // 2 + 1, n + 1))
        if n % 2 == 0: s += .5 * comb(n, n // 2) * p ** (n // 2) * (1 - p) ** (n // 2)
        return s
    pr = np.array([pc(n) for n in ns])
    a3.plot(ns, pr, 'o-', color=JADE, ms=4.5)
    a3.axvspan(.6, 2.4, color=RED, alpha=.08, lw=0)
    note(a3, 1.5, pr[0] - .02, '1—2 口井\n%s' % pct(pr[0]), RED, 9.2, 'center', 'top', True)
    note(a3, 8, pr[7] - .03, '8 口井 %s' % pct(pr[7]), JADE, 9.2, 'center', 'top', True)
    a3.set_xlim(.6, 10.4); a3.set_ylim(.6, 1.0); a3.set_xticks([1, 2, 4, 6, 8, 10]); a3.set_yticks([.6, .7, .8, .9, 1], ['60%', '70%', '80%', '90%', '100%'])
    a3.set_xlabel('用来标定一类的井数'); a3.set_ylabel('标定正确的概率')
    title(a3, 'trap', '井太少偶然性大')
    note(a3, 10.3, .61, '单口井相符概率设为 70%', MUTE, 8.4, 'right', 'bottom')
    return f

def s5():
    n1, n2 = 110, 160
    g = np.stack([field((n1, n2), 11, s + 10) for s in range(5)]); truth = g.argmax(0)
    g2 = g + .2 * np.stack([field((n1, n2), 6, s + 30) for s in range(5)]); pred = g2.argmax(0)
    rng = np.random.default_rng(6)
    tw = rng.uniform([6, 6], [n2 - 6, n1 - 6], (18, 2))
    wrong = np.argwhere(ndimage.binary_erosion(pred != truth, iterations=1)); right = np.argwhere(ndimage.binary_erosion(pred == truth, iterations=3))
    inner = lambda a: a[(a[:, 0] > 10) & (a[:, 0] < n1 - 10) & (a[:, 1] > 10) & (a[:, 1] < n2 - 30)]
    wrong, right = inner(wrong), inner(right)
    pick = lambda a, k: a[rng.choice(len(a), k, replace=False)][:, ::-1].astype(float)
    bw = np.r_[pick(right, 6), pick(wrong, 2)]
    ok_b = np.array([pred[int(y), int(x)] == truth[int(y), int(x)] for x, y in bw])
    acc_t = .95
    f, (a1, a2) = fig(2, widths=[1.25, 1], wspace=.26, top=.84, bottom=.2, left=.02)
    a1.imshow(pred, cmap=ListedColormap(FC), vmin=0, vmax=4, aspect='auto', interpolation='nearest')
    for x, y in tw: a1.plot(x, y, 'o', ms=4.5, color=INK)
    for (x, y), ok in zip(bw, ok_b):
        a1.plot(x, y, 'o', ms=8, mfc='white', mec=JADE if ok else RED, mew=2)
        if not ok: note(a1, x + 5, y, '不符', RED, 8.8, 'left', 'center', True, box=True)
    img_axes(a1)
    note(a1, .5, -.04, '黑点：训练井　空心圈：8 口盲井', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'check', '只在盲井上算符合率')
    v = [acc_t, ok_b.mean()]
    a2.bar([0, 1], v, color=[RED, JADE], width=.55)
    for i, val in enumerate(v): note(a2, i, val + .02, pct(val), [RED, JADE][i], 10.5, 'center', 'bottom', True)
    a2.set_xticks([0, 1], ['训练井（虚高）', '8 口盲井']); a2.set_ylim(0, 1.15); a2.set_yticks([0, .5, 1], ['0', '50%', '100%'])
    a2.set_ylabel('相带符合率')
    title(a2, 'trap', '训练井也算进去')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['同一条楔形地层剖面：沿顶底层位按比例取切片，全部样点都在目的层内；取等时切片时，一部分样点落到上下层段。',
        '左：先给 5 类相带配上典型剖面和井点；右：“过渡相”的特征夹在两类之间，模型和人都很难分开。',
        '左：无监督聚类先看数据自然分成几组；右：同一份数据换个随机种子再跑一次，簇编号对应的相带就变了，编号本身没有地质含义。',
        '左、中：分类结果去碎斑并用井点赋予地质含义；右：每口井与所属类别相符的概率为 70% 时，只用 1—2 口井标定，有约三成概率标错。',
        '左：8 口盲井预先留出，不参与训练；右：训练井上的符合率接近满分，盲井上的才是真实水平。']
