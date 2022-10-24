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
* 
* Dofile编写：刘安然 
* 参考：1. 连享会公众号推文
	   2. 黄炜,张子尧,刘安然.从双重差分法到事件研究法[J].产业经济评论,2022(02):17-36.
	   3. Stata.com
                           
*-----------------------------------------------------------------------------*/
clear all
*请修改为个人电脑上的工作路径
cd "..."

set seed 1010



**********************************大样本****************************************

*一共50个村庄（vid)，每个村庄10个个体，每个个体经历20个时期，共50*10*20=10000条数据

*-----------------------------单个结果呈现--------------------------------------

**#DGP
    clear all     
    set obs 50
    gen vid = _n
    expand 10
	sort vid
	gen id =_n
    expand 20
    bysort id: gen time = _n  
	
    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前100人，处理期为第11期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=2
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 
	
**#回归

    *回归1：常规标准误
    reghdfe y D x, a(id time) 
    gen D_ordinary = _b[D]
    gen D_ordinary_se = _se[D]

	*回归2：聚类标准误
    reghdfe y D x, a(id time) vce (cluster vid)
    gen D_cluster = _b[D]
    gen D_cluster_se = _se[D]

	*回归3：自助（bootstrap）标准误	
    bootstrap, reps(20) seed(1):reghdfe y D x, a(id time) 
    gen D_bootstrap = _b[D]
    gen D_bootstrap_se = _se[D]

	keep D_ordinary D_cluster D_bootstrap D_ordinary_se D_cluster_se D_bootstrap_se
	keep if _n==1
	
save simulation_big_1.dta, replace 
	
	
	
*---------------------200次模拟
clear all
preserve
  save big_file, replace emptyok
restore

forvalues i = 1(1)200{  
    qui:{    
    clear all     
    set obs 50
    gen vid = _n
    expand 10
	sort vid
	gen id =_n
    expand 20
    bysort id: gen time = _n  
	
    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前100人，处理期为第11期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=2
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 

    *回归1：常规标准误
    reghdfe y D x, a(id time) 
    gen D_ordinary = _b[D]
    gen D_ordinary_se = _se[D]

	*回归2：聚类标准误
    reghdfe y D x, a(id time) vce (cluster vid)
    gen D_cluster = _b[D]
    gen D_cluster_se = _se[D]

    keep D_ordinary D_cluster D_ordinary_se D_cluster_se 
    keep if _n==1


    append using big_file
    save big_file, replace
    }
    if mod(`i',10)==0{
          disp "Iteration " `i' " is done."
        }
}

*回归3：自助（bootstrap）标准误	
capture program drop myprog1
program define myprog1
	* drop all variables to create an empty dataset, do not use clear
	drop _all
	set obs 50
    gen vid = _n
    expand 10
	sort vid
	gen id =_n
    expand 20
    bysort id: gen time = _n  

    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前30人，处理期为第2期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=11
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 

    * 基准回归
    reghdfe y D x, a(id time) 

end

simulate _b[D] _se[D], reps(200): myprog1

save big_file_bootstrap,replace

*合并三种回归结果    
use big_file, clear
merge 1:1 _n using big_file_bootstrap
drop _merge
ren _sim_1 D_bootstrap
ren _sim_2 D_bootstrap_se
save simulation_big_200.dta, replace 


**********************************小样本****************************************

*一共30个村庄（vid)，每个村庄2个个体(id)，每个个体经历4个时期(time)，共30*2*4=240条数据

*-----------------------------单个结果呈现--------------------------------------

**#DGP
	clear all     
    set obs 30
    gen vid = _n
    expand 2
	sort vid
	gen id =_n
    expand 4
    bysort id: gen time = _n  
	
    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前30人，处理期为第2期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=2
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 
	
**#回归

    *回归1：常规标准误
    reghdfe y D x, a(id time) 
    gen D_ordinary = _b[D]
    gen D_ordinary_se = _se[D]

	*回归2：聚类标准误
    reghdfe y D x, a(id time) vce (cluster vid)
    gen D_cluster = _b[D]
    gen D_cluster_se = _se[D]

	*回归3：自助（bootstrap）标准误	
    bootstrap, reps(20) seed(1):reghdfe y D x, a(id time) 
    gen D_bootstrap = _b[D]
    gen D_bootstrap_se = _se[D]

	keep D_ordinary D_cluster D_bootstrap D_ordinary_se D_cluster_se D_bootstrap_se
	keep if _n==1
	
save simulation_small_1.dta, replace 
	
	
	
*---------------------200次模拟
clear all
preserve
  save small_file, replace emptyok
restore

forvalues i = 1(1)200{  
    qui:{    
    clear all     
    set obs 30
    gen vid = _n
    expand 2
	sort vid
	gen id =_n
    expand 4
    bysort id: gen time = _n  
    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前30人，处理期为第2期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=2
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 

    *回归1：常规标准误
    reghdfe y D x, a(id time) 
    gen D_ordinary = _b[D]
    gen D_ordinary_se = _se[D]

	*回归2：聚类标准误
    reghdfe y D x, a(id time) vce (cluster vid)
    gen D_cluster = _b[D]
    gen D_cluster_se = _se[D]

    keep D_ordinary D_cluster D_ordinary_se D_cluster_se 
    keep if _n==1


    append using small_file
    save small_file, replace
    }
    if mod(`i',10)==0{
          disp "Iteration " `i' " is done."
        }
}

*回归3：自助（bootstrap）标准误	
capture program drop myprog1
program define myprog1
	* drop all variables to create an empty dataset, do not use clear
	drop _all
    set obs 30
    gen vid = _n
    expand 2
	sort vid
	gen id =_n
    expand 4
    bysort id: gen time = _n   

    * 生成个体固定效应
    gen  unit_c     = runiform() if time==1
    egen unit_spec  = mean(unit_c), by(id)
    egen unit_spec_v= mean(unit_c), by(vid)

    * 协变量x根据固定效应生成，与固定效应相关
    gen x = rnormal(unit_spec) 

    * 定义处理组为前30人，处理期为第2期
    gen     treat = 0
    gen     indicator_c = unit_c + x
    qui sum indicator_c,d
    scalar  threshold   = r(p50)
    egen    indicator   = mean(indicator_c), by(id)
    replace treat = 1 if indicator>threshold
    gen     post  = 0
    replace post  = 1 if time>=2
    gen     D     = treat*post

    * 定义潜在结果y0和y1
    gen y0 = 0 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 
    gen y1 = 1 + unit_spec + 1*x + 0.06*time  + runiform(0,1) + rnormal() 

    * 生成观测样本y 
    cap drop y
    gen y = (1-D)*y0 + D*y1 

    * 基准回归
    reghdfe y D x, a(id time) 

end

simulate _b[D] _se[D], reps(200): myprog1

save small_file_bootstrap,replace

use small_file, clear 
merge 1:1 _n using small_file_bootstrap
drop _merge
ren _sim_1 D_bootstrap
ren _sim_2 D_bootstrap_se
save simulation_small_200.dta, replace 
