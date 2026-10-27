from pathlib import Path
p=Path(__file__).resolve().parents[1]/'assets'/'lab.js'
s=p.read_text(encoding='utf-8')
s=s.replace("'#a47769','#63805f'", "'#a47769','#bbc5b8'")
helper="""function legendItems(){const map={'geo-anomaly':[['未触发异常','#c6a765'],['触发异常','#53898c']],'geo-fracture':[['裂缝预测 / 真值方向','#d6ac4a'],['预测方向分布','#40817d']],'seis-fault':[['超阈值断层像素','#d6ac4a'],['负振幅','#266571'],['正振幅','#c5a76a']],'seis-firstbreak':[['合成真值','#70b6a5'],['模型拾取','#f1c75d'],['STA/LTA基线','#9eaaa1']],'seis-reservoir':[['有井区散点','#548b8c'],['外推区散点','#b49657']],'seis-denoise':[['负振幅','#266571'],['正振幅','#c5a76a']]};return map[C.id]||C.labels.map((l,i)=>[l,colors[i]])}\n"""
if 'function legendItems()' not in s: s=s.replace('let seed=20261023',helper+'let seed=20261023')
old='C.labels.map((l,i)=>`<span><i style="background:${colors[i]}"></i>${esc(l)}</span>`).join(\'\')'
new='legendItems().map(([l,col])=>`<span><i style="background:${col}"></i>${esc(l)}</span>`).join(\'\')'
s=s.replace(old,new).replace('background:#63805f','background:#bbc5b8')
s=s.replace('<label class="ctrl"><span>', '<label class="ctrl" for="${p[0]}"><span>')
p.write_text(s,encoding='utf-8')
css=p.with_name('lab.css')
extra='\n@media(min-width:761px) and (max-width:1100px){.lab-layout{grid-template-columns:1fr}.controls{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 20px;padding:16px}.controls h3{grid-column:1/-1;margin-bottom:15px}.ctrl{margin-bottom:12px}.control-note{grid-column:1/-1;margin:8px 0 0}.control-btn{align-self:end}.plots{grid-template-columns:1fr 1fr}}\n'
if extra not in css.read_text(encoding='utf-8'): css.write_text(css.read_text(encoding='utf-8')+extra,encoding='utf-8')
print('Aligned plot legends with encodings and improved tablet lab layout.')
