# -*- coding: utf-8 -*-
"""油气地球化学异常识别：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree, ConvexHull
from matplotlib.patches import Ellipse, Polygon
from common import *

def s1():
    rng = np.random.default_rng(1)
    a = 10 ** rng.normal(1.25, .22, 600)            # 春季批次 ppm
    b = 10 ** (rng.normal(1.25, .22, 600) + .28)    # 秋季批次：系统性偏高
    allv = np.r_[a, b]; thr = np.quantile(allv, .95)
    fa, fb = (a > thr).mean(), (b > thr).mean()
    la, lb = np.log10(a) - np.median(np.log10(a)), np.log10(b) - np.median(np.log10(b))
    thr2 = np.quantile(np.r_[la, lb], .95); ga, gb = (la > thr2).mean(), (lb > thr2).mean()
    f, (a1, a2) = fig(2, wspace=.30, top=.84, bottom=.2)
    bins = np.linspace(0, 110, 34)
    a1.hist(a, bins, color=BLUE, alpha=.55, label='春季批次'); a1.hist(b, bins, color=CLAY, alpha=.55, label='秋季批次')
    a1.axvline(thr, color=RED, lw=1.4, ls='--'); note(a1, thr + 2, a1.get_ylim()[1] * .30, '异常阈值', RED, 9.2)
    note(a1, 108, a1.get_ylim()[1] * .55, '超阈值比例\n春季 %s\n秋季 %s' % (pct(fa), pct(fb)), INK, 9.3, 'right', 'center')
    a1.set_xlabel('甲烷含量 / ppm'); a1.set_ylabel('样品数'); a1.set_xlim(0, 110)
    a1.legend(loc='upper right', handlelength=1, borderaxespad=0)
    title(a1, 'trap', '直接混用两批样品')
    bins = np.linspace(-.8, .8, 34)
    a2.hist(la, bins, color=BLUE, alpha=.55); a2.hist(lb, bins, color=CLAY, alpha=.55)
    a2.axvline(thr2, color=JADE, lw=1.4, ls='--'); note(a2, thr2 + .03, a2.get_ylim()[1] * .30, '异常阈值', JADE, 9.2)
    note(a2, -.78, a2.get_ylim()[1] * .82, '超阈值比例\n春季 %s\n秋季 %s' % (pct(ga), pct(gb)), INK, 9.3, 'left', 'center')
    a2.set_xlabel('log10(含量) − 本批次中位数'); a2.set_xlim(-.8, .8)
    title(a2, 'do', '对数变换 + 批次校正')
    return f

def _survey(seed=2, n=300):
    rng = np.random.default_rng(seed)
    xy = rng.uniform(0, 100, (n, 2))
    fc, fr = np.array([32, 62]), np.array([13, 8])                 # 已知油气田（椭圆）
    dfield = np.hypot(*((xy - fc) / fr).T) - 1
    droad = np.abs(xy[:, 1] - (.35 * xy[:, 0] + 8)) / np.hypot(1, .35)
    halo = 2.6 * np.exp(-np.clip(dfield, 0, None) * 1.4) * (dfield > -1)
    road = 3.0 * np.exp(-droad / 1.5)
    z = rng.normal(0, 1, n) + halo + road
    return xy, z, dfield, droad, halo, fc, fr

def s2():
    xy, z, dfield, droad, halo, fc, fr = _survey()
    bg = (dfield > 1.2) & (droad > 6)
    t_clean = z[bg].mean() + 2 * z[bg].std(); t_dirty = z.mean() + 2 * z.std()
    true_anom = halo > 1.2
    hit_c, hit_d = (z[true_anom] > t_clean).mean(), (z[true_anom] > t_dirty).mean()
    f, (a1, a2) = fig(2, widths=[1, 1.15], wspace=.22, top=.84, bottom=.2, left=.02)
    a1.add_patch(Ellipse(fc, 2 * fr[0], 2 * fr[1], fc=JADE, alpha=.22, ec=JADE, lw=1.2))
    xs = np.array([0, 100]); a1.fill_between(xs, .35 * xs + 8 - 6.4, .35 * xs + 8 + 6.4, color=GREY, alpha=.12, lw=0)
    a1.plot(xs, .35 * xs + 8, color=MUTE, lw=2)
    a1.scatter(*xy[bg].T, s=9, color=INK, lw=0)
    a1.scatter(*xy[~bg].T, s=10, facecolor='white', edgecolor=GREY, lw=.8)
    note(a1, fc[0], fc[1], '已知油气区', JADE, 9.2, 'center', 'center', True, box=True)
    note(a1, 97, .35 * 97 + 8 - 7, '公路', MUTE, 9.2, 'right', 'top', box=True)
    map_axes(a1, (0, 100), (0, 100))
    note(a1, .5, -.04, '实心：背景样本　空心：排除', MUTE, 9, 'center', 'top', transform=a1.transAxes)
    title(a1, 'do', '远离油气区与公路取背景')
    bins = np.linspace(-3, 6, 40)
    a2.hist(z[bg], bins, color=INK, alpha=.7, label='干净背景')
    a2.hist(z[~bg], bins, color=GREY, alpha=.45, label='混入的点')
    a2.axvline(t_clean, color=JADE, lw=1.5, ls='--'); a2.axvline(t_dirty, color=RED, lw=1.5, ls='--')
    ym = a2.get_ylim()[1]
    note(a2, t_clean - .12, ym * 1.0, '干净背景阈值\n真异常检出 %s' % pct(hit_c), JADE, 9, 'right', 'top', box=True)
    note(a2, t_dirty + .1, ym * .95, '混入后阈值\n检出 %s' % pct(hit_d), RED, 9, 'left', 'top')
    a2.set_xlabel('综合指标（标准化）'); a2.set_ylabel('样品数'); a2.set_xlim(-3, 6)
    a2.legend(loc='center right', bbox_to_anchor=(1, .5), handlelength=1, borderaxespad=0)
    title(a2, 'trap', '背景混入异常，阈值被抬高')
    return f

def s3():
    rng = np.random.default_rng(3)
    mu, sd = np.array([300., .40]), np.array([60., .08])
    bg = rng.normal(mu, sd, (220, 2))
    pts = {'A 甲烷单项高': np.array([560., .41]), 'B 碳同位素单项高': np.array([305., .63]), 'C 两项都偏高': np.array([455., .60])}
    raw = {k: np.hypot(*(v - mu)) for k, v in pts.items()}
    zs = {k: np.clip((v - mu) / sd, 0, None).sum() for k, v in pts.items()}
    cols = [CLAY, BLUE, JADE]
    f, (a1, a2) = fig(2, widths=[.9, 1.2], wspace=.42, top=.84, bottom=.2)
    names = list(pts); short = ['A', 'B', 'C']
    rk = lambda d: {k: i + 1 for i, k in enumerate(sorted(d, key=d.get, reverse=True))}
    rr, rz = rk(raw), rk(zs)
    x = np.arange(3); w = .36
    rv = np.array([raw[k] for k in names]); zv = np.array([zs[k] for k in names])
    a1.bar(x - w / 2, rv / rv.max(), w, color=GREY); a1.bar(x + w / 2, zv / zv.max(), w, color=cols)
    for i, k in enumerate(names):
        note(a1, i - w / 2, rv[i] / rv.max() + .02, '第%d' % rr[k], MUTE, 8.8, 'center', 'bottom')
        note(a1, i + w / 2, zv[i] / zv.max() + .02, '第%d' % rz[k], cols[i], 9.2, 'center', 'bottom', True)
    a1.set_xticks(x, short); a1.set_ylim(0, 1.25); a1.set_yticks([0, .5, 1]); a1.set_ylabel('异常得分（归一化）')
    note(a1, 1, 1.2, '灰：原始量纲　彩：标准化后', MUTE, 8.8, 'center', 'center')
    note(a1, 1, -.2, 'A 甲烷单项高　B 碳同位素单项高　C 两项都偏高', MUTE, 8.6, 'center', 'top', transform=a1.get_xaxis_transform()) if False else None
    title(a1, 'trap', '量纲不统一')
    zb = (bg - mu) / sd
    a2.scatter(*zb.T, s=7, color=GREY, lw=0, alpha=.8)
    for r in (2, 3, 4, 5):
        a2.plot([r + 4, -4], [-4, r + 4], color=LGREY if r != 3 else GREY, lw=.9, ls='-' if r != 3 else '--', zorder=0)
        if r != 3: note(a2, r + .1, .1, '%d' % r, GREY, 8.5, 'left', 'center') if False else None
    for (k, v), c, s in zip(pts.items(), cols, short):
        zz = (v - mu) / sd; a2.scatter(*zz, s=46, color=c, zorder=4, edgecolor='white', lw=.8)
        note(a2, zz[0] + .3, zz[1], '%s  %.1f' % (s, zs[k]), c, 9.6, 'left', 'center', True)
    a2.set_xlim(-3.5, 6.2); a2.set_ylim(-3.5, 4.6); a2.set_aspect('equal', adjustable='box')
    a2.set_xlabel('甲烷 z 值'); a2.set_ylabel('碳同位素 z 值')
    note(a2, 6.0, -3.2, '斜线：得分等值线（z 值之和）', GREY, 8.8, 'right', 'center')
    title(a2, 'do', '标准化后按偏离程度打分')
    return f

def _dbscan(xy, eps, minpts=4):
    tree = cKDTree(xy); nb = tree.query_ball_point(xy, eps)
    lab = -np.ones(len(xy), int); c = 0
    for i in range(len(xy)):
        if lab[i] != -1 or len(nb[i]) < minpts: continue
        stack = [i]; lab[i] = c
        while stack:
            j = stack.pop()
            if len(nb[j]) < minpts: continue
            for k in nb[j]:
                if lab[k] == -1: lab[k] = c; stack.append(k)
        c += 1
    return lab

def s4():
    rng = np.random.default_rng(6)
    c1 = rng.normal([28, 70], [4, 3], (16, 2)); c2 = rng.normal([60, 62], [3.5, 4], (14, 2))
    scat = np.r_[rng.uniform(10, 90, (6, 2)), [[40, 63], [48, 67], [36, 52]]]
    rx = rng.uniform(5, 95, 7); road = np.c_[rx, .35 * rx + 8 + rng.normal(0, .8, 7)]
    xy = np.r_[c1, c2, scat]
    def draw(ax, eps, kind, ttl):
        lab = _dbscan(xy, eps)
        ax.plot([0, 100], [8, 43], color=MUTE, lw=2); ax.fill_between([0, 100], [1.6, 36.6], [14.4, 49.4], color=GREY, alpha=.12, lw=0)
        areas = []
        for c in range(lab.max() + 1):
            p = xy[lab == c]
            if len(p) >= 3:
                h = ConvexHull(p); cc = JADE if kind == 'do' else RED; ax.add_patch(Polygon(p[h.vertices], closed=True, fc=mpl.colors.to_rgba(cc, .18), ec=cc, lw=1.5))
                areas.append(h.volume)
        ax.scatter(*xy.T, s=14, color=INK, lw=0, zorder=3)
        ax.scatter(*road.T, s=18, facecolor='white', edgecolor=CLAY, lw=1.2, zorder=3)
        map_axes(ax, (0, 100), (0, 100))
        title(ax, kind, ttl)
        return lab, areas
    f, (a1, a2) = fig(2, wspace=.08, left=.03, right=.97, top=.84, bottom=.17)
    l1, ar1 = draw(a1, 6, 'do', '聚类半径 6 km')
    l2, ar2 = draw(a2, 13, 'trap', '聚类半径 13 km')
    note(a1, .5, -.04, '%d 个靶区；公路旁孤立点（空心）降权' % len(ar1), JADE, 9, 'center', 'top', transform=a1.transAxes)
    note(a2, .5, -.04, '无关的点被连成一个 %.0f km² 的大靶区' % max(ar2), RED, 9, 'center', 'top', transform=a2.transAxes)
    return f

def s5():
    f, (a1, a2) = fig(2, widths=[1.3, 1], wspace=.34, top=.84, bottom=.2, left=.03)
    tg = [('T1', 9.1, '微渗漏', 1), ('T2', 8.6, '公路污染', 5), ('T3', 7.9, '微渗漏', 2), ('T4', 7.2, '待定', 4), ('T5', 6.8, '微渗漏', 3)]
    for i, (n, s, cause, er) in enumerate(tg):
        y0, y1 = 5 - i, 6 - er
        col = RED if cause == '公路污染' else (JADE if cause == '微渗漏' else GREY)
        a1.plot([0, 1], [y0, y1], color=col, lw=2.2 if col != GREY else 1.4)
        a1.scatter([0, 1], [y0, y1], s=28, color=col, zorder=3)
        note(a1, -.06, y0, '%s  %.1f' % (n, s), INK, 9.3, 'right', 'center')
        note(a1, 1.06, y1, '%s · %s' % (n, cause), col, 9.3, 'left', 'center')
    a1.set_xlim(-.62, 1.75); a1.set_ylim(.6, 6.2); a1.axis('off')
    note(a1, 0, 5.5, '按得分', MUTE, 9, 'center', 'bottom'); note(a1, 1, 5.5, '按成因复排', MUTE, 9, 'center', 'bottom')
    title(a1, 'do', '看成因再排序')
    r = np.arange(1, 4); hit = np.array([2, 3, 4]); n = np.array([6, 6, 6])
    a2.bar(r, n, color=LGREY, width=.55); a2.bar(r, hit, color=JADE, width=.55)
    for x, h, m in zip(r, hit, n): note(a2, x, h + .15, '%d/%d' % (h, m), JADE, 9.6, 'center', 'bottom', True)
    a2.set_xticks(r, ['第1轮', '第2轮', '第3轮']); a2.set_ylim(0, 7.2); a2.set_ylabel('钻探靶区数')
    note(a2, 2, 6.9, '绿：见油气显示（示意）', MUTE, 8.8, 'center', 'top')
    title(a2, '回流', '钻探结果校准背景')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：两批样品直接混用，秋季批次整体偏高，超阈值的几乎都来自秋季；右：对数变换并扣除各批次中位数后，两批按同一标准比较。',
        '左：只用远离已知油气区和公路缓冲带的样本（实心）建背景；右：背景里混进异常点后，阈值右移，一部分真异常检不出来。',
        'A 只有甲烷高，B 只有碳同位素高，C 两项都偏高。左：原始量纲下甲烷数值大，A 排第一；右：换算成 z 值后相加，C 排第一。',
        '同一批高分点：半径合适时得到两个靶区，公路旁的孤立点降权；半径过大时无关的点被连成一个大靶区。',
        '左：专家结合成因复排，公路污染引起的 T2 从第 2 降到最后；右：每轮钻探结果回流后，靶区命中率逐轮提高（示意）。']
