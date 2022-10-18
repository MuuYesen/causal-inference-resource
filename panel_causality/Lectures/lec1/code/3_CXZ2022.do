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
  Cao, J., Xu, Y., & Zhang, C. (2022). Clans and calamity: How social capital saved 
  lives during China's Great Famine. Journal of Development Economics, 157, 102865.

* 展示顺序：Fig 2 4 5 6 7 8; Table 1 3 2

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)                            
------------------------------------------------------------------------------*/

*************************************
* Set path to the replication folder  
*************************************

*！请将Stata的工作路径设置为保存论文复现材料的路径
cd "...cxz2022"


clear all
set more off
set scheme s1color

**============================================================================**
**                                Figures                                     **
**============================================================================**


**********************************
**Figure 2: Genealogies by Year
**********************************

***Figure 2a: Distribution of compilation date
use "gbooks_byyear.dta",replace

*绘制直方图
hist year if year>=1400 & year<=2010, freq bin(200) ylabel(0(500)2500) xtitle("Year") xline(1950 1980,lw(thin)) ///
     text(1500 1950 "Year=1950", place(w)) text(2000 1980 "Year=1980", place(w)) 
	 /*text: 在图中y轴坐标1500、x轴坐标1950处添加文本注释"Year=1950"*/
gr export "graphs/Figure2a.pdf",replace


***Figure 2b: Distribution of #Genealogies

use "clan_distr.dta",clear

*绘制直方图
hist lnzupunum50 if lnzupunum50<=3.5,freq bin(70) ylabel(0(100)500) xlabel(0(0.5)3.5) ///
xtitle("log(#Genealogies/Population)") xline(0.052 0.256,lw(thin) lp(dash)) ///
     text(550 0.75 "median=0.052", place(w)) text(500 0.9 "mean=0.256", place(w)) 
gr export "graphs/Figure2b.pdf",replace


*****************************************
**Figure 4: Persistence of social capital
*****************************************

use "clan_persistence.dta",clear

gen lnbook_50 = log(zupunum50+1)
gen lnbook_80 = log(zupunum80+1)

***Figure 4a: Persistence of Genealogies

*相关系数
corr lnbook_80 lnbook_50

*设定暂元corrcoef(下文代码中将会引用)
local corrcoef = round(r(rho),0.01)
/*round: r(rho)四舍五入为两位小数（0.01）*/
/*r(rho): 存储的相关系数的值*/
/*当执行corr的命令后，stata会自动储存一些返回值，通过return list可以查看;
r(rho)是其中的一个返回值*/

*绘制图象
tw (sc lnbook_80 lnbook_50, msym(oh) mc(gray) text(5 2 "Correlation =`corrcoef'")) ///
   (lowess lnbook_80 lnbook_50, legend(off) ytit("Genealogies after 1980") xtit("Genealogies before 1950") xlab(0(1)6.5))
gr export "graphs/Figure4a.pdf",replace


***Figure 4b: Preservation of Genealogies
use "clan_persistence.dta",clear

gen lnbook_50 = log(zupunum50+1)
gen lnbook_80 = log(zupunum80+1)

gen CR1_high = CR1>=CR1_m

corr lnbook_80 lnbook_50 if CR1_high==1
local corrcoef1 = round(r(rho),0.01)
corr lnbook_80 lnbook_50 if CR1_high==0
local corrcoef0 = round(r(rho),0.01)

tw (sc lnbook_80 lnbook_50 if CR1_high==1, msym(oh) mc(red) ) ///
   (lowess lnbook_80 lnbook_50 if CR1_high==1, lc(red) xlabel(0(2)7) ) ///
   (sc lnbook_80 lnbook_50 if CR1_high==0, msym(th) mc(blue)) ///
    (lowess lnbook_80 lnbook_50 if CR1_high==0, lc(blue) ytit("#Genealogies compiled after 1980") xtit("#Genealogies compiled before 1950") legend(label (1 "High intensity of CR") label (2 "Corr = `corrcoef1'") label (3 "Low intensity of CR") label (4 "Corr = `corrcoef0'") pos(11) ring(0)))
gr export "graphs/Figure4b.pdf",replace



**********************************************
**Figure 5: Mortality trends by social capital
**********************************************
use "mortality_sample.dta",clear

***Figure 5a:level

*展示根据highzupu50和year分组后的变量drqianfen均值；
collapse (mean) drqianfen,by(highzupu50 year)

*绘制图象
twoway (con drqianfen year if highzupu50==1, lp(dash)) (con drqianfen year if highzupu50==0), legend(label(1 "High") label(2 "Low") ring(0) pos(11)) ytitle("Mortality rate(‰)") xtitle("Year") xlabel(1954(2)1966) 
gr export "graphs/Figure5a.pdf",replace

***Figure 5b:demeaned

use "mortality_sample.dta",clear

*生成drqianfen的根据年份分组后的均值变量
bys year : egen meandrqianfen = mean(drqianfen)
replace drqianfen = drqianfen -meandrqianfen

collapse (mean) drqianfen,by(highzupu50 year)
g high = 3
g low = -3

*绘制图象
twoway (con drqianfen year if highzupu50==1, lp(dash) ms(t) yline(0,lp(dash) lc(red))  ) ///
       (con drqianfen year if highzupu50==0, lp(solid)  ylabel(-3(1)3) legend(label(1 "High") label(2 "Low")  ring(0) pos(11)) ytitle("Deviation from the mean of ortality rate(‰)") xtitle("Year") xlabel(1954(1)1966))
        
gr export "graphs/Figure5b.pdf",replace


**********************************************
**Figure 6: Mortality dynamic
**********************************************

use "mortality_sample.dta",clear

*生成新变量
gen famineyear = (year>=1958&year<=1961)

gen lnzupu50_fyr = lnzupunum50*famineyear
gen high50_fyr = highzupu50*famineyear
gen zupu50per_fyr = zupu50per*famineyear

gen nograin_fyr = nograinratio*famineyear
gen avggrain_fyr = avggrain*famineyear
gen urban_fyr= urbanratio57*famineyear
gen minor_fyr = minor*famineyear
gen edu_fyr = ysch*famineyear
gen dis_bj_fyr = distance_bj*famineyear
gen dis_pc_fyr = distance_pc*famineyear
gen migrants_fyr = migrants*famineyear
gen rice_fyr = ln_wetland_rice*famineyear

gen lggrain = log(grainoutput01)
gen lggrain_pc = log(grainoutput01/pop1957)

gen t = year-1954

*添加变量标签
label var lggrain "Lg(Total grain output)"
label var lggrain_pc "Lg(Grain output pc)"

label var avggrain_fyr "Per capita grainproduction x Famine period"
label var nograin_fyr "Non-agricultural land ratio x Famine period"
label var urban_fyr "Urbanization rate in 1957 x Famine period"
label var minor_fyr "Share of minority x Famine period"
label var edu_fyr "Averaged schooling x Famine period"

label var dis_bj_fyr "Distance from Beijing x Famine period"
label var dis_pc_fyr "Distance from provincial capital x Famine period"
label var migrants_fyr "Historical migrants x Famine period"
label var rice_fyr "Crop suitability index for rice x Famine period"

label var high50_fyr "High x Famine period"
label var zupu50per_fyr "Book intensity x Famine period"
label var lnzupu50_fyr "LgBook x Famine period"



g rsample = !mi(avggrain_fyr) & !mi(nograin_fyr) & !mi(urban_fyr)& !mi(dis_bj_fyr) & !mi(dis_pc_fyr) & !mi(migrants_fyr)& !mi(rice_fyr) & !mi(minor_fyr) & !mi(edu_fyr)

global CONTROL = "avggrain_fyr nograin_fyr urban_fyr dis_bj_fyr dis_pc_fyr migrants_fyr rice_fyr minor_fyr edu_fyr"


*生成highzupu和1954-1966的year虚拟变量间的交乘项
forvalues i=1954/1966{
g High_Y`i' = highzupu50*(year==`i')
label var High_Y`i' "`i'"
} 

ren High_Y1957 High_Base

*TWFE回归
reghdfe drqianfen High_Y* $CONTROL,absorb(year countyid) cluster(countyid)

gen coef = . 
gen se = . 

//local se_0 = _se[_cons]

*逐个存储High_Y*的系数（1954-1966，除去基期1957，共12个；存为前12条数据）
local j = 1 
foreach var of var High_Y* {
replace coef = _b[`var'] in `j'
replace se = _se[`var'] in `j'

local ++j
}

*生成置信区间上下界
gen up_ci = coef + 1.96* se
gen low_ci = coef - 1.96*se

keep coef* se* up_* low_*

g Year=_n+1953

*空出1957年
replace Year=Year+1 if Year>=1957

*保留前13行数据
keep in 1/13

*将基期（1957年）的系数与置信区间上下界替换为0。
replace Year = 1957 in 13 
replace coef = 0 in 13 
replace up_ci = 0 in 13 
replace low_ci = 0 in 13 
sort Year

*绘制图象
tw  (con coef Year, yline(0) xlabel(1954(1)1966) xline(1957.5 1961.5,lp(dash) lc(gray)) text(1 1959.5 "famine") ytit("Estimated Coef. with 95 Percent Confidence Interval") xtit("Year", size(small))) ///
   (rcap up_ci low_ci Year, lp(dash)  legend(ring(0) pos(11) label(1 "Coef.")  label(2 "95% CI") col(2) size(small))) 
gr export "graphs/Figure6.pdf",replace


***********************************************************
**Figure 7a: Clan and Average Hunger Experience
***********************************************************

use "CFPS_hunger_sample.dta",clear

keep if urban==0
keep if byear>=1941 & byear<=1970

collapse (mean) hunger,by(highczupu byear)

*分组绘制图象
twoway (con hunger byear if highczupu==1) (con hunger byear if highczupu==0) , ///
 legend(label(1 "High Clan Density") label(2 "Low Clan Density")) ytitle("Hunger Experience") xtitle("Birth Year") xline(1962)
gr export "graphs/Figure7a.pdf",replace


***********************************************************
**Figure 7b: Dynamic Effect of Clans on Hunger Experience
***********************************************************

use "CFPS_hunger_sample.dta",clear

gen rsample = !mi(gender) & !mi(minor) & !mi(urbanhk) & !mi(educ) & !mi(sibnum)

global CONTROLS = "gender minor urbanhk i.educ sibnum"

keep if urban==0

*生成1950-1965年各年份的虚拟变量与highczupu的交乘项
forvalues i=1950(1)1965 {

g Y_`i' = (byear==`i')*highczupu
label var Y_`i' "`i'"
}

*将早于1950的数据归并处理至1950年
replace Y_1950 = (byear<=1950)*highczupu

reghdfe hunger Y_1950-Y_1965 $CONTROLS, absorb(commid byear) cluster(commid)
est sto hunger_dynamic

* ssc install coefplot //如果加载不出来 coefplot 命令，则运行此行代码安装
coefplot hunger_dynamic, ytit("Estimated Coefficient") xtit("Year") yline(0) level(90) vertical keep(Y_*) recast(connect) offset(0) xline(9 12,lc(red) lp(dash))
gr export "graphs/Figure7b.pdf",replace



**********************************************
**Figure 8a: Clan and Grain Production
**********************************************

use "mortality_sample.dta",clear

gen lggrain = log(grainoutput01)

*逐年生成13个1954-1966年的虚拟变量
forvalues i=1954(1)1966 {

g Y_`i' = (year==`i')
label var Y_`i' "`i'"
}

reg lggrain Y_1955-Y_1966 if highzupu50==0
est sto grain_trend1
reg lggrain Y_1955-Y_1966 if highzupu50==1
est sto grain_trend2

coefplot grain_trend1 grain_trend2, ytit("log(Grain Output)") xtit("Year") yline(0) noci vertical keep(Y_*) recast(connect) plotlabels("Low" "High")  offset(0)
gr export "graphs/Figure8a.pdf",replace


**********************************************
**Figure 8b: Clan and Grain Production
**********************************************

use "procurement_trends.dta",clear

*逐年生成11个1956-1966年的虚拟变量
forvalues i=1956(1)1966 {

g Y_`i' = (year==`i')
label var Y_`i' "`i'"
}
reg procurement Y_1956-Y_1966 if highzupu50==0,noc
est sto procure_t1
reg procurement Y_1956-Y_1966 if highzupu50==1,noc 
est sto procure_t2
coefplot procure_t1 procure_t2, ytit("Excess Procurement Ratio") xtit("Year") noci yline(0) level(90) vertical keep(Y_*) recast(connect) plotlabels("Low" "High")  offset(0)
gr export "graphs/Figure8b.pdf",replace


**============================================================================**
**                                 Tables                                     **
**============================================================================**

use "mortality_sample.dta",clear


gen famineyear = (year>=1958&year<=1961)

gen lnzupu50_fyr = lnzupunum50*famineyear
gen high50_fyr = highzupu50*famineyear
gen zupu50per_fyr = zupu50per*famineyear

gen nograin_fyr = nograinratio*famineyear
gen avggrain_fyr = avggrain*famineyear
gen urban_fyr= urbanratio57*famineyear
gen minor_fyr = minor*famineyear
gen edu_fyr = ysch*famineyear
gen dis_bj_fyr = distance_bj*famineyear
gen dis_pc_fyr = distance_pc*famineyear
gen migrants_fyr = migrants*famineyear
gen rice_fyr = ln_wetland_rice*famineyear

gen lggrain = log(grainoutput01)
gen lggrain_pc = log(grainoutput01/pop1957)

gen t = year-1954

label var lggrain "Lg(Total grain output)"
label var lggrain_pc "Lg(Grain output pc)"

label var avggrain_fyr "Per capita grainproduction x Famine period"
label var nograin_fyr "Non-agricultural land ratio x Famine period"
label var urban_fyr "Urbanization rate in 1957 x Famine period"
label var minor_fyr "Share of minority x Famine period"
label var edu_fyr "Averaged schooling x Famine period"

label var dis_bj_fyr "Distance from Beijing x Famine period"
label var dis_pc_fyr "Distance from provincial capital x Famine period"
label var migrants_fyr "Historical migrants x Famine period"
label var rice_fyr "Crop suitability index for rice x Famine period"

label var high50_fyr "High x Famine period"
label var zupu50per_fyr "Book intensity x Famine period"
label var lnzupu50_fyr "LgBook x Famine period"



g rsample = !mi(avggrain_fyr) & !mi(nograin_fyr) & !mi(urban_fyr)& !mi(dis_bj_fyr) & !mi(dis_pc_fyr) & !mi(migrants_fyr)& !mi(rice_fyr) & !mi(minor_fyr) & !mi(edu_fyr)

*设定控制变量暂元
global CONTROL = "avggrain_fyr nograin_fyr urban_fyr dis_bj_fyr dis_pc_fyr migrants_fyr rice_fyr minor_fyr edu_fyr"


***********************************************************
**Table 1: Clans and mortality rate during the great famine
***********************************************************

*清除可能存在的磁盘文件
cap erase "outfiles/Table1.xls"
cap erase "outfiles/Table1.txt"

*对变量high50_fyr、lnzupu50_fyr进行下列回归并导出结果至Table1.xls。
foreach x in "high50_fyr" "lnzupu50_fyr"  {

reghdfe drqianfen `x' if rsample,absorb(countyid year) cluster(countyid) summarize(mean sd)
outreg2 using "outfiles/Table1.xls", append  lab bdec(3) sdec(3) addtext(County FE,YES,Year FE,YES,County FE x Trend,NO)
reghdfe drqianfen `x' $CONTROL,absorb(year countyid) cluster(countyid) summarize(mean sd) 
outreg2 using "outfiles/Table1.xls", append  lab bdec(3) sdec(3) addtext(County FE,YES,Year FE,YES,County FE x Trend,NO)
reghdfe drqianfen `x' $CONTROL,absorb(year countyid countyid#c.t) cluster(countyid) summarize(mean sd) 
outreg2 using "outfiles/Table1.xls", append  lab bdec(3) sdec(3) addtext(County FE,YES,Year FE,YES,County FE x Trend,YES)

}

***********************************************************
**Table 3: Clans,grain output and grain procurement
***********************************************************

*清除可能存在的磁盘文件
cap erase "outfiles/Table3.xls"
cap erase "outfiles/Table3.txt"

*分别对以下的x/y进行回归（共计2*3=6个回归）并导出结果至Table3.xls。
foreach y in "lggrain" "lggrain_pc" "procurement" {
foreach x in "high50_fyr" "lnzupu50_fyr"  {
reghdfe `y' `x' $CONTROL,absorb(year countyid) cluster(provcd) summarize(mean sd) 
outreg2 using "outfiles/Table3.xls", append   lab bdec(3) sdec(3) keep(`x') addtext(County FE,YES,Year FE,YES,County FE x Trend,NO)
}
}



******************************************
**Table 2: Clans and hunger experience
******************************************

use "CFPS_hunger_sample.dta",clear

**born before 1962
gen old = (byear<=1961) 

**born before 1962 X Community Clan Intensity
gen treat_book1 = old*comzupu
gen treat_book2 = old*highczupu
gen treat_temple = old*comcitang

label var old "Pre-famine cohorts"
label var treat_book1 "Share of households having a genealogy x Pre-famine cohorts"
label var treat_book2 "High genealogy share (dummy) x Pre-famine cohorts"
label var treat_temple "Ancestral hall in the community x Pre-famine cohorts"


gen rsample = !mi(gender) & !mi(minor) & !mi(urbanhk) & !mi(educ) & !mi(sibnum)

*设定控制变量暂元
global CONTROLS = "gender minor urbanhk i.educ sibnum"


*清除可能存在的磁盘文件
cap erase "outfiles/Table2.xls"
cap erase "outfiles/Table2.txt"

*依次进行回归并将结果append至一张表格内。
reghdfe hunger treat_book1, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3) keep(treat_book1)

reghdfe hunger treat_book1 $CONTROLS, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3) keep(treat_book1) 

reghdfe hunger treat_book1 $CONTROLS if !urban, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3) keep(treat_book1) 

reghdfe hunger treat_book1 $CONTROLS if urban, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3) keep(treat_book1)

reghdfe hunger treat_book2, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3)  keep(treat_book2)

reghdfe hunger treat_book2 $CONTROLS, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3)  keep(treat_book2) 

reghdfe hunger treat_book2 $CONTROLS if !urban, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3)  keep(treat_book2)

reghdfe hunger treat_book2 $CONTROLS if urban, absorb(commid byear) cluster(commid)
outreg2 using "outfiles/Table2.xls",append lab bdec(3) sdec(3)  keep(treat_book2)


