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
							 
* 参考文献：Bleakley, H. (2006). 
  Malaria in the Americas: A retrospective analysis of childhood exposure.
  
* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)                            
------------------------------------------------------------------------------*/

*！请修改工作路径
cd "..."

graph drop _all

******************************
* 回归分析：2*2倍差法
******************************

use malaria, clear

*根据出生年份定义不同组别：“老年人”old，“年轻人”young
**赋值法则：满足条件（如yob>=1920）则赋值为1，否则为0
gen young = yob>=1920
gen old   = yob<=1899

*生成firstobs变量：将每个出生地区的第一个样本赋值为1（以便之后通过该变量标记来查看各地区指标）
bys bplg: gen firstobs = _n==1

*查看1890年各地区疟疾死亡率数据的百分比分布
sum  malmort1890 if firstobs==1, detail

*将"高"疟疾地区定义为"malmort1890"中的第90百分位数或更高的地区
gen high =  malmort1890 >= r(p90)
*将"低"疟疾地区定义为"malmort1890"第10百分位数或更低的地区
gen low  =  malmort1890 <= r(p10)

save malaria1, replace

//数据设定

use malaria1, clear
*如果变量low或者high值为1，则保留该条数据信息（即保留上文中定义的高疟疾地区或低疟疾地区的数据）
keep if inlist(1, low, high)
*如果变量old或者young值为1，则保留该条数据信息(即保留上文中定义的年轻人信息和老年人的数据)
keep if inlist(1, old, young) 

*展示根据出生年份（yob）、是否为高疟疾地区（high)和是否为老年人（old)分组、并通过cellsize加权（weight）后的sei均值；
/*[注] SEI：使用OCC1950变量中提供的1950年职业分类计划，为每个职业分配一个邓肯社会经济指数（SEI）得分。
SEI是一个基于1950年与每个职业相关的收入水平和教育程度的职业状况的测量。
*/
collapse (mean) sei [aw = cellsize], by(yob high old)

*将长数据转换为宽数据：本例中，生成新变量来储存不同high值对应的sei值[即将纵向展示的high（取值为0/1)对应sei值变为横向展示]--sei0/sei1
reshape wide sei, i(yob old) j(high)

*生成差分变量
gen sei_diff = sei1 - sei0

*根据old变量分组绘制散点图并附加回归线（regression line)
sc sei_diff yob if old==1 || lfit sei_diff yob if old==1 || ///
sc sei_diff yob if old==0 || lfit sei_diff yob if old==0


// *分组加权回归
use malaria1, clear

reg sei high [aw = cellsize] if old
reg sei high [aw = cellsize] if young

reg occscore high [aw = cellsize] if old
reg occscore high [aw = cellsize] if young


// *更细的组别

use malaria1, clear

*生成新组别变量vold：如果yob不为缺失值且yob<=1860，则vold等于1；如果yob不为缺失值且yob>1860，则vold等于0
gen vold = yob<=1860 if !mi(yob)
gen vyoung = yob>=1940 if !mi(yob)

*更新原有年轻人、老年人的划定年份
replace old=0 if vold==1
replace young=0 if vyoung==1
label var vold "Very old"
label var vyoung "Very young"


*分组加权回归
**例：回归1回归样本要求vold==1，且 high或者low==1
reg sei high [aw = cellsize] if inlist(1, vold) & inlist(1, high, low)
reg sei high [aw = cellsize] if inlist(1, old) & inlist(1, high, low)
reg sei high [aw = cellsize] if inlist(1, vyoung) & inlist(1, high, low)
reg sei high [aw = cellsize] if inlist(1, young) & inlist(1, high, low)

reg occscore high [aw = cellsize] if inlist(1, vold) & inlist(1, high, low)
reg occscore high [aw = cellsize] if inlist(1, old) & inlist(1, high, low)
reg occscore high [aw = cellsize] if inlist(1, vyoung) & inlist(1, high, low)
reg occscore high [aw = cellsize] if inlist(1, young) & inlist(1, high, low)

*保留高疟疾或低疟疾地区的样本
keep if inlist(1, low, high)

*删去yob取值为缺失值，或者yob取值在[1900,1920)的样本
drop if yob==. | (yob>=1900 & yob<1920)

gen cohort=0
*如果young==1，则将cohort的值替换为1
replace cohort=1 if young
replace cohort=2 if old
replace cohort=3 if vold

*展示根据出生年份（yob）、是否为高疟疾地区（high)和cohort分组、并通过cellsize加权（weight）后的sei均值；
collapse (mean) sei [aw = cellsize], by(yob high cohort)

*将长数据转换为宽数据：
reshape wide sei, i(yob cohort) j(high)

*生成差分变量
gen sei_diff = sei1 - sei0

*根据cohort绘制散点图并附加回归线（regression line)
sc sei_diff yob if cohort==0 || lfit sei_diff yob if cohort==0 || ///
sc sei_diff yob if cohort==1 || lfit sei_diff yob if cohort==1 || ///
sc sei_diff yob if cohort==2 || lfit sei_diff yob if cohort==2 || ///
sc sei_diff yob if cohort==3 || lfit sei_diff yob if cohort==3 


*******************************
* 利用疟疾严重度信息(intensity)
*******************************

use malaria1, clear

*保留old==1或young==1的样本
keep if inlist(1, old, young)

*展示根据出生地区（bplg)和是否为老年人（old)分组，并通过cellsize加权（weight）后的变量sei occscore malmort1890 south lebergott99均值；
collapse (mean) sei occscore malmort1890 south lebergott99 [aw = cellsize], by(bplg old)

*将长数据转换为宽数据
reshape wide sei occscore, i(bplg) j(old)

*生成差分变量
gen sei_youngold=sei0-sei1
gen occ_youngold=occscore0-occscore1

*OLS回归
reg  sei_youngold malmort1890 south lebergott99 , r
reg  occ_youngold malmort1890 south lebergott99 , r

******************************
* 图示
******************************


*重新打开malaria.dta数据库
use malaria, clear

*根据年份变量的每一个取值生成一组0-1变量（qui表示不展示运行过程）
qui tab year, gen(yr__)

gen coeff_occscore = .
gen coeff_sei = .
gen se_occscore = .
gen se_sei = .
gen rmse_occscore=.  //rss
gen rmse_sei=. 

*嵌套循环
/*
第一层：对occscore、sei两个变量均重复以下操作
第二层：根据yob取值，对1825-1955每个年份进行分组回归，并储存下每个回归的malmort系数、标准误和均方根偏差。
*/
qui foreach v in occscore sei {
	forval i = 1825/1955{
		reg `v' malmort lebergott99 south hookworm yr__* [aw = cellsize] if yob==`i'
		replace coeff_`v' = _b[malmort] if yob==`i'
		replace se_`v' = _se[malmort] if yob==`i'
		replace rmse_`v'=e(rmse) if yob==`i'
	}
}

*呈现coeff* se* rmse*等变量根据yob分组的均值
collapse coeff* se* rmse*, by(yob)

*如果yob满足1825≤yob≤1899则pre取值为1,否则pre取值为0。mid、post生成过程类似。
gen pre = inrange(yob, 1825, 1899)
gen mid = inrange(yob, 1899, 1919)
gen post = inrange(yob, 1920, 1960)

*嵌套循环
/*
第一层：对occscore、sei两个变量均重复操作
第二层：对pre 、post两个变量均重复操作
	根据pre 、post分组得到occscore、sei系数的均值，并存为变量avg_occscore和avg_sei。
*/
foreach v in occscore sei {
gen avg_`v' = .
	foreach w in pre post{
		summ coeff_`v' if `w'==1
		replace avg_`v' = r(mean) if `w'==1
	}
}

*循环生成置信区间上下界
foreach v in occscore sei {
  gen upper_`v'=coeff_`v' + 1.96*se_`v'
  gen lower_`v'=coeff_`v' - 1.96*se_`v'
}

*绘制散点图与折线图
sc coeff_occscore yob || line avg_occscore yob || ///
    line upper_occscore yob || line lower_occscore yob, ///
	name(a) xlab(1820(20)1960) legend(off) lp(dash) ///
	title("Occupational Income Score") 
	
*调取图象
graph display a

sc coeff_sei yob || line avg_sei yob, ///
	name(b) xlab(1820(20)1960) legend(off) lp(dash) ///
	title("Duncan Socio-Economic Indicator") 
	
graph display b
	
*绘制散点图
twoway (sc se_occscore yob) ///
       (sc rmse_occscore yob, yaxis(2)), ///
   name(se) xlab(1820(20)1960) title("S.E. of bata and RMSE") ///
   ytitle(se_occscore) ytitle(rmse_occscore, axis(2))
	
graph display se
   

* 对应的回归
*生成变量exp：首先比较出18和yob -(1920-18)中的最小值，然后选出这一最小值和0之间的最大值，即为exp的取值
gen exp = max(min(18, yob -(1920-18)), 0)  //max is 18, start from 1902

*循环：yob依次乘2/3/4/5
forval i = 2/5{
	gen yob`i' = yob^`i' 
}

*回归
reg coeff_occscore exp [aw = 1/se_occscore] 
reg coeff_occscore exp yob [aw = 1/se_occscore]
reg coeff_occscore exp yob yob2 [aw = 1/se_occscore]
reg coeff_occscore exp yob yob2 yob3 [aw = 1/se_occscore]
