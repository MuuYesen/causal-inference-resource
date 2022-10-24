
*-绘制背景色带: 表示经济周期等

	clear
	set seed 13579
	set obs 100
	gen x = rnormal()
	twoway (function y=0.4, range(-2 -1.7) recast(area) color(green*0.3)) ///
		   (function y=0.4, range(-1 -0.9) recast(area) color(red*0.4)) ///
		   (function y=0.4, range( 1  1.5) recast(area) color(blue*0.2)) ///
		   (kdensity x, lw(*3) lc(black*0.5)), ///
		   legend(off)
		   
	*view browse "http://bbs.pinggu.org/thread-2343230-1-1.html"
