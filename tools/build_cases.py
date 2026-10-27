"""Build the nine portable, teacher-compatible case packs. Standard library only."""
from pathlib import Path
import sys as _sys, os as _os
_sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
from case_content import CONTENT as CASE_CONTENT
from case_content_more import MORE as _MORE
CASE_CONTENT.update(_MORE)
import importlib
from case_steps import STEP_FIGS
for _cid,_figs in STEP_FIGS.items():
    for _st,(_svg,_cap) in zip(CASE_CONTENT[_cid]['workflow']['steps'],_figs):
        _st['fig']=_svg; _st['figcap']=_cap
# 新版：由合成数据计算的示意图（tools/build_step_figs.py 生成到 assets/steps/<case>/）
import importlib.util as _ilu, os as _os
_spec=_ilu.spec_from_file_location('build_step_figs', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'build_step_figs.py'))
_bsf=_ilu.module_from_spec(_spec); _spec.loader.exec_module(_bsf)
for _cid,_mod in _bsf.MODS.items():
    _m=importlib.import_module(_mod)
    for _i,(_st,_cap) in enumerate(zip(CASE_CONTENT[_cid]['workflow']['steps'],_m.CAPS)):
        _st['fig']='<img src="assets/steps/%s/s%d.svg" alt="%s" loading="lazy" width="432" height="205">'%(_cid,_i+1,_st['name']+'示意图')
        _st['figcap']=_cap
import json, shutil, zipfile

# 可运行示范开头的数据说明（参照老师示范案例的写法）
DATA_NOTES={
 'seis-fault':'这是一条程序合成的含断层地震剖面，断层位置已知，所以能精确计算 IoU、查准率和召回率；模型（类别平衡的逻辑回归）打开页面时用另一条合成剖面现场训练。',
 'geo-spectral':'这是一幅程序合成的三波段影像，每个像素的真实岩性已知，所以能精确统计分类正确率；分类器是一个小型神经网络，打开页面时用合成光谱现场训练。',
 'geo-anomaly':'这是一组程序合成的化探采样点，哪里是油气微渗漏、哪里是污染已知，所以能精确计算查准率和召回率；异常分按与背景参考样本的距离计算，并与单指标阈值对比。',
 'geo-symbol':'这是一幅程序合成的图件，每个符号的真实类别已知，所以能精确统计识别正确率；识别用 k 近邻投票，参考样本也是现场合成的。',
 'geo-fracture':'这是一张程序合成的露头影像，每条裂缝的位置和方向已知，所以能精确计算 IoU 并与真实方向对比；模型（方向滤波特征 + 逻辑回归）打开页面时用另一张合成影像现场训练。',
 'seis-facies':'这是一组程序合成的地震属性样本，每个样本的真实相带已知，所以能用混淆矩阵精确评价；先用 k-means 聚类，再把簇对应到相带。',
 'seis-firstbreak':'这是一组程序合成的炮集记录，每一道的真实初至时间已知，所以能精确计算拾取误差；学习模型（能量比特征 + 逻辑回归）在 6 种噪声水平的合成记录上现场训练，并与经典 STA/LTA 对比。',
 'seis-reservoir':'这是一条程序合成的孔隙度剖面，各处真实孔隙度已知，所以能精确计算有井区和外推区的误差；回归模型只用“井”位置上的样本训练。',
 'seis-denoise':'这是一条程序合成的地震剖面，叠加了随机噪声和倾斜相干干扰，干净信号已知，所以能精确计算信噪比；去噪滤波器在另一条合成剖面上用岭回归现场学出，并与 3×3 均值滤波对比。',
}
DATA_TAIL='结果只用来说明方法原理和参数影响，不代表真实工区的效果。'

ROOT = Path(__file__).resolve().parents[1]

def case(id, scene, title, en, method, question, concept, value, data, limitation, controls, steps, labels, sources):
    return dict(id=id, scene=scene, title=title, en=en, method=method, question=question,
                concept=concept, value=value, data=data, limitation=limitation, controls=controls,
                steps=steps, labels=labels, sources=sources)

USGS=['USGS · 光谱遥感与岩性识别','https://www.usgs.gov/labs/spectroscopy-lab']
FAULT=['FaultSeg3D · 合成地震数据与断层分割','https://doi.org/10.1190/geo2018-0646.1']
IMP=['SLB · 声阻抗的物理含义','https://glossary.slb.com/en/terms/a/acoustic_impedance']
CASES=[
case('geo-spectral','g1','遥感岩性智能解译','SPECTRAL LITHOLOGY','多层感知机 MLP',
 '同一片地表，机器能否从光谱中读出岩性？',
 '砂岩、页岩与灰岩在不同波段的反射率有差异。地表岩性与界线为区域地质制图提供线索；露头结果需要地面核查，不能直接外推为地下含油性。',
 '用三波段反射率训练小型神经网络，将逐点判读变为像素分类，并把低置信度区域留给解释员。',
 '演示：合成三波段地表与三个岩性标签；训练使用独立生成的光谱样本，测试图幅不参加训练。实际项目需要配准影像、岩性掩膜和地面调查点，按地区分组验证。',
 '植被、风化和阴影改变光谱；示例只含三个理想岩类，不代表真实遥感分割网络。',
 [['noise','光谱扰动',0,0.65,0.16,0.01],['threshold','接纳置信度',0.35,0.95,0.6,0.01]],
 [['影像配准','三波段 → 同一像素','让不同波段描述同一地点。先排除云层、植被和阴影。'],['采集标签','地面岩样 → 岩性类别','用独立地块采样，避免相邻像素同时落入训练和测试。'],['学习光谱','3 输入 → 10 隐层 → 3 类','MLP 学习波段之间的组合，而不是只比较一个波段。'],['绘制岩性图','类别概率 → 岩性与待复核区','阈值越高，自动接纳覆盖率越低；对不确定位置做地面核验。']],
 ['砂岩','页岩','灰岩'],[USGS]),
case('geo-anomaly','g2','油气化探异常识别','GEOCHEMICAL ANOMALY','kNN 距离异常检测',
 '烃类指标同时偏离背景，是否值得优先复查？',
 '地下油气微渗漏可能改变土壤烃类指标，但污染也会造成异常。组合异常只表示偏离背景，不能直接等同于油气藏。',
 '从背景区学习多指标的正常分布，以到近邻的距离排序异常点；对比单指标阈值，观察联合证据与污染干扰。',
 '演示：240 个空间采样点与三项合成烃类指标；背景参考集与测试点独立生成。实际需要采样坐标、化验记录、检出限、重复样、污染记录与已知区块。',
 '未知背景区可能混入异常；空间相关会高估随机划分的精度，生产验证应按空间分块。',
 [['noise','化验扰动',0.02,0.8,0.18,0.01],['threshold','异常距离阈值',0.25,2.5,0.9,0.05]],
 [['采样与质控','坐标＋化验 → 有效采样点','核对检出限、重复样与污染记录，保留点位空间关系。'],['学习背景','背景指标 → 近邻参考集','三项指标使用统一量纲；背景样本独立于用于计算指标的测试点。'],['计算异常','三维近邻距离 → 异常分数','计算每点到背景 5 个近邻的平均距离，观察联合异常。'],['靶区复核','异常点＋地质 → 复采建议','把多指标异常与污染单指标异常并列；地图上圈出复查区域。']],
 ['背景','微渗漏','表层污染'],[USGS]),
case('geo-symbol','g3','地质图件要素提取','GEOLOGICAL MAP DIGITIZATION','像素特征 kNN 分类',
 '扫描地质图里的符号，怎样变成可查询的图层？',
 '历史图上的钻孔、产状与化石符号只是像素。将符号定位、识别并关联图例，才能恢复为结构化地质图层，服务区域资料整编。',
 '对已定位符号的灰度小图做近邻分类，输出类别、坐标与置信度；本演示聚焦识别环节，不声称完成 OCR 或自动检测。',
 '演示：三种符号的 11×11 灰度小图，每个符号带随机位移、缩放与旋转；360 个训练样本与地图测试符号使用独立随机种子。实际需图例表、人工框选样本、地图配准与坐标系统。',
 '演示已知符号中心；真实地图还需要检测、OCR、线追踪与拓扑修复。不同年代图例不能混为同一类别。',
 [['noise','扫描污损',0,0.7,0.18,0.01],['threshold','接纳置信度',0.34,0.98,0.64,0.01]],
 [['定位符号','扫描图 → 小图块','本演示提供定位结果；真实流程需检测模型或人工候选框。'],['学习图例','11×11 灰度 → 样本库','独立生成三类带位移、缩放与旋转的训练符号，样本库覆盖书写差异；单一固定模板难以覆盖这些变化。'],['近邻分类','121 维像素 → 五近邻投票','按距离寻找相似符号，投票结果决定类别与置信度。'],['落图复核','类别＋坐标 → 图层表','标记低置信度图块，逐条核对图例语义；可导出结果。']],
 ['钻孔','产状','采样点'],[USGS]),
case('geo-fracture','g4','露头裂缝智能统计','OUTCROP FRACTURE ANALYSIS','方向特征＋逻辑回归',
 '一面露头上的裂缝，如何变成储层建模参数？',
 '裂缝影响流体流动。露头影像提供二维迹线和方向信息；照片中的迹线角度不是三维产状，必须结合面向与摄影测量才能恢复空间方向。',
 '学习局部暗线与方向响应，将像素分为裂缝和背景，再统计方向分布，辅助裂缝型储层的类比研究。',
 '演示：合成二维露头、独立训练影像与像素标签；输入已统一比例。实际需标尺、照明记录、多角度照片、裂缝标注及罗盘实测。',
 '阴影、岩层界面与风化纹理会造成误检。玫瑰图反映图像平面内的迹线方向，不能当作地下裂缝走向。',
 [['noise','岩面纹理',0.02,0.65,0.16,0.01],['threshold','裂缝阈值',0.2,0.9,0.5,0.01]],
 [['拍摄与标定','影像＋标尺 → 等尺度图像','消除透视并统一尺度；本演示假定正视拍摄。'],['提取特征','灰度窗口 → 暗线方向响应','对 12 个方向计算邻域响应，区分裂缝与随机纹理。'],['学习分割','独立像素标签 → 逻辑回归','用合成训练图拟合参数，在另一张图上预测裂缝概率。'],['统计与复核','裂缝掩膜 → 玫瑰图与 IoU','比较真值与预测，检查阈值对误检和漏检的影响。']],
 ['背景','裂缝'],[FAULT]),
case('seis-fault','s1','地震断层自动解释','SEISMIC FAULT INTERPRETATION','相干特征＋逻辑回归',
 '地层反射的突然错断，能被模型稳定识别吗？',
 '地震剖面中的同相轴对应反射界面，断层使两侧地层错动。识别断层有助于理解圈闭几何与井位部署，但断层是否封闭还需岩性和压力证据。',
 '从局部横向不连续特征学习断层概率，再用阈值控制解释范围；演示可解释的像素分类，生产方向可扩展至 3D CNN。',
 '演示：独立生成的含错断地层训练剖面与测试剖面；标签为合成断层邻域。实际需要三维地震振幅、相干属性、人工断层面和跨工区验证。',
 '不连续也可能来自噪声和地层变化；二维特征模型不能替代三维断层解释，IoU 仅评价当前合成剖面。',
 [['noise','地震噪声',0.01,0.75,0.16,0.01],['threshold','断层概率阈值',0.2,0.95,0.56,0.01]],
 [['构造正演','地层＋断距 → 含断层剖面','反射事件在断层两侧发生相位错动，生成独立训练和测试剖面。'],['提取属性','局部窗口 → 横向不连续度','组合多尺度差异与纵向平均，减少单点振幅误判。'],['学习断层','属性＋标签 → 概率图','逻辑回归学习特征权重；类别平衡采样防止背景淹没断层。'],['解释质控','概率阈值 → 断层叠加图','比较 Precision、Recall 和 IoU，定位阈值带来的漏检和误检。']],
 ['连续地层','断层'],[FAULT]),
case('seis-facies','s2','地震相智能分类','SEISMIC FACIES CLASSIFICATION','K-means 属性聚类',
 '不同反射纹理，能否帮助勾画沉积相带？',
 '连续平行、杂乱和丘状反射纹理可描述为不同地震相。地震相是波形特征的归纳，不等于岩性或沉积环境，需要测井与岩心标定。',
 '用局部振幅、频率与连续性属性进行 K-means 聚类，展示无标签分组如何揭示相带变化，再经地质解释赋予含义。',
 '演示：三种合成纹理的独立训练切片与测试剖面，三个特征标准化；三类相在单一属性上相互重叠，需要组合多个属性才能区分。实际需要同一坐标体系的地震属性体，以及不参与聚类的井点验证。',
 '聚类编号没有天然地质语义；本例用独立合成训练标签对齐编号后评价，真实工程需要人工标定。',
 [['noise','属性扰动',0.01,0.75,0.18,0.01],['threshold','边界模糊度',0,0.5,0.12,0.01]],
 [['提取属性','反射纹理 → 三维属性','观察振幅、频率与横向连续性；统一量纲避免幅值主导距离。'],['无监督学习','标准化属性 → 三个聚类中心','迭代分配与更新中心，不向聚类提供测试类别。'],['生成相带','近邻中心 → 聚类分区','按中心距离分配各像素，观察边界混合带。'],['地质标定','聚类＋井点 → 相带解释','独立标签只用于对齐编号和评价；聚类本身不证明含油性。']],
 ['平行反射','杂乱反射','丘状反射'],[IMP,FAULT]),
case('seis-firstbreak','s3','初至波智能拾取','FIRST-BREAK PICKING','窗口特征＋逻辑回归',
 '怎样从含噪道集中找到最早到达的地震波？',
 '初至是震源激发后最先到达检波器的有效信号。初至走时支持近地表速度分析和静校正；噪声尖峰可能比有效波更早出现。',
 '从短窗能量、前后能量比、跨道一致性和初至前背景能量学习到达概率，并与经典 STA/LTA 基线并列，体现有监督学习的介入位置。',
 '演示：24 道合成记录，采样间隔 2 ms；训练样本来自 6 个不同噪声水平的独立炮集，当前炮集仅用于测试。实际需采样率、炮检坐标、人工初至标签和低信噪比样本。',
 '该模型是小型特征分类器，不能声称为 PhaseNet。合成波形简单，复杂折射、面波和仪器差异均需专项验证。',
 [['noise','背景噪声',0.02,0.9,0.22,0.01],['threshold','到达概率阈值',0.2,0.95,0.45,0.01]],
 [['整理炮集','24 道 × 220 点 → 波形阵列','每点 2 ms，保留道序；训练炮集与测试炮集独立。'],['窗口特征','短窗能量＋前后比＋背景能量 → 特征向量','能量用于区分背景与有效波；邻道特征抑制孤立噪点；背景能量让同一模型适应不同噪声水平。'],['学习拾取','标注到达段 → 逻辑回归','按首个达到阈值的位置拾取，同时计算经典 STA/LTA 基线（5 / 30 采样点窗口，比值 3）。'],['检查走时','拾取点＋真值 → 误差分布','报告 MAE、漏拾道数与 10 ms 内命中率，漏拾不计为零误差。']],
 ['背景','已到达'],[['SLB · 初至术语','https://glossary.slb.com/terms/b/break'],FAULT]),
case('seis-reservoir','s4','储层孔隙度智能反演','RESERVOIR PROPERTY INVERSION','非线性特征岭回归',
 '从地震属性到孔隙度，中间需要哪些约束？',
 '孔隙度表示岩石孔隙体积占比，决定储集空间的一部分。地震振幅对阻抗差异敏感，不能把亮反射直接解释成高孔隙度或含油层。',
 '用少量合成井点标定多属性到孔隙度的回归映射，展示井数、噪声与外推误差的关系；结果用于候选储层区的辅助解释。',
 '演示：合成属性剖面、3—24 口训练井及独立测试区；阻抗随孔隙度呈指数变化并受泥质含量干扰，振幅同时反映泥质，单靠阻抗无法分离两者；输入使用标准化声阻抗和振幅。实际需井震标定、尺度匹配、盲井验证与地质先验。',
 '映射依赖岩石物理关系，少井区存在多解性；模型没有建模流体饱和度，不能预测油气产量。',
 [['noise','属性扰动',0.01,0.65,0.14,0.01],['threshold','标定井数',3,24,9,1]],
 [['井震匹配','地震属性＋井点 → 同尺度样本','先校正时深关系，避免用米级测井直接拟合十米级地震。'],['构造特征','阻抗＋振幅 → 非线性特征','加入平方与交互项，拟合可解释的简化非线性关系。'],['训练回归','训练井 → 岭回归系数','加入正则抑制少井条件下的过拟合，测试区不参加拟合。'],['盲区评估','预测剖面＋真值 → RMSE','训练井位于左部，右部为外推区；分别统计误差，检查地质变化。']],
 ['低孔隙度','高孔隙度'],[IMP,['SLB · 地震反演','https://www.slb.com/-/media/files/oilfield-review/seismic-inversion']]),
case('seis-denoise','s5','地震资料智能去噪','LEARNED SEISMIC DENOISING','学习型卷积滤波器',
 '压低噪声的同时，怎样知道有效反射没有被抹掉？',
 '地下界面的反射信号叠加在随机噪声与倾斜的线性相干干扰（类似面波）之中。过度平滑会削弱薄层与小构造；只看输出是否干净不足以判断去噪是否成功。',
 '用独立含噪／干净样本对学习 5×5 卷积核，与普通 3×3 均值滤波比较：均值滤波只能平滑随机噪声，学习核可按干扰倾角定向压制，联动显示输出、残差与信噪比。',
 '演示：独立合成剖面对训练卷积核，测试剖面含随机噪声与倾斜线性干扰，两者幅度由同一噪声参数控制。实际需正演样本或自监督训练策略，并对真实工区做信号保真检查。',
 '这是线性单层卷积学习，不是深层 U-Net；训练与测试的干扰倾角相同，真实工区中倾角、频率变化与域迁移的效果不能从本演示推出。',
 [['noise','噪声强度',0.05,1.1,0.42,0.01],['threshold','去噪混合比例',0,1,0.9,0.01]],
 [['生成样本','反射正演＋随机噪声＋线性干扰 → 训练对','干净信号只作为合成标签，测试信号及随机种子独立。'],['学习卷积','5×5 噪声窗口 → 干净中心点','最小二乘学习 25 个权重，而非手工固定均值核；权重呈现与干扰倾角相关的方向性。'],['执行去噪','测试剖面 → 学习滤波输出','调混合比例观察去噪强度；同时计算均值滤波基线。'],['检查保真','输入−输出 → 残差剖面','若残差含连续反射，说明伤及信号；结合 SNR 与误差核验。']],
 ['负振幅','正振幅'],[FAULT])
]

# Course scene names are authoritative; algorithm names belong in the method field.
COURSE_TITLES={
 'g1':'地质剖面遥感解译','g2':'油气地球化学异常识别','g3':'地质图件要素智能提取','g4':'露头裂缝自动统计',
 's1':'地震断层自动解释','s2':'地震相智能分类','s3':'初至波自动拾取','s4':'储层参数反演','s5':'地震资料噪声压制'
}
SCENE_SOURCES={
 'g2':[['USGS · 地表油气化探的方法与局限','https://pubs.usgs.gov/publication/70018699']],
 'g3':[['USGS · 扫描地质图的数据采集与矢量化','https://pubs.usgs.gov/of/1997/of97-269/wahl.html']],
 'g4':[['FracPaQ · 二维裂缝特征的定量分析','https://researchportal.hw.ac.uk/en/publications/fracpaq-a-matlab-toolbox-for-the-quantification-of-fracture-patte/']],
 's2':[['SLB · 地质相的含义','https://glossary.slb.com/en/terms/f/facies'],['算法原理 · K-means 聚类','https://scikit-learn.org/stable/modules/clustering.html#k-means']],
 's3':[['基线参考 · ObsPy STA/LTA 触发教程','https://docs.obspy.org/tutorial/code_snippets/trigger_tutorial.html']],
 's5':[['研究延伸 · 卷积神经网络地震插值与去噪','https://arxiv.org/abs/1901.07927']]
}
for c in CASES:
    c['title']=COURSE_TITLES[c['scene']]
    if c['scene'] in SCENE_SOURCES: c['sources']=SCENE_SOURCES[c['scene']]
    if c['scene']=='g3':
        c['concept']='历史图上的钻孔、产状记录与采样点符号只是像素。将符号识别并关联原图图例，才能恢复结构化地质图层。演示使用明确给定的自定义教学图例，不代表标准地质符号。'
    if c['scene']=='s3': c['steps'][0][1]='24 道 × 170 点 → 波形阵列'
    if c['scene']=='s4': c['data']=c['data'].replace('标准化声阻抗和振幅','无量纲合成阻抗与振幅属性')
    if c['scene']=='s5': c['controls'][1][4]=1

def svg(c):
    """Accessible self-contained concept illustration for original teacher renderer."""
    ix=CASES.index(c)
    if ix < 4:
        terrain='<path d="M12 105 Q80 55 150 95 T290 85 L290 178 L12 178Z" fill="#cec3aa"/><path d="M12 122 Q90 88 155 116 T290 108 L290 178 L12 178Z" fill="#676767"/><path d="M12 147 Q110 116 190 142 T290 133 L290 178 L12 178Z" fill="#606060"/>'
    else:
        terrain=''.join(f'<path d="M12 {65+i*16} Q100 {40+i*16} 158 {70+i*16} L165 {86+i*16} Q220 {65+i*16} 290 {78+i*16}" fill="none" stroke="{["#c7c7c7","#7d7d7d"][i%2]}" stroke-width="3"/>' for i in range(6))
    terms=[['多波段观测','学习光谱差异','岩性制图'],['地表化探','联合指标异常','优先复采'],['扫描图件','符号像素分类','结构化图层'],['露头迹线','像素学习分割','方向分布'],['同相轴错断','不连续性学习','断层概率'],['反射纹理','属性空间聚类','相带分区'],['含噪波形','到达概率学习','初至走时'],['井震标定','属性回归映射','孔隙度剖面'],['含噪剖面','样本学习卷积','信号与残差']][ix]
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 215" role="img" aria-label="{c["title"]}概念图" style="width:100%;height:auto;background:#1c222e;border-radius:12px"><g>{terrain}</g><g font-family="sans-serif" fill="#e7ecf3"><text x="20" y="28" font-size="12">{terms[0]} / 专业对象</text><path d="M310 112H350M342 105l8 7-8 7M540 112H580M572 105l8 7-8 7" fill="none" stroke="#c3b287" stroke-width="2"/><rect x="360" y="72" width="175" height="80" rx="12" fill="#2c3549"/><text x="447" y="108" text-anchor="middle" font-size="17">{terms[1]}</text><text x="447" y="132" text-anchor="middle" font-size="11" fill="#c5c5c5">{c["method"]}</text><rect x="590" y="72" width="155" height="80" rx="12" fill="#a87a36"/><text x="667" y="118" text-anchor="middle" font-size="17" fill="#1c222e">{terms[2]}</text><text x="20" y="202" fill="#bebebe" font-size="11">示意图 · 表面观测与地下解释之间仍需地质验证</text></g></svg>'

def build():
    listing=[]
    old_catalog=ROOT/'assets'/'catalog.js'
    old_names=[]
    if old_catalog.exists():
        old=json.loads(old_catalog.read_text(encoding='utf8').removeprefix('window.CATALOG=').rstrip(';'))
        old_names=[x.get('zip','') for x in old]
    theories=json.loads((ROOT/'assets'/'theories.json').read_text(encoding='utf-8')) if (ROOT/'assets'/'theories.json').exists() else {}
    workflow_figures=json.loads((ROOT/'assets'/'workflows.json').read_text(encoding='utf-8')) if (ROOT/'assets'/'workflows.json').exists() else {}
    for n,c in enumerate(CASES):
        p=ROOT/'cases'/c['id']; (p/'demo').mkdir(parents=True,exist_ok=True)
        c['number']=n+1; c['category']='地质勘察' if n<4 else '物探'
        c['methods']={'g1':['cv'],'g2':['opt'],'g3':['cv'],'g4':['cv'],'s1':['cv'],'s2':['cv'],'s3':['ts'],'s4':['cv','opt'],'s5':['cv']}[c['scene']]
        c['difficulty']='高' if c['scene']=='s1' else '中'
        c['figure']=theories[c['id']][0] if c['id'] in theories else svg(c)
        pkg={'id':c['id'],'sceneId':c['scene'],'title':c['title'],'methods':c['methods'],'version':'1.2.0','updated':'2026-10-23',
             'tabs':{'background':{'label':'专业背景','lede':c['concept'], 'judge':[{'label':'数据','value':'合成数据','desc':'固定种子，可重复计算'},{'label':'方法','value':c['method'],'desc':'浏览器内实际学习'},{'label':'目标','value':'辅助解释','desc':'结果需专业复核'}],
                'sections':[{'no':1,'en':'CONCEPT','title':'先看懂专业对象','html':c['figure']+'<p>'+c['concept']+'</p>'},{'no':2,'en':'AI VALUE','title':'智能化介入点','html':'<p>'+c['value']+'</p>'},{'no':3,'en':'DATA','title':'数据与验证条件','html':'<p>'+c['data']+'</p>'},{'no':4,'en':'BOUNDARY','title':'适用边界与参考','html':'<p>'+c['limitation']+'</p>'+''.join(f'<p><a href="{u}" target="_blank" rel="noopener">{t} ↗</a></p>' for t,u in c['sources'])}]},
             'workflow':{'label':'案例流程','title':'从地质问题到可复核的结果','lead':[c['value']], 'steps':[{'name':s[0],'role':['数据','特征','学习','质控'][i],'do':s[2],'effect':s[1],'trap':c['limitation'] if i==3 else '训练与测试独立，保留尺度、单位和坐标信息。'} for i,s in enumerate(c['steps'])], 'metrics':{'title':'用当前测试样本评价','html':'<p>演示中所有指标均从当前合成测试数据实时计算；导出文件包含参数、种子与结果，不能作为工业精度证明。</p>'+c['figure']}},
             'demo':{'label':'案例演示','mode':'auto','html':'demo/index.html','intro':c['question'],'height':1080}}}
        pkg['tabs']['background']['judge'].append({'label':'技术难度','value':c['difficulty'],'desc':'需跨区域验证和专业复核'})
        if c['id'] in workflow_figures:
            pkg['tabs']['workflow']['metrics']['html']='<p>以下图解释每步输入与产出，实际运行结果请进入案例演示。</p>'+''.join(workflow_figures[c['id']])
        if c['id'] in CASE_CONTENT:
            cc=CASE_CONTENT[c['id']]
            pkg['tabs']['background']={'label':'专业背景','judge':cc['judge'],'lede':cc['lede'],'sections':[dict(no=i+1,**sec) for i,sec in enumerate(cc['sections'])]}
            pkg['tabs']['workflow']=dict(label='案例流程',**cc['workflow'])
            pkg['tabs']['demo'].update(cc.get('demo',{}))
            if c['id'] in DATA_NOTES: pkg['tabs']['demo']['intro']=DATA_NOTES[c['id']]+DATA_TAIL+'\n'+pkg['tabs']['demo']['intro']
        (p/'case.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2),encoding='utf-8')
        (p/'demo'/'config.js').write_text('window.LAB_CONFIG='+json.dumps(c,ensure_ascii=False)+';',encoding='utf-8')
        for name in ['science.js','charts.js','model-contracts.js','lab-tools.js','lab.js','lab.css']:
            shutil.copy2(ROOT/'assets'/name,p/'demo'/name)
        scripts=''.join('<script src="'+name+'"></script>' for name in ['science.js','charts.js','model-contracts.js','lab-tools.js','config.js','lab.js'])
        (p/'demo'/'index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+c['title']+'</title><link rel="stylesheet" href="lab.css"></head><body><main id="lab"></main>'+scripts+'</body></html>',encoding='utf-8')
        (p/'README.txt').write_text(f'{c["title"]}\n\n与老师 firstbreak-pick-case 相同的导入方式：\n1. 解压本案例压缩包。\n2. 主网站点击“添加案例”。\n3. 选择或拖入整个 {c["id"]} 文件夹。\n4. 校验通过后添加，浏览专业背景、案例流程、案例演示。\n\n直接双击 demo/index.html 也可离线运行。无需安装、联网或后端。\n方法：{c["method"]}\n数据：程序生成的教学合成数据；页面指标实时计算，不代表真实工区效果。\n\n{c["limitation"]}\n',encoding='utf-8')
        name=c['category']+'-'+c['title']+'.zip'; c['zip']=name
        with zipfile.ZipFile(ROOT/'downloads'/name,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(p.rglob('*')):
                if f.is_file(): z.write(f,Path(c['id'])/f.relative_to(p))
        listing.append(c)
    (ROOT/'assets'/'catalog.js').write_text('window.CATALOG='+json.dumps(listing,ensure_ascii=False)+';',encoding='utf-8')
    # Remove only the obsolete generated ZIP names recorded in the prior catalog.
    wanted={x['zip'] for x in listing}
    download_root=(ROOT/'downloads').resolve()
    for old_name in old_names:
        if old_name and old_name not in wanted:
            target=(download_root/old_name).resolve()
            if target.parent!=download_root: raise RuntimeError('ZIP path escapes downloads')
            if target.is_file(): target.unlink()
    # Built-ins use the same manifest and identical demo files as the downloadable packages.
    text='(function(){\n'
    for c in listing:
        p=ROOT/'cases'/c['id']; pkg=json.loads((p/'case.json').read_text(encoding='utf-8'))
        fs=[dict(name=str(f.relative_to(p)).replace('\\','/'),data=f.read_text(encoding='utf-8'),enc='text',size=f.stat().st_size) for f in sorted((p/'demo').rglob('*')) if f.is_file()]
        text+='(function(){const p='+json.dumps(pkg,ensure_ascii=False)+', files='+json.dumps(fs,ensure_ascii=False)+';let h;const t=JSON.parse(JSON.stringify(p.tabs));t.demo.mount=function(root,ctx){h=CaseDemoHost.create(root,{files:files,demo:p.tabs.demo},ctx)};t.demo.unmount=function(){if(h)h.destroy();h=null};Cases.register({...p,status:"ready",tabs:t});})();\n'
    text+='})();'
    (ROOT/'assets'/'builtins.js').write_text(text,encoding='utf-8')
    print('Built',len(listing),'standalone cases and individual ZIP packages.')

if __name__=='__main__': build()
