

*			  ==========================================
*						     Stata公开课 
*  
*                           软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			       ============================
*					 	 第一讲 Stata简介   
*                  ============================

**-注意：执行后续命令之前，请先执行如下几条命令

  global D "`c(sysdir_stata)'ado\personal\open1_intro\data"  //定义课程资料 
  cd "$D"     
  set scheme s2color  //设定图形格式为默认格式
  
  *-note: 
  /*	`c(sysdir_stata)'是一个暂元，里面存放了Stata的安装路径：
	输入 sysdir 后显示的第一个文件路径。
	例如, 我的 stata17存放于D盘study文件下, 
	所以, `c(sysdir_stata)' = D:\study\Stata17\     	*/
  
*----------------
*   本讲目录  
*----------------
* 1.1 Stata简介
* 1.2 Stata窗口和快捷键介绍
* 1.3 Stata安装路径和文件路径设置
* 1.4 Stata数据文件、命令文件、程序文件介绍
* 1.5 Stata语法命令格式
* 1.6 Stata帮助文件和外部命令














*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			       ============================
*					 	 第一讲 Stata简介   
*                  ============================
*                         -1.1- Stata 速览

* What？

* Why？
  *-短小精悍
  *-运算速度快
  *-操作简单、功能强大
	 cd "$D"
     do "L1_butterfly.do"       //函数图: 一只蝴蝶
  *-更新和发展速度快
     ssc new  //列出近一个月最新的stata命令
	 
* When？
	/* 实证分析的流程
  [1] 一个想法：研究假设
  [2] 模型设定
  [3] 变量界定
  [4] 收集数据
  [5] 数据清洗与变量生成
  [6] 统计和回归分析
  [7] 支持-->[8]  |  不支持-->[1]-[7]
  [8] 解释结果和得出结论
  在上述过程中，Stata的角色和作用是什么？[5]-[6]   */

* How?










*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			        ============================
*					 	 第一讲 Stata简介   
*                   ============================
*                    -1.2- Stata窗口和快捷键介绍

*-1.2.1-  Stata窗口介绍

  *-历史窗口：记录着本次Stata启动以来执行过的命令
  *-结果窗口：执行Stata命令之后的输出结果
  *-命令窗口：输入想要执行的Stata命令
  *-变量窗口：当前Stata内存中的所有变量
  *-性质窗口：当前数据文件与变量的性质
  
  *-菜单栏
  *-快捷键栏

*-1.2.2-  Stata常用的快捷键

/*
  *- F-key 	Definition
	---------------------------
	  F1 		打开帮助系统的首页，查看关于帮助的帮助文件
	  F2 		describe
	  F3 		打开结果窗口的搜索功能，Esc键退出
	  F7 		save
	  F8 		use
	---------------------------

	*- 主窗口其他快捷键	Definition
	---------------------------  
	  Ctrl+3	聚焦到历史窗口
	  Ctrl+4	聚焦到变量窗口
	  Ctrl+5	聚焦到属性窗口
	  Ctrl+8	打开数据编辑窗口
	  Ctrl+9	新建一个do文件
	---------------------------	  
	  	
	*- Do编辑器快捷键	Definition
	----------------------------------------------
	  Ctrl+D	执行(Do)选中的命令 (*) 
	  Ctrl+R	运行程序(Run)      (*)    无输出执行
	  Ctrl+F	在do-editor中搜索特定的关键词
	  Ctrl+O	打开do文档
	  Ctrl+N	新建do文档
	  Ctrl+S	保存do文档         (*)
	  Ctrl+L	选中一行
	  Ctrl+Shift+/	给选中的do命令添加块注释（/* */）
	---------------------------
                                        */		










*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			        ============================
*					 	 第一讲 Stata简介   
*                   ============================
*                    -1.3- Stata安装路径和文件路径设置

*-1.3.1-  Stata安装路径

  sysdir   //系统文件路径
  
  sysdir set BASE "D:\Stata16\ado\base\"

  sysdir set BASE "F:\Stata17\ado\base\"


  *-Stata安装路径的注意事项：① 安装路径中不可存在中文字符
  *-						 ② 安装路径中不可存在空格

*-1.3.2-  Stata文件路径
  
*   当前工作路径	
	pwd              //显示当前工作路径
	cd               //显示当前工作路径 (等价于 pwd)
	cd "D:\Stata16"  //改变(设置)当前工作路径
     * 建议在路径名称外加双引号,醒目
     * 通常是从电脑的 [地址栏] 中复制粘贴过来的 
	cd "$D"
	dir       //列示当前路径下的文件
	cdout	  //打开当前工作路径对应的文件夹

*	程序文件路径
	adopath   //Stata只能识别存放于这些文件夹下的程序文件
	adopath + "D:\stata16"  //新增一条程序文件路径
	adopath - "D:\stata16"  //去掉一条程序文件路径
	








*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			        ============================
*					 	 第一讲 Stata简介   
*                   ============================
*                        -1.4- Stata文件

*-1.4.1-  Stata数据文件  

*   Stata 默认的数据文件是后缀名为“.dta”的文件
  
*   Stata 数据文件的读取和保存

*-1.4.2-  Stata命令文件
  
*	Stata 默认的命令文件是后缀名为“.do”的文件 （命令的集合）

*   1.4.2.1 命令文件的打开与保存
  
*	新建do文档
      doedit
*	  Ctrl+9
*	  快捷键栏-->新Do-file编辑器

*	打开do文档
	  doedit "L1_color_brand.do"
*	  Ctrl+O 
* 	  快捷键栏-->打开
 
*	保存do文档
*	  Ctrl+S  
*	  快捷键栏-->保存

*	1.4.2.2 命令文件的注释
  
*	单行注释
	sysuse  auto,clear     //行尾注释
    /* 多行注释  */ 
	

*	1.4.2.3 命令文件中的断行

	tw(scatter mpg weight if foreign==0)(scatter mpg weight if foreign==1),title(行驶历程与车重关系)ytitle(里程)legend(label(1 国产车)label(2 进口车))    //示例
	
*	用 /* */ 实现断行
	tw(scatter mpg weight if foreign==0) /*
	*/(scatter mpg weight if foreign==1), /*
	*/title(行驶历程与车重关系)ytitle(里程) /*
	*/legend(label(1 国产车)label(2 进口车))
  
*	用 #delimit ; 和 #delimit cr 定义换行符
	#delimit ;
	tw(scatter mpg weight if foreign==0)
	(scatter mpg weight if foreign==1),
	title(行驶历程与车重关系)ytitle(里程)
	legend(label(1 国产车)label(2 进口车));
	#delimit cr
 
*	用///实现断行
	tw(scatter mpg weight if foreign==0)   ///
	(scatter mpg weight if foreign==1),   ///
	title(行驶历程与车重关系)ytitle(里程) ///
	legend(label(1 国产车)label(2 进口车))

*	1.4.2.4 Profile.do (Stata启动设定)

*	设定文件路径
*	开机自动生成log日志
	doedit profile.do
		 
*-1.4.3-  Stata 程序文件
  
	*-Stata 默认的程序文件是后缀名为“.ado”的文件
	adopath 

*-1.4.4-  Stata日志文件 
 

  
  





*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			        ============================
*					 	 第一讲 Stata简介   
*                   ============================
*                      -1.5- Stata语法命令格式

*-1.5.1-  Stata的一般语法格式

  help language

  *----------------------------------------------------------------------
  * [prefix:] cmd [varlist] [=exp] [if] [in] [using filename] [, options]
  *----------------------------------------------------------------------
  
  *-Note: 逗号后为 options, 整条命令只能有一个裸露在外的逗号
  
  *-e.g. 1
	sysuse nlsw88, clear
	gen lnwage = ln(wage)
	gen yes_white = (race==1)  // [=exp]
	tabstat lnwage hours married age, by(yes_white) s(mean) f(%3.2f) 
  
  *-e.g. 2
    twoway scatter wage hours, title("工资和工作时长", place(left))  

*-1.5.2-  Stata语法中的符号
	sysuse nlsw88, clear
	sum wage
	sum wage if race==1  // if 限定样本
	sum wage in 1/10     // in 指定观察值
	sum age race married never_married grade
    sum age-grade    // 顺序出现的变量，列出头尾两个变量即可
    sum s*           // "*" 通配符，可以表示`任何'长度的字母或数字
	sum *arr*        // 可以用在任何位置
    sum ?a?e         // "?" 只能替代`一个'长度的字母或数字 
	
*-1.5.3-  因子变量: 变量的前缀
	sysuse nlsw88, clear
	tab race                                 // 类别变量
	reg wage tenure hours i.race i.industry  // 种族和行业虚拟变量
	reg wage tenure hours age c.age#c.age    // 平方项        #
	reg wage tenure hours i.marr i.marr#c.hours // 交乘项
	reg wage tenure i.marr##c.hours       // 等价命令,简写 ##
	

	















*			  ==========================================
*						Stata公开课 软件及计量基础   
*             ==========================================

*                    	 主讲人：候丹丹
*                   	 主办方：连享会（www.lianxh.cn）
*           课程主页：https://gitee.com/lianxh/stataopen
*                     :: 课件下载，答疑等 ::

*			        ============================
*					 	 第一讲 Stata简介   
*                   ============================
*                  -1.6- Stata帮助文件和外部命令

*-1.6.1-  Stata帮助文件

	help        //帮助文件使用建议
  
  *-e.g. 
  
    help tabstat  //注意右上角的三个按钮，对于初学者很实用

*-1.6.2-  Stata外部命令

*	ssc
	ssc install winsor2 , replace  //安装
	ssc uninstall winsor2  	  //移除
	ssc describe winsor2      //描述
	ssc new   			//显示最近更新的命令
	ssc hot, n(10)  	//显示排名前10的命令
	
	
*	search              不仅可以搜索外部命令，也能搜索相关文档资料
	search reg
	search reg, all		//搜索所有资料
	search reg, net		//搜索互联网上用户编写的补充内容
	search reg, sj		//搜索 Stata Journal 和 Stata Technical Bulletin 上的资源
	search reg, faq		//搜索Stata 官网FAQS 条目下的资源
	search reg, manual	//搜索 Stata 电子手册文档上的资源
	
	
*	findit		可以搜索系统文件, FAQs, Stata Journal, 互联网资源等
	findit reg  //等价于 search reg, all

	
*	net
	net search reg          //等价于 search reg, net	
	net install github, from("https://haghish.github.io/github/")   //从特定的网站安装外部命令
	net sj 18-3  		//安装Stata Journal 18卷第3期涉及的所有文件
		



  
  
  
  
  
  
  
  
  
  
  
  
  

