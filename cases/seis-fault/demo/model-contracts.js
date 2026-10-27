/* Actual baselines and plotting metadata. No performance values are hard-coded. */
(function(g){'use strict';const S=g.PetroScience,mean=a=>a.reduce((s,v)=>s+v,0)/(a.length||1),rate=(a,b)=>a.filter((v,i)=>v===b[i]).length/a.length,clamp=S.clamp;
function binary(pred,truth){let tp=0,fp=0,fn=0;pred.forEach((p,i)=>{if(p&&truth[i])tp++;if(p&&!truth[i])fp++;if(!p&&truth[i])fn++});return {iou:tp/(tp+fp+fn||1),f1:2*tp/(2*tp+fp+fn||1)}}
function comparison(id,r,t,api,C){let baseline=0,model=0,label='',baselineLabel='',direction='higher',unit='%',n=r.rows.length;const rows=r.rows;
 if(id==='geo-spectral'){const truth=rows.map(x=>x.truth),base=rows.map(x=>{let ds=S.spectralPrototypes.map(p=>Math.abs(p[0]-x.b1));return ds.indexOf(Math.min(...ds))});baseline=rate(base,truth)*100;model=rate(rows.map(x=>x.pred),truth)*100;label='全像素分类准确率';baselineLabel='单波段最近中心'}
 else if(id==='geo-anomaly'){const truth=rows.map(x=>+(x.type===C.labels[1])),base=rows.map(x=>+(x.single>1)),pred=rows.map(x=>+(x.score>=t));baseline=binary(base,truth).f1*100;model=binary(pred,truth).f1*100;label='微渗漏识别 F1';baselineLabel='单指标固定阈值'}
 else if(id==='geo-symbol'){const templates=[0,1,2].map(k=>api.symbol(k,()=>.5,0,0)),base=rows.map(row=>{let ds=templates.map(v=>mean(v.map((z,i)=>(z-row.pixels[i])**2)));return C.labels[ds.indexOf(Math.min(...ds))]});baseline=rate(base,rows.map(x=>x.truth))*100;model=rate(rows.map(x=>x.prediction),rows.map(x=>x.truth))*100;label='全部候选符号准确率';baselineLabel='固定中心模板'}
 else if(id==='geo-fracture'){const a=r.plots[0].data.a,truth=rows.map(x=>x.truth),base=a.map(v=>+(v<.35));baseline=binary(base,truth).iou*100;model=binary(rows.map(x=>x.prediction),truth).iou*100;label='裂缝像素 IoU';baselineLabel='固定灰度阈值 0.35'}
 else if(id==='seis-fault'){const d=r.plots[0].data,fs=api.featureFault(d),truth=rows.map(x=>x.truth),base=fs.map(x=>+(x[0]>.8));baseline=binary(base,truth).iou*100;model=binary(rows.map(x=>x.prediction),truth).iou*100;label='断层像素 IoU';baselineLabel='单属性阈值 0.8'}
 else if(id==='seis-facies'){const truth=rows.map(x=>x.truth),base=rows.map(x=>x.attribute0<-.15?0:x.attribute0<.25?1:2);baseline=rate(base,truth)*100;model=rate(rows.map(x=>x.cluster),truth)*100;label='全部测试相准确率';baselineLabel='单属性固定分区'}
 else if(id==='seis-firstbreak'){baseline=rows.filter(x=>x.stalta_ms!==null&&Math.abs(x.stalta_ms-x.true_ms)<=10).length/n*100;model=rows.filter(x=>x.picked_ms!==null&&Math.abs(x.picked_ms-x.true_ms)<=10).length/n*100;label='全道 10 ms 内命中率';baselineLabel='STA/LTA 比值 3'}
 else if(id==='seis-reservoir'){const wells=r.plots[0].data.overlay.wells,train=rows.filter(x=>wells.includes(x.x)&&x.y%4===1),fit=api.ridge(train.map(x=>[1,x.impedance]),train.map(x=>x.true_porosity),.02),test=rows.filter(x=>x.zone==='extrapolation');baseline=Math.sqrt(mean(test.map(x=>(clamp(fit.predict([1,x.impedance]),0,.4)-x.true_porosity)**2)))*100;model=Math.sqrt(mean(test.map(x=>(x.predicted_porosity-x.true_porosity)**2)))*100;label='右侧外推区 RMSE';baselineLabel='单属性线性回归';direction='lower';unit='pp';n=test.length}
 else if(id==='seis-denoise'){const energy=rows.reduce((s,x)=>s+x.clean*x.clean,0),snr=field=>10*Math.log10(energy/rows.reduce((s,x)=>s+(x[field]-x.clean)**2,0));baseline=snr('mean_filter');model=snr('learned');label='测试剖面信噪比';baselineLabel='3×3 均值滤波';unit='dB'}
 return {label,baseline,model,baselineLabel,modelLabel:C.method,direction,unit,n,same_test_data:true};
}
function prepare(id,r,t,api,C){r.comparison=comparison(id,r,t,api,C);r.plots.forEach((p,index)=>{const d=p.data;if(d.kind==='heat'){
 const seismic=id.startsWith('seis-')&&id!=='seis-reservoir';d.meta={xLabel:seismic?'道号':id==='seis-reservoir'?'水平网格编号':'图像 x / 像素',yLabel:seismic?'合成时间 / ms':id==='seis-reservoir'?'纵向网格编号':'图像 y / 像素',yScale:seismic?S.dtMs:1};
 // First-break shot gathers represent recording time, not reflection two-way time.
 if(id==='seis-firstbreak')d.meta.yLabel='记录时间 / ms';
 d.scale=d.mode==='prob'?{min:0,max:1,mode:'sequential',label:'概率'}:d.mode==='gray'?{min:0,max:1,mode:'gray',label:'灰度'}:d.mode==='phi'?{min:0,max:.35,mode:'sequential',label:'孔隙度',displayScale:100,unit:'%'}:{min:-2,max:2,mode:'diverging',label:'相对振幅'};
 if(id==='seis-reservoir'&&index===2){d.a=r.rows.map(x=>x.error_pp);d.scale={min:-8,max:8,mode:'diverging',label:'误差',unit:' pp'};p.caption='预测减真值，以孔隙度百分点 pp 表示；所有参数下固定使用 −8 至 +8 pp 色标，超过范围会限幅。'}
 if(id==='seis-denoise'&&index===0)p.caption='输入、输出与残差共用 −2 至 +2 的相对振幅色标；超出范围会限幅。';
 if(id==='seis-reservoir'&&index<2)p.sub='固定孔隙度色标：0% — 35%';
 if(id==='seis-firstbreak'&&index===0)p.sub='真值点线 · 模型实线 · 基线虚线';
 }
 if(d.kind==='line'){
 d.series.forEach((s,i)=>{s.color=i===0?S.series.model.color:S.series.baseline.color;s.dash=i===0?[]:S.series.baseline.dash});
 const labels={
 'geo-spectral':['MLP 训练交叉熵'],'geo-anomaly':['测试点近邻距离','当前异常阈值'],'geo-symbol':['5 近邻投票比例','当前接纳阈值'],'geo-fracture':['逻辑回归训练交叉熵'],'seis-fault':['逻辑回归训练交叉熵'],'seis-facies':['平均簇内平方距离'],'seis-firstbreak':index===2?['学习模型误差','STA/LTA 误差']:['第 12 道相对振幅','到达段概率']};
 d.series.forEach((s,i)=>s.label=(labels[id]||[])[i]||'当前结果');
 if(id==='geo-spectral'){d.xScale=5;d.xLabel='训练轮次';p.caption='训练共 100 轮，每 5 轮采样一次交叉熵；曲线由本次训练计算。'}
 if(['geo-fracture','seis-fault'].includes(id)){d.xScale=7;d.xLabel='训练轮次';p.caption='逻辑回归训练共 140 轮，每 7 轮记录一次训练交叉熵；测试标签不参与拟合。'}
 if(['geo-anomaly','geo-symbol'].includes(id)){d.series[0].pointsOnly=true;d.yMin=0;if(id==='geo-symbol')d.yMax=1;p.caption+=' 点为离散样本，不用折线连接；虚线表示当前阈值。'}
 if(id==='seis-firstbreak'&&index===3){d.kind='stacked';d.xScale=S.dtMs;d.yLabel='';p.caption='振幅与概率量纲不同，分成上下两幅，共用记录时间轴。'}
 }
 if(d.kind==='rose'){p.caption='蓝色填充为预测方向，金色轮廓为合成裂缝真实方向；面积与方向像素占比成正比，按 180° 周期镜像。'}
 });return r;
}
g.PetroModelContracts={prepare};
})(window);
