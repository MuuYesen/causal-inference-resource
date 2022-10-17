


*--------------------------------- Stata 花蝴蝶-------------------------------
*-蝴蝶身体部分
  clear
  local b0 = -400
  local b1 = 4
  local d  = 0.01
  local N = int((`b1'-`b0')/`d')
  set obs `N'
  gen t = -400 + _n*`d'
  gen a = cos(t)
  gen b = cos(4*t)
  gen x = sin(t)*(exp(a)-2*b-(sin(t/12)*sin(t/12)*sin(t/12)*sin(t/12)*sin(t/12)))
  gen y = cos(t)*(exp(a)-2*b-(sin(t/12)*sin(t/12)*sin(t/12)*sin(t/12)*sin(t/12)))
	   
*-胡须
  dropvars x2 y2 x3
  gen y2 =.
  gen x2 =.	
  local j = 1
  local end = (_pi/4+0.20)
  forvalues i = 0.20(0.01)`end'{
    qui replace x2 = `i' in `j++'
  }
  replace y2 = 3*sin(2*(x2-0.20))+2.5 
  gen x3 = -x2  //左半只

*-绘图
  twoway (line y x if y>0, lc(pink*0.55) lw(*2.5)) ///
         (line y x if y<0, lc(pink*0.70) lw(*2.5)) ///
	     (line y2 x2     , lc(yellow*1.2) lw(*3.5))   ///
	     (line y2 x3     , lc(yellow*1.2) lw(*3.5)),  ///
		 yscale(off) xscale(off) legend(off)
*-----------------------------------------------------------------------------	  
	  
	  
/*	  
*--------------------用 Stata 绘制花儿: 忽悠小朋友用------------------------------------
  clear
  local b0 = -400
  local b1 = 4
  local d  = 0.005  //0.01
  local N = int((`b1'-`b0')/`d')
  set obs `N'
  gen t = -400 + _n*`d'
  gen a = cos(t)
  
*-主要参数  
  local i = 30  // 4   花瓣的数量
  local j = 24  // 12  花瓣叠入程度
  local s = 20  // 2   内瓣和外瓣比例
  gen b = cos(`i'*t)
  gen x = sin(t)*(exp(a)-`s'*b-(sin(t/`j')*sin(t/`j')*sin(t/`j')*sin(t/`j')*sin(t/`j')))
  gen y = cos(t)*(exp(a)-`s'*b-(sin(t/`j')*sin(t/`j')*sin(t/`j')*sin(t/`j')*sin(t/`j')))
	   
*-绘图
  set scheme s2color
  local c "pink"
  local c "red*0.3"
  local z "0.8"     //线宽
  twoway (line y x if y>0, lc(`c') lw(*`z')) ///
         (line y x if y<0, lc(`c') lw(*`z')) ///
	     , yscale(off) xscale(off) legend(off)   	  
*------------------------------------------------------------------------------------------	
*/
