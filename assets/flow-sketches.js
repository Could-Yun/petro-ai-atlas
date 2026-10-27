/* Small, method-specific process diagrams. Values illustrate operations, not test scores. */
(function(g){'use strict';
const S=g.PetroScience,colors=S.darkPalette;
const txt=(s,x,y,size=12,col='#dce8df')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${col}">${String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}</text>`;
const line=(x,y,x2,y2,col=colors[3],w=2,dash='')=>`<path d="M${x} ${y}L${x2} ${y2}" fill="none" stroke="${col}" stroke-width="${w}" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;
const dot=(x,y,k=0,r=4)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${colors[k]}"/>`;
const rect=(x,y,w,h,col='#2c555b')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="2" fill="${col}"/>`;
const poly=(pts,k=0,w=2)=>`<polyline points="${pts.map(p=>p.join(',')).join(' ')}" fill="none" stroke="${colors[k]}" stroke-width="${w}"/>`;
let noiseSeed=71;const noise=Array.from({length:100},()=>{noiseSeed=(1664525*noiseSeed+1013904223)>>>0;return noiseSeed/4294967296*2-1});
const arrow=(x,y,x2,y2)=>line(x,y,x2,y2,colors[0])+line(x2-7,y2-5,x2,y2,colors[0])+line(x2-7,y2+5,x2,y2,colors[0]);
function image(kind=0){let z=rect(28,32,250,132);for(let j=0;j<7;j++){const y=48+j*15;if(kind===1)z+=line(38,y,147,y+2,colors[j%2])+line(154,y+13,269,y+15,colors[j%2]);else z+=poly(Array.from({length:35},(_,i)=>[38+i*6.7,y+Math.sin(i*.28+j*.12)*4]),j%3,1.6)}return z}
function scatter(split=false){let z='';for(let i=0;i<32;i++){const k=i%3,x=65+k*69+Math.sin(i*2.7)*19,y=80+(i%7)*10+Math.cos(i*1.9)*9;z+=dot(x,y,k,3)}if(split)z+=line(175,30,175,183,colors[3],1,'5 5');return z}
function glyph(k,x,y){return k===0?line(x-12,y,x+12,y,colors[k],3)+line(x,y-12,x,y+12,colors[k],3):k===1?`<circle cx="${x}" cy="${y}" r="11" fill="none" stroke="${colors[k]}" stroke-width="3"/>`:`<path d="M${x} ${y-12}L${x-12} ${y+10}H${x+12}Z" fill="none" stroke="${colors[k]}" stroke-width="3"/>`}
function probability(){let z=line(30,169,270,169)+line(30,169,30,36);const pts=Array.from({length:51},(_,j)=>[35+j*4.6,160-110/(1+Math.exp(-(j-25)/5))]);return z+poly(pts,1)+line(32,105,265,105,colors[0],1,'5 4')+txt('特征响应 → 概率',65,199)}
function wave(j=0){return Array.from({length:100},(_,i)=>[25+i*2.6,65+j*54-S.waveform(i,30+j*3)*15])}
function sketch(c,i){let z='',note='';
switch(c.id){
case 'geo-spectral':
 if(i===0){for(let j=0;j<3;j++){z+=rect(50+j*41,42+j*29,135,76,colors[j])+txt('B'+(j+1),58+j*41,64+j*29,13,'#252c3d')}z+=line(170,35,170,177,'#fff',1)+line(140,112,200,112,'#fff',1);note='三个波段必须对应同一地点。'}
 if(i===1){z=rect(23,40,120,136)+rect(165,40,120,136)+txt('独立训练样本',26,28)+txt('测试图幅',180,28);for(let side=0;side<2;side++)for(let j=0;j<24;j++)z+=dot(37+side*142+j%4*28,56+Math.floor(j/4)*21,j%3,3);z+=txt('两组均包含三个岩类',66,203);note='演示独立生成训练样本；真实项目按地块划分。'}
 if(i===2){const layers=[{x:45,n:3},{x:151,n:10},{x:257,n:3}];layers.slice(0,2).forEach((a,j)=>{const b=layers[j+1];for(let u=0;u<a.n;u++)for(let v=0;v<b.n;v++)z+=line(a.x,40+u*140/(a.n-1),b.x,40+v*140/(b.n-1),'#40636a',.7)});layers.forEach((a,j)=>{for(let u=0;u<a.n;u++)z+=dot(a.x,40+u*140/(a.n-1),j,5);z+=txt([3,10,3][j]+' 个单元',a.x-23,204)});note='真实演示运行 3→10→3 的小型 MLP。'}
 if(i===3){const vals=[.72,.18,.10];vals.forEach((v,j)=>z+=rect(70,45+j*42,v*220,23,colors[j])+txt(c.labels[j],22,62+j*42)+txt(v.toFixed(2),235,62+j*42));z+=txt('示例 max(p)=0.72',67,195);note='示例：阈值 0.80 时，此像素留待复核。'}break;
case 'geo-anomaly':
 if(i===0){for(let j=0;j<24;j++)z+=dot(35+j%6*43,40+Math.floor(j/6)*38,j===16?2:3,j===16?6:4);z+=txt('点位 × 三项化验记录',39,207);note='保留异常点与污染记录，先做采样质控。'}
 if(i===1){z=scatter()+txt('仅用独立背景样本建参考库',30,201);note='近邻方法存储参考样本，无神经网络训练。'}
 if(i===2){let q=[232,115],ns=[[65,70],[80,140],[111,65],[128,153],[154,106]];ns.forEach(p=>z+=line(...p,...q,'#6a9190',1)+dot(...p,1,5));z+=dot(...q,0,7)+txt('待测点',217,94)+txt('score = 五个距离的平均',30,201);note='图示为二维投影；实际使用三维指标距离。'}
 if(i===3){z=rect(25,25,252,151)+`<ellipse cx="194" cy="81" rx="50" ry="30" fill="none" stroke="${colors[0]}"/>`+rect(50,117,68,36,'#474747')+dot(180,74,0)+dot(212,90,0)+dot(76,132,2)+txt('联合异常',171,48)+txt('污染复查',46,200);note='异常偏离背景；需复采才能判断成因。'}break;
case 'geo-symbol':
 if(i===0){z=image();for(let j=0;j<3;j++)z+=`<rect x="${53+j*77}" y="69" width="40" height="40" fill="#273041" stroke="${colors[j]}"/>`+glyph(j,73+j*77,89);note='示例已提供中心；真实流程先定位候选框。'}
 if(i===1){for(let j=0;j<3;j++)z+=rect(35+j*87,43,68,90)+glyph(j,69+j*87,83)+txt('11 × 11',42+j*87,155);z+=txt('每个符号保留 121 个灰度像素',32,199);note='训练库加入位移和污损，与测试独立生成。'}
 if(i===2){[0,0,0,1,2].forEach((k,j)=>z+=glyph(k,45+j*53,91));z+=txt('五近邻投票：3 : 1 : 1',40,149)+txt('示例置信度 = 3 / 5 = 0.60',30,189);note='按相似度投票，置信度不等于校准概率。'}
 if(i===3){['类别      x      y','钻孔    128     42','产状     85    113','待复核  210     76'].forEach((s,j)=>z+=txt(s,43,52+j*39,15,j===3?colors[2]:'#dce8df'));note='将类别连回像素坐标，再由图例赋予语义。'}break;
case 'geo-fracture':
 if(i===0){z=rect(35,35,232,125,'#9eaf99')+line(65,45,218,140,'#2b3448',4)+line(225,42,135,153,'#2b3448',4)+line(45,183,255,183,colors[0],3)+txt('统一比例 / 正视影像',60,211);note='图像尺度统一后才能比较迹线统计。'}
 if(i===1){for(let a=0;a<12;a++){let theta=a*Math.PI/12;z+=line(150-Math.cos(theta)*72,106-Math.sin(theta)*72,150+Math.cos(theta)*72,106+Math.sin(theta)*72,colors[a===2?0:3],a===2?4:1)}z+=txt('0°—165°，每 15° 一个方向',42,201);note='12 个方向响应描述局部暗线，而非三维产状。'}
 if(i===2){z=probability();note='逻辑回归拟合方向特征到裂缝概率的映射。'}
 if(i===3){for(let a=0;a<12;a++){let th=a*Math.PI/12,r=20+45*Math.abs(Math.cos(th-.6));z+=line(150,108,150+Math.cos(th)*r,108+Math.sin(th)*r,colors[1],6)+line(150,108,150-Math.cos(th)*r,108-Math.sin(th)*r,colors[1],6)}z+=txt('方向示意，定量玫瑰图见演示',38,205);note='对照真值统计 IoU，同时检查方向分布。'}break;
case 'seis-fault':
 if(i===0){z=image(1);note='同一反射事件在断层两侧产生错动。'}
 if(i===1){z=image(1)+`<rect x="120" y="77" width="67" height="51" fill="none" stroke="${colors[0]}"/>`+arrow(98,102,128,102)+arrow(211,102,179,102);z+=txt('跨窗口比较连续性',77,200);note='多尺度横向差异用于识别不连续。'}
 if(i===2){z=probability();note='独立像素标签监督逻辑回归，输出概率。'}
 if(i===3){z=image(1)+line(151,36,151,167,colors[0],7)+txt('高阈值：少误检，也可能多漏检',27,201);note='用 Precision、Recall、IoU 检查取舍。'}break;
case 'seis-facies':
 if(i===0){['振幅','频率','连续性'].forEach((s,j)=>z+=rect(49,43+j*46,[170,115,207][j],23,colors[j])+txt(s,49,36+j*46));note='三项属性标准化，避免量纲主导距离。'}
 if(i===1){z=scatter();[0,1,2].forEach(k=>{z+=line(64+k*69,80,77+k*69,100,colors[k],2)+`<circle cx="${77+k*69}" cy="100" r="10" fill="none" stroke="${colors[k]}"/>`});z+=txt('分配样本 ↔ 更新中心',60,200);note='K-means 反复更新中心，不使用测试类别。'}
 if(i===2){for(let j=0;j<3;j++)z+=rect(35+j*82,40,80,130,colors[j])+txt('簇 '+(j+1),48+j*82,195);note='把各像素分给最近中心，生成空间分区。'}
 if(i===3){z=scatter()+line(225,35,225,174,colors[0],3)+txt('井点 / 地质背景',148,202);note='用独立参考标签评价，并用井点解释地质含义。'}break;
case 'seis-firstbreak':
 if(i===0){for(let j=0;j<3;j++)z+=poly(wave(j),j,1.4);z+=txt('展示 3 道；实际 24 道 × 170 点',26,214);note='固定道序与 2 ms 采样间隔，训练炮集独立。'}
 if(i===1){z=poly(wave(1),1)+rect(99,146,31,12,colors[0])+txt('短窗',99,183)+txt('能量 / 前后比 / 邻道特征',28,212);note='将局部波形转成可比较的窗口特征。'}
 if(i===2){z=probability()+line(150,30,150,172,colors[2],2)+txt('首个越阈值点',162,48);note='取首个满足条件的位置；另算 STA/LTA 基线。'}
 if(i===3){[0,1,2].forEach(j=>z+=line(73,60+j*46,235,60+j*46,'#42676b',1)+dot(135+j*8,60+j*46,3)+dot(148+j*10,60+j*46,1)+line(135+j*8,60+j*46,148+j*10,60+j*46,colors[0],2));z+=txt('真值点 → 拾取点：逐道误差',35,208);note='误差使用 ms；漏拾单独统计，不能计为零。'}break;
case 'seis-reservoir':
 if(i===0){z=image();for(let j=0;j<4;j++)z+=line(65+j*58,27,65+j*58,176,colors[0],1.4);z+=txt('同尺度的属性与井点样本',40,207);note='生产流程需井震匹配；演示直接生成同网格样本。'}
 if(i===1){['1, Z, A','Z², A², Z·A'].forEach((s,j)=>z+=rect(46,44+j*70,222,48)+txt(s,70,75+j*70,22,colors[j]));note='Z 为阻抗、A 为振幅；增加平方及交互项。'}
 if(i===2){z=scatter(true)+txt('有井训练区',30,28)+txt('右部外推区',179,28)+txt('最小化误差 + 系数正则',45,203);note='只从训练井拟合系数，右部样本不参与。'}
 if(i===3){z=line(35,176,272,176)+line(35,176,35,35)+line(35,176,272,35,colors[3],1,'5 4');for(let j=0;j<24;j++)z+=dot(60+j*7.9,162-j*4.7+Math.sin(j*3)*9,j%2,3);z+=txt('预测 vs 合成真值（示意）',36,210);note='分别统计有井区和外推区误差，不能只看平滑。'}break;
case 'seis-denoise':
 if(i===0){const pts=Array.from({length:90},(_,j)=>[25+j*2.9,65-Math.sin(j*.23)*21]);z=poly(pts.map(([x,y],j)=>[x,y+noise[j]*8]),0)+poly(pts.map(([x,y])=>[x,y+84]),1)+txt('含噪训练输入',30,25)+txt('干净中心标签',30,115);note='成对训练与测试独立；真实资料难获干净标签。'}
 if(i===1){for(let j=0;j<9;j++)z+=rect(42+j%3*40,40+Math.floor(j/3)*40,37,37)+txt('w'+(j+1),49+j%3*40,63+Math.floor(j/3)*40,12,colors[0]);z+=arrow(172,100,223,100)+dot(250,100,1,10)+txt('中心点',226,140);note='最小二乘学习九个系数，并非手工均值核。'}
 if(i===2){z=image()+`<rect x="105" y="72" width="51" height="51" fill="none" stroke="${colors[0]}"/>`+arrow(168,100,235,100)+dot(250,100,1,8)+txt('滑动窗口 → 预测中心',45,206);note='学习核扫描测试剖面；另计算均值滤波基线。'}
 if(i===3){for(let j=0;j<3;j++){const pts=Array.from({length:90},(_,k)=>{let clean=Math.sin(k*.23)*15,n=noise[k]*7;return [25+k*2.9,48+j*57-(j===0?clean+n:j===1?clean+n*.2:n*.8)]});z+=poly(pts,j,1.4)}z+=txt('输入 / 输出 / 相减残差，同一尺度',20,216);note='检查残差是否仍含反射事件，再看信噪比。'}break;
}
return {svg:`<g transform="translate(38 85)">${z}</g>`,note};
}
g.PetroFlowSketches={sketch};
})(window);
