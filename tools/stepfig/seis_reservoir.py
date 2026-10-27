# -*- coding: utf-8 -*-
"""储层参数反演：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

def s1():
    rng = np.random.default_rng(1)
    z = np.arange(2000, 2060, .125)
    nb = 26; beds = np.repeat(rng.choice([.06, .1, .16, .22, .27], nb, p=[.15, .2, .25, .25, .15]), len(z) // nb + 1)[:len(z)]
    beds = beds + .06 * (rng.random(len(z)) < .03).astype(float).cumsum() % 2 * 0
    thin = ndimage.uniform_filter1d(rng.normal(0, 1, len(z)), 4) * .05
    log = np.clip(beds + thin, .02, .33)
    k = np.hanning(65); k /= k.sum()                      # 约 8 m 的地震尺度平均
    seis = np.convolve(log, k, 'same')
    f, (a1, a2) = fig(2, widths=[.8, 1.25], wspace=.34, top=.84, bottom=.2, left=.115)
    m = (z > 2006) & (z < 2054)
    a1.plot(log[m] * 100, z[m], color=GREY, lw=.8, label='测井（0.125 m）')
    a1.plot(seis[m] * 100, z[m], color=JADE, lw=2.2, label='平均到地震尺度')
    a1.set_ylim(2054, 2006); a1.set_xlim(0, 35); a1.set_xlabel('孔隙度 / %'); a1.set_ylabel('深度 / m')
    a1.legend(loc='lower right', handlelength=1, borderaxespad=.2, fontsize=8.4, frameon=True, framealpha=.92, edgecolor='none', facecolor='white')
    title(a1, 'do', '尺度对齐')
    n = 400; r = np.random.default_rng(2)
    phis = r.uniform(.06, .26, n)
    attr = -9.5 * phis + r.normal(0, .18, n)                  # 地震属性只反映地震尺度的孔隙度
    phil = np.clip(phis + r.normal(0, .07, n), .01, .35)       # 米级测井值带有薄层变化
    c1, c2 = np.corrcoef(attr, phil)[0, 1], np.corrcoef(attr, phis)[0, 1]
    a2.scatter(attr, phil * 100, s=8, color=GREY, alpha=.55, lw=0, label='属性 vs 米级测井值  r = %.2f' % c1)
    a2.scatter(attr, phis * 100, s=8, color=JADE, alpha=.85, lw=0, label='属性 vs 地震尺度值  r = %.2f' % c2)
    a2.set_xlabel('地震属性（归一化阻抗）'); a2.set_ylabel('孔隙度 / %'); a2.set_ylim(0, 40)
    a2.legend(loc='upper right', handlelength=.8, borderaxespad=0, markerscale=2, fontsize=8.8)
    title(a2, 'trap', '直接用米级值当标签')
    return f

def _wells(n=22, p=12, seed=3):
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n, p))
    y = .55 * X[:, 0] + .35 * X[:, 1] + .2 * X[:, 2] + rng.normal(0, .35, n)
    return X, y

def s2():
    names = ['声阻抗', '纵横波速比', '泊松比', '密度', '均方根振幅', '瞬时频率', '甜点', '弧长', '相干', '曲率', '倾角', '谱分解 40Hz']
    phys = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    rng = np.random.default_rng(4); n = 22
    X = rng.normal(0, 1, (n, 12)); y = .6 * X[:, 0] + .35 * X[:, 1] + .25 * X[:, 2] + .2 * X[:, 3] + rng.normal(0, .3, n)
    cor = np.array([abs(np.corrcoef(X[:, i], y)[0, 1]) for i in range(12)])
    f, (a1, a2) = fig(2, widths=[1.05, 1], wspace=.42, top=.84, bottom=.2, left=.15)
    yy = np.arange(12)[::-1]
    a1.barh(yy, cor, color=[JADE if p else LGREY for p in phys], height=.66)
    a1.set_yticks(yy, names, fontsize=8.4); a1.set_xlim(0, 1); a1.set_xlabel('与孔隙度的相关系数 |r|')
    a1.tick_params(axis='y', length=0); a1.spines['left'].set_visible(False)
    note(a1, .98, 1, '绿：有岩石物理依据', JADE, 8.6, 'right', 'center')
    note(a1, .98, 0, '灰：可能是偶然相关', MUTE, 8.6, 'right', 'center')
    title(a1, 'do', '只留有物理联系的属性')
    ks = np.arange(1, 13); tr, bl = [], []
    for k in ks:
        t_, b_ = [], []
        for sd in range(300):
            r = np.random.default_rng(sd)
            Xw = r.normal(0, 1, (22, 12)); yw = .6 * Xw[:, 0] + .35 * Xw[:, 1] + .25 * Xw[:, 2] + .2 * Xw[:, 3] + r.normal(0, .3, 22)
            idx = r.permutation(22); ti, bi = idx[:16], idx[16:]
            A = np.c_[np.ones(16), Xw[ti, :k]]; w = np.linalg.lstsq(A, yw[ti], rcond=None)[0]
            t_.append(np.sqrt(np.mean((A @ w - yw[ti]) ** 2))); b_.append(np.sqrt(np.mean((np.c_[np.ones(6), Xw[bi, :k]] @ w - yw[bi]) ** 2)))
        tr.append(np.mean(t_)); bl.append(np.median(b_))
    a2.plot(ks, tr, 'o-', color=GREY, ms=4, label='训练井（16 口）')
    a2.plot(ks, bl, 'o-', color=RED, ms=4, label='盲井（6 口）')
    a2.axvspan(3.5, 4.5, color=JADE, alpha=.12, lw=0); note(a2, 4, .02, '4 个', JADE, 9, 'center', 'bottom', True)
    a2.set_xlabel('使用的属性个数'); a2.set_ylabel('孔隙度误差（标准化）'); a2.set_xticks([1, 4, 8, 12]); a2.set_ylim(0, max(bl) * 1.12)
    a2.legend(loc='upper left', handlelength=1.2, borderaxespad=0)
    title(a2, 'trap', '属性多、井少')
    return f

def s3():
    rng = np.random.default_rng(6)
    ip = rng.uniform(6.6, 9.2, 22)
    phi = np.clip(.42 - .036 * ip + rng.normal(0, .012, 22), .02, .35)
    xx = np.linspace(5.6, 10.4, 300)
    b = np.polyfit(ip, phi, 1); lin = np.clip(np.polyval(b, xx), 0, .35)
    pol = np.polyval(np.polyfit(ip, phi, 8), xx)
    f, (a1, a2) = fig(2, wspace=.24, top=.84, bottom=.2)
    for ax, yv, k, t_, c in [(a1, lin, 'do', '平滑 + 物理约束', JADE), (a2, pol, 'trap', '只追求训练误差', RED)]:
        ax.axvspan(5.6, ip.min(), color=GREY, alpha=.1, lw=0); ax.axvspan(ip.max(), 10.4, color=GREY, alpha=.1, lw=0)
        ax.axhspan(-.5, 0, color=RED, alpha=.07, lw=0); ax.axhspan(.35, 1, color=RED, alpha=.07, lw=0)
        ax.plot(xx, yv * 100, color=c, lw=2)
        ax.scatter(ip, phi * 100, s=22, color=INK, zorder=3)
        ax.set_xlim(5.6, 10.4); ax.set_ylim(-12, 48); ax.set_xlabel('纵波阻抗 / (km/s·g/cm³)')
        note(ax, 5.75, 46, '外推区', MUTE, 8.8, 'left', 'top'); note(ax, 10.3, 46, '外推区', MUTE, 8.8, 'right', 'top')
        title(ax, k, t_)
    a1.set_ylabel('孔隙度 / %')
    tr = lambda yfit: np.sqrt(np.mean((np.polyval(yfit, ip) - phi) ** 2)) * 100
    note(a1, 8, -9, '训练误差 %.1f 个百分点\n全程落在 0—35%%' % tr(b), JADE, 9, 'center', 'bottom', True)
    note(a2, 8, -9, '训练误差 %.1f 个百分点\n外推出现负值和 40%% 以上' % tr(np.polyfit(ip, phi, 8)), RED, 9, 'center', 'bottom', True)
    return f

def _maps(n=110, m=160):
    true_r = .05 * (field((n, m), 9, 2) - .5)
    trend = .17 + .05 * (field((n, m), 30, 3) - .5)
    rng = np.random.default_rng(5)
    wells = np.c_[rng.uniform(15, 95, 16), rng.uniform(10, 70, 16)]      # 井集中在西部
    blind = np.r_[np.c_[rng.uniform(20, 90, 4), rng.uniform(15, 70, 4)], [[100, 130], [60, 148]]]
    yy, xx = np.mgrid[0:n, 0:m]
    W = np.stack([1 / (np.hypot(yy - wy, xx - wx) + 3) ** 2 for wy, wx in wells])
    rw = np.array([true_r[int(wy), int(wx)] for wy, wx in wells])
    dist = np.min(np.stack([np.hypot(yy - wy, xx - wx) for wy, wx in wells]), 0)
    decay = np.exp(-dist / 18)
    pred_r = (W * rw[:, None, None]).sum(0) / W.sum(0) * decay
    east = .035 / (1 + np.exp(-(xx - 115) / 9))          # 东部沉积环境变化，西部井上看不到
    return trend + true_r + east, trend + pred_r, dist, wells, blind

def s4():
    true, pred, dist, wells, blind = _maps()
    err = np.abs(pred - true) * 100
    f, (a1, a2) = fig(2, widths=[1.2, 1], wspace=.30, top=.84, bottom=.2, left=.02)
    im = a1.imshow(pred * 100, cmap=LinearSegmentedColormap.from_list('p', ['#f3efe2', '#d9c68f', CLAY, '#6b3f25']), vmin=8, vmax=26, aspect='auto')
    a1.contour(dist, [25], colors=[INK], linewidths=1, linestyles='--')
    a1.plot(wells[:, 1], wells[:, 0], 'o', ms=4, color=INK)
    for wy, wx in blind: a1.plot(wx, wy, 'o', ms=7, mfc='white', mec=BLUE, mew=1.8)
    note(a1, 140, 20, '外推区', INK, 9.2, 'center', 'center', True, box=True)
    img_axes(a1)
    note(a1, .5, -.04, '黑点：训练井　蓝圈：盲井　虚线：离井 25 格', MUTE, 8.6, 'center', 'top', transform=a1.transAxes)
    title(a1, 'check', '盲井 + 外推区单独看')
    bins = np.arange(0, 110, 10); mid = (bins[1:] + bins[:-1]) / 2
    mean = [err[(dist >= a) & (dist < b)].mean() for a, b in zip(bins[:-1], bins[1:])]
    p90 = [np.percentile(err[(dist >= a) & (dist < b)], 90) for a, b in zip(bins[:-1], bins[1:])]
    a2.fill_between(mid, 0, p90, color=RED, alpha=.12, lw=0)
    a2.plot(mid, mean, 'o-', color=RED, ms=4)
    for wy, wx in blind:
        d = dist[int(wy), int(wx)]; e = err[int(wy), int(wx)]; a2.plot(d, e, 'o', ms=7, mfc='white', mec=BLUE, mew=1.8)
    a2.axvline(25, color=INK, lw=.9, ls='--')
    note(a2, 27, max(p90) * .95, '外推区', INK, 9, 'left', 'top', True)
    a2.set_xlabel('到最近训练井的距离（格）'); a2.set_ylabel('孔隙度误差 / 百分点'); a2.set_xlim(0, 100); a2.set_xticks([0, 25, 50, 75]); a2.set_ylim(0, max(p90) * 1.05)
    note(a2, 98, .3, '线：平均误差　色带：90% 分位', MUTE, 8.4, 'right', 'bottom')
    title(a2, 'trap', '只看井附近')
    return f

def s5():
    n, m = 110, 160
    yy, xx = np.mgrid[0:n, 0:m]
    cen = 55 + 18 * np.sin(xx / 30)
    chan = np.abs(yy - cen) < 12
    por = .11 + .1 * np.exp(-((yy - cen) / 10) ** 2) + .02 * (field((n, m), 5, 1) - .5)
    blob = ((xx - 120) / 14) ** 2 + ((yy - 18) / 9) ** 2 < 1
    por = por + .09 * np.exp(-(((xx - 120) / 12) ** 2 + ((yy - 18) / 7) ** 2))
    f, (a1, a2) = fig(2, widths=[1.2, 1], wspace=.28, top=.84, bottom=.2, left=.02)
    a1.imshow(por * 100, cmap=LinearSegmentedColormap.from_list('p', ['#f3efe2', '#d9c68f', CLAY, '#6b3f25']), vmin=8, vmax=24, aspect='auto')
    a1.contour(chan, [.5], colors=[BLUE], linewidths=1.4)
    a1.contour(blob, [.5], colors=[RED], linewidths=1.6, linestyles='--')
    note(a1, 120, 34, '高孔隙但不在河道内\n→ 复查属性', RED, 8.8, 'center', 'top', True, box=True)
    note(a1, 10, 50 + 18 * np.sin(10 / 30) - 15, '河道相带', BLUE, 9, 'left', 'bottom', True, box=True)
    img_axes(a1); title(a1, 'check', '对照相带审核')
    note(a1, .5, -.04, '底色：孔隙度预测（深 = 高）', MUTE, 8.6, 'center', 'top', transform=a1.transAxes)
    mo = np.arange(0, 13)
    no = 1.6 + .09 * mo + .012 * mo ** 2
    yes = 1.6 + .25 * ((mo % 3) / 3) + .05 * np.sin(mo)
    a2.plot(mo, no, color=RED, lw=1.8, label='新井不回流')
    a2.plot(mo, yes, color=JADE, lw=1.8, label='每 3 个月回流重训')
    for k in (3, 6, 9, 12): a2.axvline(k, color=JADE, lw=.7, ls=':')
    a2.set_xlabel('上线后月数'); a2.set_ylabel('新井孔隙度误差 / 百分点（示意）'); a2.set_ylim(1.2, 4.2); a2.set_xlim(0, 12)
    a2.legend(loc='upper left', handlelength=1.2, borderaxespad=0)
    title(a2, 'trap', '新井不回流就脱节')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：米级测井孔隙度（灰）平均到地震尺度（绿）；右：地震属性与地震尺度孔隙度相关性高，直接用米级值当标签，相关性被薄层变化冲淡。',
        '左：只保留有岩石物理依据的属性；右：22 口井中留 6 口盲井，属性越多训练误差越小，盲井误差反而上升。',
        '左：单调、限定在合理范围内的映射，外推区仍然合理；右：只追求训练误差的高次曲线，在外推区出现负孔隙度和过高值。',
        '左：训练井集中在西部，东部为外推区；右：误差随到最近训练井的距离增大，只看井附近看不出外推区的偏差。',
        '左：孔隙度图对照河道相带审核，相带外的高值区需要复查；右：新井不回流时误差逐月变大，定期回流重训能稳住（示意）。']
