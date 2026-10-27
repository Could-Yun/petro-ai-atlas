# -*- coding: utf-8 -*-
"""地质图件要素智能提取：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

SYM = [('o', 'full', '实心圆'), ('o', 'none', '空心圆'), ('o', 'left', '半实心圆'), ('^', 'full', '三角')]

def _mk(ax, x, y, m, fs, c=INK, s=8):
    ax.plot(x, y, m, ms=s, fillstyle=fs, color=c, mec=c, mew=1.3, mfc=c if fs != 'none' else 'white',
            **({'markerfacecoloralt': 'white'} if fs == 'left' else {}), clip_on=False)

def s1():
    f, (a1, a2) = fig(2, widths=[1.05, 1], wspace=.30, top=.84, bottom=.2, left=.02)
    a1.axis('off'); a1.set_xlim(0, 10); a1.set_ylim(0, 5.6)
    tabs = [('1975 版图例', ['油井', '干井', '气井', '油气显示']), ('1990 版图例', ['油井', '干井', '油气同井', '气井'])]
    for j, (ttl, means) in enumerate(tabs):
        x0 = j * 5.1
        note(a1, x0 + .2, 5.25, ttl, INK, 9.6, 'left', 'center', True)
        for i, ((m, fs, _), mean) in enumerate(zip(SYM, means)):
            y = 4.3 - i * 1.0
            bad = i >= 2
            if bad: a1.add_patch(mpl.patches.FancyBboxPatch((x0 + .05, y - .38), 4.6, .76, boxstyle='round,pad=.02', fc=mpl.colors.to_rgba(RED, .09), ec=RED, lw=.9))
            _mk(a1, x0 + .7, y, m, fs)
            note(a1, x0 + 1.4, y, mean, RED if bad else INK, 9.4, 'left', 'center', bad)
    note(a1, 5, -.15, '红框：同一个符号，两版图例含义不同', RED, 9, 'center', 'top')
    title(a1, 'trap', '图例体系不同')
    names = [s[2] for s in SYM]
    mixed = [.97, .96, 300 / 520, 210 / 390]; split = [.97, .96, .95, .94]
    x = np.arange(4); w = .36
    a2.bar(x - w / 2, mixed, w, color=GREY); a2.bar(x + w / 2, split, w, color=JADE)
    for i in range(4):
        note(a2, x[i] - w / 2, mixed[i] + .02, pct(mixed[i]), RED if mixed[i] < .8 else MUTE, 8.8, 'center', 'bottom', mixed[i] < .8)
    a2.set_xticks(x, names, fontsize=9); a2.set_ylim(0, 1.25); a2.set_yticks([0, .5, 1], ['0', '50%', '100%'])
    a2.set_ylabel('识别出正确含义的比例')
    note(a2, 1.5, 1.2, '灰：混在一起训练　绿：先标注图例版本', MUTE, 8.8, 'center', 'center')
    title(a2, 'do', '按图例版本分别对应')
    return f

def s2():
    f, (a1, a2) = fig(2, widths=[1.15, 1], wspace=.30, top=.84, bottom=.2, left=.02)
    a1.axis('off'); a1.set_xlim(0, 10); a1.set_ylim(0, 6.2)
    cols = [(.2, '符号'), (1.6, '版本'), (3.2, '语义'), (5.3, '属性字段')]
    for x, t in cols: note(a1, x, 5.7, t, MUTE, 9.2, 'left', 'center', True)
    a1.plot([0, 10], [5.35, 5.35], color=INK, lw=.9)
    rows = [(SYM[0], '通用', '油井', 'well_type=oil'), (SYM[1], '通用', '干井', 'well_type=dry'),
            (SYM[2], '1975', '气井', 'well_type=gas'), (SYM[2], '1990', '油气同井', 'well_type=oil_gas'),
            (SYM[3], '1975', '油气显示', 'show=true')]
    for i, ((m, fs, _), v, sem, fld) in enumerate(rows):
        y = 4.8 - i * .95
        _mk(a1, .55, y, m, fs)
        note(a1, 1.6, y, v, INK, 9.2, 'left', 'center'); note(a1, 3.2, y, sem, INK, 9.4, 'left', 'center')
        note(a1, 5.3, y, fld, BLUE, 8.8, 'left', 'center', family='monospace')
        a1.plot([0, 10], [y - .47, y - .47], color=LGREY, lw=.6)
    title(a1, 'do', '符号 → 语义 → 属性字段')
    cls = ['油井', '干井', '气井', '油气同井', '油气显示', '断层符号', '产状', '注记']
    n = np.array([1420, 860, 520, 390, 160, 640, 1180, 2300])
    y = np.arange(len(cls))[::-1]
    a2.barh(y, n, color=[JADE if v >= 200 else RED for v in n], height=.62)
    a2.axvline(200, color=RED, lw=1.1, ls='--'); note(a2, 230, -.95, '虚线：每类至少 200 个', RED, 8.8, 'left', 'center')
    for yi, v in zip(y, n): note(a2, v + 40, yi, '%d' % v + ('  需补标' if v < 200 else ''), RED if v < 200 else MUTE, 8.8, 'left', 'center', v < 200)
    a2.set_yticks(y, cls); a2.set_xlim(0, 2900); a2.set_ylim(-1.3, 7.5)
    a2.set_xlabel('已标注实例数'); a2.spines['left'].set_visible(False); a2.tick_params(axis='y', length=0)
    title(a2, '样本', '逐类清点')
    return f

def _iou(a, b, s):
    dx = np.clip(s - np.abs(a[0] - b[0]), 0, None); dy = np.clip(s - np.abs(a[1] - b[1]), 0, None)
    inter = dx * dy; return inter / (2 * s * s - inter)

def _nms(boxes, scores, s, thr):
    order = np.argsort(-scores); keep = []
    for i in order:
        if all(_iou(boxes[i], boxes[j], s) <= thr for j in keep): keep.append(i)
    return keep

def s3():
    rng = np.random.default_rng(3); s = 6.0
    gt = np.r_[rng.uniform(8, 92, (12, 2)), [[40, 40], [41.6, 40.6], [40.4, 41.8], [70, 62], [71.5, 62.8], [24, 70], [25.4, 69.2]]]
    det = gt + rng.normal(0, .5, gt.shape); sc = rng.uniform(.7, .99, len(gt))
    keep = _nms(det, sc, s, .5)
    miss = [i for i in range(len(gt)) if i not in keep]
    f, (a1, a2) = fig(2, widths=[1, 1.15], wspace=.26, top=.84, bottom=.2, left=.02)
    for i, (x, y) in enumerate(gt):
        _mk(a1, x, y, 'o', 'full' if i % 3 else 'left', s=6.5)
    for i in keep:
        x, y = det[i]; a1.add_patch(mpl.patches.Rectangle((x - s / 2, y - s / 2), s, s, fill=False, ec=JADE, lw=1.2))
    for i in miss:
        x, y = gt[i]; a1.add_patch(mpl.patches.Circle((x, y), 4.2, fill=False, ec=RED, lw=1.6))
    map_axes(a1, (0, 100), (0, 100))
    note(a1, .5, -.04, '绿框：检出　红圈：密集处被合并而漏掉（%d 个）' % len(miss), MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    title(a1, 'trap', '符号相互压盖')
    sp = np.linspace(.2, 2, 37)
    for thr, c in [(.3, RED), (.5, CLAY), (.7, JADE)]:
        rec = []
        for d in sp:
            ok = 0; n = 200
            for _ in range(n):
                a = np.array([0, 0]) + rng.normal(0, .08 * s, 2); b = np.array([d * s, 0]) + rng.normal(0, .08 * s, 2)
                ok += 2 if _iou(a, b, s) <= thr else 1
            rec.append(ok / (2 * n))
        a2.plot(sp, rec, color=c, lw=1.8, label='合并阈值 %.1f' % thr)
    a2.set_xlim(.2, 2); a2.set_ylim(.45, 1.05); a2.set_yticks([.5, .75, 1], ['50%', '75%', '100%'])
    a2.set_xlabel('相邻符号中心距 / 符号尺寸'); a2.set_ylabel('井位召回率')
    a2.axvspan(.2, 1, color=GREY, alpha=.1, lw=0); note(a2, .6, .47, '相互压盖', MUTE, 9, 'center', 'bottom')
    a2.legend(loc='lower right', handlelength=1.4, borderaxespad=.3)
    title(a2, 'do', '调低合并、密集区单独处理')
    return f

def s4():
    f, (a1, a2) = fig(2, wspace=.06, top=.84, bottom=.15, left=.015, right=.985)
    xs = np.linspace(0, 100, 400)
    fault = 30 + .45 * xs + 3 * np.sin(xs / 9)
    gaps = [(28, 36), (61, 68)]
    segs = []; start = 0
    for g0, g1 in gaps: segs.append((start, g0)); start = g1
    segs.append((start, 100))
    contour = 52 + 10 * np.sin(xs / 11 + 1.2) - .1 * xs
    for ax, k in [(a1, 'do'), (a2, 'trap')]:
        for c0 in (-14, 0, 14): ax.plot(xs, contour + c0, color='#b89a6a', lw=1.1)
        for s0, s1_ in segs:
            m = (xs >= s0) & (xs <= s1_); ax.plot(xs[m], fault[m], color=INK, lw=2.4)
        map_axes(ax, (0, 100), (0, 100))
    def ang(a, b): return abs(np.rad2deg(np.arctan2(b[1] - a[1], b[0] - a[0])))
    for g0, g1 in gaps:
        p0 = (g0, np.interp(g0, xs, fault)); p1 = (g1, np.interp(g1, xs, fault))
        a1.plot([p0[0], p1[0]], [p0[1], p1[1]], color=JADE, lw=2.4, ls=(0, (2, 1.5)))
        tang = np.rad2deg(np.arctan(.45)); d = np.hypot(p1[0] - p0[0], p1[1] - p0[1])
        note(a1, (p0[0] + p1[0]) / 2 + 2, (p0[1] + p1[1]) / 2 - 4, '间隔 %.0f · 夹角 %.0f°' % (d, abs(ang(p0, p1) - tang)), JADE, 8.8, 'left', 'top', True, box=True)
    title(a1, 'do', '按方向和距离接断点')
    note(a1, .5, -.04, '黑：断层　褐：等高线　绿虚线：满足规则后连接', MUTE, 8.8, 'center', 'top', transform=a1.transAxes)
    g0, g1 = gaps[0]
    p0 = (g0, np.interp(g0, xs, fault))
    j = np.argmin(np.abs(xs - 34)); q = (xs[j], contour[j] + 14)
    a2.plot([p0[0], q[0]], [p0[1], q[1]], color=RED, lw=2.4, ls=(0, (2, 1.5)))
    m = (xs >= q[0]) & (xs <= 70); a2.plot(xs[m], contour[m] + 14, color=RED, lw=2.4)
    note(a2, 52, 84, '沿颜色相近的等高线追下去', RED, 9, 'center', 'bottom', True, box=True)
    title(a2, 'trap', '只按颜色追踪')
    note(a2, .5, -.04, '没有夹角和拓扑检查，断层被接到等高线上', RED, 8.8, 'center', 'top', transform=a2.transAxes)
    return f

def s5():
    rng = np.random.default_rng(5); n = 2000
    conf = np.clip(rng.beta(6, 1.4, n), .3, .999)
    err = rng.random(n) > conf ** 1.6
    f, (a1, a2) = fig(2, wspace=.32, top=.84, bottom=.2, right=.955)
    bins = np.array([.3, .6, .7, .8, .9, 1.0])
    idx = np.digitize(conf, bins) - 1
    rate = [err[idx == i].mean() for i in range(5)]; share = [(idx == i).mean() for i in range(5)]
    x = np.arange(5)
    a1.bar(x, rate, color=[RED if r > .2 else GREY for r in rate], width=.62)
    for i, (r, sh) in enumerate(zip(rate, share)): note(a1, i, r + .015, '%s\n占 %s' % (pct(r), pct(sh)), RED if r > .2 else MUTE, 8.6, 'center', 'bottom')
    a1.set_xticks(x, ['<0.6', '0.6–0.7', '0.7–0.8', '0.8–0.9', '≥0.9'], fontsize=8.8)
    a1.set_ylim(0, .85); a1.set_yticks([0, .2, .4, .6, .8], ['0', '20%', '40%', '60%', '80%'])
    a1.set_xlabel('置信度'); a1.set_ylabel('错误率')
    title(a1, '数据', '错误集中在低置信度')
    k = np.arange(0, n + 1); tot = err.sum()
    low = np.r_[0, np.cumsum(err[np.argsort(conf)])] / tot
    rnd = np.r_[0, np.cumsum(err[rng.permutation(n)])] / tot
    high = np.r_[0, np.cumsum(err[np.argsort(-conf)])] / tot
    a2.plot(k / n, low, color=JADE); a2.plot(k / n, rnd, color=GREY); a2.plot(k / n, high, color=RED)
    i20 = int(.2 * n)
    a2.axvline(.2, color=INK, lw=.8, ls=':')
    for arr, c, lab, dy in [(low, JADE, '低置信度优先', .04), (rnd, GREY, '随机抽查', .04), (high, RED, '只抽高置信度', .04)]:
        note(a2, .23, arr[i20], '%s %s' % (lab, pct(arr[i20])), c, 8.8, 'left', 'center', True, box=True)
        a2.plot(.2, arr[i20], 'o', color=c, ms=4.5)
    a2.set_xlim(0, 1); a2.set_ylim(0, 1.05); a2.set_xticks([0, .2, .5, 1], ['0', '20%', '50%', '100%']); a2.set_yticks([0, .5, 1], ['0', '50%', '100%'])
    a2.set_xlabel('已核对的要素比例'); a2.set_ylabel('找出的错误比例')
    title(a2, 'do', '先核低置信度')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：两版图例里，半实心圆和三角的含义不同；右：不区分图例版本混在一起训练，这两种符号的含义只能猜对一半左右。',
        '左：把各版图例整理成“符号 → 语义 → 属性字段”对照表；右：逐类清点标注数量，不到 200 个的类别补标。',
        '左：井位密集处检测框相互重叠，被合并后漏掉；右：符号间距小于自身尺寸时召回率下降，合并阈值越低下降越多。',
        '左：断开的断层按间隔和夹角规则连接；右：只按颜色追踪时，断层末端被接到颜色相近的等高线上。',
        '左：错误几乎都集中在低置信度的要素上；右：同样只核对 20% 的要素，先核低置信度能找出大部分错误，只抽高置信度几乎找不到。']
