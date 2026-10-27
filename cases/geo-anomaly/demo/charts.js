/* Canvas plots with figure-scoped legends, explicit units and shared scales. */
(function(g){'use strict';const S=g.PetroScience,clamp=S.clamp;
const hex=h=>h.replace('#','').match(/../g).map(x=>parseInt(x,16)),mix=(a,b,t)=>a.map((v,i)=>Math.round(v+(b[i]-v)*t));
function color(v,scale){let t=clamp((v-scale.min)/(scale.max-scale.min||1));if(scale.mode==='gray')return mix([33,44,45],[239,239,220],t);if(scale.mode==='diverging')return t<.5?mix(hex('#24698f'),hex('#f2f2e7'),t*2):mix(hex('#f2f2e7'),hex('#bb8d3e'),(t-.5)*2);return t<.5?mix(hex('#183e59'),hex('#668c89'),t*2):mix(hex('#668c89'),hex('#dfca79'),(t-.5)*2)}
function fmt(v){return Math.abs(v)>=100?String(Math.round(v)):Math.abs(v)>=10?v.toFixed(1):Number(v.toFixed(2)).toString()}
function render(canvas,p,C){const d=p.data,ctx=canvas.getContext('2d'),W=1000,H=620;canvas.width=W;canvas.height=H;ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);let L=84,R=65,T=68,B=140,pw=W-L-R,ph=H-T-B;
function text(s,x,y,align='left',size=21,fill='#3f4b4e'){ctx.font=Math.round(size*1.3)+'px Segoe UI, Microsoft YaHei';ctx.fillStyle=fill;ctx.textAlign=align;ctx.fillText(String(s),x,y)}
function rule(x1,y1,x2,y2,col='#dce5de',width=1,dash=[]){ctx.save();ctx.strokeStyle=col;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.restore()}
function dot(x,y,col,r=4){ctx.beginPath();ctx.fillStyle=col;ctx.arc(x,y,r,0,Math.PI*2);ctx.fill()}
function legend(items,y=570){let x=L;items.forEach(it=>{const width=ctx.measureText(it.label).width+90;if(x+width>W-20){x=L;y+=28}if(it.dot)dot(x+13,y-7,it.color,5);else rule(x,y-7,x+28,y-7,it.color,3,it.dash||[]);text(it.label,x+39,y,'left',19);x+=width})}
function axes(xmin,xmax,ymin,ymax,xlabel,ylabel,xTicks=true,integerX=false){for(let j=0;j<=4;j++){const f=j/4,y=T+ph*(1-f);rule(L,y,W-R,y);text(fmt(ymin+f*(ymax-ymin)),L-14,y+6,'right',18)}rule(L,T,L,T+ph,'#9bb1a5');rule(L,T+ph,W-R,T+ph,'#9bb1a5');if(xTicks)for(let j=0;j<=4;j++){const f=j/4,v=integerX?Math.round(xmin+f*(xmax-xmin)):xmin+f*(xmax-xmin),x=L+pw*(v-xmin)/(xmax-xmin||1);text(integerX?v:fmt(v),x,T+ph+30,'center',18)}text(ylabel,L,T-27,'left',20);text(xlabel,W-R,T+ph+69,'right',20)}
if(d.kind==='heat'){
 R=128;B=155;pw=W-L-R;ph=H-T-B;
 const x=i=>L+(i+.5)/d.w*pw,y=i=>T+(i+.5)/d.h*ph,meta=d.meta||{},sc=d.scale||{min:-2,max:2,mode:'diverging',label:'相对振幅'},off=document.createElement('canvas');off.width=d.w;off.height=d.h;const ox=off.getContext('2d'),im=ox.createImageData(d.w,d.h);
 d.a.forEach((v,i)=>{let co=d.mode==='rgb'?v:d.mode==='class'?hex(S.palette[v]||'#aeb8b0'):color(v,sc);if(Array.isArray(d.overlay)&&d.overlay[i])co=hex('#e4b84f');im.data.set([co[0],co[1],co[2],255],i*4)});ox.putImageData(im,0,0);ctx.imageSmoothingEnabled=false;ctx.drawImage(off,L,T,pw,ph);
 for(let j=0;j<=4;j++){let xi=Math.round((d.w-1)*j/4),yi=Math.round((d.h-1)*j/4);text(xi,x(xi),T+ph+31,'center',18);text(fmt(yi*(meta.yScale||1)),L-14,y(yi)+5,'right',18)}text(meta.yLabel||'图像 y / 像素',L,T-26,'left',20);text(meta.xLabel||'图像 x / 像素',W-R,T+ph+67,'right',20);
 let items=[];
 if(d.mode==='class'){items=C.labels.map((label,i)=>({label,color:S.palette[i],dot:true}));if(d.a.some(v=>v===3))items.push({label:'待复核',color:'#aeb8b0',dot:true})}
 else if(d.mode==='rgb')items=[{label:'R=B1，G=B2，B=B3（合成三波段）',color:'#758b77',dot:true}];
 else{const xx=W-93,yy=T+20,ch=ph-40;for(let i=0;i<ch;i++){ctx.fillStyle='rgb('+color(sc.max-i/ch*(sc.max-sc.min),sc).join(',')+')';ctx.fillRect(xx,yy+i,17,1)}[0,.5,1].forEach(f=>text(fmt((sc.max-f*(sc.max-sc.min))*(sc.displayScale||1)),xx+25,yy+ch*f+6,'left',17));text(sc.label||'',xx+9,T-26,'center',16);items=[{label:(sc.mode==='diverging'?'色标限幅：':'色标范围：')+fmt(sc.min*(sc.displayScale||1))+' ～ '+fmt(sc.max*(sc.displayScale||1))+(sc.unit||''),color:'#8da494'}]}
 if(Array.isArray(d.overlay)){items.push({label:'接纳的预测像素',color:'#e4b84f'})}
 if(d.overlay?.kind==='picks'){const ls=[['trueTime',S.series.truth],['baseline',{...S.series.baseline,label:'STA/LTA'}],['picks',{...S.series.model,label:'学习模型拾取'}]];ls.forEach(([key,s])=>{ctx.save();ctx.beginPath();ctx.strokeStyle=s.color;ctx.lineWidth=3;ctx.setLineDash(s.dash);let started=false;d.overlay[key].forEach((v,i)=>{if(v<0){started=false;return}started?ctx.lineTo(x(i),y(v)):ctx.moveTo(x(i),y(v));started=true});ctx.stroke();ctx.restore();items.push(s)})}
 if(d.overlay?.kind==='wells'){d.overlay.wells.forEach(i=>rule(x(i),T,x(i),T+ph,'#e4b84f',2));items.push({label:'标定井位置',color:'#e4b84f'})}
 legend(items,565);
 canvas.onpointermove=e=>{const rect=canvas.getBoundingClientRect(),X=Math.floor(((e.clientX-rect.left)/rect.width*W-L)/pw*d.w),Y=Math.floor(((e.clientY-rect.top)/rect.height*H-T)/ph*d.h);if(X>=0&&X<d.w&&Y>=0&&Y<d.h){const v=d.a[Y*d.w+X],out=document.getElementById('readout');if(out)out.textContent=p.title+' ｜ 列 '+X+'，'+(meta.yLabel?.includes('ms')?'时间 '+(Y*(meta.yScale||1))+' ms':'行 '+Y)+' ｜ '+(d.mode==='class'?(C.labels[v]||'待复核'):Array.isArray(v)?v.map(x=>fmt(x)).join(' / '):fmt(v*(sc.displayScale||1))+(sc.unit||''))}};
}
else if(d.kind==='line'){
 let vals=d.series.flatMap(s=>s.a).filter(v=>v!==null&&Number.isFinite(v)),low=d.yMin??Math.min(0,...vals),high=d.yMax??Math.max(...vals);if(low===high)high=low+1;const xs=d.x||d.series[0].a.map((_,i)=>i*(d.xScale||1)),xmin=Math.min(...xs),xmax=Math.max(...xs),x=v=>L+(v-xmin)/(xmax-xmin||1)*pw,y=v=>T+ph-(v-low)/(high-low)*ph;axes(xmin,xmax,low,high,d.xLabel,d.yLabel,true,!d.x);
 d.series.forEach((s,j)=>{if(!s.pointsOnly){ctx.save();ctx.strokeStyle=s.color||S.palette[j];ctx.lineWidth=3;ctx.setLineDash(s.dash||[]);ctx.beginPath();let started=false;s.a.forEach((v,i)=>{if(v===null){started=false;return}started?ctx.lineTo(x(xs[i]),y(v)):ctx.moveTo(x(xs[i]),y(v));started=true});ctx.stroke();ctx.restore()}if(s.a.length<30||s.pointsOnly)s.a.forEach((v,i)=>{if(v!==null)dot(x(xs[i]),y(v),s.color||S.palette[j],s.pointsOnly?3:4)})});legend(d.series.map((s,j)=>({label:s.label||'序列 '+(j+1),color:s.color||S.palette[j],dash:s.dash,dot:s.pointsOnly})),577);
}
else if(d.kind==='stacked'){
 const xs=d.series[0].a.map((_,i)=>i*(d.xScale||1)),xmin=0,xmax=xs.at(-1),rowH=175,gap=68;d.series.forEach((s,j)=>{const top=T+j*(rowH+gap),lo=j===1?0:Math.min(...s.a),hi=j===1?1:Math.max(...s.a),x=i=>L+xs[i]/(xmax||1)*pw,y=v=>top+rowH-(v-lo)/(hi-lo||1)*rowH;for(let q=0;q<=2;q++){let yy=top+rowH*q/2;rule(L,yy,W-R,yy);text(fmt(hi-(hi-lo)*q/2),L-12,yy+5,'right',17)}text(s.label,L,top-15,'left',20,s.color);ctx.beginPath();ctx.strokeStyle=s.color;ctx.lineWidth=3;s.a.forEach((v,i)=>i?ctx.lineTo(x(i),y(v)):ctx.moveTo(x(i),y(v)));ctx.stroke()});text('时间 / ms',W-R,594,'right',20);[0,.25,.5,.75,1].forEach(f=>text(fmt(xmax*f),L+pw*f,562,'center',18));
}
else if(d.kind==='confusion'){
 const k=d.a.length,max=Math.max(...d.a.flat())||1,sz=118,x0=275,y0=78;d.a.forEach((row,i)=>row.forEach((v,j)=>{ctx.fillStyle=`rgba(39,125,168,${.08+.82*v/max})`;ctx.fillRect(x0+j*sz,y0+i*sz,sz-4,sz-4);text(v,x0+(j+.5)*sz,y0+(i+.55)*sz,'center',29,v/max>.5?'#fff':'#294c55')}));d.labels.forEach((s,i)=>{text(s,x0-20,y0+(i+.5)*sz,'right',19);text(s,x0+(i+.5)*sz,y0+k*sz+32,'center',19)});text('真实类别 → 行',L,38,'left',20);text('预测类别 → 列',x0+sz*k,y0+sz*k+77,'right',20);text('数字为测试样本计数；颜色越深计数越多。',L,580,'left',19);
}
else if(d.kind==='points'){
 B=185;ph=H-T-B;
 const x=v=>L+v*pw,y=v=>T+v*ph;for(let q=0;q<=4;q++){const f=q/4;rule(L,y(f),W-R,y(f));text(f.toFixed(2),L-15,y(f)+5,'right',18);text(f.toFixed(2),x(f),T+ph+31,'center',18)}text('图面 y（向下）/ 归一化',L,T-26,'left',20);text('图面 x / 归一化',W-R,T+ph+65,'right',20);d.pts.forEach(p=>{dot(x(p.x),y(p.y),S.palette[p.k]||'#aeb8b0',p.label?7:5);if(p.label)text(p.label,x(p.x)+8,y(p.y)-8,'left',14)});let items=(d.labels||C.labels).map((label,i)=>({label,color:S.palette[i],dot:true}));if(C.id==='geo-anomaly'){ctx.strokeStyle='#597b68';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(x(.67),y(.38),Math.sqrt(.018)*pw,Math.sqrt(.018)*ph,0,0,Math.PI*2);ctx.stroke();ctx.save();ctx.setLineDash([8,5]);ctx.strokeStyle='#6d7182';ctx.strokeRect(x(.105),y(.6),.23*pw,.24*ph);ctx.restore();items.push({label:'微渗漏合成区域（圆）',color:'#597b68'},{label:'污染合成区域（框）',color:'#6d7182',dash:[8,5]})}else if(d.pts.some(p=>p.k===3))items.push({label:'待复核',color:'#aeb8b0',dot:true});legend(items,565);
}
else if(d.kind==='rose'){
 const sa=d.a.reduce((s,v)=>s+v,0)||1,sb=d.b.reduce((s,v)=>s+v,0)||1,a=d.a.map(v=>v/sa),b=d.b.map(v=>v/sb),max=Math.max(...a,...b,.01),cx=495,cy=270,rad=188;
 [.25,.5,1].forEach(f=>{ctx.beginPath();ctx.strokeStyle='#d4dfd8';ctx.arc(cx,cy,rad*Math.sqrt(f),0,Math.PI*2);ctx.stroke();text((max*f*100).toFixed(1)+'%',cx+9,cy-rad*Math.sqrt(f)+5,'left',16)});
 a.forEach((v,i)=>{const angle=i*Math.PI/12;for(let side=0;side<2;side++){const r=rad*Math.sqrt(v/max),rb=rad*Math.sqrt(b[i]/max),st=angle+side*Math.PI-Math.PI/24,en=angle+side*Math.PI+Math.PI/24;ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,st,en);ctx.closePath();ctx.fillStyle='#277da8a0';ctx.fill();ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,rb,st,en);ctx.closePath();ctx.strokeStyle='#b98732';ctx.lineWidth=2;ctx.stroke()}});[0,45,90,135].forEach(a=>text(a+'°',cx+Math.cos(a*Math.PI/180)*(rad+35),cy+Math.sin(a*Math.PI/180)*(rad+35)+6,'center',20));text('方向像素占比；面积与占比成正比',L,37,'left',20);legend([{label:'预测方向（填充）',color:'#277da8'},{label:'真值方向（轮廓）',color:'#b98732'}],568);text('180° 周期，镜像显示；0° 向右，90° 向下。',L,605,'left',18);
}
else if(d.kind==='scatter'){
 axes(0,40,0,40,'合成真值孔隙度 / %','预测孔隙度 / %');rule(L,T+ph,W-R,T,'#9aa89b',2,[7,5]);d.pts.forEach(p=>dot(L+p.x/.4*pw,T+ph-p.y/.4*ph,p.test?'#b98732':'#277da8',3.5));legend([{label:'左部有井区评价点',color:'#277da8',dot:true},{label:'右部外推区评价点',color:'#b98732',dot:true},{label:'预测 = 真值',color:'#9aa89b',dash:[7,5]}],577);
}
else if(d.kind==='kernel'){
 const max=Math.max(...d.a.map(Math.abs))||1,K=Math.round(Math.sqrt(d.a.length))||3,sz=Math.floor(378/K),x0=300+Math.floor((378-sz*K)/2),fs=K>3?20:28,scale={min:-max,max,mode:'diverging'};d.a.forEach((v,i)=>{ctx.fillStyle='rgb('+color(v,scale).join(',')+')';ctx.fillRect(x0+i%K*sz,T+Math.floor(i/K)*sz,sz-3,sz-3);text(v.toFixed(K>3?2:3),x0+(i%K+.5)*sz,T+(Math.floor(i/K)+.55)*sz,'center',fs,Math.abs(v)/max>.7?'#fff':'#294c55')});for(let i=0;i<378;i++){ctx.fillStyle='rgb('+color(max-i/377*2*max,scale).join(',')+')';ctx.fillRect(830,T+i,19,1)}[max,0,-max].forEach((v,i)=>text(v.toFixed(3),864,T+i*189+6,'left',18));text('权重',830,T-22,'left',18);text('卷积权重（无量纲）',L,35,'left',21);text('颜色范围：'+(-max).toFixed(3)+' ～ '+max.toFixed(3),L,567,'left',19);text('每格直接标出本次学习到的数值。',L,602,'left',18);
}
else if(d.kind==='bars'){
 axes(0,d.vals.length,0,100,'查准率 P / 召回率 R','比例 / %',false);d.vals.forEach((v,i)=>{const x=L+(i+.18)/d.vals.length*pw,w=pw/d.vals.length*.6;ctx.fillStyle=i%2?'#277da8':'#b98732';ctx.fillRect(x,T+ph*(1-v),w,ph*v);text((v*100).toFixed(1)+'%',x+w/2,T+ph*(1-v)-9,'center',22);text(d.names[i],x+w/2,T+ph+31,'center',18)});legend([{label:'单指标基线',color:'#b98732'},{label:'近邻联合异常',color:'#277da8'}],580);
}
canvas.setAttribute('aria-label',p.title+'。'+p.caption+'。坐标、图例和连续色标详见图内。');canvas.dataset.chartKind=d.kind;
}
g.PetroCharts={render,color};
})(window);
