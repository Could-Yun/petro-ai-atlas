# -*- coding: utf-8 -*-
"""案例正文：按教师示范案例「测井曲线智能分层」的结构撰写。
每个案例 = 30 秒判断 + 专业场景介绍 + 四段式（当前做法与问题 / AI 能做什么 / 你需要准备什么 / 技术难度与参考方向）
         + 案例流程（具体落地情境、统计、步骤、怎么算做对了、失败模式）。
生成的 HTML 与教师 kit.js 的组件输出一致（figure / checklist / refs / dtag / meter / dtable），
因此在教师原版门户与本网站中显示效果相同。"""
import html as _h, math, random

def esc(s): return _h.escape(str(s), quote=True)
def rich(s):
    import re
    out = esc(s)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', out)
    return out
def P(*paras): return ''.join('<p>' + rich(p) + '</p>' for p in paras)
def figure(svg, no, caption): return '<div class="figure">' + svg + '</div><div class="figcap"><b>图 ' + esc(no) + '</b><span>' + rich(caption) + '</span></div>'
def dtag(d): return '<span class="dtag" data-d="' + esc(d) + '">难度 ' + esc(d) + '</span>'
def meter(d):
    lv = 1 if d == '低' else 3 if d == '高' else 2
    return '<div class="meter">' + ''.join('<i class="' + ('on' if i <= lv else '') + (' hi' if i == 3 and lv == 3 else '') + '"></i>' for i in (1, 2, 3)) + '</div>'
def checklist(items, title='数据准备清单'):
    box = '<span class="cl-box"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg></span>'
    rows = ''.join('<div class="cl-item" data-cl="%d">%s<span><span class="cl-t">%s</span><span class="cl-s">%s</span></span><span class="cl-n">%s</span></div>' % (i, box, esc(a), esc(b), esc(c)) for i, (a, b, c) in enumerate(items))
    return ('<div class="checklist"><div class="cl-head"><span>%s · %d 项</span><span class="cl-prog"><span id="cl-txt">0 / %d</span><span class="cl-bar"><i id="cl-fill"></i></span></span></div>' % (esc(title), len(items), len(items))) + rows + '</div>'
def refs(lst, href=None):
    return '<div class="refs">' + ''.join(('<a class="ref" href="%s">%s<span class="ar">↗</span></a>' % (href, esc(r))) if href else ('<span class="ref">%s</span>' % esc(r)) for r in lst) + '</div>'
def dtable(head, rows):
    return '<table class="dtable"><thead><tr>' + ''.join('<th>' + esc(h) + '</th>' for h in head) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + rich(c) + '</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'
def kicker(t): return '<p style="margin-top:18px"><span class="kicker plain" style="color:var(--ink-4)">' + esc(t) + '</span></p>'
STAGE_LINKS = {'地质勘察': 'geology', '物探': 'seismic', '钻井': 'drilling', '录井': 'mudlogging', '测井': 'welllog', '固井': 'cementing', '完井': 'completion', '射孔': 'perforation', '采油': 'production', '修井': 'workover', '增采': 'eor', '运输': 'transport', '加工': 'refining'}
def cross(names): return '<p style="margin-top:18px" class="small muted">交叉环节：' + ' · '.join('<a href="#/stage/%s" style="color:var(--jade-d);font-weight:600">%s</a>' % (STAGE_LINKS[n], esc(n)) for n in names) + '</p>'
DIFF_NOTE = '<p>难度按三档标注：<b>低</b> = 数据现成、任务边界清晰、错了代价小；<b>中</b> = 需要一个月量级的标注与清洗，效果依赖后处理规则；<b>高</b> = 标签稀缺或安全约束硬，通常要先做小范围可行性验证再立项。</p>'
CHECK_INTRO = '<p style="margin-bottom:14px">立项前先对着这张清单打勾。<b>勾不满不代表不能做</b>，但每一项空缺都会在后期变成返工。清单可点击，勾选状态只在本页有效。</p>'

def pipeline_fig(steps, split, algo_note, human_note, label):
    """与教师 figAI 相同的五步流程图：steps=[(标题, 说明),...]，split=算法负责的步数。"""
    pal = [('#e6f1ec', '#2f7d6b'), ('#f0f0f0', '#41699b'), ('#eeeeee', '#7e5a8d'), ('#f8ecdf', '#b26a39'), ('#f1f1dd', '#767a2e')]
    s = '<svg viewBox="0 0 620 132" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % esc(label)
    w, gap, x, y = 108, 17, 8, 26
    for i, (t, d) in enumerate(steps):
        bg, c = pal[i]
        s += '<rect x="%d" y="%d" width="%d" height="72" rx="8" fill="%s" stroke="%s" stroke-opacity=".28"/><rect x="%d" y="%d" width="3" height="72" rx="1.5" fill="%s"/>' % (x, y, w, bg, c, x, y, c)
        s += '<text x="%d" y="%d" font-size="11.5" font-weight="600" fill="#212837">%s</text>' % (x + 13, y + 23, esc(t))
        for k, line in enumerate(d.split(' · ')):
            s += '<text x="%d" y="%d" font-size="9" fill="#4c4c4c">%s</text>' % (x + 13, y + 43 + k * 14, esc(line))
        s += '<text x="%d" y="%d" text-anchor="end" font-size="8.5" font-family="monospace" fill="%s">0%d</text>' % (x + w - 11, y + 66, c, i + 1)
        if i < len(steps) - 1:
            s += '<path d="M%d %dh9m-3.5-3.4 3.6 3.4-3.6 3.4" stroke="#c9c2b0" stroke-width="1.2" fill="none" stroke-linecap="round"/>' % (x + w + 3, y + 36)
        x += w + gap
    ae = 8 + split * w + (split - 1) * gap
    hs = 8 + split * (w + gap)
    s += '<text x="8" y="16" font-size="9.5" font-family="monospace" fill="#505050" letter-spacing="1">ALGORITHM</text>'
    s += '<text x="%d" y="16" font-size="9.5" font-family="monospace" fill="#b26a39" letter-spacing="1">HUMAN CORE</text>' % hs
    s += '<line x1="8" y1="112" x2="%d" y2="112" stroke="#2f7d6b" stroke-width="1.4"/><text x="%d" y="126" text-anchor="middle" font-size="9.5" fill="#2f7d6b">%s</text>' % (ae, (8 + ae) / 2, esc(algo_note))
    he = 8 + 5 * w + 4 * gap
    s += '<line x1="%d" y1="112" x2="%d" y2="112" stroke="#b26a39" stroke-width="1.4"/><text x="%d" y="126" text-anchor="middle" font-size="9.5" fill="#b26a39">%s</text>' % (hs, he, (hs + he) / 2, esc(human_note))
    return s + '</svg>'

# ---------------------------------------------------------------- 地震断层自动解释
def fault_manual_fig():
    """剖面：解释员 A/B 断面不一致、深层小断层漏解释；平面：抽线解释漏掉线间短断层。"""
    rnd = random.Random(11)
    s = '<svg viewBox="0 0 620 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="人工断层解释的典型问题">'
    x0, x1, yT, yB = 40, 380, 34, 270
    fx = lambda y: 205 + (y - yT) * 0.22          # 真实断面
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#fdfcf9" stroke="#e9e4d8"/>' % (x0, yT, x1 - x0, yB - yT)
    s += '<rect x="%d" y="208" width="%d" height="%d" fill="#eeeeee"/>' % (x0, x1 - x0, yB - 208)
    s += '<text x="%d" y="204" font-size="9" fill="#505050" text-anchor="end">深层 · 信噪比低</text>' % (x1 - 6)
    for k in range(11):
        y0 = yT + 14 + k * 21
        for side in (0, 1):
            pts = []
            for x in range(x0 + 2, x1 - 1, 3):
                fy = fx(y0)
                if (x < fy) != (side == 0): continue
                dy = 14 if side == 1 else 0
                small = 5 if (side == 0 and 90 < x < 205 and y0 > 200 and x > 112 + (y0 - 200) * 0.3) else 0
                yy = y0 + dy + small + 3 * math.sin(x / 38) + (rnd.uniform(-2.2, 2.2) if y0 > 200 else 0)
                if yT + 2 < yy < yB - 2: pts.append('%.1f,%.1f' % (x, yy))
            if len(pts) > 1:
                s += '<polyline points="%s" fill="none" stroke="#565656" stroke-width="1.5" opacity=".75"/>' % ' '.join(pts)
    # 真实断面
    s += '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#2f7d6b" stroke-width="1.6" stroke-dasharray="5 3"/>' % (fx(yT), yT, fx(yB), yB)
    # 解释员 A / B
    s += '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#b26a39" stroke-width="1.8"/>' % (fx(yT) - 10, yT + 4, fx(yB) - 3, yB - 4)
    s += '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#41699b" stroke-width="1.8" stroke-dasharray="7 4"/>' % (fx(yT) + 12, yT + 4, fx(yB) + 16, yB - 4)
    s += '<text x="%.1f" y="%d" font-size="9.5" fill="#b26a39" text-anchor="end">解释员 A</text>' % (fx(yT) - 14, yT + 16)
    s += '<text x="%.1f" y="%d" font-size="9.5" fill="#41699b">解释员 B</text>' % (fx(yT) + 18, yT + 16)
    s += '<text x="%.1f" y="%d" font-size="9.5" fill="#2f7d6b">真实断面</text>' % (fx(150) + 8, 150)
    # 深层小断层漏解释
    s += '<rect x="100" y="206" width="56" height="60" rx="3" fill="#f2d98a" opacity=".45"/>'
    s += '<line x1="112" y1="200" x2="132" y2="266" stroke="#2f7d6b" stroke-width="1.2" stroke-dasharray="3 3"/>'
    s += '<rect x="64" y="186" width="128" height="15" rx="3" fill="#fdfcf9" opacity=".92"/><text x="128" y="197" font-size="10" fill="#b26a39" text-anchor="middle">深层小断层 · 漏解释</text>'
    s += '<text x="%d" y="22" font-size="9.5" font-family="monospace" fill="#505050" letter-spacing="1">剖面 INLINE 1240</text>' % x0
    # 平面：抽线解释
    px, py, pw, ph = 420, 34, 170, 236
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#fdfcf9" stroke="#e9e4d8"/>' % (px, py, pw, ph)
    for k in range(7):
        xx = px + 14 + k * 24
        s += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#c9c2b0" stroke-width="1"/>' % (xx, py + 4, xx, py + ph - 4)
    s += '<path d="M%d %d C%d %d,%d %d,%d %d" fill="none" stroke="#2f7d6b" stroke-width="2.2"/>' % (px + 8, py + 40, px + 70, py + 70, px + 110, py + 100, px + pw - 8, py + 150)
    for k in range(7):
        xx = px + 14 + k * 24
        t = (xx - px - 8) / (pw - 16)
        yy = py + 40 + t * 110 + 6 * math.sin(t * 3)
        s += '<circle cx="%d" cy="%.1f" r="3" fill="#2f7d6b"/>' % (xx, yy)
    s += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#b26a39" stroke-width="2.4"/>' % (px + 42, py + 175, px + 56, py + 205)
    s += '<text x="%d" y="%d" font-size="9.5" fill="#b26a39" text-anchor="middle">线间短断层 · 漏掉</text>' % (px + pw / 2, py + ph - 10)
    s += '<text x="%d" y="22" font-size="9.5" font-family="monospace" fill="#505050" letter-spacing="1">平面 · 每 8 条线解释一次</text>' % px
    return s + '</svg>'

def fault_tolerance_fig():
    s = '<svg viewBox="0 0 620 186" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="断层容差匹配示意">'
    cols = [(8, 'TP · 命中', '#2f7d6b', '#e6f1ec', 0, '预测落在 ±2 道容差带内'), (214, 'FP · 误报', '#b26a39', '#f8ecdf', 34, '容差带外：不整合面、河道边缘'), (420, 'FN · 漏检', '#b05a51', '#efefef', None, '真实断层没有被检出')]
    for x, tag, c, bg, off, note in cols:
        w, yT, yH = 192, 34, 108
        s += '<rect x="%d" y="10" width="%d" height="%d" rx="9" fill="#fdfcf9" stroke="#e9e4d8"/>' % (x, w, yH + 42)
        s += '<text x="%d" y="26" font-size="9.5" font-family="monospace" fill="%s" letter-spacing=".8">%s</text>' % (x + 12, c, tag)
        ax = x + 60
        s += '<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s"/>' % (ax - 11, yT, ax + 11, yT, ax + 41, yT + yH, ax + 19, yT + yH, bg)
        s += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#2f7d6b" stroke-width="1.3" stroke-dasharray="4 3"/>' % (ax, yT, ax + 30, yT + yH)
        s += '<text x="%d" y="%d" font-size="8" font-family="monospace" fill="#2f7d6b">真</text>' % (ax - 22, yT + 10)
        if off is not None:
            s += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.4"/>' % (ax + 3 + off, yT + 6, ax + 30 + off, yT + yH - 4, c)
            s += '<text x="%d" y="%d" font-size="8" font-family="monospace" fill="%s">测</text>' % (ax + 36 + off, yT + 14, c)
        s += '<text x="%d" y="%d" font-size="9.5" fill="#454545">%s</text>' % (x + 12, yT + yH + 26, esc(note))
    return s + '</svg>'

CONTENT = {}
CONTENT['seis-fault'] = {
 'judge': [
  {'label': '任务类型', 'value': '三维语义分割', 'desc': '逐体素判断"是不是断层"，再连成断面'},
  {'label': '数据门槛', 'value': '5—10 个工区', 'desc': '每工区 ≥ 100 条人工解释剖面'},
  {'label': '收益', 'value': '3 周 → 5 天', 'desc': '200 km² 数据体一轮解释（含人工质检）'},
  {'label': '难度', 'value': '高', 'desc': '断层像素不足 1%，跨工区迁移难'}],
 'lede': '三维地震数据体是构造解释的底图。断层决定圈闭是否封闭、井打在断块的哪一侧、注采井之间是否连通——**漏掉一条小断层，后面的井位与开发方案都可能整体偏移**。',
 'sections': [
  {'en': 'PROBLEM', 'title': '当前做法与问题', 'html': P(
     '解释员在工作站上每隔 5—10 条 inline 剖面手工追踪一次断层，再在时间切片上把各剖面的断点组合成断面。一个 200 km² 的数据体，全人工解释需要 2—4 周。',
     '问题集中在三处：**深层信噪比低，小断层容易漏**；**断层组合有分歧**——同一组错断，有人连成一条大断层，有人拆成两条；**抽线解释**会漏掉夹在两条解释线之间的短断层。还有一个容易被忽略的事实：断层像素在数据体里通常不到 1%，这决定了后面的评价方式——**不能看"像素准确率"，只能看断层是否落在容差内、有没有整条漏掉**。') +
     figure(fault_manual_fig(), 1, '左：同一条断层，两位解释员给出的断面位置不同，深层低信噪比区的小断层没有被解释；右：每 8 条线解释一次时，两条解释线之间的短断层直接被漏掉。这些是"抽线追踪 + 经验判断"的固有代价，也是算法要替代的部分。')},
  {'en': 'INTERVENTION', 'title': 'AI 能做什么', 'html': P(
     '把断层识别建模成**三维语义分割**：先用相干、曲率等属性把"不连续"增强出来，再用 3D U-Net 之类的分割网络对每个体素输出断层概率，最后经阈值和骨架化，把概率体变成一张张可编辑的断面。',
     '注意这里替换的是**工序中的一步**——"逐线追踪断层"，不是整个构造解释。算法负责把数十 GB 的数据体压缩成几十个候选断面，并且不再抽线、每一条 inline 都被扫描；断层组合、断距合理性以及与井断点的对比，仍然由解释员负责。',
     '本案例的可运行示范是这一步的**二维简化版**：在合成剖面上用多尺度不连续特征＋逻辑回归输出逐像素断层概率。输入、输出和评价方式与生产流程一致，差别在于模型容量与数据维度。') +
     figure(pipeline_fig([('振幅体', 'SEG-Y 三维数据 · 统一面元'), ('断层增强', '相干 · 曲率属性'), ('分割网络', '3D U-Net · 断层概率体'), ('骨架与组合', '细化 · 连成断面'), ('候选断面', '人工质检与修正')], 3, '算法负责扫描全部数据体，给出候选断面', '人负责组合与地质合理性', 'AI 介入点流程'), 2, '从振幅体到候选断面的五步。真正决定能不能用的，往往不是网络有多深，而是第 4 步：**阈值与骨架化**决定了深层弱断层是连成整条还是碎成一地，**断面组合规则**决定了交给开发方案的是不是一套地质上讲得通的断层系统。')},
  {'en': 'DATA', 'title': '你需要准备什么', 'html': CHECK_INTRO + checklist([
     ('三维地震振幅体', '200 km² 级，SEG-Y 数十 GB', '5—10 个工区，每工区 ≥ 100 条剖面标注'),
     ('相干 / 曲率等属性体', '与振幅体同网格', '可由振幅体自动生成'),
     ('历史解释断层', '已有解释成果的工区', '直接转为标签，需统一断层命名'),
     ('井断点数据', '区块内钻遇断点的深度', '用于验证断层位置'),
     ('时深关系 / 速度模型', '工区级', '时间域断面转深度、与井对比')]) +
     kicker('可参考的公开数据集') + refs(['F3 Netherlands 公开数据体（含断层解释）', 'FaultSeg3D 合成含断层训练数据'])},
  {'en': 'DIFFICULTY', 'title': '技术难度与参考方向', 'html':
     '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:2px">' + dtag('高') + '<span class="small muted">断层像素占比常低于 1%，标签稀缺，跨工区的频率与信噪比差异导致迁移困难。</span></div>' + meter('高') + DIFF_NOTE +
     kicker('可借鉴的通用技术') + refs(['三维语义分割', '类别不均衡学习', '断层增强属性', '合成数据预训练'], '#/method/cv') + cross(['钻井', '采油'])}],
 'workflow': {
  'title': '案例：B 工区 200 km² 三维数据体的断层自动解释',
  'lead': ['B 工区是一个复杂断块油田的扩边评价区，三维数据体 200 km²，已有 6 口探井。解释组过去完成一轮断层解释需要 3 周。目标不是"训练出一个分割网络"，而是**把一轮断层解释压缩到一周以内（含人工质检），同时不漏掉断距 ≥ 10 m 的断层**。',
           '下面五步是这个案例的落地流程。注意第 2 步和第 4 步：它们不涉及网络结构，却决定了结果能不能交给开发方案使用。'],
  'stats': [['数据体', '200 km²'], ['已解释剖面', '160 条'], ['探井', '6 口'], ['断层目标', '断距 ≥ 10 m'], ['人工周期', '3 周 / 轮'], ['辅助后周期', '5 天 / 轮']],
  'steps': [
   {'name': '数据整理与标签准备', 'role': '工程环节', 'do': '把数据体统一到同一采样与面元，抽取 160 条历史解释剖面作为标签；**按区块划分训练 / 验证集**，不能把相邻剖面随机分到两个集合。', 'effect': '训练集和验证集之间没有空间相邻的信息泄漏', 'trap': '相邻 inline 几乎一模一样，随机划分会让验证分数虚高'},
   {'name': '合成数据预训练', 'role': '工程环节', 'do': '本工区标注太少，先用正演生成的含断层合成数据体预训练，再用本工区剖面微调。', 'effect': '用一百多条本地剖面就能得到可用模型', 'trap': '合成数据的频带与真实资料不一致，不微调直接用会大量误报'},
   {'name': '断层概率体预测', 'role': '算法核心', 'do': '分割网络逐体素输出断层概率；损失函数对断层像素加权，抵消不到 1% 的类别占比。', 'effect': '召回优先：宁可多给候选，也不漏掉真断层', 'trap': '不加权时，模型把所有体素判为"非断层"也有 99% 的准确率'},
   {'name': '骨架化与断面组合', 'role': '效果关键', 'do': '阈值 + 细化得到断层骨架，按走向、倾角连接成断面，面积过小的碎片直接过滤。', 'effect': '把"概率体"变成可编辑的"断面"', 'trap': '阈值过高，深层弱断层会被截成碎片；过低，不整合面会混进来'},
   {'name': '人工质检与回流', 'role': '闭环', 'do': '解释员在候选断面上增删改，逐条核对井断点；修正后的剖面回流为下一轮的训练标签。', 'effect': '每做完一轮，本工区的标签就多一批', 'trap': '不核对井断点，地层削截、河道边界会被当成断层留下来'}],
  'metrics': {'title': '怎么算"解释对了"', 'html': P('断层是细线目标，逐像素准确率没有意义——全部判成"非断层"也有 99% 以上。评价分两层：**像素层**按容差匹配，预测落在人工断层 ±2 道以内算命中，再统计精确率、召回率与 IoU；**断层层**按条数统计，看断距 ≥ 10 m 的断层有没有整条漏掉。') +
     figure(fault_tolerance_fig(), 3, '按容差匹配后统计 TP / FP / FN。**漏检（FN）比误报（FP）代价更高**：漏掉一条断层意味着井位可能打到断块另一侧，而多一个候选断面，解释员点一下就能删掉。') +
     dtable(['指标', '定义', '验收目标'], [
       ['精确率 P', 'TP / (TP + FP)，预测断层像素中有多少在容差内', '≥ 0.75'],
       ['召回率 R', 'TP / (TP + FN)，真实断层像素中找回了多少', '≥ 0.85'],
       ['断层级漏检', '断距 ≥ 10 m 的断层中整条未被检出的条数', '0 条'],
       ['断面位置偏差', '命中断层与人工断面的平均水平距离', '≤ 1 道（25 m）']]) +
     P('可运行示范中的 IoU、精确率与召回率由页面在合成剖面上实时计算，用来理解阈值与漏检的关系，不代表真实工区效果。')},
  'fails': [
   {'name': '不整合面与河道边界误报', 'why': '振幅的突然变化不一定是断层：地层削截、河道边缘在相干属性上同样表现为"不连续"。需要结合构造样式和井资料判别，或把这类样本单独标注成负样本。'},
   {'name': '深层弱断层碎片化', 'why': '深层信噪比低，概率体断断续续，骨架化后变成大量短碎片。可用多尺度属性，或沿断层走向加连续性约束。'},
   {'name': '跨工区迁移失效', 'why': '换一个工区，主频、采集脚印和噪声特征都变了，模型会大面积误报或漏报。每个新工区至少要几十条本地剖面做微调。'},
   {'name': '断层组合错误', 'why': '网络只回答"哪里是断层"，不回答"哪几段属于同一条断层"。组合仍是解释员的职责；自动连接必须设置走向与断距一致性规则。'}]},
 'demo': {'label': '可运行示范', 'intro': '在合成剖面上调噪声与阈值，观察断层概率、漏检与误报怎样此消彼长——对应流程第 3、4 步。'}
}
