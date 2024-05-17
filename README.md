# GitLog-To-Excel
基于AngularJS规范的GitLog提取脚本，能在客户端简单处理提交记录并输出为xlsx文件

没什么好介绍的

适合一些懒得构建CI/CD流程，但是又想使用Angular规范实现commit标准化，并按某次元的混沌考核标准生成数据表格的小项目

## Usage
将本文件放置在仓库目录下并执行
```
py git-parser.py --after YYYY-MM-DD --before YYYY-MM-DD
```
会在本脚本目录下生成git_log.xlsx