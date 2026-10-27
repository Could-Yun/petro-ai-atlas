# -*- coding: utf-8 -*-
"""地震资料噪声压制：5 步示意图（由合成数据计算）"""
import numpy as np
from scipy import ndimage
from common import *

DT = .004

def gather(nx=64, nt=220, seed=1, f=28, gr=1.0, rnd=.0):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1600, nx); t = np.arange(nt) * DT
    clean = np.zeros((nt, nx))
    for t0, v, a in [(.18, 1800, 1), (.33, 2100, -.8), (.47, 2400, .7), (.62, 2700, -.6), (.76, 3000, .55)]:
        tt = np.sqrt(t0 ** 2 + (x / v) ** 2)
        for j in range(nx): clean[:, j] += a * np.exp(-((t - tt[j]) * f * np.pi) ** 2) * (1 - 2 * ((t - tt[j]) * f * np.pi) ** 2)
    noise = np.zeros((nt, nx))
    if gr:
        for vg, fg in [(380, 7), (520, 10)]:
            for j in range(nx):
                tau = t - x[j] / vg - .02
                env = np.exp(-np.clip(tau, 0, None) / .25) * (tau > 0)
                noise[:, j] += gr * 2.2 * env * np.sin(2 * np.pi * fg * tau) * (1 + x[j] / 1600)
    if rnd: noise += rng.normal(0, rnd, noise.shape)
    return x, t, clean, noise

def spec(a, axis=0):
    s = np.abs(np.fft.rfft(a * np.hanning(a.shape[axis])[:, None], axis=axis)) ** 2
    return ndimage.gaussian_filter1d(s.mean(1), 1.5)

def show(ax, d, clip=1.2, title_kind=None, ttl=''):
    ax.imshow(d, cmap=SEIS, vmin=-clip, vmax=clip, aspect='auto', interpolation='bilinear')
    img_axes(ax)
    if title_kind: title(ax, title_kind, ttl)

def s1():
    x, t, clean, gr = gather(gr=1)
    _, _, _, rn = gather(gr=0, rnd=.55, seed=2)
    f, (a1, a2, a3) = fig(3, widths=[1, 1, 1.2], wspace=.18, top=.84, bottom=.2, left=.015)
    show(a1, clean + rn, 1.2, 'trap', '理想随机噪声')
    show(a2, clean + gr, 1.2, 'do', '叠加实测面波')
    note(a1, .5, -.04, '噪声均匀铺开', RED, 9, 'center', 'top', transform=a1.transAxes)
    note(a2, .5, -.04, '低速、低频、扇形分布', JADE, 9, 'center', 'top', transform=a2.transAxes)
    fr = np.fft.rfftfreq(len(t), DT)
    for d, c, lab in [(clean, INK, '有效反射'), (rn, RED, '随机噪声'), (gr, JADE, '面波')]:
        s = spec(d); a3.plot(fr, s / s.max(), color=c, lw=1.6)
    a3.set_xlim(0, 80); a3.set_ylim(0, 1.08); a3.set_xlabel('频率 / Hz'); a3.set_ylabel('归一化能量')
    note(a3, 13, .98, '面波', JADE, 9.2, 'left', 'top', True); note(a3, 41, .78, '有效反射', INK, 9.2, 'left', 'center', True)
    note(a3, 79, .5, '随机噪声', RED, 9.2, 'right', 'top', True)
    title(a3, '数据', '频谱完全不同')
    return f

def _wiener(sig, noi, alpha=1.):
    S, N = spec(sig), spec(noi)
    return S / (S + alpha * N + 1e-12)

def _apply(d, G):
    D = np.fft.rfft(d * 1, axis=0); return np.fft.irfft(D * G[:, None], n=d.shape[0], axis=0)

def s2():
    x, t, c_syn, _ = gather(f=42, gr=0)
    _, _, _, n_syn = gather(gr=0, rnd=.5, seed=3)
    x, t, c_real, n_real = gather(f=22, gr=.5, seed=4)
    n_real = n_real + np.random.default_rng(5).normal(0, .25, n_real.shape)
    G_syn, G_ft = _wiener(c_syn, n_syn), _wiener(c_real, n_real)
    snr = lambda o: 10 * np.log10((c_real ** 2).sum() / ((o - c_real) ** 2).sum())
    d = c_real + n_real
    s0, s1_, s2_ = snr(d), snr(_apply(d, G_syn)), snr(_apply(d, G_ft))
    fr = np.fft.rfftfreq(len(t), DT)
    f, (a1, a2) = fig(2, widths=[1.25, 1], wspace=.34, top=.84, bottom=.2)
    sr = spec(c_real); a1.fill_between(fr, sr / sr.max(), color=CLAY, alpha=.18, lw=0)
    note(a1, 3, .5, '实测有效\n信号频带', CLAY, 8.8, 'left', 'center')
    a1.plot(fr, G_syn, color=BLUE, lw=1.8); a1.plot(fr, G_ft, color=JADE, lw=1.8)
    note(a1, 60, .72, '只用合成样本\n学到的通带', BLUE, 9, 'center', 'center')
    note(a1, 34, .98, '自监督微调后', JADE, 9, 'left', 'top')
    a1.set_xlim(0, 90); a1.set_ylim(0, 1.08); a1.set_xlabel('频率 / Hz'); a1.set_ylabel('保留比例')
    title(a1, 'trap', '合成样本频带偏高')
    bars = [('输入', s0, GREY), ('只用合成', s1_, BLUE), ('合成 + 微调', s2_, JADE)]
    a2.bar(range(3), [b[1] for b in bars], color=[b[2] for b in bars], width=.58)
    for i, (_, v, c) in enumerate(bars): note(a2, i, v + (.3 if v >= 0 else -.3), '%.1f dB' % v, c, 9.8, 'center', 'bottom' if v >= 0 else 'top', True)
    a2.set_xticks(range(3), [b[0] for b in bars]); a2.set_ylabel('信噪比 / dB'); a2.set_ylim(min(0, s0 - 1.8), max(s2_ + 2, 6))
    a2.axhline(0, color='#6b6b6b', lw=.8)
    title(a2, 'do', '真实资料微调')
    return f

def s3():
    x, t, c, gr = gather(gr=1.6, seed=6)
    zone_a = (slice(0, 110), slice(0, 24))           # 面波强的近偏移距浅层
    zone_b = (slice(150, 220), slice(30, 64))        # 深层弱信号
    rng = np.random.default_rng(7)
    n = gr + rng.normal(0, .02, gr.shape)
    cb = c.copy(); cb[150:] *= .3
    S, N = spec(cb), spec(n)
    def err(alpha, z):
        G = S / (S + alpha * N + 1e-12)
        o = _apply(cb + n, G)[z]; return ((o - cb[z]) ** 2).sum() / (cb[z] ** 2).sum()
    al = np.geomspace(.008, 100, 50)
    ea = np.array([err(a, zone_a) for a in al]); eb = np.array([err(a, zone_b) for a in al])
    f, (a1, a2) = fig(2, widths=[.62, 1.4], wspace=.36, top=.84, bottom=.2)
    a1.bar([0, 1], [6.5, .15], color=[GREY, JADE], width=.58)
    note(a1, 0, 6.6, '约 6.5 小时', MUTE, 9.2, 'center', 'bottom'); note(a1, 1, .25, '约 9 分钟', JADE, 9.2, 'center', 'bottom', True)
    a1.set_xticks([0, 1], ['常规流程', '一次前向']); a1.set_ylabel('全工区耗时 / h（示意）'); a1.set_ylim(0, 7.8)
    title(a1, 'do', '批量处理')
    a2.plot(al, ea / ea.min(), color=CLAY, label='强噪声区'); a2.plot(al, eb / eb.min(), color=BLUE, label='弱信号区')
    ia, ib = ea.argmin(), eb.argmin()
    a2.plot(al[ia], 1, 'o', color=CLAY, ms=5); a2.plot(al[ib], 1, 'o', color=BLUE, ms=5)
    fixed = np.sqrt(al[ia] * al[ib])
    a2.axvline(fixed, color=RED, lw=1.3, ls='--')
    ya, yb = np.interp(fixed, al, ea / ea.min()), np.interp(fixed, al, eb / eb.min())
    note(a2, fixed / 1.15, 3.85, '统一强度', RED, 9.2, 'right', 'top', True)
    note(a2, al[ia], .93, '最优', CLAY, 8.6, 'center', 'top'); note(a2, al[ib], .93, '最优', BLUE, 8.6, 'center', 'top')
    a2.plot(fixed, ya, 's', color=CLAY, ms=5); a2.plot(fixed, yb, 's', color=BLUE, ms=5)
    note(a2, fixed * 1.25, ya, '×%.1f %s' % (ya, '欠去噪' if fixed < al[ia] else '过去噪'), CLAY, 9.2, 'left', 'center', True, box=True)
    note(a2, fixed / 1.25, yb + .05, '%s ×%.1f' % ('欠去噪' if fixed < al[ib] else '过去噪', yb), BLUE, 9.2, 'right', 'bottom', True)
    a2.set_xscale('log'); a2.set_ylim(.75, 4); a2.set_xlabel('去噪强度（对数轴）；方块为统一强度下的误差', fontsize=9.4); a2.set_ylabel('误差 / 该区最优误差')
    a2.legend(loc='upper right', handlelength=1.2, borderaxespad=0)
    title(a2, 'trap', '两区最优强度不同')
    return f

def s4():
    x, t, c, gr = gather(gr=1.0, seed=8)
    rng = np.random.default_rng(9); n = gr + rng.normal(0, .15, gr.shape)
    d = c + n
    o = _apply(d, _wiener(c, n, 9.0)); r = d - o
    rc = lambda a, b: np.corrcoef(ndimage.gaussian_filter(a, 1).ravel(), ndimage.gaussian_filter(b, 1).ravel())[0, 1]
    f, axs = fig(3, wspace=.06, top=.84, bottom=.15, left=.012, right=.988)
    show(axs[0], d, 1.3, '输入', ''); show(axs[1], o, 1.3, '输出', ''); show(axs[2], r, 1.3, 'check', '残差 = 输入 − 输出')
    note(axs[1], .5, -.04, '看上去很干净', MUTE, 9, 'center', 'top', transform=axs[1].transAxes)
    note(axs[2], .5, -.04, '残差里有连续同相轴 → 伤及有效波', RED, 9, 'center', 'top', True, transform=axs[2].transAxes)
    note(axs[0], .5, -.04, '面波 + 随机噪声', MUTE, 9, 'center', 'top', transform=axs[0].transAxes)
    j = np.arange(64); tt = np.sqrt(.33 ** 2 + (np.linspace(0, 1600, 64) / 2100) ** 2) / DT
    axs[2].plot(j, tt, color=RED, lw=1.2, ls=(0, (3, 2)), alpha=.9)
    return f

def s5():
    rng = np.random.default_rng(10)
    f, (a1, a2) = fig(2, widths=[1, 1.3], wspace=.26, top=.84, bottom=.2, left=.02)
    g = np.clip(rng.normal(.12, .05, (5, 8)), 0, None); g[1, 5] = .46; g[3, 2] = .38; g[2, 6] = .31
    im = a1.imshow(g, cmap=LinearSegmentedColormap.from_list('q', ['#eef1ec', '#c9d3c4', CLAY, RED]), vmin=0, vmax=.5, aspect='auto')
    for (i, j), v in np.ndenumerate(g):
        note(a1, j, i, '%.2f' % v, 'white' if v > .3 else MUTE, 8, 'center', 'center', v > .3)
    acts = {(1, 5): '回退', (3, 2): '调强度', (2, 6): '调强度'}
    for (i, j), t_ in acts.items():
        a1.add_patch(mpl.patches.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=1.6))
    img_axes(a1)
    note(a1, .5, -.04, '数字：残差与输出的相关系数；黑框为报警区段', MUTE, 8.6, 'center', 'top', transform=a1.transAxes)
    title(a1, 'check', '分区质控报警')
    cdp = np.arange(400)
    base = 1 + .05 * np.sin(cdp / 23)
    zone = (cdp > 230) & (cdp < 300)
    raw = base + rng.normal(0, .18, 400)
    ai = base * np.where(zone, .45, 1) + rng.normal(0, .04, 400)
    fb = np.where(zone, base * .93 + rng.normal(0, .08, 400), ai)
    a2.plot(cdp, raw, color=LGREY, lw=1, label='原始叠加')
    a2.plot(cdp, ai, color=RED, lw=1.6, label='无回退')
    a2.plot(cdp, fb, color=JADE, lw=1.6, label='报警区回退到常规方法')
    a2.axvspan(230, 300, color=RED, alpha=.07, lw=0); note(a2, 265, 1.55, '过度去噪区段', RED, 9, 'center', 'top')
    a2.set_ylim(-.15, 1.65); a2.set_xlim(0, 399); a2.set_xlabel('CDP'); a2.set_ylabel('目的层反射振幅（相对值）')
    a2.legend(loc='lower left', ncols=1, handlelength=1.2, borderaxespad=0, fontsize=8.8)
    title(a2, 'do', '报警区回退')
    return f

FIGS = [s1, s2, s3, s4, s5]
CAPS = ['左：只叠加理想随机噪声的合成记录；中：叠加从实测资料提取的面波；右：两种噪声的频谱完全不同，只学随机噪声的模型对面波无效。',
        '左：只用合成样本学到的通带比实测信号频带高；右：同一份实测资料，只用合成样本训练去噪不足，用真实资料微调后信噪比明显提高。',
        '左：一次前向计算处理全工区（耗时为示意）；右：强噪声区和弱信号区的最优去噪强度相差很大，统一强度时一处欠去噪、一处过去噪。',
        '同一道集：输出看上去很干净，但残差里出现了连续的反射同相轴（虚线处），说明有效波被去掉了。',
        '左：按区段统计残差与输出的相关系数，超限的区段报警；右：报警区段回退到常规方法后，目的层振幅恢复。']
