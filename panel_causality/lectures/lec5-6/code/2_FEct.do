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

* 协助代码整理：刘安然 (liuanran123@ruc.edu.cn)             
               
*------------------------------------------------------------------------------*/


/* 固定效应 */



*** fect ***
*cap ado uninstall fect
*net install fect, from(https://raw.githubusercontent.com/xuyiqing/fect_stata/master/) replace

global path = "..."
cd $path



************************
* EDR and Turnout
************************

use "turnout", clear

***1. Fixed Effects(FE)***
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("fe") force("two-way") preperiod(-15) offperiod(5) se nboots(50) 

* 安慰剂检验 Placebo Test:
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("fe") force("two-way") placeboTest preperiod(-15) offperiod(5) se nboots(50)


***2. Interactive Fixed Effects(IFE)***
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("ife") force("two-way") r(2) preperiod(-15) offperiod(5) se nboots(50)

* 安慰剂检验 Placebo Test:
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("ife") force("two-way") r(2) placeboTest preperiod(-15) ///
	offperiod(5) se nboots(50)


***3. Matrix Completion(MC)***
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("mc") lambda(0.004) preperiod(-15) offperiod(5) se nboots(50)

* 安慰剂检验 Placebo Test:
fect turnout, treat(policy_edr) unit(abb) time(year) ///
	method("mc") lambda(0.004) placeboTest preperiod(-15) offperiod(5) se nboots(50)


************************
* FM2015
************************

use "fm2015", clear

***1. Fixed Effects(FE)***
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("fe") force("two-way") preperiod(-6) offperiod(4) se nboots(50) 

* 安慰剂检验 Placebo Test:
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("fe") force("two-way") placeboTest preperiod(-6) offperiod(4) se nboots(50)


***2. Interactive Fixed Effects(IFE)***
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("ife") force("two-way") r(2) preperiod(-6) offperiod(4) se nboots(50)

* 安慰剂检验 Placebo Test:
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("ife") force("two-way") r(2) placeboTest preperiod(-6) ///
	offperiod(4) se nboots(50)


***3. Matrix Completion(MC)***
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("mc") lambda(0.004) preperiod(-6) offperiod(4) se nboots(50)

* 安慰剂检验 Placebo Test:
fect logSgwaPercap, treat(treat) unit(councilnumber) time(year) ///
	method("mc") lambda(0.004) placeboTest preperiod(-6) offperiod(4) se nboots(50)


************************
* HH2015
************************

use "hh2015", clear

***1. Fixed Effects(FE)***
fect nat_rate_ord, treat(indirect) unit(bfs) time(year) ///
	method("fe") force("two-way") preperiod(-15) offperiod(5) se nboots(50) 

* 安慰剂检验 Placebo Test:
fect nat_rate_ord, treat(indirect) unit(bfs) time(year) ///
	method("fe") force("two-way") placeboTest preperiod(-15) offperiod(5) se nboots(50)

	
***2. Interactive Fixed Effects(IFE)*** 有点慢
fect nat_rate_ord, treat(indirect) unit(bfs) time(year) ///
	method("ife") cv force("two-way") preperiod(-15) offperiod(5) se nboots(50)






