
*--------------------------
* profile.do 文档
*--------------------------



*-说明：
* 此文件设定了每次启动 stata 时需要做的一些基本设定
* 你可以在此文件中添加你希望在stata启动时立刻执行的命令

*-不要自动更新
set update_query  off  // on 
				
set type double           // 设定 generate 命令产生的新变量为双精度类型
set matsize 800          // 设定矩阵的维度为 2000x2000
set scrollbufsize 2000000 // 结果窗口中显示的行数上限
set more off, perma       // 关闭分页提示符

set cformat  %4.3f  //回归结果中系数的显示格式
set pformat  %4.3f  //回归结果中 p 值的显示格式      
set sformat  %4.2f  //回归结果中 se值的显示格式     

/*
set showbaselevels off, permanently
set showemptycells off, permanently
set showomitted off, permanently
*/
set fvlabel on, permanently



*-有关这一部分的完整设定命令，请输入 help set 命令进行查看

sysdir set PLUS "`c(sysdir_stata)'ado\plus"    // 外部命令的存放位置
sysdir set PERSONAL "`c(sysdir_stata)'ado\personal"  // 个人文件夹位置

/*
`c(sysdir_stata)'是一个暂元，里面存放了 Stata 的安装路径：输入sysdir后显示的第一个文件路径。例如，我的 stata17 存放于D盘根目录下，所以，`c(sysdir_stata)' = D:\stata17
*/


*采用相似的方式，可添加其它允许stata搜索的目录
*adopath + ""



* log文件：自动以当前日期为名存放于 stata15\do 文件夹下
* 若 stata1x\ 下没有 do 文件夹，则本程序会自动建立一个 
cap cd `c(sysdir_stata)'do
if _rc{
   mkdir `c(sysdir_stata)'do  //检测后发现无 do 文件夹，则自行建立一个
}

local fn = subinstr("`c(current_time)'",":","-",2)
local fn1 = subinstr("`c(current_date)'"," ","",3)
log    using `c(sysdir_stata)'do\log-`fn1'-`fn'.log, text replace
cmdlog using `c(sysdir_stata)'do\cmd-`fn1'-`fn'.log, replace


*-默认路径

  cd "`c(sysdir_personal)'"


*----- 以下摘自连享会提供的 profile.do 文档 ----

*-常逛网址
 
  dis in w _n "   "
  
  dis _n in w _col(10) _dup(45) "="
  dis    in w _col(10) _n _skip(20) "Hello World! Hello Stata!" _n
  dis    in w _col(10) _dup(45) "=" _n 
  
  dis in w  "Stata官网：" ///
      `"{browse "http://www.stata.com": [Stata.com] }"' ///
      `"{browse "http://www.stata.com/support/faqs/":   [Stata-FAQ] }"' ///
      `"{browse "https://blog.stata.com/":      [Stata-Blogs] }"' ///
      `"{browse "http://www.stata.com/links/resources.html":   [资源链接] }"' _n
	  
  dis in w  "Stata论坛：" ///
	  `"{browse "http://www.statalist.com": [Stata-list] }"'      ///
      `"{browse "https://stackoverflow.com":  [Stack-Overflow] }"'  //_n
  
  dis in w  "Stata资源：" /// 
      `"{browse "https://www.lianxh.cn": [连享会-主页] }"' ///
      `"{browse "https://www.zhihu.com/people/arlionn/":    [连享会-知乎] }"'  ///
	  `"{browse "https://gitee.com/arlionn/Course":    [连享会-码云] }"'
	  
	  
  dis in w  "Stata课程：" ///
      `"{browse "https://stats.idre.ucla.edu/stata/": [UCLA在线课程] }"' ///
      `"{browse "http://www.princeton.edu/~otorres/Stata/":        [Princeton在线课程] }"'  _n
	  

  dis in w  "学术论文：" ///
	  `"{browse "http://scholar.chongbuluo.com/":  [学术搜索] }"'  ///
	  `"{browse "http://scholar.cnki.net/":       [CNKI] }"' ///
	  `"{browse "http://xueshu.baidu.com/":       [百度学术] }"'  ///
	  `"{browse "http://www.jianshu.com/p/494e6feab565":         [Super Link] }"' _n  
  
  