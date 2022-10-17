*  
*  ███████╗████████╗ █████╗ ████████╗ █████╗ 
*  ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
*  ███████╗   ██║   ███████║   ██║   ███████║
*  ╚════██║   ██║   ██╔══██║   ██║   ██╔══██║
*  ███████║   ██║   ██║  ██║   ██║   ██║  ██║
*  ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
*
/*-----------------------------------------------------------------------------*\
*                      面板数据因果推断：从入门到精通 Lecture 2               
*                              徐轶青  2022.10  
*/

/* 双重差分法 */

/*
Reference
Card, David, and Alan B. Krueger. 1994. "Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania." American Economic Review, 84 (4): 772-92.
*/


global path = "..."
cd $path



* sheet: unique id for each unit
* after: post treatment
* nj: 1 if NJ; 0 if Pa
* njafter: 1 if NJ and post treatment; 0 otherwise
* fte: full-time-equivalent employment
* dfte: difference in fte for each unit before and after treatment

*panelview install: 
/*
net install grc1leg, from(http://www.stata.com/users/vwiggins) replace
net install gr0075, from(http://www.stata-journal.com/software/sj18-4) replace
ssc install labutil, replace
ssc install sencode, replace

cap ado uninstall panelview //in-case already installed
net install panelview, all replace from("https://yiqingxu.org/packages/panelView_stata")

ssc install xtdidregress
*/

use "cardkreuger", clear
tab after
tab nj
tab after nj

panelview fte njafter, i(sheet) t(after) type(treat) ylabdist(20)  ///
  bytiming xtitle("Period") ytitle("Restaurant")

* 1. Use mean differences to compute the difference in means estimate of the change in minimum wage
*ssc install diff
diff fte, t(nj) p(after) robust

* 2. Estimate the difference-in-differences using a regression model
reghdfe fte njafter, absorb(sheet after) vce(cluster sheet) 

* 3. Visualization of the result
egen mean_y=mean(fte), by(after nj)

graph twoway (connect mean_y after if nj==1,sort msize(small)) ///
(connect mean_y after if nj==0,sort lpattern(dash) msize(small)), ///
ytitle("fte") xtitle("Treatment") ///
ylabel(,angle(0) labsize(*0.75)) xlabel(minmax,labsize(*0.75)) ///
legend(label(1 "处理组") label( 2 "控制组")) ///图例
graphregion(color(white)) //白底
