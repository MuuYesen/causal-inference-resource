*  
*  ███████╗████████╗ █████╗ ████████╗ █████╗ 
*  ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
*  ███████╗   ██║   ███████║   ██║   ███████║
*  ╚════██║   ██║   ██╔══██║   ██║   ██╔══██║
*  ███████║   ██║   ██║  ██║   ██║   ██║  ██║
*  ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
*
/*------------------------------------------------------------------------------

                       面板数据因果推断：从入门到精通 
					   
                             徐轶青  2022.10       
							 
* 参考文献：
[1] TROUNSTINE, J. (2020). The Geography of Inequality: How Land Use Regulation Produces Segregation. American Political Science Review, 114(2), 443-455. 

* 方法参考文献：
[2] A Practical Guide to Counterfactual Estimators for Causal Inference with Time-Series Cross-Sectional Data with Licheng Liu and Ye Wang. American Journal of Political Science, forthcoming.
[3] Borusyak, Kirill, Xavier Jaravel, and Jann Spiess (2021). "Revisiting Event Study Designs: Robust and Efficient Estimation," Working paper.
[4] Callaway, Brantly, and Sant'Anna, Pedro H. C. 2020.  "Difference-in-Differences with multiple time periods." Journal of Econometrics.
[5] Sant'Anna, Pedro H. C., and Jun Zhao. 2020.  "Doubly Robust Difference-in-Differences Estimators." Journal of Econometrics 219 (1): 101–22.
  
* 展示顺序：panelview, Goodmanbacon分解, TWFE, SA, CS, FEct, FEct-Test(no pretrend; placebo)

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)             
               
------------------------------------------------------------------------------*/
clear

set more off

*可根据偏好自行设定绘图主题
*set scheme tufte

ssc install eventstudyinteract
ssc install avar
ssc install csdid
ssc install drdid, replace

*******************************************************************************
/*
导语：

*本文利用1968-2011年期间美国城市层面的TSCS数据，调查了土地使用变化（通过Fair Housing Act Lawsuit《公平住房法》诉讼衡量）对种族隔离的影响。

*论文发现，当城市被法院强迫放宽土地使用法时，当地有色人种人口会增加（"Table 2 offers clear evidence that when cities are threatened or forced by the court to liberalize their land use laws they see growth in their population of people of color (p451)."）。

*我们重点关注表2中的模型1。
*/
*******************************************************************************


*设置工作路径
cd "..."

*use trounstine_apsr2020,clear
*keep if year==1969|year==1979|year==1989|year==1999|year==2009

use trounstine2020,clear

*设定文章暂元，便于后文引用
global article Trounstine2020

*-----------------修改变量名称
/*
此处修改了原数据 变量名称，以便大家明确Y、D等变量出现在代码中的位置，更好地理解代码含义。
Y		pctnhwht_cityi	
D		fairhousingimp_v1	
id		geo_id2	           
*/

*设置控制变量暂元
global control pctrenter_cityi pctwlth_city2i logpop homevali pct_vacanti



****************** 数据结构图示 ******************

*选取部分观测值利用panelview绘制图示以直观了解数据
panelview Y D if id < 300000, i(id) t(year) type(treat) bytiming



********************* TWFE ***********************

*TWFE回归
use trounstine2020,clear

reghdfe Y D $control, absorb(id year) cluster(id)

* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

gen _tintra=(year-treatyear)/10
tab _tintra,m

global t 4

forvalues l = 0/$t {
    gen L_`l' =  _tintra==`l'
}

forvalues l = 1/$t {
    gen F_`l' = _tintra==-`l'
}


ren (L_3 L_4 F_4) ///
    (L3 L4  F4)

*将-1期设定为基期

replace F_1 = 0


*TWFE回归
reghdfe Y L* F* $control, absorb(id year) cluster(id) 

*绘制图象
event_plot e(b)#e(V), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_TWFE, replace) ///
	title("$article-TWFE") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal effect") ///
	xlabel(-3(1)2) ylabel(-0.2(0.05)0.15) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-1, lp(dash) lc(gs0) lw(thin)) ) 	

	
	
************* SA (Sun & Abraham, 2020) ****************
use trounstine2020, clear

* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

gen _tintra=(year-treatyear)/10
tab _tintra,m

global t 4

forvalues l = 0/$t {
    gen L_`l' =  _tintra==`l'
}

forvalues l = 1/$t {
    gen F_`l' = _tintra==-`l'
}


ren (L_3 L_4 F_3 F_4) ///
    (L3 L4 F3 F4)

*将-1期设定为基期

replace F_1 = 0

* 生成从未受处理组的虚拟变量
cap drop num
bys id: egen num = total(D)
tab num,m
gen lastcohort = num==0

*SA回归估计
/*!在TWFE部分已经生成L*和F*，故此处未另外再生成。*/
/*！此代码运行较为耗费时间*/
eventstudyinteract Y L* F*, vce(cluster id) absorb(id year) ///
	cohort(treatyear) control_cohort(lastcohort)  

*绘制图象		
event_plot e(b_iw)#e(V_iw), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_SA, replace) ///
	title("$article-SA") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal effect")   ///
	xlabel(-3(1)2) ylabel(-0.2(0.05)0.15) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-0.5, lp(dash) lc(gs0) lw(thin)) ) 


	
********** CS (Callaway & SantAnna, 2021) *************

use trounstine2020, clear

/*
Callaway 和 SantAnna (2021) 使用t期前从未受处理的组作为控制组进行估计。
该方法将样本分为不同的子组别，并分别估计不同组别的 ATT(g)；然后通过特定策略将不同组别的 ATT(g) 加总得出样本期的 ATT。
加总策略主要为降低可能存在偏误组的 ATT(g)的加总权重。
*/
bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

recode treatyear (1969 = 1) (1979 = 2) (1989 = 3) (1999 = 4) (2009 = 5)

recode year (1969 = 1) (1979 = 2) (1989 = 3) (1999 = 4) (2009 = 5)

/*
gvar为多时期 DID 标识变量。
赋值时需要注意，如果在样本期受到过政策冲击，其值等于其受到冲击的期数次序。
Always-treated 组（某个个体在样本期开始前就已经受到冲击）默认不进入回归中。
*/
gen gvar = cond(treatyear==., 0, treatyear)



*-----------CS回归-----------*

*-估计冲击的动态效应

csdid Y $control, ivar(id) time(year) gvar(gvar) agg(event)

/*csdid 命令不要求数据为强平衡面板数据；不过在估计不同组的 ATT 时，存在缺失值的样本并不会进入回归*/

estat event, window(-2 2) estore(cs) 

event_plot cs, plottype(scatter) ///
	stub_lag(Tp#) stub_lead(Tm#) together ///
	graph_opt(name($article_CS, replace) ///
	title("$article-CS") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal  effect") ///
	xlabel(-2(1)2)  ylabel(-0.2(0.05)0.15) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(0, lp(dash) lc(gs0) lw(thin)) ) 


	
***********************FEct ****************************

use trounstine2020,clear

fect Y, treat(D) unit(id) time(year) cov($control) method(fe) force(two-way) ///
	preperiod(-2) offperiod(2) minT0(1)
/*此处同样可以使用graph一系列命令进行图片的调用、保存与导出，略去不表。*/

*绘制置信区间（bootstrap 标准误）
fect Y, treat(D) unit(id) time(year) cov($control) method(fe) force(two-way) ///
	preperiod(-2) offperiod(2) se nboots(100) minT0(1)

*倘若需要知道 ATT 的精确数值，输入如下命令:
mat list e(ATT)

*倘若需要获取协变量和常数项的具体估计结果，输入如下命令:
mat list e(coefs)


*----------事前趋势检验（Pretrends Test）
/*
采用Wald Test来测度处理前的趋势。
原假设：在不同时期内样本处理前的残差均值都等于零。
*/

fect Y, treat(D) unit(id) time(year) cov($control) method(fe) force(two-way) ///
	preperiod(-2) offperiod(2) se nboots(100) wald minT0(1)

/*
结果：左上角为事前趋势检验验的 p 值。通常当 p 值大于0.05时认为无法拒绝原假设，即样本在处理前的趋势是相似的。
*/




*----------安慰剂检验（Placebo Test）
/*
选定处理前的某一时间段作为"安慰剂期"，删除该时段后对模型进行拟合，然后检验该时段内的 ATT 是否显著不为零。
通常使用处理前 -2、-1和 0期作为安慰剂周期；也可以使用 placeboperiod() 自定义安慰剂期。
*/

fect Y, treat(D) unit(id) time(year) cov($control) method(fe) force(two-way) ///
	preperiod(-2) offperiod(2) se nboots(100) minT0(1) ///
	placeboTest placeboperiod(1) 

/*
结果：左上角为安慰剂检验的 p 值。 p 值小于 0.05时，则认为应当拒绝安慰剂周期内的 ATT 等于 0 的原假设。不通过安慰剂检验的情况下，可以看到安慰剂区域 (Placebo Region) 与y轴零值不存在交集。
*/

*----------加入线性趋势控制---------*

fect Y, treat(D) unit(id) time(year) cov($control) method(polynomial) degree(1) ///
	force(two-way) preperiod(-2) offperiod(2) minT0(1)
/*注意此处y轴刻度非常小，所以折线已经高度接近直线*/





