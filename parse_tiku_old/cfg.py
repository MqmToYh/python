#!/usr/bin/env python
#-*-coding:utf-8-*-

#数据库配置
db={
    "host":"127.0.0.1",
    "user":"root",
    "passwd":"mqm",
    "db":"tiku_mqm",
    "port":3306,
    "charset":"utf8",
    "mincached":1,
    "maxcached":10,
    "maxconnections":30
}
#分析爬取的文件并生成SQL的配置
contentroot='../../data_registry/crawler_chemistry_middle/crawler_out/content/2/22/'
analysisroot='../../data_registry/crawler_chemistry_middle/crawler_out/analysis/2/22/'
subjectfilename='../../data_registry/chemistry.middle.html'
sqlPath='../../data_registry/sql/'
errPath='../../data_registry/err/'
#待实现处理完的文件标记
#success

#将生成的SQL导入mysql数据的的配置
errSqlPath='log/'
sqlfiledir = "../../download_sql/old_sql/history.high.sql"

#从mysql中导入数据到postgres的配置
TAB_NAME = 'k12_tiku_details_history_high'
SQL_FILE = 'sql/history.high.postgresql.sql'