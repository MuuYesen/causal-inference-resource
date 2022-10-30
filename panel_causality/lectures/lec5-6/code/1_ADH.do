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
[1] Alberto Abadie, Alexis Diamond & Jens Hainmueller (2010). Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program, Journal of the American Statistical Association, 105:490, 493-505, DOI: 10.1198/jasa.2009.ap08746

[2] Abadie, Alberto, Alexis Diamond, and Jens Hainmueller (2015). "Comparative Politics and the Synthetic Control Method." American Journal of Political Science 59.2: 495-510.
							
* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)             
               
*------------------------------------------------------------------------------*/

ssc install synth
net install synth_runner, ///
	from("https://raw.github.com/bquistorff/synth_runner/master/") replace


clear
set more off

global path = "..."
cd $path

set scheme s1mono

/****** 1. California smoking ******/

*----------------
/* 合成控制法 */
*----------------

use "california", clear

gen treat=0
replace treat=1 if year > 1989 & state==3

panelview cigsale treat, i(state) t(year) type(treat)


panelview cigsale treat, i(state) t(year) type(outcome) prepost

** 实现方式1 **
		  
xtset state year


synth_runner cigsale ///
	lnincome age15to24 retprice beer cigsale(1988) cigsale(1980) cigsale(1975), ///
	trunit(3) trperiod(1989) xperiod(1980(1)1988) gen_vars

		* cigsale(1975) cigsale(1980) cigsale(1988) 分别表示人均香烟消费在1975、1980与1988年的取值
		* 必选项 trunit(3) 表示第 3 个州（即加州）为处理地区
		* 必选项 trperiod(1989) 表示控烟法在 1989 年开始实施
		* 结果报告的表格显示，加州控烟法对于人均香烟消费量有很大的负效应，而且此效应随着时间推移而变大，且统计上显著。具体来说，在 1989-2000 年（C1-C12）期间，加州的人均年香烟消费逐年减少
		

*绘制图形查看合成效果，并绘制加州与合成加州人均香烟消费之差（即处置效应）：
single_treatment_graphs, trlinediff(-1) effects_ylabels(-30(10)30)  ///
effects_ymax(35) effects_ymin(-35)
	*one raw graph for each unit 每州有一个原始图
	*one effect graph for each unit 每州有一个效果图


effect_graphs, trlinediff(-1)
	*one effect graph for California 加州效果图
	*one comparison graph for real California and synthetic California 真实加州和合成加州的一个比较图象

	
** 实现方式2 **
/*
命令语法：
synth2 depvar indepvars, trunit(#) trperiod(#) [options]
*/
synth2 cigsale lnincome age15to24 retprice beer ///
	cigsale(1988) cigsale(1980) cigsale(1975), ///
	trunit(3) trperiod(1989) xperiod(1980(1)1988) placebo(unit cut(2))

*展示图象
graph display eff_pboUnit
	
*----------------
/* 合成倍差法 */
*----------------

use "california", clear

gen treat=0
replace treat=1 if year > 1989 & state==3

*ssc install sdid, replace // https://github.com/Daniel-Pailanir/sdid

/*
命令语法：
sdid Y S T D [if] [in], vce(method) seed(#) reps(#) covariates(varlist [, method]) ///
    graph g1_opt(string) g2_opt(string) unstandardized graph_export([stub] , type)
*/
sdid cigsale state year treat, vce(placebo) seed(123) reps(50) ///
	graph graph_export(sdid_, .eps) g1_opt(xtitle(""))

	* 导出图象：
	* g1 -- Unit-Specific Weights 各州权重图示
  	* g2 -- Outcome Trends and Time-Specific Weights 结果趋势和特定时间权重图示

				
				
				
/****** 2. West Germany reunification ******/

*----------------
/* 合成控制法 */
*----------------

use "germany", clear

gen treat=0
replace treat=1 if year > 1990 & index==7

panelview gdp treat, i(index) t(year) type(outcome) prepost

panelview gdp treat, i(index) t(year) type(treat)

** 实现方式1 **
xtset index year

synth_runner gdp ///
	infrate trade ///
    industry  ///
    schooling(1980) invest80(1980),  ///
    trunit(7) trperiod(1990) xperiod(1981(1)1990) gen_vars
		

*绘制图形查看合成效果，并绘制德国与合成德国人均gdp之差（即处置效应）：
single_treatment_graphs, trlinediff(-1) 
	*one raw graph for each unit
	*one effect graph for each unit

effect_graphs, trlinediff(-1)
	*one effect graph for California
	*one comparison graph for real West Germany and synthetic West Germany

	
** 实现方式2 **

synth2 gdp trade infrate industry schooling(1980) invest80(1980), ///
	trunit(7) trperiod(1990) xperiod(1981(1)1990) placebo(unit cut(2))

*展示图象
graph display eff_pboUnit

	
*----------------
/* 合成倍差法 */
*----------------

use "germany", clear

gen treat=0
replace treat=1 if year > 1990 & index==7

sdid gdp index year treat, vce(placebo) seed(123) reps(50) ///
	graph graph_export(sdid_, .eps) g1_opt(xtitle(""))

	* 导出图象：
	* g1 -- Unit-Specific Weights 各个country权重图示
	* g2 -- Outcome Trends and Time-Specific Weights 结果趋势和特定时间权重图示

	
