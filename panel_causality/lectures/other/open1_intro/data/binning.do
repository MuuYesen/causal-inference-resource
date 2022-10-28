* not shown in paper 
set scheme sj 
clear 

sjlog using speak54a, replace
display int(3.4)
display int(-3.4)
mata : trunc((3.4, -3.4))
sjlog close, replace

sjlog using speak54b, replace
webuse grunfeld 
summarize year 
sjlog close, replace

sjlog using speak54c, replace
mata 
years = (1935..1944)
years
5 * floor(years/5)
end 
sjlog close, replace

sjlog using speak54d, replace
generate year5 = 5 * floor(year/5) 
egen mean_mvalue = mean(mvalue), by(year5) 
sjlog close, replace

sjlog using speak54e, replace
mata 
years = (1936..1945)
5 * ceil(years/5)
end 
sjlog close, replace

sjlog using speak54f, replace
mata 
years = (1937..1946)
1 :+ 5 * ceil((years :- 1)/5)
2 :+ 5 * floor((years :- 2)/5)
end 
sjlog close, replace

sjlog using speak54g, replace
mata 
years = (1935..1944)
round(years, 5)
round(years :+ 3, 5)
round(years :- 2, 5)
2 :+ round(years :- 2, 5)
end 
sjlog close, replace

sjlog using speak54h, replace
mata 
years \ round(years, 2)
end 
sjlog close, replace

sjlog using speak54i, replace
correlate mvalue invest
display r(rho)
sjlog close, replace

sjlog using speak54j, replace
display round(r(rho), 0.01)
display %23.18f round(r(rho), 0.01)
sjlog close, replace

sjlog using speak54k, replace
display %03.2f r(rho)
local wanted: display %03.2f r(rho)
display "`wanted'"
display `wanted'
sjlog close, replace

sjlog using speak54l, replace
display 0.86 
sjlog close, replace

sjlog using speak54m, replace
generate X = runiform() 
generate id = company 
sort X
generate bin5 = ceil(5 * _n/_N) 
sjlog close, replace

sjlog using speak54n, replace
drop bin5 
bysort id (X): generate bin5 = ceil(5 * _n/_N) 
sjlog close, replace

sjlog using speak54o, replace
sysuse auto, clear
xtile mpg5 = mpg, nquantiles(5)
_pctile mpg, nquantiles(5)
return li
tabstat mpg, by(mpg5) statistics(n min max)
sjlog close, replace

sjlog using speak54p, replace
quantile mpg, msymbol(none) mlabel(mpg5) mlabposition(0) rlopts(lcolor(none))
sjlog close, replace
graph export speak54a.eps, replace

sjlog using speak54q, replace
generate negmpg = -mpg
xtile mpg5rev = negmpg, nquantiles(5)
replace mpg5rev = 6 - mpg5rev
tabstat mpg, by(mpg5rev) statistics(n min max)
sjlog close, replace
