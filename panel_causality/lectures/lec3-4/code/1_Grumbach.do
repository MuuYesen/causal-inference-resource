*  
*  ███████╗████████╗ █████╗ ████████╗ █████╗ 
*  ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
*  ███████╗   ██║   ███████║   ██║   ███████║
*  ╚════██║   ██║   ██╔══██║   ██║   ██╔══██║
*  ███████║   ██║   ██║  ██║   ██║   ██║  ██║
*  ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
*
/*------------------------------------------------------------------------------

*                      面板数据因果推断：从入门到精通 
					   
*                             徐轶青  2022.10       
							 
* 复制文献：
[1] Grumbach, J. M., & Sahn, A. (2020). Race and representation in campaign finance. American Political Science Review, 114(1), 206-221. 

* 方法参考文献：
[2] A Practical Guide to Counterfactual Estimators for Causal Inference with Time-Series Cross-Sectional Data with Licheng Liu and Ye Wang. American Journal of Political Science, forthcoming.
[3] Borusyak, Kirill, Xavier Jaravel, and Jann Spiess (2021). "Revisiting Event Study Designs: Robust and Efficient Estimation," Working paper.
[4] Callaway, Brantly, and Sant'Anna, Pedro H. C. 2020.  "Difference-in-Differences with multiple time periods." Journal of Econometrics.
[5] Sant'Anna, Pedro H. C., and Jun Zhao. 2020.  "Doubly Robust Difference-in-Differences Estimators." Journal of Econometrics 219 (1): 101–22.
  
* 展示顺序：panelview TWFE FEct FEct-Test(no pretrend; placebo)

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)             
               
------------------------------------------------------------------------------*/
clear

set more off

*可根据偏好自行设定绘图主题
*set scheme tufte

*所需要的软件包（可按需要安装）
ssc install reghdfe, replace
ssc install ftools, replace
ssc install panelview
ssc install event_plot


/*fect 命令依赖 reghdfe 和 ftools 命令，因此首先安装最新的 reghdfe 命令和 ftools 命令*/

*ssc install reghdfe, replace
*ssc install ftools, replace

*----------安装 fect 命令

cap ado uninstall fect

*访问 github 安装
net install fect, from("https://raw.githubusercontent.com/xuyiqing/fect_stata/master/") replace

/*本地安装方法：
*首先从 fect 命令所在网址：https://github.com/xuyiqing/fect_stata，下载 ZIP 压缩文件。（考虑到国内访问 github 较慢，可以访问国内码云链接：https://gitee.com/caolinjun/fect_stata.git， 点击【克隆/下载】）。
*将文件解压到特定位置，如 D:\fect ，并将文件存放路径粘贴至 from() 中，运行以下命令即可完成安装。
cap ado uninstall fect
net install fect, all replace from("~/Downloads/fect_stata-master") //macOS
net install fect, all replace from("D:\fect") //Windows
*/


*******************************************************************************
/*
导语：
本文利用1980年至2012年美国众议院大选中地区-选举年级别的面板数据，发现：
	亚裔（黑人/拉丁裔）候选人在大选中的出现会增加亚裔（黑人/拉丁裔）捐助者的竞选捐款份额

为了便于理解，我们重点讨论亚裔候选人的影响，以及论文中图5的左上角子图的相关设定。
*/
*******************************************************************************


*设置工作路径
cd "..."


*设定文章暂元，便于后文引用
global article Grumbach-Sahn2020

*-----------------变量名称对应
/*
此处修改了原数据 变量名称，以便大家明确Y、D等变量出现在代码中的位置，更好地理解代码含义。

Y		general_sharetotal_A_all	亚裔捐款份额
DA		cand_A_all	亚裔候选人
DB  	cand_B_all	非洲裔候选人
DH		cand_H_all	拉美裔候选人
id		dfe			选区
cycle 	cycle		选举周期
*/



****************** 数据结构图示 ******************

use gs2020, clear

*选取部分观测值利用panelview绘制图示以直观了解数据
panelview Y DA, i(id) t(cycle) type(treat)



********************* TWFE ***********************

*TWFE回归

reghdfe Y DA DB DH, absorb(id cycle) cluster(id)

* 生成各期处理组的虚拟变量

bys id: egen treatcycle_m = min(cycle) if DA==1
tab treatcycle_m,m

bys id: egen treatcycle = mean (treatcycle_m)
tab treatcycle,m

gen _tintra=(cycle-treatcycle)/2
tab _tintra,m

global t 11

tab _tintra,m

forvalues l = 1/$t {
    gen F_`l' = _tintra==-`l'
}

sum _tintra
forvalues l = 11/16 {
    gen F`l'event = _tintra==-`l'
}

forvalues l = 0/16 {
    gen L`l'event =  _tintra==`l'
}

ren (L0event) (L_0)

*将-1期设定为基期
replace F_1 = 0

*TWFE回归
reghdfe Y L* F* DB DH, absorb(id cycle) cluster(id) 

*绘制图象
/*本文数据事后的observation数量很少，noise很大，故不在图中显示*/	
event_plot e(b)#e(V), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_TWFE, replace) ///
	title("$article-TWFE") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal effect")   ///
	xlabel(-11(1)0) ylabel(-0.15(0.05)0.2) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-1, lp(dash) lc(gs0) lw(thin)) ) 	
	
/*
！graph常用功能与命令：

*如需调用图象：
graph dis $article_TWFE

*另存为stata可编辑图象：
graph save "命名.gph", replace

*导出图象为png图片：
graph export "命名.png", replace

*/



****************FEct ***************************

/*
基于 fect 命令，研究者可以生成 3 个关于 ATT 的反事实因果估计指标：
(1) 固定效应的反事实因果估计量  (Fixed-effect counterfactual estimator) ;
(2) 交互固定效应的反事实估计量 (Interactive fixed-effect counterfactual estimator) ;
(3) 矩阵完备估计量 (Matrix completion estimator)。
此处代码主要采用固定效应的反事实因果估计量 (FEct) 进行演示。
*/


*----------运行命令----------*

fect Y, treat(DA) unit(id) time(cycle) cov(DB DH) method(fe) ///
	force(two-way) preperiod(-11) offperiod(1) minT0(1)
/*此处同样可以使用graph一系列命令进行图片的调用、保存与导出，略去不表。*/

*绘制置信区间（bootstrap 标准误）
fect Y, treat(DA) unit(id) time(cycle) cov(DB DH) method(fe) ///
	force(two-way) preperiod(-11) offperiod(1) se nboots(100) minT0(1)

*倘若需要知道 ATT 的精确数值，输入如下命令:
mat list e(ATT)

*倘若需要获取协变量和常数项的具体估计结果，输入如下命令:
mat list e(coefs)


*----------事前趋势检验（Pretrends Test）----------*
/*
采用Wald Test来测度处理前的趋势。
原假设：在不同时期内样本处理前的残差均值都等于零。
*/

fect Y, treat(DA) unit(id) time(cycle) cov(DB DH) method(fe) ///
	force(two-way) preperiod(-11) offperiod(1) minT0(1) ///
	se nboots(200) wald 

/*
 p 值大于 0.05，无法拒绝原假设；即样本在处理前的趋势是相似的。
*/


*----------安慰剂检验（Placebo Test）----------*
/*
选定处理前的某一时间段作为"安慰剂期"，删除该时段后对模型进行拟合，然后检验该时段内的 ATT 是否显著不为零。
通常使用处理前 -2、-1和 0期作为安慰剂周期；也可以使用 palceboperiod() 自定义安慰剂期。
*/

fect Y, treat(DA) unit(id) time(cycle) cov(DB DH) method(fe) ///
	force(two-way) preperiod(-11) offperiod(1) minT0(1) ///
	se nboots(100) placeboTest

/*
结果：左上角为安慰剂检验的 p 值。 p 值为 0.571 ，不能拒绝安慰剂周期内的 ATT 等于 0 的原假设。图中也显示，安慰剂区域 (Placebo Region) 与零值存在交集，通过安慰剂检验。
*/


