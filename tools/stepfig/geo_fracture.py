# -*- coding: utf-8 -*-
"""露头裂缝自动统计：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from skimage.draw import line_aa, line as dline
from skimage.morphology import skeletonize
from common import *

SET1, SET2 = 42., 128.          # 两组裂缝的真实走向

def s1():
    rng = np.random.default_rng(1)
    strike = np.r_[rng.normal(SET1, 6, 220), rng.normal(SET2, 7, 160)]
    head = [0., 35.]               # 两个拍摄方向（相机朝向）
    f, (a1, a2) = fig(2, wspace=.26, top=.84, bottom=.2)
    bins = np.arange(0, 181, 5)
    for h, c, lab in zip(head, [BLUE, CLAY], ['从南面拍', '从西南面拍']):
        img = np.mod(strike - h + rng.normal(0, 2, len(strike)), 180)
        a1.hist(img, bins, histtype='stepfilled', color=c, alpha=.35, lw=0)
        a1.hist(img, bins, histtype='step', color=c, lw=1.4)
    a1.set_xlim(0, 180); a1.set_xticks([0, 45, 90, 135, 180]); a1.set_xlabel('照片里的线方向 / °'); a1.set_ylabel('裂缝条数')
    ym = a1.get_ylim()[1]
    note(a1, 50, ym * .97, '从南面拍', BLUE, 9.2, 'left', 'top', True)
    note(a1, 21, ym * .80, '从西南面拍', CLAY, 9.2, 'left', 'top', True)
    note(a1, 178, ym * .97, '同一组裂缝\n落在不同角度', RED, 9.2, 'right', 'top')
    title(a1, 'trap', '只有图像方向')
    for h, c in zip(head, [BLUE, CLAY]):
        geo = np.mod(strike + rng.normal(0, 2, len(strike)), 180)
        a2.hist(geo, bins, histtype='step', color=c, lw=1.4)
    for v in (SET1, SET2): a2.axvline(v, color=JADE, lw=1.3, ls='--')
    note(a2, SET1 - 4, a2.get_ylim()[1] * .95, '罗盘实测\n%.0f°' % SET1, JADE, 9, 'right', 'top')
    note(a2, SET2 + 3, a2.get_ylim()[1] * .95, '%.0f°' % SET2, JADE, 9, 'left', 'top')
    a2.set_xlim(0, 180); a2.set_xticks([0, 45, 90, 135, 180]); a2.set_xlabel('换算后的走向 / °')
    title(a2, 'do', '用标定板换算成地质产状')
    return f

def _outcrop(n=110, seed=2, size=(150, 260)):
    rng = np.random.default_rng(seed)
    H, Wd = size
    tex = .55 + .25 * field(size, 6, seed) + .08 * rng.normal(size=size)
    bed = np.zeros(size, bool)
    for y in range(12, H, 22):
        yy = (y + 3 * np.sin(np.arange(Wd) / 30)).astype(int)
        bed[np.clip(yy, 0, H - 1), np.arange(Wd)] = True
    fr1, fr2 = np.zeros(size, bool), np.zeros(size, bool)
    segs = []
    for k in range(14):
        x0, y0 = rng.uniform(10, Wd - 10), rng.uniform(10, H - 10); L = rng.uniform(30, 70)
        for tgt, ang in [(fr1, 70), (fr2, -38)] if k % 2 == 0 else [(fr2, -38)]:
            a = np.deg2rad(ang + rng.normal(0, 4)); dx, dy = np.cos(a) * L / 2, np.sin(a) * L / 2
            rr, cc = dline(int(y0 - dy), int(x0 - dx), int(y0 + dy), int(x0 + dx))
            ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < Wd); tgt[rr[ok], cc[ok]] = True
            segs.append((x0, y0, ang, L, tgt is fr1))
    return tex, bed, fr1, fr2

def s2():
    tex, bed, fr1, fr2 = _outcrop()
    f, (a1, a2) = fig(2, widths=[1.55, 1], wspace=.12, top=.84, bottom=.16, left=.02, polar=(1,))
    rgb = np.dstack([tex] * 3) * np.array([1, .97, .9])
    rgb[ndimage.binary_dilation(bed)] = mpl.colors.to_rgb('#9a8f7a')
    rgb[ndimage.binary_dilation(fr1)] = mpl.colors.to_rgb(JADE)
    rgb[ndimage.binary_dilation(fr2)] = mpl.colors.to_rgb(BLUE)
    a1.imshow(np.clip(rgb, 0, 1), aspect='auto'); img_axes(a1)
    note(a1, .5, -.04, '绿：充填（早期）　蓝：未充填（晚期）　褐：层理，不标', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'do', '先定分组规则再标注')
    rng = np.random.default_rng(3)
    good = np.r_[rng.normal(SET1, 6, 200), rng.normal(SET2, 7, 150)]
    bad = np.r_[good, rng.normal(92, 4, 170)]
    rose(a2, bad, color=RED, alpha=.55)
    rose(a2, good, color=JADE, alpha=.9)
    title(a2, 'trap', '层理混进标注')
    note(a2, .5, -.1, '红：多出的假峰', RED, 9, 'center', 'top', transform=a2.transAxes)
    return f

def s3():
    rng = np.random.default_rng(4)
    H, Wd = 140, 250
    tex = .62 + .22 * field((H, Wd), 7, 5) + .07 * rng.normal(size=(H, Wd))
    inst = []
    for x0, y0, ang, L, w in [(40, 70, 68, 90, 1.6), (95, 60, -40, 80, 1.2), (150, 80, 72, 100, 1.4), (205, 55, -35, 70, 1.0), (120, 115, -38, 45, .8)]:
        a = np.deg2rad(ang); m = np.zeros((H, Wd), bool)
        rr, cc = dline(int(y0 - np.sin(a) * L / 2), int(x0 - np.cos(a) * L / 2), int(y0 + np.sin(a) * L / 2), int(x0 + np.cos(a) * L / 2))
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < Wd); m[rr[ok], cc[ok]] = True
        m = ndimage.binary_dilation(m, iterations=int(round(w))); inst.append(m); tex[m] -= .42
    yy, xx = np.mgrid[0:H, 0:Wd]
    shadow = ((xx - 222) / 26) ** 2 + ((yy - 112) / 15) ** 2 < 1; tex[shadow] -= .28
    t = np.linspace(0, 1, 200); rx = (62 + 30 * t + 6 * np.sin(t * 14)).astype(int); ry = (8 + 30 * t).astype(int)
    root = np.zeros((H, Wd), bool); root[ry, rx] = True; root = ndimage.binary_dilation(root); tex[root] -= .35
    rain = np.zeros((H, Wd), bool); rain[20:70, 238] = True; rain[30:85, 243] = True; tex[ndimage.binary_dilation(rain)] -= .16
    tex = np.clip(tex, 0, 1)
    f, (a1, a2) = fig(2, wspace=.05, top=.84, bottom=.15, left=.015, right=.985)
    for ax in (a1, a2): ax.imshow(tex, cmap='gray', vmin=0, vmax=1.05, aspect='auto'); img_axes(ax)
    conf = [.96, .93, .95, .88, .71]
    cols = [JADE, BLUE, JADE, BLUE, BLUE]
    for m, c, p in zip(inst, cols, conf):
        a1.contour(m, [.5], colors=[c], linewidths=1.3)
        cy, cx = np.argwhere(m).mean(0); note(a1, cx + 6, cy, '%.2f' % p, c, 8.8, 'left', 'center', True, box=True)
    title(a1, 'do', '逐条输出掩膜与置信度')
    note(a1, .5, -.04, '5 条裂缝都找到，细裂缝置信度较低', JADE, 9, 'center', 'top', transform=a1.transAxes)
    for m in inst: a2.contour(m, [.5], colors=[LGREY], linewidths=1)
    for m, lab, (lx, ly) in [(shadow, '阴影 0.64', (196, 133)), (root, '植物根系 0.58', (98, 14)), (ndimage.binary_dilation(rain, iterations=2), '雨痕 0.52', (232, 16))]:
        a2.contour(m, [.5], colors=[RED], linewidths=1.5)
        note(a2, lx, ly, lab, RED, 8.8, 'right' if lx > 200 else 'left', 'center', True, box=True)
    title(a2, 'trap', '暗色条带都像裂缝')
    note(a2, .5, -.04, '没有困难负样本时，这三处也被输出', RED, 9, 'center', 'top', transform=a2.transAxes)
    return f

def s4():
    rng = np.random.default_rng(7)
    H, Wd = 120, 120
    m = np.zeros((H, Wd), bool)
    t = np.linspace(0, 1, 400); ang = np.deg2rad(SET1)
    xs = 15 + t * 92 * np.sin(ang) + 2.5 * np.sin(t * 9); ys = 105 - t * 92 * np.cos(ang) + 2 * np.cos(t * 7)
    m[ys.astype(int), xs.astype(int)] = True
    m = ndimage.binary_dilation(m, iterations=3) & (rng.random((H, Wd)) > .04)
    m = ndimage.binary_closing(m, iterations=2)
    sk = skeletonize(m)
    py, px = np.nonzero(sk)
    c = np.c_[px, -py].astype(float); c -= c.mean(0)
    v = np.linalg.svd(c, full_matrices=False)[2][0]
    est = np.rad2deg(np.arctan2(v[0], v[1])) % 180
    f, (a1, a2) = fig(2, widths=[1, 1.35], wspace=.30, top=.84, bottom=.2, left=.03)
    a1.imshow(m, cmap=ListedColormap(['#f4f4f0', '#c9c9c4']), aspect='equal')
    a1.imshow(np.ma.masked_where(~ndimage.binary_dilation(sk), sk), cmap=ListedColormap([INK]), aspect='equal')
    cx, cy = px.mean(), py.mean(); L = 60
    a1.plot([cx - v[0] * L, cx + v[0] * L], [cy + v[1] * L, cy - v[1] * L], color=JADE, lw=1.6, ls='--')
    a1.annotate('', xy=(10, 2), xytext=(10, 20), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.2)); note(a1, 10, 23, 'N', INK, 9, 'center', 'top', True)
    note(a1, 116, 112, '拟合走向 %.0f°\n（实测 %.0f°）' % (est, SET1), JADE, 9.4, 'right', 'bottom', True)
    img_axes(a1); a1.set_xlim(0, Wd - 1); a1.set_ylim(H - 1, 0)
    note(a1, .5, -.04, '灰：掩膜　黑：骨架　虚线：拟合方向', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'do', '骨架化后拟合产状')
    th = np.linspace(0, 90, 91)
    for phi, c in [(0, JADE), (20, CLAY), (40, RED)]:
        app = np.rad2deg(np.arctan(np.tan(np.deg2rad(th)) * np.cos(np.deg2rad(phi))))
        a2.plot(th, app - th, color=c, lw=1.8)
        k = np.argmin(app - th)
        if phi: note(a2, th[k], (app - th)[k] - .8, '倾斜 %d°：最大偏 %.0f°' % (phi, -(app - th)[k]), c, 9, 'center', 'top')
    note(a2, 88, .8, '正对拍摄：无偏差', JADE, 9, 'right', 'bottom')
    a2.set_xlim(0, 90); a2.set_ylim(-10.5, 2.5); a2.set_xticks([0, 30, 60, 90])
    a2.set_xlabel('裂缝真实方向（与水平夹角）/ °'); a2.set_ylabel('照片中的方向偏差 / °')
    title(a2, 'trap', '倾斜拍摄不做纠正')
    return f

def s5():
    rng = np.random.default_rng(9)
    main = np.r_[rng.normal(SET1, 6, 90), rng.normal(SET2, 7, 70)]; Lm = rng.lognormal(1.3, .4, len(main))
    weath = rng.uniform(0, 180, 420); Lw = rng.lognormal(-.6, .35, len(weath))
    ang, L = np.r_[main, weath], np.r_[Lm, Lw]
    f, (a1, a2, a3) = fig(3, widths=[1, 1, 1.25], wspace=.36, top=.76, bottom=.22, left=.04, polar=(0, 1))
    rose(a1, ang, color=RED, alpha=.8); rose(a2, ang, weights=L, color=JADE)
    for ax, k, t in [(a1, 'trap', '按条数'), (a2, 'do', '按长度加权')]:
        title(ax, k, t)
    note(a1, .5, -.1, '风化裂隙占多数\n主裂缝被淹没', RED, 9, 'center', 'top', transform=a1.transAxes)
    note(a2, .5, -.1, '%.0f° 与 %.0f°\n两组突出' % (SET1, SET2), JADE, 9, 'center', 'top', transform=a2.transAxes)
    n = 14; comp = rng.uniform(20, 150, n); auto = comp + rng.normal(0, 2.5, n); auto[[3, 9]] += [16, -15]
    bad = np.abs(auto - comp) > 6
    a3.fill_between([0, 180], [-6, 174], [6, 186], color=JADE, alpha=.12, lw=0)
    a3.plot([0, 180], [0, 180], color=JADE, lw=1)
    a3.scatter(comp[~bad], auto[~bad], s=24, color=INK, zorder=3)
    a3.scatter(comp[bad], auto[bad], s=34, facecolor='white', edgecolor=RED, lw=1.6, zorder=3)
    for i in np.nonzero(bad)[0]: note(a3, comp[i] + (7 if auto[i] < comp[i] else -7), auto[i], '重拍', RED, 9, 'left' if auto[i] < comp[i] else 'right', 'center', True)
    a3.set_xlim(0, 180); a3.set_ylim(0, 180); a3.set_xticks([0, 90, 180]); a3.set_yticks([0, 90, 180])
    a3.set_xlabel('罗盘实测走向 / °'); a3.set_ylabel('自动统计 / °'); a3.set_aspect('equal', adjustable='box')
    note(a3, 175, 8, '绿带：±6°', JADE, 8.8, 'right', 'bottom')
    title(a3, 'check', '罗盘抽查')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：同一组裂缝从两个方向拍，照片里的角度对不上；右：用标定板求出相机朝向和比例尺后，换算成走向与罗盘实测一致。',
        '左：先按充填物和切割关系分组，层理面不标；右：层理面混进标注后，玫瑰图多出一个假峰（红色）。',
        '左：模型逐条输出裂缝掩膜和置信度；右：阴影、植物根系、雨痕都是暗色条带，没有困难负样本时会被当成裂缝。',
        '左：掩膜骨架化后拟合出走向，与实测相差很小；右：相机倾斜时，照片里的方向系统性偏转，倾斜越大偏差越大。',
        '左、中：同一批数据，按条数统计被短小风化裂隙主导，按长度加权后两组主裂缝才显现；右：罗盘抽查，偏差大的露头重拍。']
