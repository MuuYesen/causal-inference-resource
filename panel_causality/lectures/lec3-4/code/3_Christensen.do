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
							 
* 文献：
[1] Christensen, D., & Garfias, F. (2021). The politics of property taxation: 
  Fiscal infrastructure and electoral incentives in Brazil. The Journal of Politics, 83(4), 1399-1416.

  
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

*安装下更软件包
*ssc install eventstudyinteract, replace

*ssc install avar, replace
*ssc install drdid, replace
*ssc install csdid, all replace


cd "..."

use christensen-garfias_jop2021,clear

global article Christensen-Garfias-2021

*------------ 修改变量名称 ------------*
/*
此处修改了原数据 变量名称，以便大家明确Y、D等变量出现在代码中的位置，更好地理解代码含义。

Y	logiptu
D	cad_update
id	c6_ibge

*/





****************** 数据结构图示 ******************

use cg2021, clear

*选取部分观测值利用panelview绘制图示以直观了解数据
panelview Y D if id < 200000, i(id) t(year) type(treat) bytiming




********************* TWFE ***********************

use cg2021, clear

*TWFE回归

reghdfe Y D, absorb(id year) cluster(id)

* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

gen _tintra=year-treatyear
tab _tintra,m

global t 5

*此处为了同另一篇复现文章结果相对应比较，故如此设定期限区间

forvalues l = 0/4 {
    gen L_`l' =  _tintra==`l'
}

forvalues l = 1/6 {
    gen F_`l' = _tintra==-`l'
}

sum _tintra

forvalues l = 5/11 {
    gen L`l' =  _tintra==`l'
}

forvalues l = 7/11 {
    gen F`l' = _tintra==-`l'
}

*将-1期设定为基期

replace F_1 = 0


*TWFE回归
reghdfe Y L* F*, absorb(id year) cluster(id) 

*绘制图象
event_plot e(b)#e(V), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_TWFE, replace) ///
	title("$article-TWFE") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal effect") ///
	xlabel(-6(1)4) ylabel(-1(0.5)1) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-1, lp(dash) lc(gs0) lw(thin)) ) 	

	
*************SA (Sun & Abraham, 2020) *********************

use cg2021, clear

*TWFE回归
reghdfe Y D, absorb(id year) cluster(id)

* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

gen _tintra=year-treatyear
tab _tintra,m

*此处为了同另一篇复现文章结果相对应比较，故如此设定期限区间

tab _tintra,m

forvalues l = 0/5 {
    gen L_`l' =  _tintra==`l'
}

forvalues l = 1/6 {
    gen F_`l' = _tintra==-`l'
}

sum _tintra

forvalues l = 6/11 {
    gen L`l' =  _tintra==`l'
}

forvalues l = 7/11 {
    gen F`l' = _tintra==-`l'
}

* 生成 never_treated 和 last_cohort
gen never_treat = treatyear==.

sum treatyear

gen last_cohort = treatyear==r(max) 

replace F_1 = 0

**#SA回归估计
/*！此代码运行可能较为耗费时间*/

*使用last_cohort作为控制组
eventstudyinteract Y L* F*, vce(cluster id) ///
	absorb(id year) cohort(treatyear) ///
	control_cohort(last_cohort)  

*绘制图象
event_plot e(b_iw)#e(V_iw), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_SA1, replace) ///
	title("$article-SA1") ///
	xtitle("Periods since the event")  ///
	ytitle("Average causal effect")   ///
	xlabel(-6(1)5) ylabel(-1(0.5)1) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-1, lp(dash) lc(gs0) lw(thin))) 

*使用never_treated作为控制组
eventstudyinteract Y L* F*, vce(cluster id) ///
	absorb(id year) cohort(treatyear) ///
	control_cohort(never_treat)  

*再次绘制图象
event_plot e(b_iw)#e(V_iw), plottype(scatter) ///
	stub_lag(L_#) stub_lead(F_#) together ///
	graph_opt(name($article_SA2, replace) ///
	title("$article-SA2") ///
	xtitle("Periods since the event")  ///
	ytitle("Average causal effect")   ///
	xlabel(-6(1)5) ylabel(-1(0.5)1) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(-1, lp(dash) lc(gs0) lw(thin)) ) 

	
	
*********** CS (Callaway & SantAnna, 2021) *******************

use cg2021, clear

/*
Callaway 和 SantAnna (2021) 使用t期前从未受处理的组作为控制组进行估计。
该方法将样本分为不同的子组别，并分别估计不同组别的 ATT(g)；然后通过特定策略将不同组别的 ATT(g) 加总得出样本期的 ATT。
加总策略主要为降低可能存在偏误组的 ATT(g)的加总权重。
*/

* 生成各期处理组的虚拟变量

bys id: egen treatyear_m = min(year) if D==1
tab treatyear_m,m

bys id: egen treatyear = mean (treatyear_m)
tab treatyear,m

/*
gvar为多时期 DID 标识变量。
赋值时需要注意，如果在样本期受到过政策冲击，其值等于其受到冲击的期数次序。
Always-treated 组（某个个体在样本期开始前就已经受到冲击）默认不进入回归中。
*/

gen gvar = cond(treatyear==., 0, treatyear)

*-----------CS回归----------*

*-估计冲击的动态效应

csdid Y, ivar(id) time(year) gvar(gvar) agg(event) 

estat event, window(-5 5) estore(cs) 

event_plot cs,  plottype(scatter) ///
	stub_lag(Tp#) stub_lead(Tm#) together ///
	graph_opt(name($article_CS, replace) ///
	title("$article-CS") ///
	xtitle("Periods since the event") ///
	ytitle("Average causal  effect") ///
	xlabel(-5(1)5) ylabel(-1(0.5)1) ///
	yline(0, lp(dash) lc(gs0) lw(thin)) ///
	xline(0.5, lp(dash) lc(gs0) lw(thin)) ) 



************************ FEct ************************

use cg2021, clear

*此处0标记的是处理前一期
fect Y, treat(D) unit(id) time(year) method(fe) ///
	force(two-way) preperiod(-5) offperiod(5) minT0(1)
/*此处同样可以使用graph一系列命令进行图片的调用、保存与导出，略去不表。*/

*绘制置信区间（bootstrap 标准误）
/*！此代码运行较为耗费时间*/
fect Y, treat(D) unit(id) time(year) method(fe) ///
	force(two-way) preperiod(-5) offperiod(5) se nboots(100) minT0(1)

*倘若需要知道 ATT 的精确数值，输入如下命令:
mat list e(ATT)

*倘若需要获取协变量和常数项的具体估计结果，输入如下命令:
mat list e(coefs)


*---------- 事前趋势检验（Pretrends Test） ------------*
/*
采用Wald Test来测度处理前的趋势。
原假设：在不同时期内样本处理前的残差均值都等于零。
*/

fect Y, treat(D) unit(id) time(year) method(fe) ///
	force(two-way) preperiod(-6) offperiod(6) ///
	se nboots(100) wald minT0(1)


*---------- 安慰剂检验（Placebo Test） ------------*
/*
选定处理前的某一时间段作为"安慰剂期"，删除该时段后对模型进行拟合，然后检验该时段内的 ATT 是否显著不为零。
通常使用处理前 -2、-1和 0期作为安慰剂周期；也可以使用 palceboperiod() 自定义安慰剂期。
*/

fect Y, treat(D) unit(id) time(year) method(fe) ///
	force(two-way) preperiod(-6) offperiod(4) ///
	se nboots(100) placeboTest minT0(1)












