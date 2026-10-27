/* 接入指南与案例校验控制台
   内容与教师框架 docs/如何添加新案例.md 保持一致；文件名按本站实际结构标注。 */
(function (global) {
  'use strict';
  var esc = K.esc, rich = K.rich;

  function head(kicker, title, p, num, tag) {
    return '<div class="sec-head" style="margin-top:34px">' +
      (num ? '<div class="sec-rail"><span class="sec-num">' + num + '</span><span class="kicker">' + esc(kicker) + '</span>' +
        (tag ? '<span class="r"><span class="tag">' + esc(tag) + '</span></span>' : '') + '</div>'
        : '<div><span class="kicker">' + esc(kicker) + '</span></div>') +
      '<h2 style="margin-top:8px">' + esc(title) + '</h2>' + (p ? '<p>' + rich(p) + '</p>' : '') + '</div>';
  }
  function step(n, title, body) {
    return '<div class="gstep"><div class="gn">' + n + '</div><div><h3>' + esc(title) + '</h3>' + body + '</div></div>';
  }
  function P() { return Array.prototype.map.call(arguments, function (t) { return '<p>' + rich(t) + '</p>'; }).join(''); }
  function ul(items) { return '<ul class="g-ul">' + items.map(function (t) { return '<li>' + rich(t) + '</li>'; }).join('') + '</ul>'; }
  function contract(rows, head3) {
    return '<div class="matrix-wrap"><table class="contract"><thead><tr><th>' + head3.join('</th><th>') + '</th></tr></thead><tbody>' +
      rows.map(function (r) {
        var lv = r[1] === '必填' ? '<span class="req">必填</span>' : '<span class="opt">' + esc(r[1]) + '</span>';
        return '<tr><td>' + esc(r[0]) + '</td><td>' + lv + '</td><td>' + rich(r[2]) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  var SAMPLE = [
    "Cases.register({",
    "  id: 'logging-mud-loss',          // 必填，kebab-case，全局唯一",
    "  sceneId: 'd3',                    // 必填，data.js 里已有的场景 id",
    "  title: '钻井液漏失层位识别',",
    "  status: 'ready',                  // ready | draft",
    "  version: '1.0.0',",
    "  updated: '2026-10-22',",
    "",
    "  tabs: {",
    "    // ① 专业背景：四段式，返回 HTML 字符串",
    "    background: {",
    "      label: '专业背景',",
    "      judge: [",
    "        { label: '任务', value: '序列分割' },",
    "        { label: '数据', value: '随钻曲线 + 漏失记录' }",
    "      ],",
    "      lede: '一句话说明这个场景到底在做什么。',",
    "      sections: [",
    "        { no: 1, en: 'PROBLEM', title: '当前做法与问题',",
    "          html: '<p>……</p>' + K.figure(svgManual(), 1, '图注') },",
    "        { no: 2, en: 'INTERVENTION', title: 'AI 能做什么', html: '……' },",
    "        { no: 3, en: 'DATA', title: '你需要准备什么',",
    "          html: K.checklist([['随钻曲线', '1 s 采样'], ['漏失记录', '人工登记']]) },",
    "        { no: 4, en: 'DIFFICULTY', title: '技术难度与参考方向', html: '……' }",
    "      ]",
    "    },",
    "",
    "    // ② 案例流程：一条真实项目走过的路",
    "    workflow: {",
    "      label: '案例流程',",
    "      title: '某某区块 18 口井的漏失识别',",
    "      lead: ['项目目标不是做模型，而是把漏失层位定位时间压到 10 分钟。'],",
    "      stats: [['样本井', '18 口'], ['目标准确率', '85%']],",
    "      steps: [",
    "        { name: '数据对齐', do: '……', role: '工程环节',",
    "          effect: '……', trap: '……' }",
    "      ],",
    "      fails: [{ name: '标签滞后', why: '……' }]",
    "    },",
    "",
    "    // ③ 可运行示范（可选）：给一个 DOM 容器就能跑",
    "    demo: {",
    "      label: '可运行示范',",
    "      mount: function (root, ctx) {",
    "        root.innerHTML = '<div>……</div>';",
    "        // ctx.scene / ctx.kase / ctx.K / ctx.atlas 都可直接用",
    "      },",
    "      unmount: function () { /* 清理定时器、事件监听 */ }",
    "    }",
    "  }",
    "});"
  ].join('\n');

  function html() {
    var o = '';
    o += '<div class="s-breadcrumb"><a href="#/">探索地图</a><span>/</span><span>接入指南</span></div>';
    o += '<div class="s-detail-en">EXTENDING / ADD A CASE</div><h1>如何添加新案例</h1>' +
      '<p class="g-lede">两条路：不写代码就<b>上传案例包</b>；要把案例永久发布给所有访问者，就<b>写插件</b>。两条路走完效果一样——场景页自动长出三个 tab，按环节、按方法两条检索路径自动收录。</p>' +
      '<p class="g-note">本页与项目里的 <code>docs/如何添加新案例.md</code> 内容一致。上传弹窗、校验器和存储方式直接使用老师框架的 <code>case-upload.js</code> / <code>registry.js</code>，步骤和要求与老师网站相同。</p>';

    /* 两条路 */
    o += head('TWO PATHS', '两条路');
    o += K.dtable(['', '方式 A · 上传案例包', '方式 B · 写插件'], [
      ['门槛', '不写代码（示范页会 HTML/CSS/JS 即可）', '会一点 JS'],
      ['内容', '专业背景 + 案例流程 + 完整示范', '三块内容全可定制'],
      ['可运行示范', '自带：整页 HTML / demo.js 均可', '可以放真实算法'],
      ['保存位置', '本机浏览器（localStorage）', '磁盘文件，永久'],
      ['入口', '导航「＋ 添加案例」', '下文三步接入']
    ]);

    /* 方式 A */
    o += head('UPLOAD PACKAGE · 推荐先试这个', '方式 A：上传案例包', null, 'A', '不需要改任何文件');
    o += '<h3 class="g-h3">案例包长什么样</h3>' +
      P('一个**文件夹**，最少只有一份清单，其余随便：') +
      K.tree([
        '<b>my-case/</b>',
        '  case.json          <span class="cm">清单（必需）：元信息 + 专业背景 + 案例流程</span>',
        '  demo/index.html    <span class="cm">示范页（可选，整页模式）</span>',
        '  demo/demo.css      <span class="cm">示范页样式（可选）</span>',
        '  demo/demo.js       <span class="cm">示范脚本（可选；没有 html 时它就是模块模式的挂载脚本）</span>',
        '  *.png / *.svg / *.json…   <span class="cm">任意素材，放进来即可被引用</span>'
      ]);
    o += '<h3 class="g-h3">怎么接入</h3><div class="gsteps">' +
      step(1, '下载模板', P('在「添加案例」弹窗里点 **下载案例包模板（.zip）**——解压就是一个能直接跑的完整包（清单 + 示范页 + 样式 + 脚本）；也可以只用 `assets/cases/_template.case.json` 这份清单模板。') +
        '<div class="upcard-acts"><button class="btn primary" data-import>＋ 打开「添加案例」</button><button class="btn" data-dl-template>↓ 下载案例包模板（.zip）</button></div>') +
      step(2, '改清单', P('改清单里的 `id`（小写字母 / 数字 / 连字符，全站唯一）、`sceneId`（绑定哪个场景，等于选定分类）、`title`，以及两块正文——`tabs.background`（导语 + 30 秒判断 + 四段式 `sections[]`）和 `tabs.workflow`（步骤 `steps[]`、指标 `metrics`、失败模式 `fails[]`）。')) +
      step(3, '把整个文件夹拖回弹窗', P('把 `my-case` **整个文件夹**拖回弹窗（推荐方式，支持多级子目录）。如果浏览器不支持「选择文件夹」按钮（点了弹出的仍是文件选择框，常见于国产浏览器兼容模式），三个替代办法：') +
        ul(['直接把文件夹拖进虚线框；', '点「选择文件」后 Ctrl+A 全选包内所有文件；', '改用 Chrome 或 Edge。']) +
        P('多选文件时清单、示范页仍能按文件名自动对上（支持文件夹、多选文件、逐个添加），右侧会**逐项显示校验结果**——红色必须改，黄色可以忽略；点「▶ 试跑示范」可以在沙箱里先看效果。')) +
      step(4, '校验并添加', P('全绿后点 **校验并添加**：案例立即注册并写入本机浏览器，自动跳到对应场景页，三个 tab 当场出现。')) +
      '</div>';

    o += '<h3 class="g-h3">示范的两种写法</h3><div class="g-two">' +
      '<div class="g-card"><h4>A. 整页模式 —— 包里有 <code>demo/index.html</code></h4>' +
      ul(['整页运行在 **sandbox iframe** 里，样式脚本完全隔离，图表、Canvas、第三方库随便用；',
        '`<link href="demo.css">` 与 `<script src="demo.js">` 会被自动内联，图片等素材的相对路径会被自动替换成内嵌资源——**不需要服务器，双击 index.html 也能跑**；',
        '脚本里可以用 `window.caseAsset("core.png")` 取素材地址。']) + '</div>' +
      '<div class="g-card"><h4>B. 模块模式 —— 只有 <code>demo/demo.js</code>（没有 html）</h4>' +
      ul(['脚本被执行，挂进 **Shadow DOM**，上传的 CSS 也注入 Shadow DOM，不会污染主站；样式里可以直接用站点令牌 `var(--jade)` 等；',
        '需要导出挂载函数，三种写法任选（见下）；',
        '`api` 对象：`api.asset(name)` 取素材地址、`api.readText(name)` 读文本素材、`api.list()` 列包内文件、`api.scene` / `api.kase` 拿场景与案例元数据、`api.onDestroy(fn)` 注册清理。']) + '</div></div>' +
      K.code(['module.exports = {',
        '  mount: function (root, api) { /* root 是你的容器 */ },',
        '  unmount: function () { /* 清定时器、事件监听 */ }',
        '};',
        '// 或 exports.mount = function (root, api) {...}',
        '// 或 window.__CASE_MOUNT__ = function (root, api) {...}'].join('\n'), { file: 'demo/demo.js', note: '模块模式' }) +
      P('两者都没有时，也可以在清单里写 `tabs.demo.builtin = "welllog-layer"` 复用已有示范。');

    o += '<h3 class="g-h3">注意</h3>' + ul([
      '上传的案例保存在本机浏览器里：刷新、关页面都在；换电脑或换浏览器需要重新上传；案例库列表里带「本地导入」标记，可一键移除。要永久发布给所有人，走方式 B。',
      '单包上限 6 MB（超过会拦截，1.5 MB 以上会提醒）；图片先压缩，视频请放外部链接。',
      '同一场景上传新案例后，场景页会**优先展示上传的这份**（后传的覆盖先传的），旧案例仍留在案例库里，可在场景页的案例切换器里切回。'
    ]);

    /* 三层结构 */
    o += head('STRUCTURE', '系统的三层结构', '新增一个案例，**只动第 2 层的一个文件**，外加 `index.html` 里一行 `<script>`。');
    o += K.tree([
      '┌─ 03 外壳层  assets/core/* + assets/site.js   <span class="cm">路由 / 导航 / 组件 / 设计令牌，一般不用动</span>',
      '├─ 02 案例层  assets/cases/*                   <span class="dir">每个案例一个文件，即插即用 ← 你要改的只有这里</span>',
      '└─ 01 数据层  assets/data.js                   <span class="cm">13 环节 / 61 场景的元数据</span>'
    ]);
    o += '<h3 class="g-h3">文件在哪</h3>' + K.tree([
      '<b>petro-ai-atlas/</b>',
      '├── index.html                <span class="cm">← 新增案例时加一行 script</span>',
      '├── assets/',
      '│   ├── data.js               <span class="cm">场景元数据（13 环节 / 61 场景）</span>',
      '│   ├── core/                 <span class="cm">老师的外壳，一般不用动</span>',
      '│   │   ├── tokens.css        <span class="cm">颜色 / 字号 / 圆角</span>',
      '│   │   ├── ui.css            <span class="cm">卡片 / 表格 / 四段式 / 示范</span>',
      '│   │   ├── registry.js       <span class="cm">Cases.register 契约与校验（与老师原版一致）</span>',
      '│   │   ├── kit.js            <span class="cm">K.sec4 / K.figure / K.code…</span>',
      '│   │   ├── case-demo-host.js <span class="cm">示范宿主：iframe 整页 / Shadow DOM 模块（与老师原版一致）</span>',
      '│   │   └── case-upload.js    <span class="cm">案例包导入：校验 / 打包 / 落库（与老师原版一致）</span>',
      '│   ├── builtins.js           <span class="cm">本站 9 个原创案例（由 tools/build_cases.py 生成）</span>',
      '│   ├── site.js               <span class="cm">本站的路由与页面（相当于老师的 shell.js）</span>',
      '│   └── cases/                <span class="dir">← 插件案例都放这里</span>',
      '│       ├── welllog-layer.case.js   <span class="new">测井分层（老师的示例）</span>',
      '│       ├── welllog-layer.demo.js   <span class="new">它的可运行示范</span>',
      '│       ├── _template.case.js       <span class="new">插件模板，复制它开始</span>',
      '│       └── _template.case.json     <span class="new">清单模板（完整包请用弹窗里下载的 zip）</span>',
      '├── cases/                    <span class="cm">9 个原创案例的案例包源文件</span>',
      '├── downloads/                <span class="cm">9 个原创案例的 ZIP，可直接导入老师网站</span>',
      '└── docs/',
      '    └── 如何添加新案例.md      <span class="cm">本页的离线版</span>'
    ]);

    /* 方式 B */
    o += head('PLUGIN · 需要永久发布或真实示范时', '方式 B：写插件，三步接入', null, 'B');
    o += '<div class="gsteps">' +
      step(1, '复制模板，改三处', P('把 `assets/cases/_template.case.js` 复制成 `<你的案例id>.case.js`，只改三处：') +
        contract([
          ['id', '必填', '全局唯一，kebab-case，例如 `d3-mudloss`'],
          ['sceneId', '必填', '必须是 `data.js` 里已有的场景 id（如 `w1`）。场景不存在时先去 `data.js` 对应环节的 `scenes` 数组里加一条元数据'],
          ['tabs 里的内容', '必填', '三个 tab：background / workflow / demo（demo 可选）']
        ], ['要改的', '级别', '说明'])) +
      step(2, '在 index.html 里挂上去', P('在 `welllog-layer.demo.js` 后面加一行：') +
        K.code(['<script src="assets/cases/welllog-layer.case.js"></script>',
          '<script src="assets/cases/welllog-layer.demo.js"></script>',
          '<script src="assets/cases/你的案例.case.js"></script>   <!-- ← 加在这里 -->',
          '',
          '<script src="assets/site.js"></script>                  <!-- 必须在 site.js 之前 -->'].join('\n'), { file: 'index.html', note: '加在 site.js 之前' }) +
        P('加载顺序：`data.js → registry.js → kit.js → 案例 → site.js`（老师框架里最后一个是 `shell.js`）。案例必须在 `site.js` **之前**注册完，否则首屏渲染时找不到它。')) +
      step(3, '打开控制台看校验', '<p>刷新页面，进 <a href="#/cases" class="g-a">案例实验室</a> 页面底部的<b>案例校验控制台</b>（相当于老师网站的「案例库」）。系统自动检查：</p>' +
        ul(['id 是否规范（kebab-case）', '`sceneId` 是否存在于 data.js', 'background 是否至少 2 段、每段有无 title 和内容', 'workflow.steps 是否非空', '`tabs.demo.mount` 是否为函数', '场景的 `demo:true` 标记与案例是否一致', '同一场景是否被多个案例绑定']) +
        P('全绿即接入完成：场景页的 tab、面包屑、相关场景、方法反查页的条目都会自动出现，**不需要改任何其他文件**。')) +
      '</div>';

    /* 契约字段 */
    o += head('CONTRACT', '契约字段', '只有标「必填」的字段缺失会报错，其余缺失只是控制台里的一条提醒。');
    o += contract([
      ['case.json（文件）', '必填', '清单，放包根目录，建议就叫这个名字'],
      ['demo/index.html（文件）', '可选', '整页示范，自动内联 css/js 与素材'],
      ['demo/demo.js（文件）', '可选', '示范脚本；无 html 时为模块模式，需导出 mount'],
      ['demo/demo.css（文件）', '可选', '示范样式（整页模式进 iframe，模块模式进 Shadow DOM）'],
      ['id', '必填', 'kebab-case，全局唯一'],
      ['sceneId', '必填', '绑定到 data.js 的场景 id'],
      ['methods', '可选', '数组。案例涉及的 AI 技术（如 `["ts","cv"]`），也可在导入弹窗里勾选；不填则继承场景标签'],
      ['title', '必填', '案例标题'],
      ['status', '建议', '`ready` 可用于教学；`draft` 未定稿（控制台标黄）'],
      ['version / updated', '建议', '语义化版本 / 最后更新日期'],
      ['tabs.background', '必填', '`judge`（30 秒判断）+ `lede`（导语）+ `sections[]`（四段式）'],
      ['tabs.background.sections[]', '必填', '每段 `{ no, en, title, html }`，建议恰好四段'],
      ['tabs.workflow', '建议', '`title` / `lead[]` / `stats[]` / `steps[]` / `metrics` / `fails[]`'],
      ['tabs.workflow.steps[]', '建议', '每步 `{ name, do, role, effect, trap }`'],
      ['tabs.demo', '可选', '`{ mode, html, js, label, intro, height }` 或 `{ builtin }`'],
      ['tabs.demo.mode', '可选', '`auto`（默认，自动判断）/ `page` / `module` / `builtin`'],
      ['tabs.demo（插件写法）', '可选', '`{ label, mount(root, ctx), unmount() }`']
    ], ['字段', '级别', '说明']);

    o += head('EXAMPLE', '一个完整的案例声明', '这是最小可用的骨架，把省略号换成你的内容即可。');
    o += K.code(SAMPLE, { file: 'assets/cases/your-case.case.js' });

    /* 工具箱 */
    o += head('KIT', '工具箱（不要在案例里写 CSS 类名）', '用这些函数生成结构，版式改动会全站同步。');
    o += K.dtable(['函数', '用途'], [
      ['`K.sec4(no, en, title, html)`', '四段式中的一段'],
      ['`K.figure(svg, no, caption)`', '插图 + 图注'],
      ['`K.judge([{label,value,desc,html}])`', '顶部"30 秒判断"格子'],
      ['`K.checklist(items)`', '可勾选的数据清单，items 为 `[名称, 规格, 标注要求]`'],
      ['`K.dtable(head, rows)`', '数据表格'],
      ['`K.pipeline(steps)`', '编号流程步骤'],
      ['`K.fails([{name, why}])`', '失败模式宫格'],
      ['`K.cells([[标签, 值]])`', '指标格（纯数字自动放大）'],
      ['`K.meter(diff)`', '三段难度条，diff ∈ 低/中/高'],
      ['`K.refs([...], href)`', '参考方向胶囊'],
      ['`K.callout(text, \'warn\')`', '提示条'],
      ['`K.code(str, {file})`', '代码块（带语法着色）']
    ]);
    o += K.callout('文本里可以直接用 **粗体** 与 `等宽` 两种标记；所有函数自动转义 HTML，不需要手动防注入。');

    /* 颜色规范 */
    o += head('COLOR', '颜色规范', '案例内写颜色时只用两类值：');
    o += ul(['设计令牌：`var(--jade)` 主色、`var(--clay)` 强调、`var(--c-cv)` 等方法色、`var(--ink-2)` 等文字色（本站配色里 `--jade` 显示为藏青，令牌名与老师框架相同）；',
      '直接写低饱和的浅色 hex（如 `#e6f1ec`、`#b26a39`）。']) +
      P('**不要在案例正文里写深色背景**，令牌会随全站配色一起切换，写死的深色会掉队。');

    /* 常见错误 */
    o += head('PITFALLS', '四个常见错误');
    o += '<div class="fails" style="grid-template-columns:1fr 1fr">' + [
      ['script 顺序放反', '案例写在 site.js 后面，页面渲染完了才注册，控制台里能看到但场景页没有 tab。案例脚本必须在 site.js 之前。'],
      ['sceneId 拼错', 'id 区分大小写。写错不会报 JS 错误，只是这个案例永远不出现。控制台的「绑定场景」列会显示 ⚠。'],
      ['demo 里没有清理', '用了 setInterval / window 级事件监听的示范，要在 unmount() 里清掉，否则切换场景后老定时器还在跑。'],
      ['把样式写死在案例里', '内联深色会让案例在改配色时掉队。颜色一律用 var(--jade) 这类令牌，或干脆用 K.* 生成。']
    ].map(function (x, i) { return '<div class="fail"><div class="fi">PITFALL 0' + (i + 1) + '</div><h5>' + esc(x[0]) + '</h5><p>' + esc(x[1]) + '</p></div>'; }).join('') + '</div>';

    /* 删除 */
    o += head('REMOVE', '删除案例', '案例实验室底部的**案例校验控制台**里，每个案例都有删除入口，行为按案例来源区分：');
    o += K.dtable(['', '上传的案例（带「本地导入」徽标）', '插件案例（.case.js）'], [
      ['点击后', '清掉浏览器里保存的案例包存档', '记入隐藏名单，站点立即不再显示'],
      ['磁盘文件', '不受影响', '保留在 `assets/cases/`，不动'],
      ['刷新后', '不再出现（存档已清）', '保持隐藏'],
      ['恢复', '重新上传即可', '控制台「已删除的插件案例」区点「恢复」，刷新后回来']
    ]);
    o += P('删除是即时生效的：确认对话框点「确定」后页面就地更新。程序化接口：`CaseImport.remove(id)` 删除，`CaseImport.restore(id)` 恢复插件案例。彻底删除插件案例：删掉 `assets/cases/<id>.case.js`（和可选的 `.demo.js`）以及 index.html 里对应的 `<script>` 行，场景自动回到"待接入"状态。');

    o += '<div class="pending" style="margin-top:36px"><div class="pending-top"><span class="badge-ready">下一步</span><h3>从最简单的案例开始</h3></div>' +
      '<p>如果还没有想好做什么，先挑一个 <b>数据现成、任务边界清晰</b> 的场景：把四段式写满、流程写三步、示范可以先不做。一个只有 80 行内容的案例，也比一个空着的场景有用。</p>' +
      '<div class="pending-actions"><a class="btn primary" href="#/cases">看当前案例库 →</a><a class="btn" href="#/scene/w1">对照测井分层的写法</a><a class="btn" href="teacher/index.html">打开未修改的老师框架 ↗</a></div></div>';
    return o;
  }

  /* ---------------- 案例校验控制台（与老师框架「案例库」表格一致） ---------------- */
  function consoleHTML() {
    var list = Cases.list(), checks = Cases.validateAll ? Cases.validateAll() : {};
    var rows = list.map(function (c) {
      var sc = ATLAS.index.byScene[c.sceneId], ck = checks[c.id] || [];
      var errs = ck.filter(function (x) { return x.level === 'error'; }).length;
      var warns = ck.filter(function (x) { return x.level === 'warn'; }).length;
      var state = errs ? '<span class="bad-mark">✕ ' + errs + ' 项错误</span>'
        : warns ? '<span class="mono" style="font-size:12px;color:var(--warn)">! ' + warns + ' 项提醒</span>'
          : '<span class="ok-mark">✓ 通过</span>';
      var tabs = ['background', 'workflow', 'demo'].map(function (k) {
        return '<span class="' + (c.tabs && c.tabs[k] ? 'ok-mark' : 'dim-mark') + '" title="' + k + '">' + (c.tabs && c.tabs[k] ? '●' : '○') + '</span>';
      }).join(' ');
      return '<tr><td class="id">' + esc(c.id) + '</td>' +
        '<td><div class="nm">' + esc(c.title || (sc && sc.name) || '') + (c.imported ? '<span class="badge-local">本地导入</span>' : '') + '</div>' +
        '<div class="sc">' + (sc ? esc(sc.stageName) + ' / ' + esc(sc.name) : '⚠ sceneId 未匹配') + '</div></td>' +
        '<td class="sc">' + esc(c.version || '—') + '</td>' +
        '<td style="letter-spacing:.16em">' + tabs + '</td><td>' + state + '</td>' +
        '<td>' + (sc ? '<a class="btn sm ghost" href="#/scene/' + sc.id + '?case=' + encodeURIComponent(c.id) + '">打开 →</a>' : '—') +
        '<a href="#" class="link-remove" data-remove-case="' + esc(c.id) + '">' + (c.imported ? '移除' : '删除') + '</a></td></tr>';
    }).join('');
    var blocked = (global.CaseImport && CaseImport.blockedList ? CaseImport.blockedList() : []).filter(function (id) { return !Cases.get(id); });
    var bb = blocked.length ? '<div class="blocked-box"><div class="bb-h"><span class="kicker clay">HIDDEN</span><b>已删除的插件案例（' + blocked.length + '）</b><span class="bb-sub">恢复后刷新页面即可回到上表</span></div><div class="bb-list">' +
      blocked.map(function (id) { return '<span class="bb-item"><span class="mono">' + esc(id) + '</span><a href="#" class="link-remove" data-restore-case="' + esc(id) + '">恢复</a></span>'; }).join('') + '</div></div>' : '';
    var detail = list.map(function (c) {
      var ck = checks[c.id] || [];
      return '<details class="g-details"><summary>' + esc(c.id) + ' 的校验明细 <span class="mono">' + ck.length + ' 条</span></summary><div><table class="contract"><tbody>' +
        ck.map(function (x) {
          var m = x.level === 'ok' ? '<span class="ok-mark">✓</span>' : x.level === 'warn' ? '<span style="color:var(--warn)">!</span>' : '<span class="bad-mark">✕</span>';
          return '<tr><td style="width:28px">' + m + '</td><td>' + esc(x.label || '') + (x.detail ? '<span class="g-dt">' + esc(x.detail) + '</span>' : '') + '</td></tr>';
        }).join('') + '</tbody></table></div></details>';
    }).join('');
    return '<section id="case-console" class="g-console"><div class="sec-head"><div><span class="kicker">CONSOLE</span><h2 style="margin-top:8px">案例校验控制台</h2>' +
      '<p>所有已注册案例（内置、插件、本地导入）都会在这里按老师框架的契约逐项校验。插件接入后刷新页面，全绿即完成；上传的案例可以在这里移除。</p></div></div>' +
      '<div class="matrix-wrap"><table class="contract g-ctable"><thead><tr><th>id</th><th>案例 / 绑定场景</th><th>版本</th><th>三个 tab</th><th>校验</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>' + bb + detail + '</section>';
  }

  global.PetroGuide = { html: html, consoleHTML: consoleHTML };
})(window);
