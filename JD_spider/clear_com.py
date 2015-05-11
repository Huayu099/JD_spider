# -*- coding: utf-8 -*-
__author__ = 'KaNgai'
import pymongo
import re
import os
import jieba
from collections import Counter
'''
    目的: 清理评论数据（清理无用评论）
         获取属性（先分词，再删除程度词，再对剩下的词计数）
'''


class JD_comment_clean:
    def __init__(self, dbs):
        self.conn = pymongo.Connection(dbs["username"], dbs["port"])
        self.db = self.conn[str(dbs["dbsname"])]
        self.col = self.db[str(dbs["collections"])]

    def pick_comment(self):
        comment = []
        for com in self.col.find({},{"comment":1}):
            comment.append(com["comment"][0])
        return comment

    def clean_comment(self, clean_rule, comment):
        """
        按给定的清理正则表达式清理评论数据
        :param clean_rule: 剔除垃圾评论的正则表达式字典
        :type clean_rule: dict
        :return: clean_comment
        :rtype: list
        """
        clean_comment = []
        for com in comment:
            item = com
            for key in clean_rule:
                com = re.sub(clean_rule[key], "", com)
            len_clean_com = len(com)
            if len_clean_com == 0:
                continue
            else:
                clean_comment.append(item)
        return clean_comment

    def pick_most_dict(self, mostWordDir):
        """

        :param mostWordDir: 程度词文件目录
        :return: most_dict
        :rtype: list
        """
        most_dict = []
        Dir = str(mostWordDir)
        most_dict_dir = os.listdir(Dir)    # 获取程度词目录下文件列表
        for file in most_dict_dir:
            most_dict_file = open(os.path.join(Dir, file),  mode = 'r').readlines()
            for dict in most_dict_file:
                dict = dict.replace('\n', '')
                dict = dict.replace(' ', '')
                most_dict.append(dict.decode('gbk'))   # 去除换行符
        return most_dict

    def clean_most_comment(self, cut_comment, most_dict):
        """
        :param cut_comment: 已经分词的评论，[['','',''],[],[],[]]
        :param most_dict: 程度词列表，['','','','']
        :return: clean_mostword_comment: 去除程度词的评论分词，['','','','']
        """
        clean_mostword_comment = []
        for com in cut_comment:
            for com_cut in com:
                if com_cut in most_dict:
                    continue
                else:
                    clean_mostword_comment.append(com_cut)
        return clean_mostword_comment

    def cut_comment(self, comment):
        """
        :type comments: list
        :return cut_comment: [[],[],[]]
        """
        cut_comment = []
        for com in comment:
            cut_comment.append(list(jieba.cut(com)))
        return cut_comment

dir = "G:\Users\KaNgai\Documents\GitHub\JD_spider\JD_spider\sentiment"
dbs = {
    'username': 'localhost',
    'port': 27017,
    'dbsname': 'JD',
    'collections': 'g646197',
    }
clean_rule = {
        'num' : u'\d+',
        'punctuation' : u'[，。？/！+\-*~@#$%^&()_=,\.;\:\"\'!]+',
    }

JD = JD_comment_clean(dbs)
comment = JD.pick_comment()
cut_comment = JD.cut_comment(comment)
print 'have been cut comment'
clean_comment = []
for cut_com in cut_comment:
    clean_comment.append(JD.clean_comment(clean_rule, cut_com))
print 'have been clean comment'
most_dict = JD.pick_most_dict(dir)
print 'get most words'
clean_mostword_comment = JD.clean_most_comment(clean_comment, most_dict)
print 'have been clean most words'

count_comment = Counter(clean_mostword_comment)
print 'ok'
ccc = count_comment.most_common(20)