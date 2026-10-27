# -*- coding: utf-8 -*-
"""地震断层自动解释：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

FAULTS = [(62, .42, 11), (165, .30, 8)]

def _inline_volume(n_il=90, nx=160, nt=96, seed=3):
    rng = np.random.default_rng(seed)
    drift = np.cumsum(rng.normal(0, .3, n_il)); drift -= drift.mean()
    vol, masks = [], []
    for k in range(n_il):
        a, m = section(nx, nt, faults=[(50 + drift[k] + .12 * k, .32, 9 + 2 * np.sin(k / 14))],
                       fold=5 + 2.5 * np.sin(k / 16), seed=7, noise=.04)
        vol.append(a); masks.append(m)
    return np.array(vol), np.array(masks)

def s1():
    vol, masks = _inline_volume()
    n = len(vol); dists = np.arange(0, 31)
    corr = np.array([np.mean([np.corrcoef(vol[i].ravel(), vol[i + d].ravel())[0, 1] for i in range(4, n - 31, 3)]) for d in dists])
    def iou(a, b):
        a = ndimage.binary_dilation(a, iterations=2); b = ndimage.binary_dilation(b, iterations=2)
        return (a & b).sum() / max(1, (a | b).sum())
    rng = np.random.default_rng(5); idx = np.arange(n)
    rv = np.sort(rng.choice(idx, n // 4, replace=False)); rt = np.setdiff1d(idx, rv)
    bt, bv = idx[:55], idx[70:90]
    def score(tr, va):
        nn = [tr[np.argmin(np.abs(tr - v))] for v in va]
        return np.mean([iou(masks[a], masks[v]) for a, v in zip(nn, va)]), np.mean([abs(a - v) for a, v in zip(nn, va)])
    r_iou, r_d = score(rt, rv); b_iou, b_d = score(bt, bv)

    f, (a1, a2) = fig(2, widths=[1.45, 1], wspace=.38, top=.84)
    a1.plot(dists, corr, color=INK, lw=1.9, zorder=3)
    a1.axvspan(0, 2, color=RED, alpha=.10, lw=0); a1.axvspan(15, 30, color=JADE, alpha=.09, lw=0)
    yr, yb = np.interp(r_d, dists, corr), np.interp(b_d, dists, corr)
    a1.scatter([r_d, b_d], [yr, yb], s=36, color=[RED, JADE], zorder=4)
    note(a1, 2.4, .05, '随机划分：平均只隔 %.1f 条' % r_d, RED, 9.2, va='bottom')
    note(a1, 29.5, yb + .2, '按区块划分：\n平均隔 %.0f 条' % b_d, JADE, 9.2, 'right', 'bottom')
    a1.set_xlim(0, 30); a1.set_ylim(0, 1.05); a1.set_xticks([0, 5, 10, 15, 20, 25, 30])
    a1.set_xlabel('两条 inline 之间相隔的条数'); a1.set_ylabel('剖面相关系数')
    title(a1, '数据', '相邻 inline 几乎一模一样')

    a2.bar([0, 1], [r_iou, b_iou], color=[RED, JADE], width=.56)
    for i, v in enumerate([r_iou, b_iou]): note(a2, i, v + .025, '%.2f' % v, [RED, JADE][i], 11, 'center', 'bottom', True)
    a2.set_xticks([0, 1], ['随机划分', '按区块划分']); a2.set_ylim(0, 1.05); a2.set_yticks([0, .25, .5, .75, 1])
    a2.set_ylabel('验证集断层 IoU')
    title(a2, 'trap', '分数虚高')
    note(a2, .5, -.3, '同一个“照抄最近训练剖面”的模型', MUTE, 9, 'center', 'top', transform=a2.get_xaxis_transform())
    f.subplots_adjust(bottom=.24)
    return f

def s2():
    dt, n = .002, 512
    fr = np.fft.rfftfreq(n, dt)
    def spec(fpk, noise, seed):
        r = np.random.default_rng(seed); acc = 0
        for _ in range(200):
            tr = np.convolve(reflectivity(n, r, .2), ricker(fpk, dt), 'same') + r.normal(0, noise, n)
            acc = acc + np.abs(np.fft.rfft(tr * np.hanning(n))) ** 2
        s = ndimage.gaussian_filter1d(np.sqrt(acc), 2); return s / s.max()
    syn, fld = spec(42, 0, 1), spec(24, .05, 2)
    f, (a1, a2) = fig(2, widths=[1, 1], wspace=.34, top=.84, bottom=.2)
    a1.fill_between(fr, np.minimum(syn, fld), np.maximum(syn, fld), color=GREY, alpha=.16, lw=0)
    a1.plot(fr, syn, color=BLUE); a1.plot(fr, fld, color=CLAY)
    note(a1, 99, .60, '合成 42 Hz', BLUE, 9.4, 'right', 'center')
    note(a1, 99, .74, '实测 24 Hz', CLAY, 9.4, 'right', 'center')
    note(a1, 99, .88, '主频', MUTE, 9, 'right', 'center')
    a1.set_xlim(0, 100); a1.set_ylim(0, 1.08); a1.set_xlabel('频率 / Hz'); a1.set_ylabel('归一化振幅谱')
    title(a1, 'trap', '两种数据频带不同')

    k = np.array([10, 20, 40, 80, 160])
    scratch = .78 * (1 - np.exp(-k / 90)) + .05
    fine = .80 - .28 * np.exp(-k / 36)
    a2.axhline(.40, color=BLUE, ls='--', lw=1.2)
    a2.plot(k, scratch, 'o-', color=GREY, ms=4.5); a2.plot(k, fine, 'o-', color=JADE, ms=4.5)
    note(a2, 10, .40 - .035, '只用合成数据', BLUE, 9.2, 'left', 'top')
    note(a2, 10.5, .5, '合成预训练 + 本地微调', JADE, 9.2, 'left', 'center')
    note(a2, 21, scratch[1] - .05, '只用本地剖面从零训练', GREY, 9.2, 'left', 'top')
    a2.set_xscale('log'); a2.set_xticks(k, [str(v) for v in k]); a2.minorticks_off()
    a2.set_ylim(0, .95); a2.set_xlabel('本地标注剖面数（对数轴）'); a2.set_ylabel('验证 IoU（示意）')
    title(a2, 'do', '预训练后再微调')
    return f

def _fault_case(seed=11, mask_w=1.3):
    amp, mask = section(240, 130, faults=FAULTS, fold=6, seed=seed, mask_w=mask_w)
    tt, _ = np.mgrid[0:130, 0:240].astype(float)
    d = ndimage.distance_transform_edt(~section(240, 130, faults=FAULTS, seed=seed, mask_w=.6)[1])
    rng = np.random.default_rng(seed)
    prob = np.exp(-(d / 2.6) ** 2) * (.97 - .42 * tt / 130) * (1 - .35 * (np.sin(tt / 5) > .7) * (tt > 80))
    prob += .10 * ndimage.gaussian_filter(rng.random(mask.shape), 2.5)
    return amp, mask, np.clip(prob, 0, 1)

def s3():
    amp, mask, prob = _fault_case(mask_w=.55)
    frac = mask.mean(); pred = prob > .5
    acc_w, rec_w = (pred == mask).mean(), (pred & mask).sum() / mask.sum()
    f, (a1, a2) = fig(2, widths=[1.3, 1], wspace=.30, top=.84, bottom=.2)
    a1.imshow(amp, cmap=SEIS, vmin=-.8, vmax=.8, aspect='auto', interpolation='bilinear')
    a1.imshow(prob, cmap=PROB, vmin=.15, vmax=1, aspect='auto')
    img_axes(a1); a1.set_xlabel('CDP →'); a1.set_ylabel('双程时 →')
    title(a1, 'do', '逐像素输出断层概率')
    x = np.array([0, 1]); w = .34
    acc, rec = [1 - frac, acc_w], [0, rec_w]
    a2.bar(x - w / 2, acc, w, color=LGREY); a2.bar(x + w / 2, rec, w, color=[RED, JADE])
    for i in range(2):
        note(a2, x[i] - w / 2, acc[i] + .02, '%.0f%%' % (acc[i] * 100), MUTE, 9.3, 'center', 'bottom')
        note(a2, x[i] + w / 2, rec[i] + .02, '%.0f%%' % (rec[i] * 100), [RED, JADE][i], 9.8, 'center', 'bottom', True)
    a2.set_xticks(x, ['全判“非断层”', '断层像素加权']); a2.set_ylim(0, 1.3)
    note(a2, .5, 1.24, '灰柱：准确率　彩柱：断层召回率', MUTE, 9, 'center', 'center'); a2.set_yticks([0, .5, 1], ['0', '50%', '100%'])
    note(a2, .5, -.25, '断层像素只占全部像素的 %.1f%%' % (frac * 100), MUTE, 9, 'center', 'top', transform=a2.get_xaxis_transform())
    title(a2, 'trap', '准确率高不等于有效')
    return f

def s4():
    rng = np.random.default_rng(4); nt, nx = 120, 120
    tt, xx = np.mgrid[0:nt, 0:nx].astype(float)
    d = np.abs(xx - (34 + .5 * tt))
    strength = .96 - .38 * tt / nt + .09 * np.sin(tt / 3.2) * (tt > 50)     # 深部响应时强时弱，最低约 0.5
    prob = strength * np.exp(-(d / 2.4) ** 2)
    unc = .38 * np.exp(-((tt - 30 - .08 * xx) / 2.2) ** 2)
    prob = np.maximum(prob, unc) + .05 * ndimage.gaussian_filter(rng.random((nt, nx)), 1.2)
    f, axs = fig(3, wspace=.09, left=.015, right=.985, bottom=.15, top=.85)
    res = {}
    for ax, thr, kind in zip(axs, [.64, .46, .30], ['trap', 'do', 'trap']):
        b = ndimage.binary_opening(prob > thr, np.ones((2, 2)))
        lab, nseg = ndimage.label(b, np.ones((3, 3)))
        nseg = int((ndimage.sum(b, lab, range(1, nseg + 1)) > 5).sum())
        ax.imshow(prob, cmap='Greys', vmin=0, vmax=1.5, aspect='auto')
        ax.imshow(np.ma.masked_where(~b, b), cmap=ListedColormap([JADE if kind == 'do' else RED]), aspect='auto')
        img_axes(ax); title(ax, kind, '阈值 %.2f' % thr); res[thr] = nseg
        msg = {.64: '深部断成 %d 段' % nseg, .46: '一条连续断面', .30: '不整合面被混入'}[thr]
        note(ax, .5, -.04, msg, JADE if kind == 'do' else RED, 10, 'center', 'top', True, transform=ax.transAxes)
    note(axs[2], 118, 33, '不整合面', CLAY, 9, 'right', 'bottom')
    return f

def s5():
    amp, mask, prob = _fault_case(seed=21)
    f, (a1, a2) = fig(2, widths=[1.35, 1], wspace=.40, top=.84, right=.9, bottom=.25)
    a1.imshow(amp, cmap=SEIS, vmin=-.8, vmax=.8, aspect='auto', interpolation='bilinear')
    t = np.arange(4, 127)
    for x0, sl, _ in FAULTS: a1.plot(x0 + sl * t, t, color=JADE, lw=2)
    a1.plot(130 + .04 * t[t < 95], t[t < 95], color=RED, lw=2, ls=(0, (4, 2.5)))
    note(a1, 133, 112, 'C', RED, 10, 'center', 'center', True)
    for xw in (100, 190):
        a1.plot([xw, xw], [2, 129], color=INK, lw=1.2); a1.plot(xw, 2, 'v', color=INK, ms=6, clip_on=False)
    for xw, (x0, sl, _) in [(100, FAULTS[0]), (190, FAULTS[1])]:
        tb = (xw - x0) / sl; a1.plot(xw, tb, 's', ms=6.5, mfc='white', mec=JADE, mew=1.7)
    a1.set_xlim(0, 239); a1.set_ylim(129, 0); img_axes(a1); a1.set_xlabel('竖线：井　方框：井断点\n红色虚线 C：井上无断点，判为河道边界后删除', fontsize=9.2, linespacing=1.5)
    title(a1, 'do', '逐条核对井断点')

    rounds = np.arange(5); labels = np.array([160, 205, 248, 286, 320]); iou = np.array([.66, .72, .76, .79, .81])
    a2.bar(rounds, labels, color=LGREY, width=.58)
    for r, l in zip(rounds, labels): note(a2, r, l / 2, str(l), MUTE, 9, 'center', 'center')
    a2.set_ylim(0, 400); a2.set_ylabel('累计标注剖面（条）')
    a2.set_xticks(rounds, ['初始', '1', '2', '3', '4']); a2.set_xlabel('回流轮次')
    b = a2.twinx(); b.plot(rounds, iou, 'o-', color=JADE, ms=4.5); b.set_ylim(.45, .9); b.set_yticks([.5, .6, .7, .8, .9])
    b.spines['right'].set_visible(True); b.spines['right'].set_color(JADE); b.tick_params(axis='y', colors=JADE, labelsize=9.3)
    b.set_ylabel('验证 IoU（示意）', color=JADE)
    title(a2, '回流', '每轮多一批标签')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：相邻 inline 的相关系数随间隔衰减；右：同一个“照抄最近剖面”的模型，随机划分的验证分数明显虚高。',
        '左：合成数据与实测资料频带不同（灰色为差异）；右：先用合成数据预训练再微调，少量本地标注就接近饱和。',
        '左：合成剖面上输出的断层概率；右：断层像素不到 1%，全判“非断层”准确率也很高，但召回率为 0。',
        '同一张概率图取三个阈值：过高时深部弱断层断成碎片，过低时不整合面被当成断层。',
        '左：两口井的断点确认了两条断层，井上没有断点的候选 C 被删除；右：每轮回流后的标签数量与验证分数。']
