# -*- coding: utf-8 -*-
"""案例流程每一步的示意图：每案例 5 张，与 case_content 中的 workflow.steps 一一对应。
统一版式：340×150 画布；双栏时左栏为“这一步怎么做”，右栏为“常见问题”。"""
import math, random
from html import escape as _e

INK, JADE, CLAY, BLUE, RED, MUTE, LINE = '#212837', '#2f7d6b', '#b26a39', '#41699b', '#b05a51', '#505050', '#e2e2e2'
SAND, MOSS, GRAY, PAPER = '#d8c89a', '#9fb19c', '#c9c9c9', '#fbfbfa'
W, H = 340, 150

def esc(s): return _e(str(s), quote=True)
def T(x, y, t, col=MUTE, size=10, anchor='start', bold=False):
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, ' font-weight="600"' if bold else '', esc(t))
def R(x, y, w, h, fill='none', stroke=None, rx=3, op=None, dash=False, sw=1):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"%s%s%s/>' % (x, y, w, h, rx, fill, (' stroke="%s" stroke-width="%s"' % (stroke, sw)) if stroke else '', (' opacity="%s"' % op) if op is not None else '', ' stroke-dasharray="4 3"' if dash else '')
def L(x1, y1, x2, y2, col=INK, sw=1.4, dash=False, op=None):
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s%s/>' % (x1, y1, x2, y2, col, sw, ' stroke-dasharray="4 3"' if dash else '', (' opacity="%s"' % op) if op is not None else '')
def C(x, y, r, fill=INK, stroke=None, op=None):
    return '<circle cx="%.1f" cy="%.1f" r="%s" fill="%s"%s%s/>' % (x, y, r, fill, (' stroke="%s" stroke-width="1.4"' % stroke) if stroke else '', (' opacity="%s"' % op) if op is not None else '')
def PL(pts, col=INK, sw=1.4, dash=False, fill='none', op=None):
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s/>' % (' '.join('%.1f,%.1f' % p for p in pts), fill, col, sw, ' stroke-dasharray="4 3"' if dash else '', (' opacity="%s"' % op) if op is not None else '')
def PG(pts, fill, op=None, stroke=None):
    return '<polygon points="%s" fill="%s"%s%s/>' % (' '.join('%.1f,%.1f' % p for p in pts), fill, (' opacity="%s"' % op) if op is not None else '', (' stroke="%s"' % stroke) if stroke else '')
def ARW(x1, y1, x2, y2, col=MUTE, sw=1.3):
    a = math.atan2(y2 - y1, x2 - x1); h = 5
    return L(x1, y1, x2, y2, col, sw) + PL([(x2 - h * math.cos(a - .5), y2 - h * math.sin(a - .5)), (x2, y2), (x2 - h * math.cos(a + .5), y2 - h * math.sin(a + .5))], col, sw)
def CHK(x, y, ok=True):
    return (PL([(x - 4, y), (x - 1, y + 3), (x + 4, y - 3)], JADE, 1.8) if ok else L(x - 3, y - 3, x + 3, y + 3, RED, 1.8) + L(x - 3, y + 3, x + 3, y - 3, RED, 1.8))
def rr(s): return random.Random(s)

def svg(inner, label):
    return '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % (W, H, esc(label)) + inner + '</svg>'
def two(left, right, lt='做法', rt='常见问题', label=''):
    """左右两栏：左 = 这一步怎么做，右 = 常见问题。left/right(x0, w) 返回 svg 片段。"""
    s = ''
    for i, (fn, tag, col) in enumerate([(left, lt, JADE), (right, rt, RED)]):
        x = 4 + i * 170
        s += R(x, 4, 162, H - 8, PAPER, LINE, 7)
        s += T(x + 9, 19, tag, col, 9.5, bold=True)
        s += fn(x, 162)
    return svg(s, label)
def one(fn, tag='做法', label=''):
    s = R(4, 4, W - 8, H - 8, PAPER, LINE, 7) + T(13, 19, tag, JADE, 9.5, bold=True) + fn(4, W - 8)
    return svg(s, label)

def wig(x, y0, w, arrival, amp=6, noise=.6, seed=1, step=2):
    r = rr(seed); pts = []
    for t in range(0, int(w), step):
        dt = t - arrival
        v = 0 if dt < 0 else (1 - math.exp(-dt / 3)) * math.sin(dt * .55) * math.exp(-dt / 45) * amp
        pts.append((x + t, y0 + v + r.gauss(0, noise)))
    return pts
def reflectors(x, y, w, h, n=5, col='#4e5d61', fault=None, seed=1, sw=1.6):
    s = ''
    for k in range(n):
        y0 = y + 10 + k * (h - 18) / max(1, n - 1)
        pts = []
        for t in range(0, int(w) + 1, 4):
            dy = 3 * math.sin((t + k * 11) / 22)
            if fault and x + t > fault: dy += 9
            pts.append((x + t, y0 + dy))
        s += PL(pts, col, sw)
    return s

# ======================================================================= 地震断层
def f_fault():
    def a1(x, w):
        s = ''
        for i in range(12):
            col = JADE if i < 8 else BLUE
            s += R(x + 12 + i * 11.5, 30, 9, 78, col, rx=1.5, op=.75)
        s += L(x + 12 + 8 * 11.5 - 1.5, 26, x + 12 + 8 * 11.5 - 1.5, 112, INK, 1.4, True)
        return s + T(x + 52, 124, '训练区块', JADE, 9.5, 'middle') + T(x + 130, 124, '验证区块', BLUE, 9.5, 'middle') + T(x + 12, 138, '整块切分，块间不相邻', MUTE, 9)
    def a2(x, w):
        s = ''; r = rr(4)
        for i in range(12):
            col = JADE if r.random() < .67 else BLUE
            s += R(x + 12 + i * 11.5, 30, 9, 78, col, rx=1.5, op=.75)
        s += R(x + 46, 26, 26, 86, 'none', RED, 3, sw=1.6)
        return s + T(x + 12, 124, '相邻剖面落入两边', RED, 9.5) + T(x + 12, 138, '验证分数虚高', MUTE, 9)
    f1 = two(a1, a2, label='按区块划分训练与验证集')
    def b(x, w):
        s = ''
        for i, (t, sub, col, bx) in enumerate([('合成数据体', '正演 · 含断层', BLUE, 14), ('预训练模型', '', MUTE, 120), ('本工区微调', '160 条剖面', JADE, 226)]):
            s += R(x + bx, 42, 92, 44, '#ffffff', col, 6, sw=1.3) + T(x + bx + 46, 62, t, INK, 10.5, 'middle', True)
            if sub: s += T(x + bx + 46, 77, sub, MUTE, 9, 'middle')
        s += ARW(x + 108, 64, x + 118, 64) + ARW(x + 214, 64, x + 224, 64)
        s += T(x + 14, 112, '跳过微调：合成与实测频带不一致 → 大量误报', RED, 9.5)
        for k in range(6): s += R(x + 18 + k * 13, 94, 10, 6, BLUE, op=.35, rx=1)
        return s + T(x + 14, 130, '合成样本可大量生成，本地标注只需一百多条', MUTE, 9)
    f2 = one(b, '流程', '合成数据预训练再微调')
    def c1(x, w):
        s = R(x + 12, 30, w - 24, 84, '#f2f2f2', rx=2) + reflectors(x + 12, 30, w - 24, 84, 5, fault=x + 80, seed=2, sw=1.3)
        s += '<path d="M%.1f 32 L%.1f 112" stroke="%s" stroke-width="9" opacity=".35"/>' % (x + 72, x + 92, RED)
        s += '<path d="M%.1f 32 L%.1f 112" stroke="%s" stroke-width="2"/>' % (x + 72, x + 92, RED)
        return s + T(x + 12, 132, '逐体素输出断层概率', MUTE, 9.5)
    def c2(x, w):
        s = R(x + 14, 40, 110, 22, GRAY, rx=2) + R(x + 124, 40, 2.5, 22, RED, rx=0)
        s += T(x + 14, 78, '非断层 99%', MUTE, 9.5) + T(x + w - 10, 78, '断层 1%', RED, 9.5, 'end')
        return s + T(x + 14, 104, '不加权：全判“非断层”', INK, 9.5) + T(x + 14, 120, '准确率也有 99%', RED, 9.5, bold=True)
    f3 = two(c1, c2, label='断层概率预测与类别不平衡')
    def d(x, w):
        s = ''
        for i, (tag, thr, col) in enumerate([('阈值过高', .8, RED), ('合适', .5, JADE), ('阈值过低', .25, RED)]):
            x0 = x + 14 + i * 108
            s += R(x0, 30, 96, 80, '#f2f2f2', rx=3) + T(x0 + 48, 124, tag, col, 9.5, 'middle', True)
            if thr == .8:
                for a, b in [(36, 50), (66, 76), (92, 102)]: s += L(x0 + 30 + a * .2, a, x0 + 30 + b * .2, b, INK, 2)
            elif thr == .5:
                s += L(x0 + 36, 34, x0 + 56, 106, INK, 2.2)
            else:
                s += L(x0 + 36, 34, x0 + 56, 106, INK, 2.2) + L(x0 + 8, 70, x0 + 88, 66, CLAY, 1.8)
        s += T(x + 230, 140, '橙线：不整合面被混入', CLAY, 9, 'middle')
        return s + T(x + 14, 140, '断成碎片', MUTE, 9)
    f4 = one(d, '阈值对比', '骨架化阈值的取舍')
    def e(x, w):
        s = ''; cx, cy = x + 166, 78
        nodes = [('候选断面', cx - 110, cy - 26, BLUE), ('人工增删改', cx + 18, cy - 26, CLAY), ('核对井断点', cx + 18, cy + 18, CLAY), ('回流为标签', cx - 110, cy + 18, JADE)]
        for t, nx, ny, col in nodes: s += R(nx, ny, 92, 26, '#ffffff', col, 6, sw=1.3) + T(nx + 46, ny + 17, t, INK, 10, 'middle', True)
        s += ARW(cx - 16, cy - 13, cx + 16, cy - 13) + ARW(cx + 64, cy, cx + 64, cy + 16) + ARW(cx + 16, cy + 31, cx - 16, cy + 31) + ARW(cx - 64, cy + 16, cx - 64, cy)
        return s + T(x + 14, 138, '每一轮都给本工区增加一批可信标签', MUTE, 9)
    f5 = one(e, '闭环', '人工质检与回流')
    return [(f1, '训练集与验证集按区块整块切分；随机划分时相邻剖面同时出现在两边。'),
            (f2, '先用合成数据预训练，再用本工区少量剖面微调。'),
            (f3, '左：模型输出断层概率；右：断层体素不到 1%，损失必须加权。'),
            (f4, '阈值过高把弱断层截成碎片，过低把不整合面混进来。'),
            (f5, '候选断面经人工修改和井断点核对后，回流成下一轮的训练标签。')]

# ======================================================================= 遥感岩性
def f_spectral():
    def a1(x, w):
        s = R(x + 12, 28, w - 24, 84, SAND, rx=2) + PG([(x + 12, 80), (x + 80, 62), (x + w - 12, 74), (x + w - 12, 112), (x + 12, 112)], MOSS)
        s += '<ellipse cx="%.1f" cy="48" rx="22" ry="11" fill="#ffffff" opacity=".9"/>' % (x + 110)
        s += R(x + 86, 36, 48, 24, 'none', MUTE, 2, dash=True) + T(x + 110, 72, '云 → 掩膜', MUTE, 9, 'middle')
        return s + T(x + 12, 128, '只在看得到岩石的地方下结论', MUTE, 9)
    def a2(x, w):
        s = R(x + 12, 28, (w - 24) / 2, 84, SAND, rx=2) + R(x + 12 + (w - 24) / 2, 28, (w - 24) / 2, 84, '#e6d3a1', rx=2)
        s += L(x + w / 2, 24, x + w / 2, 116, INK, 1.2, True)
        s += T(x + 44, 74, '春季', MUTE, 9.5, 'middle') + T(x + 118, 74, '秋季', MUTE, 9.5, 'middle')
        return s + T(x + 12, 128, '同一岩性被分成两类', RED, 9.5)
    f1 = two(a1, a2, label='影像预处理与掩膜')
    def b1(x, w):
        s = ''
        for i in range(5): s += R(x + 14 + i * 28, 34, 22, 22, MOSS, JADE, 2) + T(x + 25 + i * 28, 49, '精', '#ffffff', 9, 'middle')
        s += T(x + 14, 72, '20 个样区精修 · 当真值', JADE, 9.5)
        s += R(x + 14, 82, w - 28, 22, SAND, rx=2) + T(x + w / 2, 97, '全图幅历史地质图 · 弱标签', INK, 9, 'middle')
        return s + T(x + 14, 122, '弱标签只用于预训练', MUTE, 9)
    def b2(x, w):
        s = R(x + 14, 34, w - 28, 70, SAND, rx=2)
        s += PL([(x + 14, 58), (x + 60, 70), (x + 110, 60), (x + w - 14, 72)], JADE, 2)
        s += PL([(x + 14, 72), (x + 60, 86), (x + 110, 76), (x + w - 14, 88)], RED, 2, True)
        s += T(x + 20, 50, '真实界线', JADE, 9) + T(x + 20, 118, '老图界线偏几百米', RED, 9.5)
        return s + T(x + 14, 134, '直接当真值 → 学进老图的错', MUTE, 9)
    f2 = two(b1, b2, label='样区精标与弱标签')
    def c1(x, w):
        s = ''; r = rr(7); cols = [SAND, MOSS, '#b9c7d3']
        for i in range(12):
            for j in range(7):
                k = 0 if j < 3 - (i > 6) else (1 if j < 5 else 2)
                low = r.random() < .08
                s += R(x + 14 + i * 11.5, 30 + j * 11, 10.5, 10, GRAY if low else cols[k], rx=1)
        return s + T(x + 14, 124, '每个像素：类别 + 置信度', MUTE, 9.5) + T(x + 14, 138, '灰色 = 低置信度，留给人', MUTE, 9)
    def c2(x, w):
        s = PG([(x + 14, 112), (x + 80, 36), (x + 146, 112)], '#eeeeee')
        s += PG([(x + 14, 112), (x + 80, 36), (x + 80, 112)], SAND) + PG([(x + 80, 36), (x + 146, 112), (x + 80, 112)], '#a99b72')
        s += T(x + 40, 104, '阳坡', MUTE, 9, 'middle') + T(x + 118, 104, '阴坡', '#ffffff', 9, 'middle')
        return s + T(x + 14, 130, '只看光谱：同一岩性被分开', RED, 9.5)
    f3 = two(c1, c2, label='逐像素岩性分割')
    def d1(x, w):
        s = ''; r = rr(3)
        for i in range(10):
            for j in range(6):
                k = 1 if (j + (r.random() < .2)) > 2 else 0
                s += R(x + 12 + i * 7, 32 + j * 12, 6.5, 11, MOSS if k else SAND, rx=0)
        s += ARW(x + 88, 66, x + 100, 66)
        s += R(x + 104, 32, 46, 72, SAND, rx=0) + PG([(x + 104, 68), (x + 150, 64), (x + 150, 104), (x + 104, 104)], MOSS)
        s += PL([(x + 104, 68), (x + 150, 64)], INK, 1.6)
        return s + T(x + 12, 122, '去碎斑 → 矢量界线', MUTE, 9.5)
    def d2(x, w):
        s = R(x + 14, 32, 58, 72, SAND, rx=0) + R(x + 40, 32, 5, 72, CLAY) + T(x + 43, 116, '岩脉', CLAY, 9, 'middle')
        s += ARW(x + 76, 68, x + 88, 68) + R(x + 92, 32, 58, 72, SAND, rx=0)
        return s + T(x + 92, 116, '被抹掉', RED, 9.5) + T(x + 14, 134, '平滑过度丢掉窄条地质体', MUTE, 9)
    f4 = two(d1, d2, label='矢量化与规则检查')
    def e(x, w):
        s = R(x + 14, 28, 150, 92, SAND, rx=2) + PG([(x + 14, 84), (x + 90, 66), (x + 164, 80), (x + 164, 120), (x + 14, 120)], MOSS)
        r = rr(9)
        for i in range(9):
            px, py = x + 24 + r.random() * 130, 36 + r.random() * 76
            s += C(px, py, 5, '#ffffff', JADE if i != 4 else RED) + CHK(px, py, i != 4)
        s += T(x + 182, 48, '野外观察点逐点核对', INK, 10, bold=True)
        s += T(x + 182, 66, '✓ 与解译一致', JADE, 9.5) + T(x + 182, 82, '✗ 需要修编', RED, 9.5)
        s += ARW(x + 182, 104, x + 300, 104, JADE) + T(x + 182, 120, '修编结果 → 下一幅的标签', JADE, 9.5)
        return s
    f5 = one(e, '闭环', '人工修编与野外验证')
    return [(f1, '云、阴影、浓密植被先掩膜成“不可解译”；不同季相拼接会让同一岩性分成两类。'),
            (f2, '少量样区精标当真值，历史地质图只作弱标签预训练。'),
            (f3, '逐像素输出岩性和置信度；只用光谱时，阴坡和阳坡上的同一岩性会被分开。'),
            (f4, '概率图去碎斑后转成矢量界线；平滑过度会抹掉岩脉这样的窄条地质体。'),
            (f5, '用野外观察点核对解译结果，修编后回流成下一幅图的训练标签。')]

# ======================================================================= 化探异常
def bell(x0, y0, w, h, mu, sd, col, op=.5):
    pts = [(x0 + t, y0 - h * math.exp(-((t / w - mu) ** 2) / (2 * sd * sd))) for t in range(0, int(w) + 1, 3)]
    return PG([(x0, y0)] + pts + [(x0 + w, y0)], col, op) + PL(pts, col, 1.4)
def f_anomaly():
    def a1(x, w):
        s = bell(x + 14, 96, w - 28, 54, .38, .12, BLUE) + bell(x + 14, 96, w - 28, 54, .62, .12, CLAY)
        s += L(x + 14, 96, x + w - 14, 96, MUTE, 1)
        return s + T(x + 14, 30, '校正前：两个批次整体错开', MUTE, 9) + T(x + 14, 114, '蓝 批次一  橙 批次二', MUTE, 9) + T(x + 14, 130, '季节差会被当成异常', RED, 9.5)
    def a2(x, w):
        s = bell(x + 14, 96, w - 28, 54, .5, .12, BLUE) + bell(x + 14, 96, w - 28, 50, .5, .125, CLAY, .35)
        s += L(x + 14, 96, x + w - 14, 96, MUTE, 1)
        return s + T(x + 14, 30, '校正后：两批可比', MUTE, 9) + T(x + 14, 114, '对数变换 + 批次校正', JADE, 9.5)
    f1 = two(a2, a1, '做法', '常见问题', '批次与季节偏差校正')
    def b1(x, w):
        s = R(x + 12, 28, w - 24, 90, '#f2f2f2', rx=2)
        s += '<ellipse cx="%.1f" cy="60" rx="26" ry="18" fill="%s" opacity=".18"/>' % (x + 46, JADE) + T(x + 46, 88, '已知油气区', JADE, 8.5, 'middle')
        s += L(x + 12, 104, x + w - 12, 96, '#bdbdbd', 6) + T(x + 16, 118, '公路', MUTE, 8.5)
        r = rr(5)
        for _ in range(16):
            px, py = x + 90 + r.random() * 58, 34 + r.random() * 50
            s += C(px, py, 3, BLUE)
        s += R(x + 86, 30, 66, 58, 'none', BLUE, 3, dash=True) + T(x + 119, 116, '背景区', BLUE, 9, 'middle')
        return s + T(x + 12, 134, '远离油气区与污染源', MUTE, 9)
    def b2(x, w):
        s = L(x + 14, 100, x + w - 14, 100, MUTE, 1) + bell(x + 14, 100, w - 28, 50, .4, .12, BLUE)
        s += L(x + 14 + .64 * (w - 28), 40, x + 14 + .64 * (w - 28), 100, JADE, 1.4, True)
        s += L(x + 14 + .82 * (w - 28), 40, x + 14 + .82 * (w - 28), 100, RED, 1.6)
        s += T(x + 14 + .64 * (w - 28), 36, '应有阈值', JADE, 8.5, 'middle') + T(x + 14 + .86 * (w - 28), 52, '被抬高', RED, 8.5, 'start')
        return s + T(x + 14, 120, '背景里混进异常点', RED, 9.5)
    f2 = two(b1, b2, label='背景建模')
    def c1(x, w):
        s = L(x + 20, 112, x + w - 12, 112, MUTE, 1) + L(x + 20, 112, x + 20, 28, MUTE, 1)
        s += '<ellipse cx="%.1f" cy="88" rx="30" ry="16" fill="%s" opacity=".15"/>' % (x + 58, BLUE)
        r = rr(2)
        for _ in range(16): s += C(x + 36 + r.random() * 44, 78 + r.random() * 20, 2.4, BLUE, op=.7)
        s += C(x + 132, 40, 4.5, JADE) + T(x + 126, 34, '两项都高 · 最高分', JADE, 8.5, 'end')
        s += C(x + 132, 90, 4, CLAY) + T(x + 126, 104, '单项高', CLAY, 8.5, 'end')
        return s + T(x + 24, 126, '指标 A →', MUTE, 8.5) + T(x + 24, 138, '按偏离背景的距离打分', MUTE, 9)
    def c2(x, w):
        s = L(x + 20, 112, x + w - 12, 112, MUTE, 1) + L(x + 20, 112, x + 20, 28, MUTE, 1)
        r = rr(3)
        for _ in range(16): s += C(x + 24 + r.random() * 120, 96 + r.random() * 12, 2.4, BLUE, op=.7)
        s += T(x + 24, 40, '纵轴 0—1，横轴 0—1000', RED, 9) + T(x + 24, 56, '不统一量纲 →', INK, 9)
        return s + T(x + 24, 72, '大数值指标主导距离', RED, 9.5)
    f3 = two(c1, c2, label='多指标异常打分')
    def d1(x, w):
        s = R(x + 12, 28, w - 24, 90, '#f2f2f2', rx=2) + L(x + 12, 104, x + w - 12, 96, '#bdbdbd', 6)
        s += '<ellipse cx="%.1f" cy="56" rx="34" ry="18" fill="%s" opacity=".18" stroke="%s"/>' % (x + 60, JADE, JADE)
        r = rr(6)
        for _ in range(7): s += C(x + 44 + r.random() * 32, 48 + r.random() * 16, 3, JADE)
        s += C(x + 126, 98, 3.4, CLAY) + T(x + 126, 90, '降权', CLAY, 8.5, 'middle')
        return s + T(x + 12, 134, '连片高分 → 靶区', MUTE, 9)
    def d2(x, w):
        s = R(x + 12, 28, w - 24, 90, '#f2f2f2', rx=2) + '<ellipse cx="%.1f" cy="72" rx="64" ry="38" fill="%s" opacity=".12" stroke="%s"/>' % (x + 82, RED, RED)
        for px, py in [(42, 52), (72, 92), (120, 60), (100, 46)]: s += C(x + px, py, 3, CLAY)
        return s + T(x + 12, 134, '半径过大：无关点连成大靶区', RED, 9.5)
    f4 = two(d1, d2, label='空间聚类与污染剔除')
    def e(x, w):
        s = ''; rows = [('靶区 1', .92, '微渗漏', JADE), ('靶区 2', .86, '公路污染', RED), ('靶区 3', .8, '微渗漏', JADE), ('靶区 4', .7, '待定', MUTE)]
        for i, (n, v, cause, col) in enumerate(rows):
            y = 32 + i * 22
            s += T(x + 14, y + 11, n, INK, 9.5) + R(x + 60, y + 2, v * 130, 12, col, rx=2, op=.8) + T(x + 196, y + 12, cause, col, 9.5)
        s += ARW(x + 262, 120, x + 262, 40, JADE) + T(x + 268, 82, '钻探', JADE, 9) + T(x + 268, 96, '回流', JADE, 9)
        return s + T(x + 14, 138, '不看成因只看得分，污染会排在前面', MUTE, 9)
    f5 = one(e, '排序', '专家解释成因并排序')
    return [(f1, '左：对数变换和批次校正后两批数据可以比较；右：不校正时，季节差会被当成异常。'),
            (f2, '背景区要远离已知油气区和污染源；背景里混进异常点，阈值会被整体抬高。'),
            (f3, '多项指标同时偏离背景的点得分最高；量纲不统一时，数值大的指标会主导距离。'),
            (f4, '高分点按空间位置聚成靶区，路边孤立点降权；聚类半径过大会把无关点连成一片。'),
            (f5, '专家结合地质、物探资料判断成因后排序，钻探结果再回流校准。')]

# ======================================================================= 图件要素
def sym_well(x, y, col=INK): return L(x - 6, y, x + 6, y, col, 2) + L(x, y - 6, x, y + 6, col, 2)
def sym_ring(x, y, col=INK): return C(x, y, 5.5, 'none', col)
def f_symbol():
    def a(x, w):
        s = ''
        for i, (yr, col) in enumerate([('1985 版图例', CLAY), ('2005 版图例', BLUE)]):
            x0 = x + 14 + i * 84
            s += R(x0, 30, 74, 58, '#f4efe1', '#d8cdb0', 2) + sym_ring(x0 + 22, 52) + sym_well(x0 + 50, 66)
            s += T(x0 + 37, 102, yr, col, 9, 'middle', True)
        s += ARW(x + 186, 60, x + 206, 60)
        s += R(x + 212, 30, 112, 58, '#ffffff', LINE, 2)
        for k in range(5): s += L(x + 212, 30 + k * 14.5, x + 324, 30 + k * 14.5, LINE, 1) + L(x + 212 + k * 28, 30, x + 212 + k * 28, 88, LINE, 1)
        s += T(x + 268, 102, '配准到地理坐标', JADE, 9, 'middle', True)
        return s + T(x + 14, 126, '每幅图先标明所用图例体系，再纠偏、配准', MUTE, 9)
    f1 = one(a, '做法', '扫描整理与配准')
    def b(x, w):
        s = ''; heads = ['符号', '语义', '属性字段']; xs = [14, 70, 150]
        s += R(x + 14, 28, 300, 18, '#eeeeee', rx=2)
        for hx, ht in zip(xs, heads): s += T(x + hx + 6, 41, ht, INK, 9.5, bold=True)
        rows = [(sym_ring, '1985 · 探井', 'well_type = 探井'), (sym_ring, '2005 · 采样点', 'sample_id'), (sym_well, '生产井', 'well_type = 生产井')]
        for i, (fn, sem, fld) in enumerate(rows):
            y = 60 + i * 22
            s += fn(x + 32, y) + T(x + 76, y + 4, sem, INK, 9.5) + T(x + 156, y + 4, fld, MUTE, 9)
            s += L(x + 14, y + 11, x + 314, y + 11, LINE, 1)
        return s + T(x + 14, 138, '同一个“○”在两套图例里含义不同，对照表把它们分开', CLAY, 9)
    f2 = one(b, '对照表', '图例对照表')
    def c1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f4efe1', rx=2)
        for (px, py, t, conf) in [(40, 52, 'w', .97), (112, 58, 'r', .91), (70, 92, 'w', .62)]:
            s += (sym_well if t == 'w' else sym_ring)(x + px, py)
            col = JADE if conf > .8 else CLAY
            s += R(x + px - 11, py - 11, 22, 22, 'none', col, 2, sw=1.4) + T(x + px + 14, py - 6, '%.2f' % conf, col, 8.5)
        return s + T(x + 12, 128, '定位 + 识别 + 置信度', MUTE, 9.5)
    def c2(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f4efe1', rx=2)
        for px, py in [(64, 60), (74, 66), (70, 76)]: s += sym_well(x + px, py)
        s += R(x + 50, 46, 40, 44, 'none', RED, 2, sw=1.6) + T(x + 98, 64, '3 口井', RED, 9) + T(x + 98, 78, '只剩', RED, 9) + T(x + 98, 92, '1 个框', RED, 9)
        return s + T(x + 12, 128, '密集区相互压盖', MUTE, 9.5)
    f3 = two(c1, c2, label='符号检测与识别')
    def d1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f4efe1', rx=2)
        s += L(x + 30, 36, x + 66, 70, RED, 2.4) + L(x + 76, 80, x + 110, 106, RED, 2.4)
        s += L(x + 66, 70, x + 76, 80, JADE, 2.4, True) + C(x + 71, 75, 9, 'none', JADE)
        return s + T(x + 12, 128, '按方向与距离接上断开处', MUTE, 9.5)
    def d2(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f4efe1', rx=2)
        for k in range(3): s += '<path d="M%.1f %.1f C%.1f %.1f,%.1f %.1f,%.1f %.1f" fill="none" stroke="#c5876a" stroke-width="1.3"/>' % (x + 14, 48 + k * 22, x + 60, 36 + k * 22, x + 100, 66 + k * 22, x + w - 14, 50 + k * 22)
        s += L(x + 40, 32, x + 70, 106, RED, 2.2)
        s += C(x + 52, 62, 6, 'none', RED)
        return s + T(x + 12, 128, '颜色相近的等高线被连上', RED, 9.5)
    f4 = two(d1, d2, label='线追踪与拓扑修复')
    def e(x, w):
        s = ''; vals = [.98, .95, .93, .9, .86, .74, .61, .55]
        for i, v in enumerate(vals):
            y = 28 + i * 12.5
            col = JADE if v >= .8 else CLAY
            s += R(x + 14, y, v * 160, 9, col, rx=2, op=.8) + T(x + 180, y + 8, '%.2f' % v, col, 8.5)
        s += L(x + 14 + .8 * 160, 24, x + 14 + .8 * 160, 130, INK, 1, True) + T(x + 14 + .8 * 160, 138, '0.80', INK, 8.5, 'middle')
        s += T(x + 216, 50, '≥ 0.80 自动入库', JADE, 9.5) + T(x + 216, 100, '< 0.80 逐条核对', CLAY, 9.5)
        s += T(x + 216, 116, '核对结果回流', CLAY, 9)
        return s
    f5 = one(e, '分流', '按置信度分流人工核对')
    return [(f1, '先按年代标明每幅图所用的图例体系，再纠偏、配准到地理坐标。'),
            (f2, '“符号 → 语义 → 属性字段”对照表；同一个符号在不同图例里含义不同。'),
            (f3, '每个要素都有位置、类别和置信度；符号密集时检测框会合并，导致漏检。'),
            (f4, '断开的断层线按方向和距离接上；颜色相近的等高线可能被错连。'),
            (f5, '高置信度要素自动入库，低于阈值的逐条核对，核对结果回流为训练样本。')]

# ======================================================================= 露头裂缝
def crack_field(x, y, w, h, seed, n=9, sets=True):
    r = rr(seed); s = ''
    for i in range(n):
        x0, y0 = x + 8 + r.random() * (w - 30), y + 8 + r.random() * (h - 26)
        a = math.radians(62 if (i % 3) else 150) + r.uniform(-.12, .12); Ln = 18 + r.random() * 16
        col = (JADE if i % 3 else CLAY) if sets else '#3d3424'
        s += L(x0, y0, x0 + Ln * math.cos(a), y0 + Ln * math.sin(a), col, 1.8)
    return s
def f_fracture():
    def a(x, w):
        s = R(x + 14, 28, 150, 92, '#d8ccad', rx=2) + crack_field(x + 14, 28, 150, 92, 3, sets=False)
        s += R(x + 120, 92, 30, 20, '#ffffff', INK, 1) + L(x + 120, 102, x + 150, 102, INK, 1) + L(x + 135, 92, x + 135, 112, INK, 1)
        s += T(x + 135, 126, '标定板', INK, 9, 'middle')
        s += R(x + 190, 34, 20, 14, MUTE, rx=2) + C(x + 200, 41, 3.5, '#ffffff') + T(x + 216, 45, '多角度拍照', INK, 9.5)
        s += L(x + 196, 70, x + 214, 66, MUTE, 2) + L(x + 196, 66, x + 214, 70, MUTE, 2) + T(x + 222, 72, '无人机补拍陡壁', INK, 9.5)
        s += T(x + 190, 100, '像素 → 厘米 · 真实方向', JADE, 9.5, bold=True)
        return s + T(x + 190, 118, '没有标定 = 只有图像方向', RED, 9)
    f1 = one(a, '做法', '拍摄与标定')
    def b1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#d8ccad', rx=2) + crack_field(x + 12, 28, w - 24, 84, 5)
        return s + T(x + 12, 126, '绿 一期  橙 二期', MUTE, 9) + T(x + 12, 140, '按充填物与切割关系分期', MUTE, 9)
    def b2(x, w):
        s = R(x + 12, 28, w - 24, 84, '#d8ccad', rx=2)
        for k in range(4): s += L(x + 12, 40 + k * 20, x + w - 12, 44 + k * 20, '#8a7f62', 1.4)
        s += L(x + 12, 60, x + w - 12, 64, RED, 2.2) + T(x + w - 16, 56, '层理面', RED, 9, 'end')
        return s + T(x + 12, 126, '层理面被当成裂缝标注', RED, 9.5)
    f2 = two(b1, b2, label='标注与分组规则')
    def c1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#d8ccad', rx=2)
        for (x0, y0, x1, y1, conf) in [(30, 40, 60, 96, .94), (80, 36, 104, 84, .88), (112, 60, 140, 104, .57)]:
            col = JADE if conf > .8 else CLAY
            s += L(x + x0, y0, x + x1, y1, col, 6, op=.35) + L(x + x0, y0, x + x1, y1, '#3d3424', 1.6) + T(x + x1 + 2, y1 - 2, '%.2f' % conf, col, 8.5)
        return s + T(x + 12, 128, '逐条掩膜 + 置信度', MUTE, 9.5)
    def c2(x, w):
        s = R(x + 12, 28, w - 24, 84, '#d8ccad', rx=2) + PG([(x + 70, 28), (x + 120, 28), (x + 96, 112), (x + 60, 112)], '#9e8f6b', .6)
        s += '<path d="M%.1f 40 C%.1f 60,%.1f 80,%.1f 108" stroke="#5f7a4a" stroke-width="1.6" fill="none"/>' % (x + 30, x + 40, x + 26, x + 38)
        s += R(x + 62, 30, 56, 80, 'none', RED, 2, sw=1.4) + R(x + 20, 36, 28, 76, 'none', RED, 2, sw=1.4)
        return s + T(x + 12, 128, '阴影、根系被误判为裂缝', RED, 9.5)
    f3 = two(c1, c2, label='裂缝实例分割')
    def d1(x, w):
        s = L(x + 24, 40, x + 72, 104, JADE, 8, op=.3) + L(x + 24, 40, x + 72, 104, INK, 1.6) + ARW(x + 84, 72, x + 98, 72)
        cx, cy = x + 128, 72; s += C(cx, cy, 24, 'none', MUTE)
        a = math.radians(37 - 90); s += L(cx - 24 * math.cos(a), cy - 24 * math.sin(a), cx + 24 * math.cos(a), cy + 24 * math.sin(a), JADE, 2.4)
        s += T(cx, 44, 'N', MUTE, 8.5, 'middle')
        return s + T(x + 14, 124, '掩膜 → 骨架 → 走向倾角', MUTE, 9.5)
    def d2(x, w):
        cx, cy = x + 80, 70; s = C(cx, cy, 30, 'none', MUTE) + T(cx, 36, 'N', MUTE, 8.5, 'middle')
        for ang, col, dash in [(37, JADE, False), (52, RED, True)]:
            a = math.radians(ang - 90); s += L(cx - 30 * math.cos(a), cy - 30 * math.sin(a), cx + 30 * math.cos(a), cy + 30 * math.sin(a), col, 2.2, dash)
        return s + T(x + 14, 118, '斜拍不纠正：走向整体偏转', RED, 9.5) + T(x + 14, 134, '绿 真实  红 未纠正', MUTE, 9)
    f4 = two(d1, d2, label='骨架化与产状反算')
    def e1(x, w):
        cx, cy = x + 60, 76; s = C(cx, cy, 40, 'none', LINE)
        for ang, ln in [(30, 38), (40, 32), (50, 22), (140, 26), (150, 30)]:
            a1, a2 = math.radians(ang - 5 - 90), math.radians(ang + 5 - 90)
            s += PG([(cx, cy), (cx + ln * math.cos(a1), cy + ln * math.sin(a1)), (cx + ln * math.cos(a2), cy + ln * math.sin(a2))], JADE, .6)
        s += CHK(x + 120, 60) + T(x + 108, 80, '罗盘', MUTE, 9) + T(x + 108, 94, '抽查', MUTE, 9)
        return s + T(x + 12, 134, '玫瑰图 + 线密度', MUTE, 9.5)
    def e2(x, w):
        s = T(x + 14, 34, '按条数统计', INK, 9.5, bold=True)
        s += T(x + 14, 50, '短裂隙', MUTE, 9) + R(x + 54, 42, 92, 10, RED, rx=2, op=.85) + T(x + 14, 64, '长裂缝', MUTE, 9) + R(x + 54, 56, 28, 10, GRAY, rx=2)
        s += T(x + 14, 84, '按长度加权', INK, 9.5, bold=True)
        s += T(x + 14, 100, '短裂隙', MUTE, 9) + R(x + 54, 92, 28, 10, GRAY, rx=2) + T(x + 14, 114, '长裂缝', MUTE, 9) + R(x + 54, 106, 92, 10, JADE, rx=2, op=.85)
        return s + T(x + 14, 134, '只数条数：风化短裂隙主导结果', RED, 9)
    f5 = two(e1, e2, label='统计与罗盘抽查')
    return [(f1, '每个露头放标定板、多角度拍照，陡壁用无人机补拍，像素才能换算成真实长度和方向。'),
            (f2, '先定分期规则再标注；层理面、岩性界面不能当成裂缝。'),
            (f3, '逐条输出裂缝掩膜和置信度；阴影、植物根系是最常见的误判。'),
            (f4, '掩膜提骨架后反算走向和倾角；斜拍照片不做几何纠正，走向会整体偏转。'),
            (f5, '输出玫瑰图和线密度，用罗盘实测抽查；统计时要按长度加权，不能只数条数。')]

# ======================================================================= 地震相
FACIES = [SAND, MOSS, '#b9c7d3', '#e4c6a8', '#c9d9bf']
def f_facies():
    def a1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f2f2f2', rx=2) + reflectors(x + 12, 28, w - 24, 84, 6, seed=1, sw=1.1)
        s += PL([(x + 12 + t, 52 + 4 * math.sin(t / 26)) for t in range(0, int(w - 23), 4)], JADE, 2.4)
        s += PL([(x + 12 + t, 88 + 4 * math.sin(t / 26)) for t in range(0, int(w - 23), 4)], JADE, 2.4)
        return s + T(x + 12, 126, '顶底层位之间沿层切片', MUTE, 9.5)
    def a2(x, w):
        s = R(x + 12, 28, w - 24, 84, '#f2f2f2', rx=2) + reflectors(x + 12, 28, w - 24, 84, 6, seed=1, sw=1.1)
        s += PL([(x + 12, 50), (x + w - 12, 96)], RED, 2.4)
        return s + T(x + 12, 126, '层位穿时：混进不同层段', RED, 9.5)
    f1 = two(a1, a2, label='层位与沿层切片')
    def b(x, w):
        s = ''; names = ['河道', '分流间湾', '前缘砂', '前三角洲', '湖相泥']
        for i, (n, col) in enumerate(zip(names, FACIES)): s += R(x + 14 + i * 60, 30, 52, 22, col, rx=2) + T(x + 40 + i * 60, 68, n, INK, 9, 'middle')
        s += R(x + 14, 80, 300, 40, '#e8ede4', rx=2)
        r = rr(11)
        for i in range(12):
            px = x + 26 + i * 24 + r.uniform(-4, 4); py = 92 + r.uniform(0, 16)
            s += C(px, py, 4.2, INK) if i not in (2, 5, 9) else C(px, py, 4.2, '#ffffff', CLAY)
        return s + T(x + 14, 138, '● 训练井   ○ 盲井（预先留出，不参与训练）', MUTE, 9)
    f2 = one(b, '做法', '定义相带类别并留出盲井')
    def c1(x, w):
        s = ''; r = rr(2); cents = [(46, 52), (110, 48), (78, 96)]
        for k, (cx, cy) in enumerate(cents):
            for _ in range(14): s += C(x + cx + r.gauss(0, 8), cy + r.gauss(0, 7), 2.4, FACIES[k] if k else '#c7b27a')
        s += T(x + 46, 34, '簇 1', MUTE, 8.5, 'middle') + T(x + 110, 30, '簇 2', MUTE, 8.5, 'middle') + T(x + 78, 122, '簇 3', MUTE, 8.5, 'middle')
        return s + T(x + 14, 138, '数据先自然分组', MUTE, 9)
    def c2(x, w):
        s = T(x + 14, 44, '簇 2', INK, 10, bold=True) + ARW(x + 50, 40, x + 86, 40, RED) + T(x + 92, 44, '= 相带 2 ?', RED, 10, bold=True)
        s += T(x + 14, 74, '聚类编号没有地质含义', RED, 9.5) + T(x + 14, 92, '要用井点和沉积模式', MUTE, 9) + T(x + 14, 106, '标定后才能叫“相带”', MUTE, 9)
        return s
    f3 = two(c1, c2, label='聚类与分类')
    def d1(x, w):
        s = ''; r = rr(8)
        for i in range(9):
            for j in range(6):
                k = 0 if i + j * .4 < 4 else (1 if i < 7 else 2)
                if r.random() < .14: k = r.randrange(3)
                s += R(x + 12 + i * 7.5, 32 + j * 12, 7, 11, FACIES[k], rx=0)
        s += ARW(x + 84, 66, x + 96, 66)
        for i in range(9):
            for j in range(6):
                k = 0 if i + j * .4 < 4 else (1 if i < 7 else 2)
                s += R(x + 100 + i * 6, 32 + j * 12, 5.6, 11, FACIES[k], rx=0)
        return s + T(x + 12, 122, '井点赋义 + 去碎斑', MUTE, 9.5)
    def d2(x, w):
        s = R(x + 14, 32, w - 28, 66, '#e8ede4', rx=2) + C(x + 50, 64, 5, INK) + T(x + 60, 68, '唯一一口井', INK, 9)
        return s + T(x + 14, 116, '1—2 口井标定一整类', RED, 9.5) + T(x + 14, 132, '换一口井结论就变', MUTE, 9)
    f4 = two(d1, d2, label='井点标定与边界平滑')
    def e(x, w):
        s = R(x + 14, 28, 170, 92, '#e8ede4', rx=2)
        for i, (px, py) in enumerate([(34, 46), (78, 40), (126, 50), (166, 42), (52, 82), (100, 92), (146, 86), (70, 108)]):
            px += x; ok = i not in (3, 6)
            s += C(px, py, 6, '#ffffff', JADE if ok else RED) + CHK(px, py, ok)
        s += T(x + 202, 52, '8 口盲井', INK, 10.5, bold=True) + T(x + 202, 72, '6 口符合 · 75%', JADE, 9.5)
        s += T(x + 202, 90, '不符的回看相带定义', RED, 9) + T(x + 202, 112, '训练井不能算符合率', MUTE, 9)
        return s
    f5 = one(e, '验证', '盲井验证')
    return [(f1, '在顶、底层位之间沿层取切片；层位穿时，一张切片会混进不同层段的反射。'),
            (f2, '先定义 5 类相带和典型剖面，并预先留出盲井，盲井不参与任何训练。'),
            (f3, '无监督聚类先看数据自然分成几组；聚类编号本身没有地质含义。'),
            (f4, '用井点给每一类赋予地质含义并去除碎斑；只靠一两口井标定，偶然性很大。'),
            (f5, '只在盲井上统计相带符合率；不符的井要回头检查相带定义和标定。')]

# ======================================================================= 初至
def f_firstbreak():
    def a(x, w):
        s = ''; bins = [('高信噪比', .45, .08, JADE), ('中信噪比', .35, .1, BLUE), ('低信噪比', .2, .18, CLAY)]
        for i, (n, share, lab, col) in enumerate(bins):
            y = 34 + i * 30
            s += T(x + 14, y + 12, n, INK, 9.5) + R(x + 80, y, share * 280, 16, col, rx=2, op=.25) + R(x + 80, y, lab * 280, 16, col, rx=2)
            s += T(x + 84 + share * 280, y + 12, '抽 %d%%' % round(lab / share * 100), col, 9)
        return s + T(x + 14, 134, '浅色 = 该档全部道   深色 = 抽出人工拾取的道（低信噪比档多抽）', MUTE, 8.5)
    f1 = one(a, '做法', '按信噪比分档抽样标注')
    def b1(x, w):
        s = ''
        for i in range(6):
            col = JADE if i < 4 else BLUE
            for k in range(7): s += L(x + 18 + i * 22 + k * 2.6, 34, x + 18 + i * 22 + k * 2.6, 104, col, 1.4)
        s += T(x + 56, 118, '训练炮', JADE, 9, 'middle') + T(x + 128, 118, '验证炮', BLUE, 9, 'middle')
        return s + T(x + 14, 136, '以炮为单位整炮划分', MUTE, 9)
    def b2(x, w):
        s = ''; r = rr(3)
        for i in range(6):
            for k in range(7):
                col = JADE if r.random() < .67 else BLUE
                s += L(x + 18 + i * 22 + k * 2.6, 34, x + 18 + i * 22 + k * 2.6, 104, col, 1.4)
        return s + T(x + 14, 118, '同一炮的道分到两边', RED, 9.5) + T(x + 14, 136, '验证误差虚低', MUTE, 9)
    f2 = two(b1, b2, label='按炮划分训练与验证')
    def c(x, w):
        s = PL(wig(x + 20, 52, 300, 120, 9, .9, 5), '#4e5d61', 1.2)
        pts = [(x + 20 + t, 118 - 48 / (1 + math.exp(-(t - 120) / 6))) for t in range(0, 300, 3)]
        s += PL(pts, BLUE, 2) + L(x + 20, 118 - 48 * .45, x + 320, 118 - 48 * .45, CLAY, 1, True)
        s += L(x + 140, 32, x + 140, 124, JADE, 1.6) + T(x + 144, 36, '概率跃变处 = 初至', JADE, 9.5)
        s += T(x + 20, 38, '波形', MUTE, 9) + T(x + 20, 132, '“已到达”概率', BLUE, 9) + T(x + 320, 98, '阈值', CLAY, 9, 'end')
        return s
    f3 = one(c, '做法', '逐采样点到达概率')
    def d(x, w):
        s = L(x + 24, 124, x + 320, 124, MUTE, 1) + L(x + 24, 124, x + 24, 28, MUTE, 1)
        s += T(x + 320, 138, '偏移距 →', MUTE, 8.5, 'end') + T(x + 28, 36, '初至时间', MUTE, 8.5)
        pts = [(x + 34 + i * 18, 112 - i * 5.2) for i in range(16)]
        s += PL(pts, JADE, 1.4, True)
        for i, (px, py) in enumerate(pts):
            if i == 9: s += C(px, py - 26, 4, RED) + ARW(px, py - 20, px, py - 5, CLAY) + C(px, py, 3.2, CLAY)
            else: s += C(px, py, 3, INK)
        s += T(x + 40, 52, '红点：离群拾取', RED, 9.5) + T(x + 40, 66, '→ 用邻道中位数回退并标记', CLAY, 9.5)
        return s
    f4 = one(d, '做法', '走时约束与回退')
    def e(x, w):
        s = ''; flags = {3, 9, 14}
        for i in range(18):
            px = x + 20 + i * 16
            col = CLAY if i in flags else JADE
            s += R(px, 40, 10, 50, col, rx=2, op=.85 if i in flags else .35)
        s += T(x + 20, 108, '绿：自动通过   橙：概率跃变不明显或被回退 → 人工复核', MUTE, 9)
        return s + T(x + 20, 128, '只看这一小部分；修正后回流为标签', JADE, 9.5)
    f5 = one(e, '分流', '低置信度复核')
    return [(f1, '每档都抽样人工拾取，低信噪比档抽得更多，标签才能覆盖最难的道。'),
            (f2, '以炮为单位划分训练和验证；随机按道划分时，同一炮的相邻道会同时出现在两边。'),
            (f3, '模型逐采样点输出“已到达”的概率，概率跃变的位置就是初至。'),
            (f4, '沿偏移距检查拾取曲线，偏离邻道中位数过多的道回退并打上标记。'),
            (f5, '只有概率跃变不明显或被回退的道进入人工复核，其余自动通过。')]

# ======================================================================= 储层参数
def f_reservoir():
    def a(x, w):
        s = L(x + 30, 28, x + 30, 124, MUTE, 1) + T(x + 26, 36, '深度', MUTE, 8.5, 'end')
        r = rr(5); pts = []; v = 60
        for k in range(0, 96, 2):
            v = v + r.gauss(0, 6); v = max(40, min(100, v)); pts.append((x + v, 28 + k))
        s += PL(pts, BLUE, 1) + T(x + 70, 136, '测井孔隙度（米级）', BLUE, 9, 'middle')
        s += ARW(x + 118, 76, x + 140, 76)
        blk = []
        for b in range(6):
            seg = pts[b * 8:(b + 1) * 8]; m = sum(p[0] for p in seg) / len(seg) + 110
            blk += [(m, 28 + b * 16), (m, 28 + (b + 1) * 16)]
        s += PL(blk, JADE, 2) + T(x + 180, 136, '平均到地震尺度', JADE, 9, 'middle')
        s += R(x + 222, 36, 96, 70, '#ffffff', LINE, 4) + T(x + 230, 56, '合成记录', INK, 9.5) + T(x + 230, 72, '校正时深关系', INK, 9.5)
        s += T(x + 230, 92, '标签与属性对齐', JADE, 9.5, bold=True)
        return s
    f1 = one(a, '做法', '井震标定与尺度平均')
    def b1(x, w):
        s = R(x + 12, 28, w - 24, 84, '#e8ede4', rx=2); r = rr(6)
        for i in range(14):
            px, py = x + 22 + r.random() * (w - 44), 36 + r.random() * 68
            s += C(px, py, 3.6, INK) if i % 3 else C(px, py, 3.6, '#ffffff', CLAY)
        return s + T(x + 12, 126, '● 训练井  ○ 盲井（6 口）', MUTE, 9)
    def b2(x, w):
        s = T(x + 14, 40, '属性 12 种', INK, 10, bold=True) + T(x + 14, 58, '井 22 口', INK, 10, bold=True)
        s += T(x + 14, 82, '属性太多、井太少', RED, 9.5) + T(x + 14, 98, '模型会记住井点', RED, 9.5)
        return s + T(x + 14, 122, '只留有物理联系的属性', MUTE, 9)
    f2 = two(b1, b2, label='属性优选与留井')
    def c1(x, w):
        s = L(x + 20, 112, x + w - 12, 112, MUTE, 1) + L(x + 20, 112, x + 20, 28, MUTE, 1)
        s += R(x + 20, 34, w - 32, 70, JADE, rx=0, op=.06)
        r = rr(3)
        for _ in range(16):
            t = r.random(); s += C(x + 26 + t * (w - 44), 100 - t * 60 + r.gauss(0, 6), 2.4, INK, op=.7)
        s += PL([(x + 26 + t, 100 - t / (w - 44) * 60) for t in range(0, int(w - 43), 4)], JADE, 2)
        return s + T(x + 24, 126, '阻抗 →', MUTE, 8.5) + T(x + 24, 140, '平滑 + 物理约束', JADE, 9)
    def c2(x, w):
        s = L(x + 20, 112, x + w - 12, 112, MUTE, 1) + L(x + 20, 112, x + 20, 28, MUTE, 1)
        r = rr(3)
        for _ in range(16):
            t = r.random(); s += C(x + 26 + t * (w - 44), 100 - t * 60 + r.gauss(0, 6), 2.4, INK, op=.7)
        s += PL([(x + 26 + t, 100 - t / (w - 44) * 60 + 14 * math.sin(t / 6)) for t in range(0, int(w - 43), 2)], RED, 1.6)
        return s + T(x + 24, 126, '只追训练误差：', RED, 9) + T(x + 24, 140, '曲线乱抖、外推越界', RED, 9)
    f3 = two(c1, c2, label='回归映射与物理约束')
    def d(x, w):
        s = R(x + 14, 28, 200, 92, '#e8ede4', rx=2) + R(x + 160, 28, 54, 92, RED, rx=0, op=.15) + T(x + 187, 76, '外推区', RED, 9.5, 'middle')
        r = rr(2)
        for i in range(9):
            px, py = x + 24 + r.random() * 120, 36 + r.random() * 76
            s += C(px, py, 3.4, INK) if i % 3 else C(px, py, 4, '#ffffff', CLAY)
        s += T(x + 230, 52, '盲井误差', INK, 10, bold=True) + T(x + 230, 68, 'RMSE ≤ 2 个百分点', JADE, 9)
        s += T(x + 230, 92, '外推区', INK, 10, bold=True) + T(x + 230, 108, '对照地质趋势', CLAY, 9)
        return s
    f4 = one(d, '检验', '盲井检验与外推检查')
    def e(x, w):
        s = ''; cx, cy = x + 166, 78
        nodes = [('孔隙度图', cx - 110, cy - 26, BLUE), ('对照相带与构造', cx + 18, cy - 26, CLAY), ('新钻井结果', cx + 18, cy + 18, JADE), ('重新训练', cx - 110, cy + 18, JADE)]
        for t, nx, ny, col in nodes: s += R(nx, ny, 92, 26, '#ffffff', col, 6, sw=1.3) + T(nx + 46, ny + 17, t, INK, 10, 'middle', True)
        s += ARW(cx - 16, cy - 13, cx + 16, cy - 13) + ARW(cx + 64, cy, cx + 64, cy + 16) + ARW(cx + 16, cy + 31, cx - 16, cy + 31) + ARW(cx - 64, cy + 16, cx - 64, cy)
        return s + T(x + 14, 138, '新井不回流，半年后模型就与实际脱节', MUTE, 9)
    f5 = one(e, '闭环', '地质审核与回流')
    return [(f1, '做合成记录校正时深关系，把米级测井孔隙度平均到地震尺度，标签才能和属性对齐。'),
            (f2, '按井留出盲井，只保留有物理意义的属性；属性多、井少时模型会记住井点。'),
            (f3, '回归曲线要平滑、受物理约束；只追求训练误差，曲线会乱抖、外推越界。'),
            (f4, '在盲井上统计误差，远离井的外推区单独对照地质趋势检查。'),
            (f5, '孔隙度图对照相带和构造审核，新钻井结果回流后重新训练。')]

# ======================================================================= 去噪
def seis_mini(x, y, w, h, noise=0, coh=0, smear=False, seed=1, residual=False):
    r = rr(seed); s = R(x, y, w, h, '#ffffff', LINE, 2)
    if residual:
        for _ in range(int(noise * 60)): s += R(x + 3 + r.random() * (w - 6), y + 3 + r.random() * (h - 6), 1.6, 1.6, '#9b9b9b', rx=0)
        if smear: s += PL([(x + 4 + t, y + h * .55 + 3 * math.sin(t / 14)) for t in range(0, int(w - 7), 3)], RED, 1.6)
        return s
    for k in range(4):
        y0 = y + 9 + k * (h - 16) / 3
        s += PL([(x + 4 + t, y0 + 2.5 * math.sin(t / 14) + r.gauss(0, noise)) for t in range(0, int(w - 7), 3)], '#4e5d61', 2.2 if smear else 1.3, op=.55 if smear else None)
    for k in range(int(coh * 4)):
        x0 = x + 6 + k * 18
        if x0 + 22 < x + w: s += L(x0, y + 3, x0 + 22, y + h - 3, CLAY, 1.3, op=.8)
    return s
def f_denoise():
    def a(x, w):
        s = seis_mini(x + 14, 34, 76, 60, seed=1) + T(x + 52, 108, '正演干净记录', INK, 9, 'middle')
        s += T(x + 100, 70, '+', INK, 16, 'middle')
        s += seis_mini(x + 112, 34, 76, 60, noise=1.6, coh=1, seed=2, residual=False) + T(x + 150, 108, '真实资料提取的噪声', INK, 9, 'middle')
        s += T(x + 198, 70, '=', INK, 16, 'middle')
        s += seis_mini(x + 210, 34, 76, 60, noise=1.2, coh=.8, seed=3) + T(x + 248, 108, '含噪 / 干净样本对', JADE, 9, 'middle', True)
        return s + T(x + 14, 132, '只用理想随机噪声合成 → 对真实面波无效', RED, 9)
    f1 = one(a, '做法', '构建训练样本对')
    def b(x, w):
        s = seis_mini(x + 14, 36, 70, 56, noise=1.2, coh=.8, seed=3) + T(x + 49, 106, '含噪', INK, 9, 'middle')
        s += ARW(x + 88, 64, x + 104, 64) + R(x + 108, 48, 60, 32, '#ffffff', BLUE, 6, sw=1.3) + T(x + 138, 68, '去噪模型', INK, 10, 'middle', True)
        s += ARW(x + 172, 64, x + 188, 64) + seis_mini(x + 192, 36, 70, 56, noise=.2, seed=4) + T(x + 227, 106, '输出', INK, 9, 'middle')
        s += T(x + 272, 58, '↔ 干净', JADE, 9.5) + T(x + 272, 74, '算误差', JADE, 9.5)
        return s + T(x + 14, 132, '监督训练后，再用部分真实资料自监督微调', MUTE, 9)
    f2 = one(b, '做法', '训练含噪到干净的映射')
    def c1(x, w):
        s = seis_mini(x + 14, 32, 60, 60, noise=1.4, coh=1, seed=5) + ARW(x + 80, 62, x + 92, 62) + seis_mini(x + 96, 32, 60, 60, noise=.2, seed=6)
        return s + T(x + 14, 110, '一次前向计算', MUTE, 9.5) + T(x + 14, 126, '小时级 → 分钟级', JADE, 9.5, True)
    def c2(x, w):
        s = R(x + 14, 32, 136, 30, CLAY, rx=2, op=.18) + T(x + 22, 51, '强噪声区：欠去噪', CLAY, 9.5)
        s += R(x + 14, 70, 136, 30, BLUE, rx=2, op=.12) + T(x + 22, 89, '弱信号区：过去噪', RED, 9.5)
        return s + T(x + 14, 122, '全区用同一个强度', RED, 9.5)
    f3 = two(c1, c2, label='批量去噪')
    def d1(x, w):
        s = seis_mini(x + 14, 32, 136, 60, noise=1, seed=7, residual=True)
        return s + T(x + 14, 108, '残差只剩随机噪声', JADE, 9.5) + T(x + 14, 124, '= 没伤到有效波', MUTE, 9)
    def d2(x, w):
        s = seis_mini(x + 14, 32, 136, 60, noise=.6, seed=8, residual=True, smear=True)
        return s + T(x + 14, 108, '残差里有连续同相轴', RED, 9.5) + T(x + 14, 124, '= 有效反射被去掉', MUTE, 9)
    f4 = two(d1, d2, '合格', '报警', '残差检查')
    def e(x, w):
        s = ''; segs = [JADE] * 3 + [CLAY] + [JADE] * 4 + [CLAY] + [JADE] * 3
        for i, col in enumerate(segs): s += R(x + 14 + i * 24, 34, 20, 30, col, rx=2, op=.8 if col == CLAY else .3)
        s += T(x + 14, 82, '橙：残差报警区段 → 调去噪强度，或回退常规方法', CLAY, 9.5)
        s += T(x + 14, 100, '绿：通过质控', JADE, 9.5)
        return s + T(x + 14, 126, '确认后的参数与成果，作为下一个工区的参考', MUTE, 9)
    f5 = one(e, '分流', '人工确认与回退')
    return [(f1, '本工区正演出干净记录，叠加从真实资料中提取的噪声，组成训练样本对。'),
            (f2, '模型学习从含噪到干净的映射，用输出和干净记录之间的误差来训练。'),
            (f3, '全工区一次前向计算即可完成去噪；强噪声区和弱信号区不能用同一个强度。'),
            (f4, '残差里只剩随机噪声说明没伤到有效波；出现连续同相轴就要报警。'),
            (f5, '报警区段由处理员调整去噪强度或回退常规方法，其余通过质控。')]

STEP_FIGS = {
    'seis-fault': f_fault(), 'geo-spectral': f_spectral(), 'geo-anomaly': f_anomaly(), 'geo-symbol': f_symbol(),
    'geo-fracture': f_fracture(), 'seis-facies': f_facies(), 'seis-firstbreak': f_firstbreak(),
    'seis-reservoir': f_reservoir(), 'seis-denoise': f_denoise(),
}
assert all(len(v) == 5 for v in STEP_FIGS.values())
