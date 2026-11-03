/* Browser-only CSV reader and CPU trainer for the spectral lithology demo. */
(function (g) {
  "use strict";
  var MAX_BYTES = 10 * 1024 * 1024;
  var MAX_ROWS = 12000;
  var NONE = "__none__";
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function countDelimiter(line, delimiter) {
    var quoted = false, count = 0;
    for (var i = 0; i < line.length; i++) {
      var c = line[i];
      if (c === '"' && line[i + 1] === '"' && quoted) { i++; continue; }
      if (c === '"') quoted = !quoted;
      else if (!quoted && c === delimiter) count++;
    }
    return count;
  }
  function parseCSV(text) {
    text = String(text || "").replace(/^\uFEFF/, "");
    var first = text.split(/\r?\n/, 1)[0];
    var delimiters = [",", "\t", ";"];
    delimiters.sort(function (a, b) { return countDelimiter(first, b) - countDelimiter(first, a); });
    var delimiter = delimiters[0];
    var rows = [], row = [], cell = "", quoted = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (quoted && c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = !quoted;
      else if (!quoted && c === delimiter) { row.push(cell.trim()); cell = ""; }
      else if (!quoted && (c === "\n" || c === "\r")) {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cell.trim()); cell = "";
        if (row.some(function (v) { return v !== ""; })) rows.push(row);
        row = [];
      } else cell += c;
    }
    row.push(cell.trim());
    if (row.some(function (v) { return v !== ""; })) rows.push(row);
    if (rows.length < 2) throw new Error("CSV 至少要有一行表头和一行数据。");
    var headers = rows.shift().map(function (h, i) { return h || ("未命名列" + (i + 1)); });
    var seen = {};
    headers = headers.map(function (h) {
      seen[h] = (seen[h] || 0) + 1;
      return seen[h] > 1 ? h + "_" + seen[h] : h;
    });
    var dataRows = rows.map(function (r) {
      while (r.length < headers.length) r.push("");
      return r.slice(0, headers.length);
    });
    if (dataRows.length > MAX_ROWS) throw new Error("当前试点最多处理 " + MAX_ROWS.toLocaleString("zh-CN") + " 行，请先抽样或分块。");
    return { headers: headers, rows: dataRows, delimiter: delimiter };
  }
  function random(seed) {
    var a = seed >>> 0;
    return function () {
      a += 0x6D2B79F5;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t ^= t + Math.imul(t ^ t >>> 7, 61 | t);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function shuffle(a, r) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(r() * (i + 1)), t = a[i];
      a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function split(rows, seed) {
    var classes = [0, 1, 2];
    var train = [], validation = [], method = "";
    var xs = rows.map(function (r) { return r.x; }).filter(Number.isFinite);
    if (xs.length === rows.length && new Set(xs).size >= 5) {
      var sorted = Array.from(new Set(xs)).sort(function (a, b) { return a - b; });
      var cut = sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * 0.8))];
      rows.forEach(function (r, i) { (r.x >= cut ? validation : train).push(i); });
      var valClasses = new Set(validation.map(function (i) { return rows[i].truth; }));
      var trainClasses = new Set(train.map(function (i) { return rows[i].truth; }));
      if (validation.length >= 3 && classes.every(function (k) { return !rows.some(function (r) { return r.truth === k; }) || (valClasses.has(k) && trainClasses.has(k)); })) {
        method = "按 X 坐标高值侧留出空间验证样本";
      } else { train = []; validation = []; }
    }
    if (!validation.length) {
      var r = random(seed ^ 0x51A7);
      classes.forEach(function (k) {
        var group = rows.map(function (x, i) { return x.truth === k ? i : -1; }).filter(function (i) { return i >= 0; });
        shuffle(group, r);
        var n = Math.max(1, Math.floor(group.length * 0.2));
        validation = validation.concat(group.slice(0, n));
        train = train.concat(group.slice(n));
      });
      method = "按类别分层随机留出；建议补充坐标后做空间验证";
    }
    if (train.length < 6 || validation.length < 3) throw new Error("可用样本不足以划分训练集和验证集。请增加标注样本。");
    return { train: train, validation: validation, method: method };
  }
  function mean(a) { return a.reduce(function (s, v) { return s + v; }, 0) / (a.length || 1); }
  async function train(rows, trainIndices, epochs, seed, onProgress, isCancelled) {
    var xs = rows.map(function (r) { return [r.b1, r.b2, r.b3]; });
    var ys = rows.map(function (r) { return r.truth; });
    var mu = [0, 1, 2].map(function (j) { return mean(trainIndices.map(function (i) { return xs[i][j]; })); });
    var sd = mu.map(function (m, j) {
      var v = Math.sqrt(mean(trainIndices.map(function (i) { return Math.pow(xs[i][j] - m, 2); })));
      return v || 1;
    });
    var normalized = xs.map(function (x) { return x.map(function (v, j) { return (v - mu[j]) / sd[j]; }); });
    var r = random(seed ^ 0xC0FFEE);
    function gauss() { return Math.sqrt(-2 * Math.log(Math.max(1e-8, r()))) * Math.cos(6.2831853 * r()); }
    var hidden = 10, output = 3;
    var W = Array.from({ length: hidden }, function () { return Array.from({ length: 4 }, function () { return gauss() * 0.23; }); });
    var V = Array.from({ length: output }, function () { return Array.from({ length: hidden + 1 }, function () { return gauss() * 0.23; }); });
    var losses = [];
    function forward(x) {
      var h = W.map(function (w) { return Math.tanh(w[0] + x.reduce(function (s, v, j) { return s + w[j + 1] * v; }, 0)); });
      var z = V.map(function (v) { return v[0] + h.reduce(function (s, q, j) { return s + v[j + 1] * q; }, 0); });
      var max = Math.max.apply(null, z), p = z.map(function (v) { return Math.exp(v - max); }), total = p.reduce(function (s, v) { return s + v; }, 0);
      return { h: h, p: p.map(function (v) { return v / total; }) };
    }
    for (var ep = 0; ep < epochs; ep++) {
      if (isCancelled()) throw new Error("训练已取消。");
      var order = shuffle(trainIndices.slice(), r), loss = 0;
      order.forEach(function (i) {
        var x = normalized[i], f = forward(x), e = f.p.map(function (v, k) { return v - (ys[i] === k ? 1 : 0); });
        loss -= Math.log(f.p[ys[i]] + 1e-8);
        var hiddenGrad = f.h.map(function (v, j) {
          return (1 - v * v) * e.reduce(function (s, q, k) { return s + q * V[k][j + 1]; }, 0);
        });
        for (var k = 0; k < output; k++) {
          V[k][0] -= 0.025 * e[k];
          for (var j = 0; j < hidden; j++) V[k][j + 1] -= 0.025 * e[k] * f.h[j];
        }
        for (var h = 0; h < hidden; h++) {
          W[h][0] -= 0.025 * hiddenGrad[h];
          for (var b = 0; b < 3; b++) W[h][b + 1] -= 0.025 * hiddenGrad[h] * x[b];
        }
      });
      if (ep % 2 === 0 || ep === epochs - 1) losses.push(loss / order.length);
      onProgress(ep + 1, epochs, loss / order.length);
      await new Promise(function (resolve) { setTimeout(resolve, 0); });
    }
    return {
      losses: losses,
      predict: function (x) {
        var z = x.map(function (v, j) { return (v - mu[j]) / sd[j]; });
        return forward(z).p;
      }
    };
  }
  function markup() {
    return '<section class="user-data-box" id="user-data-box">' +
      '<div class="user-data-heading"><b>数据来源</b><span id="user-source-label">教学合成数据</span></div>' +
      '<div class="user-source-switch"><button type="button" id="use-synthetic" class="is-active">教学合成</button><button type="button" id="use-user-csv">我的 CSV</button></div>' +
      '<p class="user-data-help">试点支持带岩性标签的 CSV：三波段输入训练 MLP。点击下载模板，或上传后自行匹配列名。</p>' +
      '<a class="user-template-link" href="user-data-template.csv" download>↓ 下载 CSV 模板</a>' +
      '<div class="user-data-panel" id="user-data-panel" hidden>' +
      '<label class="user-drop" id="user-drop" for="user-file"><b>选择或拖入 CSV / TSV</b><span>最多 10 MB、12,000 行；文件只在当前浏览器内读取</span><input id="user-file" type="file" accept=".csv,.tsv,text/csv,text/tab-separated-values"></label>' +
      '<p class="user-file-name" id="user-file-name">尚未选择文件</p>' +
      '<div class="user-mapping" id="user-mapping" hidden>' +
      '<b>匹配数据列</b><div class="user-map-grid">' +
      '<label>B1 波段<select id="map-b1"></select></label><label>B2 波段<select id="map-b2"></select></label><label>B3 波段<select id="map-b3"></select></label>' +
      '<label>岩性标签<select id="map-label"></select></label><label>X / 列坐标（可选）<select id="map-x"></select></label><label>Y / 行坐标（可选）<select id="map-y"></select></label></div>' +
      '<div class="user-class-map"><span>标签值对应</span>' +
      '<label>砂岩<select id="map-class-0"></select></label><label>页岩<select id="map-class-1"></select></label><label>灰岩<select id="map-class-2"></select></label></div>' +
      '<div class="user-preview" id="user-preview"></div>' +
      '<div class="user-train-controls"><label>训练轮数<select id="user-epochs"><option value="30">30 轮</option><option value="50" selected>50 轮</option><option value="100">100 轮</option></select></label>' +
      '<button type="button" class="control-btn" id="user-train" disabled>开始训练并验证</button><button type="button" class="control-btn secondary" id="user-cancel" hidden>取消训练</button>' +
      '<button type="button" class="control-btn secondary" id="user-clear">清除文件</button></div>' +
      '<progress id="user-progress" max="100" value="0" hidden></progress><p class="user-status" id="user-status" aria-live="polite"></p></div></section>';
  }
  function fingerprint(text) {
    var hash = 2166136261;
    for (var i = 0; i < text.length; i++) { hash ^= text.charCodeAt(i); hash = Math.imul(hash, 16777619); }
    return "fnv1a-" + (hash >>> 0).toString(16).padStart(8, "0");
  }
  function guessColumn(headers, patterns) {
    for (var i = 0; i < headers.length; i++) if (patterns.some(function (p) { return p.test(headers[i]); })) return String(i);
    return "";
  }
  function mount(callbacks) {
    var box = document.getElementById("user-data-box");
    if (!box) return null;
    var csv = null, prepared = null, cancelled = false;
    var $ = function (id) { return document.getElementById(id); };
    function setMode(mode) {
      var user = mode === "user";
      $("user-data-panel").hidden = !user;
      $("use-synthetic").classList.toggle("is-active", !user);
      $("use-user-csv").classList.toggle("is-active", user);
      $("user-source-label").textContent = user ? "上传数据训练" : "教学合成数据";
      if (callbacks.onModeChange) callbacks.onModeChange(mode);
    }
    function setStatus(text, kind) {
      $("user-status").textContent = text;
      $("user-status").className = "user-status" + (kind ? " " + kind : "");
    }
    function fillSelect(id, includeNone, selected) {
      var el = $(id), html = '<option value="">' + (includeNone ? "不使用坐标" : "请选择") + "</option>";
      csv.headers.forEach(function (h, i) { html += '<option value="' + i + '">' + esc(h) + "</option>"; });
      el.innerHTML = html;
      if (selected !== undefined && selected !== null) el.value = String(selected);
    }
    function fillClasses() {
      if ($("map-label").value === "") {
        ["map-class-0", "map-class-1", "map-class-2"].forEach(function (id) { $(id).innerHTML = '<option value="' + NONE + '">不使用</option>'; });
        return [];
      }
      var labelIndex = Number($("map-label").value);
      var values = Array.from(new Set(csv.rows.map(function (r) { return r[labelIndex] || ""; }).filter(Boolean))).sort(function (a, b) { return a.localeCompare(b, "zh-CN", { numeric: true }); });
      ["map-class-0", "map-class-1", "map-class-2"].forEach(function (id, target) {
        var el = $(id), option = '<option value="' + NONE + '">不使用</option>';
        values.forEach(function (v, i) { option += '<option value="' + i + '">' + esc(v) + "</option>"; });
        el.innerHTML = option;
        var guess = values.findIndex(function (v) {
          var s = v.toLowerCase();
          return target === 0 ? /砂|砂岩|sand/.test(s) : target === 1 ? /页|页岩|shale/.test(s) : /灰|灰岩|石灰|lime/.test(s);
        });
        if (guess < 0 && target < values.length) guess = target;
        el.value = guess >= 0 ? String(guess) : NONE;
      });
      return values;
    }
    function loadFile(file) {
      if (!file) return;
      setMode("user");
      if (callbacks.onClear) callbacks.onClear();
      csv = null; prepared = null;
      $("user-train").disabled = true;
      $("user-mapping").hidden = true;
      $("user-file-name").textContent = file.name + " · " + (file.size / 1024).toFixed(1) + " KB";
      if (file.size > MAX_BYTES) { setStatus("文件超过 10 MB。请先裁剪或抽样后再上传。", "error"); return; }
      file.text().then(function (text) {
        try {
          csv = parseCSV(text);
          $("user-file-name").textContent = file.name + " · " + csv.rows.length.toLocaleString("zh-CN") + " 行 · " + (csv.delimiter === "\t" ? "制表符分隔" : csv.delimiter === ";" ? "分号分隔" : "逗号分隔");
          fillSelect("map-b1", false, guessColumn(csv.headers, [/^b1$/i, /band.?1/i, /波段.?1/]));
          fillSelect("map-b2", false, guessColumn(csv.headers, [/^b2$/i, /band.?2/i, /波段.?2/]));
          fillSelect("map-b3", false, guessColumn(csv.headers, [/^b3$/i, /band.?3/i, /波段.?3/]));
          fillSelect("map-label", false, guessColumn(csv.headers, [/岩性|类别|label|class|lith/i]));
          fillSelect("map-x", true, guessColumn(csv.headers, [/^x$/i, /^col(umn)?$/i, /列坐标/]));
          fillSelect("map-y", true, guessColumn(csv.headers, [/^y$/i, /^row$/i, /行坐标/]));
          fillClasses();
          $("user-mapping").hidden = false;
          prepare();
        } catch (err) {
          setStatus(err.message, "error");
        }
      }).catch(function () { setStatus("无法读取文件，请确认它是 UTF-8 编码的 CSV / TSV。", "error"); });
    }
    function prepare() {
      if (!csv) return;
      try {
        var selectedFields = ["map-b1", "map-b2", "map-b3", "map-label"].map(function (id) { return $(id).value; });
        if (selectedFields.some(function (v) { return v === "" || !Number.isInteger(Number(v)) || !csv.headers[Number(v)]; })) throw new Error("请为 B1、B2、B3 和岩性标签选择对应列。");
        var fields = selectedFields.map(Number);
        if (new Set(fields).size !== 4) throw new Error("B1、B2、B3 和岩性标签需对应不同的数据列。");
        var xIndex = $("map-x").value === "" ? -1 : Number($("map-x").value);
        var yIndex = $("map-y").value === "" ? -1 : Number($("map-y").value);
        if ((xIndex >= 0) !== (yIndex >= 0)) throw new Error("X、Y 坐标请同时选择，或都不使用。");
        var values = Array.from(new Set(csv.rows.map(function (r) { return r[fields[3]] || ""; }).filter(Boolean)));
        values.sort(function (a, b) { return a.localeCompare(b, "zh-CN", { numeric: true }); });
        var selectedLabels = ["map-class-0", "map-class-1", "map-class-2"].map(function (id) {
          var rawIndex = $(id).value;
          return rawIndex === NONE ? null : values[Number(rawIndex)];
        });
        var usedLabels = selectedLabels.filter(function (v) { return v !== null; });
        if (new Set(usedLabels).size !== usedLabels.length) throw new Error("同一个原始标签不能重复对应多个岩性类别。");
        var rawMap = {};
        selectedLabels.forEach(function (rawValue, k) { if (rawValue !== null) rawMap[rawValue] = k; });
        if (Object.keys(rawMap).length < 2) throw new Error("至少映射两类岩性标签，才能训练和验证分类模型。");
        if (new Set(Object.keys(rawMap).map(function (v) { return rawMap[v]; })).size !== Object.keys(rawMap).length) throw new Error("每个原始标签只能对应一种目标岩性，请检查映射。");
        var rows = [], skipped = 0, counts = [0, 0, 0];
        csv.rows.forEach(function (r, i) {
          var rawLabel = r[fields[3]], truth = Object.prototype.hasOwnProperty.call(rawMap, rawLabel) ? rawMap[rawLabel] : null;
          var vals = fields.slice(0, 3).map(function (j) { return Number(r[j]); });
          var x = xIndex >= 0 ? Number(r[xIndex]) : NaN, y = yIndex >= 0 ? Number(r[yIndex]) : NaN;
          if (truth === null || vals.some(function (v) { return !Number.isFinite(v); }) || (xIndex >= 0 && (!Number.isFinite(x) || !Number.isFinite(y)))) { skipped++; return; }
          rows.push({ row: i + 2, x: x, y: y, b1: vals[0], b2: vals[1], b3: vals[2], truth: truth });
          counts[truth]++;
        });
        if (rows.length < 15) throw new Error("映射后有效样本不足 15 行；请检查数值列、标签映射和空值。");
        if (counts.filter(function (n) { return n > 0; }).some(function (n) { return n < 5; })) throw new Error("每个参与训练的类别至少需要 5 个有效样本。");
        prepared = { rows: rows, counts: counts, skipped: skipped, xField: xIndex >= 0 ? csv.headers[xIndex] : "", yField: yIndex >= 0 ? csv.headers[yIndex] : "" };
        $("user-train").disabled = false;
        $("user-preview").innerHTML = "<b>检查结果</b><span>" + rows.length.toLocaleString("zh-CN") + " 条有效样本 · " + skipped + " 条未映射或无效行 · 砂岩 " + counts[0] + " / 页岩 " + counts[1] + " / 灰岩 " + counts[2] + "</span>" +
          (xIndex >= 0 ? "<small>将按 X 坐标高值侧留出验证数据；样本图按 X、Y 坐标展示。</small>" : "<small>没有坐标列：模型可训练，但图中按 CSV 行号展示，不能视为空间分布图。</small>");
        setStatus("字段已匹配。确认类别数量后开始训练。", "ok");
      } catch (err) {
        prepared = null;
        $("user-train").disabled = true;
        $("user-preview").textContent = err.message;
        setStatus(err.message, "error");
      }
    }
    async function startTraining() {
      if (!prepared) { prepare(); if (!prepared) return; }
      var splitInfo;
      try { splitInfo = split(prepared.rows, 20261103); }
      catch (err) { setStatus(err.message, "error"); return; }
      cancelled = false;
      $("user-train").disabled = true;
      $("user-cancel").hidden = false;
      $("user-progress").hidden = false;
      $("user-progress").value = 0;
      var epochs = Number($("user-epochs").value);
      setStatus("CPU 训练中：0 / " + epochs + " 轮", "busy");
      try {
        var model = await train(prepared.rows, splitInfo.train, epochs, callbacks.getSeed ? callbacks.getSeed() : 20261103, function (ep, total) {
          $("user-progress").value = Math.round(ep / total * 100);
          setStatus("CPU 训练中：" + ep + " / " + total + " 轮", "busy");
        }, function () { return cancelled; });
        if (cancelled) throw new Error("训练已取消。");
        var text = csv.rows.map(function (r) { return r.join(","); }).join("\n");
        var datasetFingerprint = fingerprint(csv.headers.join(",") + "\n" + text);
        var fileName = $("user-file").files[0] ? $("user-file").files[0].name : "uploaded.csv";
        setStatus("训练完成。验证集 " + splitInfo.validation.length + " 条；" + splitInfo.method + "。", "ok");
        if (callbacks.onTrained) callbacks.onTrained({
          rows: prepared.rows, counts: prepared.counts, skipped: prepared.skipped, model: model,
          trainIndices: splitInfo.train, validationIndices: splitInfo.validation, splitMethod: splitInfo.method,
          hasCoordinates: Boolean(prepared.xField && prepared.yField), xField: prepared.xField, yField: prepared.yField,
          fileName: fileName, datasetFingerprint: datasetFingerprint, epochs: epochs
        });
      } catch (err) {
        setStatus(err.message, err.message.indexOf("取消") >= 0 ? "" : "error");
      } finally {
        $("user-train").disabled = !prepared;
        $("user-cancel").hidden = true;
        $("user-progress").hidden = true;
      }
    }
    $("use-synthetic").addEventListener("click", function () { setMode("synthetic"); });
    $("use-user-csv").addEventListener("click", function () { setMode("user"); });
    $("user-file").addEventListener("change", function (e) { loadFile(e.target.files && e.target.files[0]); });
    $("user-drop").addEventListener("dragover", function (e) { e.preventDefault(); $("user-drop").classList.add("dragging"); });
    $("user-drop").addEventListener("dragleave", function () { $("user-drop").classList.remove("dragging"); });
    $("user-drop").addEventListener("drop", function (e) { e.preventDefault(); $("user-drop").classList.remove("dragging"); loadFile(e.dataTransfer.files && e.dataTransfer.files[0]); });
    ["map-b1", "map-b2", "map-b3", "map-label", "map-x", "map-y", "map-class-0", "map-class-1", "map-class-2"].forEach(function (id) {
      $(id).addEventListener("change", function () {
        if (id === "map-label") fillClasses();
        if (callbacks.onClear) callbacks.onClear();
        prepare();
      });
    });
    $("user-train").addEventListener("click", startTraining);
    $("user-cancel").addEventListener("click", function () { cancelled = true; setStatus("正在结束当前训练轮…", "busy"); });
    $("user-clear").addEventListener("click", function () {
      cancelled = true; csv = null; prepared = null; $("user-file").value = ""; $("user-file-name").textContent = "尚未选择文件";
      $("user-mapping").hidden = true; $("user-progress").hidden = true; $("user-train").disabled = true; setStatus("文件已清除。原始数据不会保存在网页中。");
      if (callbacks.onClear) callbacks.onClear();
    });
    return { setMode: setMode };
  }
  g.GeoSpectralUserData = { markup: markup, mount: mount };
})(window);
