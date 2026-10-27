# -*- coding: utf-8 -*-
"""地质剖面遥感解译：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

LITH = ['#d9c68f', '#a9b8a0', '#c7a58b', '#8fa3b8', '#6d5f7d']     # 砂岩 泥岩 灰岩 火山岩 岩脉
LNAME = ['砂岩', '泥岩', '灰岩', '火山岩', '岩脉']
WL = np.array([.48, .56, .66, .86, 1.61, 2.2])

def _litho(shape=(120, 200), seed=3):
    g1, g2 = field(shape, 14, seed), field(shape, 18, seed + 1)
    lab = np.where(g1 > .55, 0, np.where(g2 > .5, 1, 2))
    return lab

def s1():
    sand = np.array([.18, .24, .31, .37, .44, .40]); mud = np.array([.12, .15, .19, .27, .33, .30])
    autumn = lambda s: s * .78 + np.array([0, .01, -.01, .06, -.02, -.03])     # 季相：太阳高度角低 + 植被
    f, (a1, a2) = fig(2, widths=[1, 1.15], wspace=.24, top=.84, bottom=.2)
    a1.plot(WL, sand, 'o-', color=CLAY, ms=4, lw=1.8); a1.plot(WL, autumn(sand), 'o--', color=CLAY, ms=4, lw=1.6)
    a1.plot(WL, mud, 'o-', color=BLUE, ms=4, lw=1.8)
    note(a1, 2.22, sand[-1] + .012, '砂岩 · 春', CLAY, 9.2, 'right', 'bottom', True)
    note(a1, 2.22, autumn(sand)[-1] - .012, '砂岩 · 秋', CLAY, 9.2, 'right', 'top')
    note(a1, .5, mud[0] - .01, '泥岩 · 春', BLUE, 9.2, 'left', 'top', True)
    d1 = np.abs(autumn(sand) - mud).mean(); d2 = np.abs(autumn(sand) - sand).mean()
    note(a1, 2.28, .02, '秋季砂岩反而更接近春季泥岩\n与泥岩差 %.3f，与春季砂岩差 %.3f' % (d1, d2), RED, 8.8, 'right', 'bottom')
    a1.set_xlabel('波长 / μm'); a1.set_ylabel('反射率'); a1.set_ylim(0, .5); a1.set_xlim(.4, 2.3)
    title(a1, 'trap', '不同季相拼接')
    lab = _litho(); rgb = np.array([mpl.colors.to_rgb(LITH[i]) for i in range(3)])[lab]
    rgb = rgb * (.9 + .1 * field(lab.shape, 2, 9))[..., None]
    yy, xx = np.mgrid[0:120, 0:200]
    cloud = (((xx - 145) / 26) ** 2 + ((yy - 32) / 16) ** 2) < 1
    shadow = (((xx - 158) / 26) ** 2 + ((yy - 52) / 14) ** 2) < 1 & ~cloud
    veg = field(lab.shape, 6, 21) > .78
    rgb[shadow] *= .45; rgb[veg] = mpl.colors.to_rgb('#5f7d4f'); rgb[cloud] = 1
    a2.imshow(np.clip(rgb, 0, 1), aspect='auto')
    mask = cloud | shadow | veg
    a2.contourf(mask, [.5, 1.5], colors='none', hatches=['////'])
    a2.contour(mask, [.5], colors=[INK], linewidths=.9)
    img_axes(a2)
    note(a2, .5, -.04, '斜线：云、阴影、浓密植被，标为“不可解译”', MUTE, 8.8, 'center', 'top', transform=a2.transAxes)
    title(a2, 'do', '同季相选景 + 掩膜')
    return f

def s2():
    true = _litho(seed=5)
    old = _litho(seed=5)
    old = ndimage.shift(old.astype(float), (12, -18), order=0, mode='nearest').astype(int)
    old = ndimage.median_filter(old, 21)
    def edges(l): return (ndimage.maximum_filter(l, 3) != ndimage.minimum_filter(l, 3))
    et = edges(true); dt = ndimage.distance_transform_edt(~et) * 30
    d_old = dt[edges(old)]
    rng = np.random.default_rng(2)
    f, (a1, a2) = fig(2, widths=[1.2, 1], wspace=.26, top=.84, bottom=.2, left=.02)
    rgb = np.array([mpl.colors.to_rgb(LITH[i]) for i in range(3)])[old]
    a1.imshow(rgb * .85 + .15, aspect='auto')
    boxes = [(rng.integers(5, 180), rng.integers(5, 100)) for _ in range(20)]
    fine_d = []
    for x, y in boxes:
        sub = true[y:y + 14, x:x + 16]
        a1.imshow(np.array([mpl.colors.to_rgb(LITH[i]) for i in range(3)])[sub], extent=(x - .5, x + 15.5, y + 13.5, y - .5), aspect='auto')
        a1.add_patch(mpl.patches.Rectangle((x - .5, y - .5), 16, 14, fill=False, ec=INK, lw=1.1))
    a1.set_xlim(-.5, 199.5); a1.set_ylim(119.5, -.5); img_axes(a1)
    note(a1, .5, -.04, '淡色：历史地质图（弱标签）　方框：20 个精标样区', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'do', '少量精标 + 大量弱标签')
    fine = np.abs(rng.normal(0, 14, 600))
    bins = np.arange(0, 720, 24)
    a2.hist(d_old, bins, color=RED, alpha=.75, label='历史图界线')
    a2.hist(fine, bins, color=JADE, alpha=.8, label='精标界线')
    a2.axvline(np.median(d_old), color=RED, lw=1.2, ls='--')
    note(a2, np.median(d_old) + 10, a2.get_ylim()[1] * .55, '中位偏差\n%.0f m' % np.median(d_old), RED, 9.2, 'left', 'center', True)
    a2.set_xlabel('与真实界线的距离 / m'); a2.set_ylabel('界线像素数'); a2.set_xlim(0, 700)
    a2.legend(loc='upper right', handlelength=1, borderaxespad=0)
    title(a2, 'trap', '老图当真值')
    return f

def s3():
    n = 140
    yy, xx = np.mgrid[0:n, 0:n] / n
    dem = 900 * np.exp(-((xx - .45) ** 2 + (yy - .5) ** 2) / .06) + 200 * xx
    gy, gx = np.gradient(dem, 30)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    az, el = np.deg2rad(135), np.deg2rad(32)
    cosi = np.clip(np.sin(el) * np.cos(slope) + np.cos(el) * np.sin(slope) * np.cos(az - aspect), 0, 1)
    lith = (dem < 330).astype(int)                       # 0=砂岩（山体）1=泥岩（谷地）
    alb = np.where(lith == 0, .42, .24)
    rng = np.random.default_rng(1)
    obs = alb * (.15 + .85 * cosi) + rng.normal(0, .012, (n, n))
    thr = .33 * (.15 + .85 * .75)
    pred_spec = (obs < thr).astype(int)
    corr = obs / (.15 + .85 * np.clip(cosi, .05, 1))
    pred_dem = (corr < .33).astype(int); low = cosi < .05
    acc1 = (pred_spec == lith).mean(); acc2 = (pred_dem == lith)[~low].mean()
    cm = ListedColormap([LITH[0], LITH[1]])
    f, (a1, a2) = fig(2, wspace=.06, top=.84, bottom=.15, left=.015, right=.985)
    shade = .55 + .45 * cosi
    for ax, p, k, t, acc in [(a1, pred_spec, 'trap', '只用光谱', acc1), (a2, pred_dem, 'do', '光谱 + DEM 坡度坡向', acc2)]:
        ax.imshow(p, cmap=cm, vmin=0, vmax=1, aspect='auto')
        ax.imshow(shade, cmap='gray', alpha=.28, aspect='auto')
        ax.contour(dem, levels=np.arange(300, 1100, 150), colors=['#ffffff'], linewidths=.5, alpha=.7)
        wrong = (p != lith) & ~(low if k == 'do' else np.zeros_like(low))
        ax.contourf(wrong, [.5, 1.5], colors='none', hatches=['xxxx'])
        if k == 'do': ax.imshow(np.ma.masked_where(~low, low), cmap=ListedColormap(['#8a8a8a']), aspect='auto')
        img_axes(ax); title(ax, k, t)
    note(a1, .5, -.04, '阴坡的砂岩被分成泥岩（交叉线）· 正确率 %s' % pct(acc1), RED, 9, 'center', 'top', transform=a1.transAxes)
    note(a2, .5, -.04, '阴阳坡归为同一岩性 · 正确率 %s；灰色为低置信度' % pct(acc2), JADE, 9, 'center', 'top', transform=a2.transAxes)
    note(a1, 110, 22, '光照方向', INK, 8.8, 'center', 'bottom', box=True)
    a1.annotate('', xy=(98, 36), xytext=(122, 14), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.2))
    return f

def s4():
    n1, n2 = 120, 200
    lab = _litho((n1, n2), seed=8)
    yy, xx = np.mgrid[0:n1, 0:n2]
    dike = np.abs(xx - (40 + .9 * yy)) < 1.6
    lab = np.where(dike, 4, lab)
    rng = np.random.default_rng(3)
    noisy = lab.copy(); sp = rng.random(lab.shape) < .10
    noisy[sp] = rng.integers(0, 3, sp.sum())
    def mode_filter(a, k):
        cnt = np.stack([ndimage.uniform_filter((a == c).astype(float), k) for c in range(5)])
        return cnt.argmax(0)
    good, bad = mode_filter(noisy, 3), mode_filter(noisy, 11)
    keep = lambda p: (p[dike] == 4).mean()
    cm = ListedColormap(LITH)
    f, (a1, a2, a3) = fig(3, wspace=.05, top=.84, bottom=.15, left=.012, right=.988)
    for ax, p, k, t in [(a1, noisy, '概率图', '逐像素结果'), (a2, good, 'do', '3×3 去碎斑'), (a3, bad, 'trap', '11×11 平滑')]:
        ax.imshow(p, cmap=cm, vmin=0, vmax=4, aspect='auto', interpolation='nearest')
        if ax is not a1:
            for c in range(5): ax.contour(p == c, [.5], colors=[INK], linewidths=.6)
        img_axes(ax); title(ax, k, t)
    note(a1, .5, -.04, '碎斑 %s' % pct(sp.mean()), MUTE, 9, 'center', 'top', transform=a1.transAxes)
    note(a2, .5, -.04, '岩脉保留 %s，转为矢量界线' % pct(keep(good)), JADE, 9, 'center', 'top', transform=a2.transAxes)
    note(a3, .5, -.04, '岩脉只剩 %s' % pct(keep(bad)), RED, 9, 'center', 'top', transform=a3.transAxes)
    note(a1, 150, 110, '岩脉', '#4a3f5c', 9, 'center', 'center', True, box=True)
    return f

def s5():
    n1, n2 = 120, 200
    lab = _litho((n1, n2), seed=11)
    yy, xx = np.mgrid[0:n1, 0:n2]
    lens = (((xx - 150) / 16) ** 2 + ((yy - 30) / 7) ** 2) < 1
    dike = np.abs(xx - (30 + .7 * yy)) < 1.5
    lab = np.where(lens, 3, np.where(dike, 4, lab))
    rng = np.random.default_rng(4)
    pred = lab.copy()
    pred[lens & (field(lab.shape, 3, 2) > .45)] = 2                     # 火山岩透镜体大半被归为灰岩
    pred[dike & (rng.random(lab.shape) < .55)] = 1                      # 岩脉断续
    edge = ndimage.maximum_filter(lab, 3) != ndimage.minimum_filter(lab, 3)
    sel = edge & (rng.random(lab.shape) < .25); pred[sel] = ndimage.maximum_filter(lab, 3)[sel]
    acc = (pred == lab).mean()
    rec = [(pred[lab == c] == c).mean() for c in range(5)]; area = [(lab == c).mean() for c in range(5)]
    f, (a1, a2) = fig(2, widths=[1.1, 1], wspace=.28, top=.84, bottom=.2, left=.02)
    a1.imshow(pred, cmap=ListedColormap(LITH), vmin=0, vmax=4, aspect='auto', interpolation='nearest')
    pts = rng.uniform([5, 5], [195, 115], (34, 2))
    pts = np.r_[pts, [[150, 30], [140, 28], [160, 33], [45, 22], [70, 56]]]
    for x, y in pts:
        ok = pred[int(y), int(x)] == lab[int(y), int(x)]
        a1.plot(x, y, 'o' if ok else 'X', ms=5 if ok else 7, mfc='white' if ok else RED, mec=JADE if ok else 'white', mew=1.3 if ok else .8)
    img_axes(a1)
    note(a1, .5, -.04, '圆点：与野外观察一致　叉：不一致，需修编', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'do', '野外观察点逐点验证')
    order = np.argsort(area)[::-1]
    y = np.arange(5)[::-1]
    a2.barh(y, [rec[i] for i in order], color=[JADE if rec[i] > .8 else RED for i in order], height=.6)
    for yi, i in zip(y, order):
        note(a2, rec[i] + .02, yi, '%s（占 %s）' % (pct(rec[i]), pct(area[i])), INK, 8.8, 'left', 'center')
    a2.axvline(acc, color=INK, lw=1.1, ls='--'); note(a2, acc + .03, 4.55, '总体精度 %s' % pct(acc), INK, 9, 'left', 'bottom', True)
    a2.set_yticks(y, [LNAME[i] for i in order]); a2.set_xlim(0, 1.55); a2.set_xticks([0, .5, 1], ['0', '50%', '100%'])
    a2.set_xlabel('各岩性的正确率'); a2.set_ylim(-.6, 5.3)
    a2.spines['left'].set_visible(False); a2.tick_params(axis='y', length=0)
    title(a2, 'trap', '只看总体精度')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：同一种砂岩，秋季影像的光谱反而更接近春季的泥岩；右：选同一季相的影像，并把云、阴影、浓密植被单独掩膜。',
        '左：历史地质图只作弱标签，20 个样区精修标注；右：历史图的界线与真实界线中位偏差约 200 米，直接当真值会把老图的错误学进去。',
        '同一座山的模拟影像。左：只用光谱，阴坡的砂岩因为暗被分成泥岩；右：加入 DEM 坡度坡向做地形校正后，阴阳坡归为同一岩性。',
        '同一张逐像素结果：3×3 去碎斑能保留窄条状岩脉，11×11 平滑过度会把岩脉整条抹掉。',
        '左：用野外观察点验证，不一致的点集中在小面积岩性上；右：总体精度很高，但面积小的火山岩和岩脉正确率明显偏低。']
