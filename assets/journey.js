/* 沿井筒的作业旅程：首页作业链插画。
   纯 SVG 生成；点击站点后通过动画 viewBox 原地放大，面板内容由 site.js 提供。 */
(function () {
  'use strict';
  const W = 1320, H = 600, G = 170, R = 470, INK = '#232a39';
  const WX = 430, IX = 690, PX = 900;
  const COLS = ['#bcb497', '#757575', '#656565', '#b89f6c', '#5c5c5c'];

  // 站点圆点位置（与作业旅程金色虚线一致）
  const STOPS = [
    { x: 120, y: G - 110, label: 'above' }, { x: 250, y: G - 110, label: 'above' }, { x: WX, y: G - 110, label: 'above' },
    { x: WX + 75, y: G - 62, label: 'right' }, { x: WX + 60, y: 262, label: 'right' }, { x: WX + 60, y: 315, label: 'right' },
    { x: WX + 60, y: R - 20, label: 'right' }, { x: WX + 60, y: R + 14, label: 'right' }, { x: PX - 20, y: G - 110, label: 'above' },
    { x: PX + 80, y: G - 110, label: 'above' }, { x: IX, y: R + 50, label: 'below' }, { x: 1120, y: G - 110, label: 'above' },
    { x: 1240, y: G - 110, label: 'above' }
  ];
  // 放大时的聚焦中心（设备或井下位置）
  const FOCUS = [[130, 175], [255, 250], [430, 210], [505, 205], [445, 285], [445, 330], [445, 445], [445, 480],
    [910, 230], [1000, 225], [700, 500], [1120, 205], [1230, 195]];
  // 每一站在旅程中的位置描述
  const PLACE = ['地表 · 区域地质', '地表 · 地震测线', '井口 · 钻机', '井场 · 录井房', '井下约 1000 m', '井下约 1500 m · 套管段',
    '井下约 2800 m · 储层顶部', '井下约 3000 m · 储层', '地面 · 采油井口', '地面 · 修井作业', '注入井 · 储层', '地面 · 集输管线', '炼厂'];

  const well = (x, g, d, casing) => (casing ? `<rect x="${x - 6}" y="${g}" width="12" height="${d - g - 30}" fill="url(#jr-cem)" stroke="#494949" stroke-width="1"/>` : '') +
    `<line x1="${x}" y1="${g}" x2="${x}" y2="${d}" stroke="#2d364b" stroke-width="2.4"/>`;

  function icon(i, x, g, r) {
    switch (i) {
      case 0: return `<g transform="translate(${x},${g - 78})"><rect x="-9" y="-6" width="18" height="12" fill="#456c59"/><rect x="-30" y="-4" width="18" height="8" fill="#97aeba"/><rect x="12" y="-4" width="18" height="8" fill="#97aeba"/><path d="M0 6 L-20 60 M0 6 L20 60" stroke="#b89f6c" stroke-dasharray="4 4"/></g>` +
        `<circle cx="${x}" cy="${g - 26}" r="10" fill="none" stroke="${INK}" stroke-width="2.4"/><line x1="${x + 7}" y1="${g - 19}" x2="${x + 16}" y2="${g - 10}" stroke="${INK}" stroke-width="3"/>`;
      case 1: return `<rect x="${x - 24}" y="${g - 20}" width="34" height="16" rx="2" fill="#b89f6c"/><rect x="${x + 10}" y="${g - 15}" width="14" height="11" fill="#b8730e"/><circle cx="${x - 14}" cy="${g - 3}" r="4" fill="${INK}"/><circle cx="${x + 14}" cy="${g - 3}" r="4" fill="${INK}"/>` +
        [30, 60, 90, 120].map(rr => `<path d="M${x - rr} ${g} A${rr} ${rr * 0.8} 0 0 0 ${x + rr} ${g}" fill="none" stroke="#e8dfc1" stroke-width="1.6" opacity="${1 - rr / 150}"/>`).join('') +
        `<path d="M${x} ${g} L${x + 50} ${r - 30} L${x + 100} ${g}" fill="none" stroke="#fff" stroke-dasharray="3 3"/>`;
      case 2: return `<path d="M${x - 16} ${g} L${x} ${g - 70} L${x + 16} ${g}" fill="none" stroke="${INK}" stroke-width="2.4"/>` +
        [1, 2, 3, 4, 5, 6].map(k => `<line x1="${x - 16 + k * 2.3}" y1="${g - k * 10}" x2="${x + 16 - k * 2.3}" y2="${g - k * 10}" stroke="${INK}" stroke-width="1.2"/>`).join('');
      case 3: return `<rect x="${x - 20}" y="${g - 26}" width="40" height="26" fill="#e0d9c6" stroke="${INK}" stroke-width="1.6"/><rect x="${x - 12}" y="${g - 19}" width="9" height="8" fill="#97aeba"/><path d="M${x + 4} ${g - 12}h10" stroke="${INK}"/>` +
        [0, 1, 2, 3, 4].map(k => `<circle cx="${x - 14 + k * 7}" cy="${g - 34 - (k % 2) * 4}" r="2.2" fill="#b8730e"/>`).join('');
      case 8: return `<path d="M${x - 28} ${g}h56" stroke="${INK}" stroke-width="3"/><path d="M${x - 4} ${g}L${x} ${g - 34}L${x + 4} ${g}" fill="none" stroke="${INK}" stroke-width="2.4"/><path d="M${x - 30} ${g - 30} L${x + 26} ${g - 42}" stroke="${INK}" stroke-width="4"/><path d="M${x - 30} ${g - 36} q-10 8 0 16" fill="#b89f6c" stroke="${INK}"/><line x1="${x - 36}" y1="${g - 20}" x2="${x - 36}" y2="${g}" stroke="${INK}" stroke-width="1.5"/>` +
        well(x - 36, g, r + 8) + `<path d="M${x - 36} ${r + 6} l-6 -12 M${x - 36} ${r + 6} l6 -12" stroke="#1c1c1c" stroke-width="1.5"/>`;
      case 9: return `<rect x="${x - 20}" y="${g - 14}" width="34" height="14" fill="#b89f6c"/><circle cx="${x - 12}" cy="${g}" r="4" fill="${INK}"/><circle cx="${x + 8}" cy="${g}" r="4" fill="${INK}"/><path d="M${x + 8} ${g - 14} L${x + 18} ${g - 62}" stroke="${INK}" stroke-width="3"/><path d="M${x + 18} ${g - 62} v30" stroke="${INK}" stroke-dasharray="2 2"/>` +
        well(x + 18, g, r - 30) + `<rect x="${x + 13}" y="${(g + r) / 2}" width="10" height="16" fill="none" stroke="#ec0d00" stroke-width="1.8"/>`;
      case 10: return `<rect x="${x - 16}" y="${g - 22}" width="32" height="22" fill="#35895f"/><path d="M${x - 8} ${g - 22}v-10h16v10" fill="#97aeba"/>` + well(x, g, r + 20) +
        `<path d="M${x} ${r - 20} l-6 -10 M${x} ${r - 20} l6 -10" stroke="#35895f" stroke-width="2"/>` +
        [r, r + 12].map(y => [-1, 1].map(s => `<path d="M${x} ${y} q${s * 20} -6 ${s * 44} ${4 * s}" fill="none" stroke="#f0f0f0" stroke-width="2"/>`).join('')).join('');
      case 11: return `<rect x="${x - 20}" y="${g - 34}" width="40" height="34" rx="4" fill="#d5d5d5" stroke="${INK}" stroke-width="1.6"/><path d="M${x - 20} ${g - 26}h40" stroke="${INK}"/><rect x="${x + 28}" y="${g - 14}" width="8" height="14" fill="#494949"/>`;
      case 12: return [[-30, 12, 60], [-14, 16, 82], [6, 12, 50], [22, 14, 40]].map(([dx, ww, hh]) => `<rect x="${x + dx}" y="${g - hh}" width="${ww}" height="${hh}" fill="#b9b9b9" stroke="${INK}" stroke-width="1.4"/>`).join('') +
        `<path d="M${x - 8} ${g - 82} q-4 -10 2 -18 q2 8 6 4 q2 8 -8 14z" fill="#c78a53"/>`;
    }
    return '';
  }

  function bands() {
    const offs = [-210, -140, -70, 0, 60];
    return offs.map((off, k) => {
      const pts = [];
      for (let x = 0; x < W; x += 20) pts.push(x);
      pts.push(W);
      const p = pts.map(x => `${x},${R + off - 60 * Math.max(0, 1 - Math.abs(x - 760) / 420)}`).join(' ');
      return `<polygon points="0,${H} ${p} ${W},${H}" fill="${COLS[k]}"/>`;
    }).join('');
  }

  function scene() {
    let s = `<defs><pattern id="jr-cem" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 6L6 0" stroke="#636363" stroke-width="1"/></pattern>` +
      `<linearGradient id="jr-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e4eaf1"/><stop offset="1" stop-color="#f3f3f3"/></linearGradient></defs>`;
    s += `<rect width="${W}" height="${H}" fill="url(#jr-sky)"/><rect y="${G}" width="${W}" height="${H - G}" fill="#d3ccb4"/>` + bands();
    s += `<line x1="0" y1="${G}" x2="${W}" y2="${G}" stroke="#5d5d5d" stroke-width="1.5"/>`;
    [['地表', G], ['1000 m', G + 100], ['2000 m', G + 200], ['3000 m', R]].forEach(([t, y]) => {
      s += `<text x="14" y="${y + 4}" font-size="12" fill="#3f3f3f">${t}</text><line x1="56" y1="${y}" x2="66" y2="${y}" stroke="#575757"/>`;
    });
    s += `<text x="1150" y="${R + 92}" font-size="11" fill="#f2f2f2" text-anchor="middle">储层（背斜圈闭，示意）</text>`;
    // 地面勘探与井场
    s += icon(0, 120, G, R) + icon(1, 250, G, R) + icon(2, WX, G, R + 40) + icon(3, WX + 75, G, R);
    // 井筒：套管与水泥、测井仪、完井筛管、射孔
    s += `<rect x="${WX - 7}" y="${G}" width="14" height="${300 - G}" fill="url(#jr-cem)" stroke="#494949"/>`;
    s += `<line x1="${WX}" y1="${G}" x2="${WX}" y2="${R + 30}" stroke="#2d364b" stroke-width="3"/>`;
    s += `<rect x="${WX - 4}" y="250" width="8" height="26" rx="4" fill="#b89f6c" stroke="${INK}"/>`;
    for (let k = 0; k < 5; k++) s += `<line x1="${WX - 6}" y1="${R - 20 + k * 6}" x2="${WX + 6}" y2="${R - 20 + k * 6}" stroke="#fff" stroke-width="1.5"/>`;
    [R + 8, R + 20].forEach(y => [-1, 1].forEach(sx => { s += `<path d="M${WX} ${y} l${sx * 24} 0" stroke="#ec0d00" stroke-width="2.2"/>`; }));
    // 注入井、采油、修井、储运与炼化
    s += icon(10, IX, G, R + 10) + icon(8, PX + 36, G, R) + icon(9, PX + 120, G, R);
    s += `<path d="M${IX + 30} ${R + 8} C${IX + 90} ${R - 6},${PX - 60} ${R - 10},${PX - 10} ${R + 2}" fill="none" stroke="#212836" stroke-width="3" stroke-dasharray="2 6" opacity=".7"/>`;
    s += icon(11, 1120, G, R) + icon(12, 1240, G, R);
    s += `<path d="M${PX + 30} ${G - 6} H1100 M1140 ${G - 6} H1210" stroke="#494949" stroke-width="5"/>`;
    // 金色旅程虚线
    const path = `M120 ${G - 110} L250 ${G - 110} L${WX} ${G - 110} L${WX + 75} ${G - 62} L${WX + 60} 230 L${WX + 60} ${R + 50} L${PX - 20} ${R + 50} L${PX - 20} ${G - 110} L1240 ${G - 110}`;
    s += `<path d="${path}" fill="none" stroke="#bd7d1e" stroke-width="2.4" stroke-dasharray="7 5"/>`;
    s += `<text x="${W - 20}" y="${H - 14}" font-size="11" fill="#f2f2f2" text-anchor="end">金色虚线＝作业顺序：地面勘探 → 沿井筒向下 → 储层 → 采出地面 → 储运炼化（深度示意，纵向放大）</text>`;
    return s;
  }

  function markers(stages, sel) {
    return stages.map((st, i) => {
      const p = STOPS[i], on = i === sel, has = st.cases > 0;
      let label;
      if (p.label === 'right') label = `<text x="${p.x + 22}" y="${p.y + 5}" text-anchor="start">${st.name}</text>`;
      else if (p.label === 'below') label = `<text x="${p.x}" y="${p.y + 30}" text-anchor="middle">${st.name}</text>`;
      else label = `<text x="${p.x}" y="${p.y - 20}" text-anchor="middle">${st.name}</text>`;
      return `<g class="jr-stop${on ? ' on' : ''}${has ? ' has' : ''}" data-stop="${i}" role="button" tabindex="0" aria-label="${String(i + 1).padStart(2, '0')} ${st.name}，${st.count} 个场景${has ? '，' + st.cases + ' 个可运行案例' : ''}">` +
        `<circle class="jr-hit" cx="${p.x}" cy="${p.y}" r="22"/>${on ? `<circle class="jr-pulse" cx="${p.x}" cy="${p.y}" r="16"/>` : ''}` +
        `<circle class="jr-dot" cx="${p.x}" cy="${p.y}" r="${on ? 14 : 11}"/><text class="jr-no" x="${p.x}" y="${p.y + 4}" text-anchor="middle">${String(i + 1).padStart(2, '0')}</text>` +
        (has ? `<circle cx="${p.x + 10}" cy="${p.y - 10}" r="4" fill="#1f508b"/>` : '') + `<g class="jr-label">${label}</g></g>`;
    }).join('');
  }

  const FULL = [0, 0, W, H], ZOOM = 1.9, PANEL_FRACTION = 0.355;
  function target(i) {
    const vw = W / ZOOM, vh = H / ZOOM, visible = vw * (1 - PANEL_FRACTION);
    const [cx, cy] = FOCUS[i];
    let vx = cx - visible / 2, vy = Math.min(cy - vh / 2, STOPS[i].y - 46);
    vx = Math.min(vx, STOPS[i].x - 70);
    vx = Math.max(0, Math.min(W - visible, vx));
    vy = Math.max(0, Math.min(H - vh, vy));
    return [vx, vy, vw, vh];
  }
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function animate(svg, to, done) {
    const from = (svg.getAttribute('viewBox') || FULL.join(' ')).split(/\s+/).map(Number);
    if (svg._jrAnim) cancelAnimationFrame(svg._jrAnim);
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const dur = reduce ? 0 : 650, t0 = performance.now();
    const step = now => {
      const k = dur ? Math.min(1, (now - t0) / dur) : 1, e = ease(k);
      svg.setAttribute('viewBox', from.map((v, j) => v + (to[j] - v) * e).join(' '));
      if (k < 1) svg._jrAnim = requestAnimationFrame(step); else { svg._jrAnim = null; if (done) done(); }
    };
    svg._jrAnim = requestAnimationFrame(step);
  }

  // 挂载：root 为容器；stages 为 [{id,name,count,cases}]；panel(i) 返回面板 HTML；bindPanel(panelEl,i) 绑定面板交互
  function mount(root, opts) {
    const { stages, panel, bindPanel } = opts;
    let sel = -1;
    root.innerHTML = `<div class="jr-stage"><svg class="jr-svg" viewBox="${FULL.join(' ')}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="石油作业旅程：从地面勘探沿井筒向下到储层，再采出地面、储运与炼化">${scene()}<g class="jr-markers">${markers(stages, sel)}</g></svg>` +
      `<div class="jr-hint">点击圆形数字，原地放大查看该环节的场景</div><aside class="jr-panel" aria-live="polite" aria-hidden="true"></aside></div>`;
    const svg = root.querySelector('.jr-svg'), panelEl = root.querySelector('.jr-panel'), stageEl = root.querySelector('.jr-stage');
    const drawMarkers = () => { root.querySelector('.jr-markers').innerHTML = markers(stages, sel); };
    function open(i) {
      sel = i; drawMarkers(); stageEl.classList.add('zoomed');
      panelEl.innerHTML = panel(i, PLACE[i]); panelEl.setAttribute('aria-hidden', 'false');
      bindPanel(panelEl, i, { open, close });
      animate(svg, target(i));
    }
    function close() {
      sel = -1; drawMarkers(); stageEl.classList.remove('zoomed'); panelEl.setAttribute('aria-hidden', 'true');
      animate(svg, FULL);
    }
    root.addEventListener('click', e => { const g = e.target.closest('[data-stop]'); if (g) open(Number(g.dataset.stop)); });
    root.addEventListener('keydown', e => {
      const g = e.target.closest('[data-stop]');
      if (g && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); open(Number(g.dataset.stop)); }
      if (e.key === 'Escape' && sel >= 0) close();
    });
    return { open, close, get selected() { return sel; } };
  }

  window.PetroJourney = { mount, PLACE };
})();
