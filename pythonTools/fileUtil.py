# -*- coding: utf-8 -*-

__author__ = "smallpi"

"""
通过输入文件夹进行目录和文件的遍历
1. 输入目录 -> 进行该目录下所有目录及文件的遍历
2. 输入文件 -> 输出该文件
3. 输入的既不是目录也不是文件 -> 返回 None
"""

import os
import shutil
import re

# 文件处理的接口(interface)
class FileOperator(object):
    def operate(self,path):
        pass
    
    def beforeScan(self):
        pass

# 打印操作
class FilePrinter(FileOperator):
    def __init__(self, bPrintFile=True, bPrintDir=True):
        self.__bPrintFile = bPrintFile
        self.__bPrintDir = bPrintDir

    def operate(self,path):
        if self.__bPrintFile and os.path.isfile(path):
            print(path)
        elif self.__bPrintDir and os.path.isdir(path):
            print(path)

# 文件收集
class FileCollector(FileOperator):
    def __init__(self,collectPath,matcher):
        self.__collectPath = collectPath
        self.__matcher = matcher

    def beforeScan(self):
        if not os.path.exists(self.__collectPath):
            os.makedirs(self.__collectPath)

    def operate(self,path):
        if self.__matcher.match(path):
            shutil.copy(path,self.__collectPath)


# 文件删除
class FileCleaner(FileOperator):
    def __init__(self,matcher):
        self.__matcher = matcher

    def operate(self,path):
        if self.__matcher.match(path):
            os.remove(path)

class FileUtil(object):
    def __init__(self,path,fileOperator=FilePrinter()):
        self.__path = path
        self.__fileOperator = fileOperator
        self.__errorPath = []

    def __beforeScan(self):
        self.__fileOperator.beforeScan()

    def __scandir(self,path):
        dirname = os.path.abspath(path)
        dirs = []
        try:
            dirs = os.listdir(dirname)
        except PermissionError as e:
            self.__errorPath.append(dirname)
        # 遍历该目录
        for filename in dirs:
            # 文件的绝对路径
            absfilename = os.path.join(dirname,filename)
            if os.path.isfile(absfilename):
                # 普通文件
                self.__fileOperator.operate(absfilename)
                # print(absfilename)
            elif os.path.isdir(absfilename):
                # 目录
                self.__fileOperator.operate(absfilename)
                self.__scandir(absfilename)

    def scan(self):
        if os.path.isdir(self.__path):
            self.__scandir(self.__path)
        elif os.path.isfile(self.__path):
            print("Warning: input is common file!")
            absfilename = os.path.abspath(self.__path)
            self.__fileOperator.operate(absfilename)
        else:
            print("InputError: not a dir")

        self.__outputError()
        return None
    
    # 不可访问的文件或目录的输出
    def __outputError(self):
        if len(self.__errorPath) > 0:
            print("========= 不可访问 =========")
            print(self.__errorPath)



# 文件名匹配器
class Matcher(object):
    def match(path):
        pass

class ExtMatcher(Matcher):
    def __init__(self,extList):
        self.__extList = extList
    
    def match(self,path):
        extName = os.path.splitext(path)[1]
        if extName in self.__extList:
            return True
        return False

class ReMatcher(Matcher):
    def __init__(self,patternStr):
        self.__patternStr = patternStr

    def match(self,path):
        if re.match(self.__patternStr,path):
            return True
        return False

if __name__ == "__main__":
    fileUtil = FileUtil("C:/Users/smallpi/Desktop/新建文件夹",FileCleaner(ReMatcher('''.*\.js$''')))
    fileUtil.scan()