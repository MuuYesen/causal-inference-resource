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
  Xu, Y., & Yao, Y. (2015). Informal institutions, collective action, and public 
  investment in rural China. American Political Science Review, 109(2), 371-391.
  
* 展示顺序：Table 1 2; Figure 3; Table 3; Table 6 7

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)                            
------------------------------------------------------------------------------*/

*！请将Stata的工作路径设置为保存论文复现材料的路径
cd ".../data"

clear all
set more off

********************************
* Table 1: descriptive stat
********************************

use xy2015, clear
tab year
unique year
unique vill_id

*列出inv等变量的样本数、均值、标准差、最小值和最大值。
tabstat inv loginv log_levies ///
     logpopl logincome logasset hhsize landpc logmigration logtax logtransfer share_admin  ///
	 postcont postopen secret_ballot proxy_voting moving_ballot ///
	 , s(N mean sd min max) c(s)

	 
use xy2015, clear
keep if elecyr==1

*列出vcfirst等变量的样本数、均值、标准差、最小值和最大值。	 
tabstat vcfirst vcsecond vcfirst2 vc_char_* vote ///
        psfirst2 vcps_clan vcps_person vc_pb ///
		, s(N mean sd min max) c(s)
        
		
use xy2015, clear
keep if year==2005

*列出clan_num等变量的样本数、均值、标准差、最小值和最大值。	 
tabstat clan_num clansz* largeclan family_tree ances_hall, s(N mean sd min max) c(s)
     
	 
********************************
* Table 2: baseline resutls
********************************

use xy2015, clear

**逐步添加变量，累次回归

*年固定效应；以下两回归等价
areg loginv vcfirst vcsecond, a(year) cl(vill_id)

reghdfe loginv vcfirst vcsecond, a(year) cl(vill_id)

*双重固定效应：以下两回归等价，标准误略不同
areg loginv vcfirst vcsecond i.year, a(vill_id) cl(vill_id)

reghdfe loginv vcfirst vcsecond, a(vill_id year) cl(vill_id)

*自助法获得标准误
bootstrap _b, rep(200) cl(vill_id): reghdfe loginv vcfirst vcsecond, a(vill_id year)

*加省趋势
reghdfe loginv vcfirst vcsecond i.year i.prov_id#c.year, a(vill_id) cl(vill_id)

*加村趋势
reghdfe loginv vcfirst vcsecond i.year c.year#i.vill_id, a(vill_id) cl(vill_id)

*加控制变量组1
reghdfe loginv vcfirst vcsecond hhsize landpc logpopl logincome logasset, ///
    a(vill_id year i.prov_id#c.year) cl(vill_id)

*加控制变量组2
reghdfe loginv vcfirst vcsecond hhsize landpc logpopl logincome logasset ///
	logmigration logtax logtransfer, a(vill_id year i.prov_id#c.year) cl(vill_id)



***********************************
* Figure 3: dynamic effect
***********************************

use xy2015, clear

*回归
reghdfe loginv vc_in_office*, a(vill_id year) cl(vill_id)

*绘制图象
gen coef = . 
gen se = . 

*逐个存储vc_in_office*的系数
local j = 2 
foreach var of var vc_in_office* {
replace coef = _b[`var'] in `j'
replace se = _se[`var'] in `j'

local ++j
}

*生成置信区间上下界
gen up_ci = coef + 1.96* se
gen low_ci = coef - 1.96*se

keep coef* se* up_* low_*

gen Year = _n-7


*保留前13行数据
keep in 1/13

*绘制图象
tw  (scatter coef Year, yline(0) msymbol(o) msize(medium) mcolor(gs2) mfcolor(white) lwidth(medthin) lcolor(navy) mlalign(center)) ///
   (rcap up_ci low_ci Year, lp(dash)  legend(ring(0) pos(11) label(1 "Coef.")  label(2 "95% CI") col(2) size(small))) , ///
   yline(0, lwidth(vthin) lpattern(dash)) ///
   xlabel(-5 -4 -3 -2 -1  0 1 2 3 4 5">4", labsize(small))
   
*导出图象，另存为pdf格式
gr export "Figure3.pdf",replace

   
********************************
* Table 3: 按投资类别
********************************

use xy2015, clear

*对带有loginv_cat_前缀的一系列变量执行如下回归
foreach var in loginv_cat_* {
  reghdfe `var' vcfirst2, a(vill_id year) cl(vill_id)
}   




********************************
* Table 6: VC characteristics
********************************

use xy2015, clear

reghdfe loginv vcfirst2 vc_char_educ, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 vc_char_educ vc_char_age vc_char_ccp vc_char_cadre vc_char_manager vc_char_exper, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 vc_char_*, a(vill_id year) cl(vill_id)


***********************************
* Table 7: electoral institutions
***********************************
 
use xy2015, clear

reghdfe loginv vcfirst2 postcont, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 postopen, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 secret_ballot, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 proxy_voting, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 moving_ballot, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 if postcont==1, a(vill_id year) cl(vill_id)

reghdfe loginv vcfirst2 if postopen==1, a(vill_id year) cl(vill_id)


