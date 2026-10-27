# -*- coding: utf-8 -*-
"""初至波自动拾取：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

DT = .002

def fb_time(x, static=0):
    return np.minimum(x / 800., x / 2600. + .19) + .02 + static

def shot(nx=96, nt=760, seed=1, static=None):
    rng = np.random.default_rng(seed)
    x = np.linspace(30, 3000, nx); t = np.arange(nt) * DT
    st = np.zeros(nx) if static is None else static
    fb = fb_time(x, st)
    w = lambda tau, f=30: (1 - 2 * (np.pi * f * tau) ** 2) * np.exp(-(np.pi * f * tau) ** 2)
    d = np.zeros((nt, nx)); amp = 1 / (1 + x / 900)
    for j in range(nx):
        tau = t - fb[j]
        d[:, j] += amp[j] * w(tau - .012) * (tau > -.02)
        for dt_, a in [(.08, .6), (.17, .5), (.26, .4)]: d[:, j] += amp[j] * a * w(tau - dt_)
    noise = .07 + .0 * x
    d += rng.normal(0, 1, d.shape) * noise[None, :]
    snr = amp / noise
    return x, t, d, fb, snr

def s1():
    x, t, d, fb, snr = shot()
    tier = np.where(snr > 7, 0, np.where(snr > 4, 1, 2))
    f, (a1, a2) = fig(2, widths=[1.25, 1], wspace=.30, top=.84, bottom=.2, left=.085)
    dn = d / (np.abs(d).max(0, keepdims=True) + 1e-9) * 0 + d / np.percentile(np.abs(d), 99, axis=0, keepdims=True)
    a1.imshow(dn, cmap=SEIS, vmin=-1, vmax=1, aspect='auto', extent=(x[0], x[-1], t[-1], 0), interpolation='bilinear')
    a1.plot(x, fb, color=RED, lw=1.2, ls=(0, (3, 2)))
    cols = [JADE, CLAY, RED]
    for k in range(3):
        xs = x[tier == k]; a1.plot([xs.min(), xs.max()], [.012, .012], color=cols[k], lw=5, solid_capstyle='butt', clip_on=False)
        note(a1, xs.mean(), .05, ['高信噪比', '中', '低信噪比'][k], cols[k], 9, 'center', 'top', True, box=True)
    a1.set_xlabel('偏移距 / m'); a1.set_ylabel('时间 / s'); a1.set_ylim(1.5, 0)
    title(a1, '数据', '按信噪比分三档')
    share = np.array([(tier == k).mean() for k in range(3)])
    uni = share; over = np.array([.25, .30, .45])
    xx = np.arange(3); w = .36
    a2.bar(xx - w / 2, uni, w, color=GREY); a2.bar(xx + w / 2, over, w, color=cols)
    for i in range(3):
        note(a2, i - w / 2, uni[i] + .01, pct(uni[i]), MUTE, 8.8, 'center', 'bottom')
        note(a2, i + w / 2, over[i] + .01, pct(over[i]), cols[i], 9.2, 'center', 'bottom', True)
    a2.set_xticks(xx, ['高', '中', '低']); a2.set_xlabel('信噪比档'); a2.set_ylabel('标注样本占比')
    a2.set_ylim(0, .62); a2.set_yticks([0, .2, .4, .6], ['0', '20%', '40%', '60%'])
    note(a2, 1, .6, '灰：按道数均匀抽　彩：低信噪比多抽', MUTE, 8.8, 'center', 'top')
    title(a2, 'do', '难的那档多标')
    return f

def _picks(n_shot=24, nx=96, seed=2):
    rng = np.random.default_rng(seed)
    x = np.linspace(30, 3000, nx)
    P = []
    for s in range(n_shot):
        st = .012 * ndimage.gaussian_filter1d(rng.normal(0, 1, nx), 6) * 6 + rng.normal(0, .006)
        P.append(fb_time(x, st) + rng.normal(0, .0015, nx))
    return x, np.array(P)

def s2():
    x, P = _picks()
    ns, nx = P.shape
    resid = P - fb_time(x)[None]
    rng = np.random.default_rng(3)
    same = [np.abs(resid[s, j] - resid[s, j + 1]) * 1000 for s in range(ns) for j in range(nx - 1)]
    other = [np.abs(resid[s, j] - resid[(s + 1 + rng.integers(ns - 1)) % ns, j]) * 1000 for s in range(ns) for j in range(nx)]
    idx = [(s, j) for s in range(ns) for j in range(nx)]
    val_r = set(map(tuple, np.array(idx)[rng.choice(len(idx), len(idx) // 5, replace=False)]))
    val_s = set((s, j) for s in range(ns - 5, ns) for j in range(nx))
    def err(val):
        e = []
        for (s, j) in val:
            cands = [(abs(jj - j) + 1000 * (ss != s), ss, jj) for ss, jj in [(s, j - 1), (s, j + 1)] if 0 <= jj < nx and (ss, jj) not in val]
            if not cands:
                o = [ss for ss in range(ns) if (ss, j) not in val]; ss = o[rng.integers(len(o))]; pred = resid[ss, j]
            else:
                _, ss, jj = min(cands); pred = resid[ss, jj]
            e.append(abs(pred - resid[s, j]) * 1000)
        return np.mean(e)
    er, es = err(val_r), err(val_s)
    f, (a1, a2) = fig(2, widths=[1.3, 1], wspace=.34, top=.84, bottom=.2)
    bins = np.linspace(0, 30, 31)
    a1.hist(same, bins, color=RED, alpha=.6, density=True, label='同一炮相邻道')
    a1.hist(other, bins, color=BLUE, alpha=.5, density=True, label='不同炮、同偏移距')
    a1.set_xlabel('两道初至时间之差 / ms'); a1.set_ylabel('概率密度'); a1.set_xlim(0, 30)
    a1.legend(loc='upper right', handlelength=1, borderaxespad=0)
    title(a1, '数据', '同一炮的相邻道几乎一样')
    a2.bar([0, 1], [er, es], color=[RED, JADE], width=.55)
    for i, v in enumerate([er, es]): note(a2, i, v + .2, '%.1f ms' % v, [RED, JADE][i], 10.5, 'center', 'bottom', True)
    a2.set_xticks([0, 1], ['随机划分', '按炮划分']); a2.set_ylabel('验证集平均误差 / ms'); a2.set_ylim(0, max(er, es) * 1.45)
    note(a2, .5, .97, '同一个“照抄最近训练道”的模型', MUTE, 8.8, 'center', 'top', transform=a2.transAxes)
    title(a2, 'trap', '随机划分误差虚低')
    return f

def s3():
    rng = np.random.default_rng(5); nt = 300; t = np.arange(nt) * DT * 1000
    t0 = 330.
    w = lambda tau, f=30: (1 - 2 * (np.pi * f * tau) ** 2) * np.exp(-(np.pi * f * tau) ** 2)
    tr = .9 * w((t - t0) / 1000 - .012) + .5 * w((t - t0) / 1000 - .07) + rng.normal(0, .08, nt)
    tr[np.abs(t - 190) < 3] += [.0, .95, -.7][:int((np.abs(t - 190) < 3).sum())] if (np.abs(t - 190) < 3).sum() <= 3 else 0
    env = np.abs(tr)
    sta = ndimage.uniform_filter1d(env, 5); lta = ndimage.uniform_filter1d(env, 60, origin=29)
    p = 1 / (1 + np.exp(-(t - t0 - 2) / 6))
    p = np.clip(p + .06 * ndimage.gaussian_filter1d(rng.normal(0, 1, nt), 3), 0, 1)
    pick_p = t[np.argmax(np.gradient(ndimage.gaussian_filter1d(p, 2)))]
    thr = .55; pick_a = t[np.argmax(env > thr)]
    f, (a1, a2) = fig(2, wspace=.28, top=.84, bottom=.2)
    for ax in (a1, a2):
        ax.plot(t, tr, color=INK, lw=1); ax.axvline(t0, color=GREY, lw=1, ls=':')
        ax.set_xlim(100, 520); ax.set_ylim(-1.15, 1.25); ax.set_xlabel('时间 / ms'); ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        note(ax, t0 + 4, -1.08, '真实初至', GREY, 8.8, 'left', 'bottom')
    a1.plot(t, p * 1.0 - .0, color=JADE, lw=1.8)
    a1.axvline(pick_p, color=JADE, lw=1.6)
    note(a1, 108, 1.0, '绿线：“已到达”概率', JADE, 9, 'left', 'center')
    note(a1, 515, -.72, '取概率跃变处\n误差 %.0f ms' % abs(pick_p - t0), JADE, 9.2, 'right', 'center', True)
    title(a1, 'do', '逐点输出到达概率')
    a2.axhline(thr, color=RED, lw=1.1, ls='--'); a2.axhline(-thr, color=RED, lw=1.1, ls='--')
    a2.axvline(pick_a, color=RED, lw=1.6)
    note(a2, pick_a + 6, .95, '噪声尖峰先越过阈值\n提前 %.0f ms' % abs(pick_a - t0), RED, 9.2, 'left', 'center', True)
    note(a2, 515, thr + .05, '固定振幅阈值', RED, 8.8, 'right', 'bottom')
    title(a2, 'trap', '固定阈值取初至')
    return f

def s4():
    rng = np.random.default_rng(8); nx = 96
    x = np.linspace(30, 3000, nx)
    st = .007 * np.sin(x / 260) + .006 * np.exp(-((x - 1900) / 120) ** 2)       # 真实近地表变化
    true = fb_time(x, st) * 1000
    pk = true + rng.normal(0, .8, nx); out = [14, 37, 61, 80]; pk[out] += [-38, 30, -26, 34]
    med = ndimage.median_filter(pk, 9, mode='nearest')
    def fix(tol):
        flag = np.abs(pk - med) > tol; fx = np.where(flag, med, pk); return flag, fx
    f, (a1, a2) = fig(2, wspace=.24, top=.84, bottom=.2)
    for ax, tol, k, t_ in [(a1, 15, 'do', '容差 ±15 ms'), (a2, 2.5, 'trap', '容差 ±2.5 ms')]:
        flag, fx = fix(tol)
        wrong = flag & (np.abs(pk - true) < 3)
        ax.plot(x, true - x / 2.6, color=LGREY, lw=4, solid_capstyle='round')
        ax.plot(x[~flag], (pk - x / 2.6)[~flag], 'o', ms=3.4, color=INK)
        ax.plot(x[flag & ~wrong], (fx - x / 2.6)[flag & ~wrong], 'o', ms=5, mfc='white', mec=JADE, mew=1.4)
        ax.plot(x[wrong], (fx - x / 2.6)[wrong], 'o', ms=5, mfc='white', mec=RED, mew=1.4)
        for i in out: ax.plot(x[i], pk[i] - x[i] / 2.6, 'x', color=GREY, ms=5, mew=1.2)
        ax.set_xlabel('偏移距 / m'); ax.set_xlim(350, 3050); r = (pk - x / 2.6)[x > 350]; ax.set_ylim(r.min() - 6, r.max() + 14)
        title(ax, k, t_)
        msg = '只改掉 %d 道真离群点' % (flag & ~wrong).sum() if k == 'do' else '改掉 %d 道，其中 %d 道本来是对的' % (flag.sum(), wrong.sum())
        note(ax, .5, .97, msg, JADE if k == 'do' else RED, 9.2, 'center', 'top', True, transform=ax.transAxes)
    a1.set_ylabel('折合走时 / ms（减去 x / 2600）')
    note(a2, .98, .04, '灰带：真实初至　叉：离群点　圈：被回退', MUTE, 8.4, 'right', 'bottom', transform=a2.transAxes)
    return f

def s5():
    rng = np.random.default_rng(9); n = 4000
    hard = rng.random(n) < .1
    conf = np.where(hard, rng.beta(1.8, 3.4, n), rng.beta(14, 1.2, n))
    err = rng.random(n) < np.where(hard, .5, .002)
    fallback = rng.random(n) < .03
    review = (conf < .6) | fallback
    f, (a1, a2) = fig(2, widths=[1.15, 1], wspace=.32, top=.84, bottom=.2)
    bins = np.linspace(0, 1, 26)
    a1.hist([conf[err], conf[~err]], bins, color=[RED, LGREY], stacked=True, label=['拾取错误', '拾取正确'])
    a1.axvline(.6, color=JADE, lw=1.4, ls='--'); note(a1, .58, a1.get_ylim()[1] * .9, '复核线', JADE, 9, 'right', 'top', True)
    a1.set_yscale('log'); a1.set_xlabel('拾取置信度'); a1.set_ylabel('道数（对数轴）')
    a1.legend(loc='upper left', handlelength=1, borderaxespad=0)
    title(a1, 'do', '只复核低置信度和回退道')
    work = [1, review.mean()]; left_ = [0, (err & ~review).sum() / n]
    found = (err & review).sum() / err.sum()
    a2.bar([0, 1], work, color=[GREY, JADE], width=.55)
    note(a2, 0, 1.02, '100%', MUTE, 10, 'center', 'bottom', True)
    note(a2, 1, work[1] + .02, '%s\n找回 %s 的错误' % (pct(work[1]), pct(found)), JADE, 9.6, 'center', 'bottom', True)
    a2.set_xticks([0, 1], ['全量复核', '只复核报警道']); a2.set_ylim(0, 1.2); a2.set_yticks([0, .5, 1], ['0', '50%', '100%'])
    a2.set_ylabel('人工复核的道数占比')
    title(a2, 'trap', '全量复核耗费人力')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：一炮记录按信噪比分三档，远偏移距信噪比最低（红虚线为初至）；右：按道数均匀抽样时低信噪比档样本最少，改为多抽。',
        '左：同一炮的相邻道初至几乎一样，不同炮之间差别大得多；右：同一个“照抄最近训练道”的模型，随机划分的验证误差明显偏低。',
        '同一道记录：左边取“已到达”概率跃变处作为初至，误差只有几毫秒；右边用固定振幅阈值，噪声尖峰提前触发。',
        '同一组拾取：容差合适时只回退真正的离群点；容差太窄时，真实的近地表变化也被当成离群点改掉（红圈）。',
        '左：错误拾取几乎都落在低置信度一侧；右：只复核低置信度道和被回退的道，工作量约为全量的一成多，就能找回大部分错误。']
