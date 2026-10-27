/* Shared numerical and visual contracts for every portable case. */
(function(g){'use strict';
 const palette=['#b98732','#277da8','#a45c71','#aeb8b0'];
 const spectralPrototypes=[[.72,.46,.25],[.27,.39,.60],[.55,.65,.48]];
 const spectralBands=['B1','B2','B3'];
 const spectralLabels=['砂岩','页岩','灰岩'];
 const spectralDescriptions=spectralPrototypes.map((p,i)=>`${spectralLabels[i]}教学样本：B1 = ${p[0].toFixed(2)}，B2 = ${p[1].toFixed(2)}，B3 = ${p[2].toFixed(2)}。这三个离散输入值与演示训练数据的类别中心一致，不代表真实岩样的标准光谱。`);
 const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
 const series={model:{label:'当前学习模型',color:'#277da8',dash:[]},baseline:{label:'简化基线',color:'#b98732',dash:[8,5]},truth:{label:'合成真值',color:'#5d7564',dash:[2,5]}};
 function waveform(t,arrival=40){const d=t-arrival;return d<0?0:(1-Math.exp(-d/5))*(Math.sin(d*.63)+.4*Math.sin(d*.29))*Math.exp(-d/100)}
 function conceptTabs(c){const tabs={
 'geo-spectral':spectralLabels.map((t,i)=>({label:t,text:spectralDescriptions[i]})),
 'geo-anomaly':[{label:'地表采样',text:'在有坐标的地表采样点测量多项烃类指标。圆环表示教学合成的微渗漏范围，方框表示污染范围；不是实际靶区边界。'},{label:'组合异常',text:'多个指标偏离背景构成复采线索；单指标污染也可能被异常模型检出，异常分数不能解释异常成因。'},{label:'复查证据',text:'异常区需要重复采样、污染调查与地下构造资料交叉验证。模型结果用于安排复查优先级。'}],
 'geo-symbol':[{label:'图例模板',text:'本教学图件约定十字、圆环、三角形分别表示钻孔、产状记录与采样点。这是合成图件自定义图例，不是标准地质符号表。'},{label:'像素特征',text:'每个符号小图为 11×11，共 121 个灰度输入。演示已知符号位置，模型只处理分类环节。'},{label:'坐标图层',text:'分类结果与候选中心坐标组合为图层表。真正地理坐标还需要原图配准；演示坐标单位为像素。'}],
 'geo-fracture':[{label:'裂缝迹线',text:'照片记录的是露头平面上的裂缝迹线。暗线、阴影与岩层界面可能相似，不能只凭颜色判断。'},{label:'二维角度',text:'以图像水平向右为 0°，沿图像坐标向下转为正角度。无向线段的方向按 180° 周期统计，不能直接当作三维走向。'},{label:'方向分布',text:'玫瑰图按裂缝像素方向分组，扇形面积与方向占比成正比；预测与合成真值分别统计。它不是独立裂缝条数。'}],
 'seis-fault':[{label:'同相轴',text:'同一反射事件在剖面上的连续轨迹称为同相轴。图中各条反射事件由同一个几何函数绘制。'},{label:'错断',text:'断层两侧反射事件发生垂向错动。示意中右侧下移，与演示中的合成构造约定一致。'},{label:'不连续特征',text:'比较断层两侧局部窗口的波形差异得到不连续属性。强噪声、岩性变化同样可能造成不连续，需要复核。'}],
 'seis-facies':[{label:'平行反射',text:'连续、近于平行的反射可组成一种地震相描述。示意纹理不直接等同某一沉积环境。'},{label:'杂乱反射',text:'连续性低、方向不稳定的反射呈杂乱纹理。噪声也会产生类似表现，需结合资料质量判断。'},{label:'丘状反射',text:'具有局部弯曲或隆起形态的反射可描述为丘状纹理。聚类编号需经过井点和地质背景标定。'}],
 'seis-firstbreak':[{label:'有效到达之前',text:'初至之前的记录包含背景噪声。噪声尖峰可能早于有效波，固定阈值容易提前触发。'},{label:'真实到达时刻',text:'竖直标线由波形生成函数中的 arrival 参数定位。到达之后波形逐渐增强；标线与生成信号共用同一时间坐标。'},{label:'概率与拾取',text:'学习模型根据窗口特征输出到达段概率。首次超过当前阈值的位置是候选拾取点，最终与合成到达时刻比较。'}],
 'seis-reservoir':[{label:'孔隙体积',text:'图中 20 个等体积单元中，有 4 个表示孔隙；这是用离散单元解释体积分数的示意。'},{label:'总岩石体积',text:'总体积包括固体骨架与孔隙。孔隙可以被水、油或气充填，孔隙体积不等于油体积。'},{label:'孔隙度',text:'本图 φ = 4 / 20 = 20%。地震属性到孔隙度的映射需要井点标定，不能由单个亮反射直接判断。'}],
 'seis-denoise':[{label:'含噪输入',text:'合成有效反射叠加随机噪声与倾斜线性干扰得到输入。噪声与干净信号使用独立项生成，干净信号只用于教学评价。'},{label:'去噪输出',text:'用独立训练样本拟合 5×5 卷积权重。学习输出与普通 3×3 均值滤波在同一测试数据、同一色标下比较。'},{label:'残差质控',text:'残差严格定义为输入减去输出。如果残差中仍存在连续反射事件，说明去噪同时移除了有效信号。'}]
 };return tabs[c.id]||[{label:'专业对象',text:c.concept},{label:'智能介入',text:c.value},{label:'验证边界',text:c.limitation}]}
 g.PetroScience={palette,darkPalette:['#e2bc70','#78c3e4','#e3a0b2','#bac5b5'],spectralPrototypes,spectralBands,spectralLabels,series,dtMs:2,clamp,waveform,conceptTabs};
})(window);
