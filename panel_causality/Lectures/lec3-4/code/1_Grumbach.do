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
  
* 展示顺序：TWFE FEct FEct-Test(no pretrend; placebo) SA CS  

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)             
               
------------------------------------------------------------------------------*/
clear

set more off

*下载黑白绘图模板tufte(可选)

*ssc install scheme_tufte,replace

set scheme tufte


*******************************************************************************
/*
导语：
本文利用1980年至2012年美国众议院大选中地区-选举年级别的TSCS数据，发现：
	亚裔（黑人/拉丁裔）候选人在大选中的出现会增加亚裔（黑人/拉丁裔）捐助者的竞选捐款份额
	（increase in coethnic contribution shares from Asian, black, or Latino donors substitutes for white contribution shares (p10)。
为了便于理解，我们重点讨论亚裔候选人的影响，以及论文中图5的左上角子图的相关设定。
*/
*******************************************************************************


*设置工作路径
cd "D:\APaper\YiQing_XU\grumbach"

use grumbach-sahn_apsr2020,clear

*设定文章暂元，便于后文引用
global article Grumbach2020

*-----------------修改变量名称
/*
方便大家明确Y、D等变量出现在代码中的位置，更好地理解代码含义（此部分操作非必选，供教学使用）。
*/

ren general_sharetotal_A_all Y
label var Y "general_sharetotal_A_all"

ren cand_A_all DA
label var DA "cand_A_all"

ren cand_B_all DB
label var DB "cand_B_all"

ren cand_H_all DH
label var DH "cand_H_all"

ren dfe id
label var id "dfe"

ren cycle year
label var year "cycle"

save grumbach2020, replace

*************************************TWFE **************************************

use grumbach2020,clear

*选取部分观测值利用panelview绘制图示以直观了解数据
panelview Y DA, i(id) t(year) type(treat)

*TWFE回归

reghdfe Y DA DB DH, absorb(id year) cluster(id)

reghdfe Y 1.DA#i.year 1.DB#i.year 1.DH#i.year, absorb(id year) cluster(id)


* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if DA==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

gen _tintra=(year-treatyear)/2
tab _tintra,m

global t 11

replace _tintra = $t if _tintra > $t
replace _tintra = -$t if _tintra < -$t

tab _tintra,m

forvalues l = 0/$t {
    gen L`l'event =  _tintra==`l'
}
forvalues l = 1/$t {
    gen F`l'event = _tintra==-`l'
}

ren (L0event) (L_0)

*将-1期设定为基期
replace F1event = 0

*TWFE回归
reghdfe Y L* F* DB DH, absorb(id year) cluster(id) 

*绘制图象
/*本文数据事后的observation数量很少，noise很大，故不在图中显示*/	
event_plot e(b)#e(V), plottype(scatter) stub_lag(L_#) stub_lead(F#event) together ///
	graph_opt(name($article_TWFE, replace) title("$article-TWFE") ///
	xtitle("Periods since the event")  ytitle("Average causal effect")   ///
	xlabel(-11(1)0) yline(0, lp(dash) lc(gs0) lw(thin)) xline(-1, lp(dash) lc(gs0) lw(thin)) ) 	
	
/*
！graph常用功能与命令：

*如需调用图象：
graph dis $article_TWFE

*另存为stata可编辑图象：
graph save "命名.gph", replace

*导出图象为png图片：
graph export "命名.png", replace

*/



***********************************FEct ****************************************

/*
基于 fect 命令，研究者可以生成 3 个关于 ATT 的反事实因果估计指标：
(1) 固定效应的反事实因果估计量  (Fixed-effect counterfactual estimator) ;
(2) 交互固定效应的反事实估计量 (Interactive fixed-effect counterfactual estimator) ;
(3) 矩阵完备估计量 (Matrix completion estimator)。
此处代码主要采用固定效应的反事实因果估计量 (FEct) 进行演示。
*/

/*fect 命令依赖 reghdfe 和 ftools 命令，因此首先安装最新的 reghdfe 命令和 ftools 命令*/

*ssc install reghdfe, replace

*ssc install ftools, replace

*----------安装 fect 命令

cap ado uninstall fect

*访问 github 安装
net install fect, from(https://raw.githubusercontent.com/xuyiqing/fect_stata/master/) replace

/*本地安装方法：
*首先从 fect 命令所在网址：https://github.com/xuyiqing/fect_stata，下载 ZIP 压缩文件。（考虑到国内访问 github 较慢，可以访问国内码云链接：https://gitee.com/caolinjun/fect_stata.git， 点击【克隆/下载】）。
*将文件解压到特定位置，如 D:\fect ，并将文件存放路径粘贴至 from() 中，运行以下命令即可完成安装。
cap ado uninstall fect
net install fect, all replace from("~/Downloads/fect_stata-master") //macOS
net install fect, all replace from("D:\fect") //Windows
*/


*----------运行命令

fect Y, treat(DA) unit(id) time(year) cov(DB DH) method(fe) force(two-way) preperiod(-11) offperiod(1) 
/*此处同样可以使用graph一系列命令进行图片的调用、保存与导出，略去不表。*/

*绘制置信区间（bootstrap 标准误）
fect Y, treat(DA) unit(id) time(year) cov(DB DH) method(fe) force(two-way) preperiod(-11) offperiod(1) se nboots(100)

*倘若需要知道 ATT 的精确数值，输入如下命令:
mat list e(ATT)

*倘若需要获取协变量和常数项的具体估计结果，输入如下命令:
mat list e(coefs)


*----------事前趋势检验（Pretrends Test）
/*
采用Wald Test来测度处理前的趋势。
原假设：在不同时期内样本处理前的残差均值都等于零。
*/

fect Y, treat(DA) unit(id) time(year) cov(DB DH) method(fe) force(two-way) preperiod(-11) offperiod(1) se nboots(200) ///
wald 

/*
 p 值大于 0.05，无法拒绝原假设；即样本在处理前的趋势是相似的。
*/


*----------安慰剂检验（Placebo Test）
/*
选定处理前的某一时间段作为"安慰剂期"，删除该时段后对模型进行拟合，然后检验该时段内的 ATT 是否显著不为零。
通常使用处理前 -2、-1和 0期作为安慰剂周期；也可以使用 palceboperiod() 自定义安慰剂期。
*/

fect Y, treat(DA) unit(id) time(year) cov(DB DH) method(fe) force(two-way) preperiod(-11) offperiod(1) se nboots(100) ///
placeboTest

/*
结果：左上角为安慰剂检验的 p 值。 p 值为 0.571 ，不能拒绝安慰剂周期内的 ATT 等于 0 的原假设。图中也显示，安慰剂区域 (Placebo Region) 与零值存在交集，通过安慰剂检验。
*/



*************************** SA (Sun & Abraham, 2020) ***************************

* 生成从未受处理组的虚拟变量
cap drop num
bys id: egen num = total(DA)
tab num,m
gen lastcohort = num==0

*SA回归估计
/*!在TWFE部分已经生成L*和F*，故此处未另外再生成。*/
eventstudyinteract Y L* F*, vce(cluster id) absorb(id year) cohort(treatyear) control_cohort(lastcohort)  

*绘制图象		
event_plot e(b_iw)#e(V_iw), plottype(scatter) stub_lag(L_#) stub_lead(F#event) together ///
	graph_opt(name($article_SA, replace) title("$article-SA") ///
	xtitle("Periods since the event")  ytitle("Average causal effect")   ///
	xlabel(-11(1)0) yline(0, lp(dash) lc(gs0) lw(thin)) xline(-1, lp(dash) lc(gs0) lw(thin)) ) 

	
	
************************ CS (Callaway & SantAnna, 2021) ************************

/*
Callaway 和 SantAnna (2021) 使用t期前从未受处理的组作为控制组进行估计。
该方法将样本分为不同的子组别，并分别估计不同组别的 ATT(g)；然后通过特定策略将不同组别的 ATT(g) 加总得出样本期的 ATT。
加总策略主要为降低可能存在偏误组的 ATT(g)的加总权重。
*/

tab treatyear,m

/*
gvar为多时期 DID 标识变量。
赋值时需要注意，如果在样本期受到过政策冲击，其值等于其受到冲击的期数次序。
Always-treated 组（某个个体在样本期开始前就已经受到冲击）默认不进入回归中。
*/
gen treat_symbol = treatyear/2
cap drop gvar
gen gvar = cond(treat_symbol==., 0, treat_symbol)

gen year_symbol = year/2

*ssc install avar, replace
*ssc install drdid, replace
*ssc install csdid, all replace


*-----------CS回归

*-估计冲击的动态效应

csdid Y DB DH, ivar(id) time(year_symbol) gvar(gvar) agg(event)

/*csdid 命令不要求数据为强平衡面板数据；不过在估计不同组的 ATT 时，存在缺失值的样本并不会进入回归*/






