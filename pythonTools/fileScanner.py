# -*- coding:utf-8 -*-

__author__ = "smallpi"

"""
对某一路径下的文本文件进行扫描
找出匹配的文本行
显示文件名、文本行号、文本行
"""


import os
import re
import chardet

class FileScanner(object):

    def __init__(self,path="./", patternStr="", bSave=False, saveFile="./scan_result.txt"):
        self.__path = path
        self.__patternStr = patternStr
        self.__bSave = bSave
        self.__saveFile = saveFile
        
        self.__file = None

    def setPath(self,path):
        self.__path = path


    def setPatternStr(self,patternStr):
        self.__patternStr = patternStr


    def saveFile(self,saveFile,bSave=True):
        self.__bSave = bSave
        self.__saveFile = saveFile


    def scan(self):
        if not self.__beforeScan():
            return
        
        absFileName = os.path.abspath(self.__path)
        if os.path.isfile(self.__path):
            self.__scanFile(absFileName)
        elif os.path.isdir(self.__path):
            self.__scanDir(absFileName)

        self.__afterScan()


    def __beforeScan(self):
        if not os.path.exists(self.__path):
            print("path: {0} dose not exists.".format(self.__path))
            return False
        if self.__bSave:
            try:
                self.__file = open(self.__saveFile,"w")
            except IOError:
                print("file: {0} open fail.".format(self.__file))
                return False
        return True


    def __afterScan(self):
        if self.__bSave and self.__file:
            self.__file.close()


    def __scanFile(self,filepath):
        #print(filepath)
        file = open(filepath,"rb")
        data = file.read()
        file.close()
        ret = chardet.detect(data)
        charcode = ret["encoding"]
        file = open(filepath,"r",encoding=charcode)
        

        lineNum = 0
        bFirstFound = False
        for line in file:
            lineNum = lineNum + 1
            if re.search(self.__patternStr, line):
                self.__process(filepath, lineNum,line,bFirstFound)
                bFirstFound = True
    

    def __scanDir(self,dirpath):
        dirs = []
        try:
            dirs = os.listdir(dirpath)
        except PermissionError:
            print("Permission Error")
        for filename in dirs:
            absFileName = os.path.join(dirpath,filename)
            if os.path.isfile(absFileName):
                self.__scanFile(absFileName)
            elif os.path.isdir(absFileName):
                self.__scanDir(absFileName)


    def __process(self,filepath,lineNum,line,bFirstFound):
        if self.__bSave:
            #保存到文件
            if self.__file:
                if not bFirstFound:
                    self.__file.write("\n########################################################################################################################\n")
                    self.__file.write("\nFound result of ==> {0}\n".format(filepath))
                self.__file.write("lineNumber [{0}]\nlineContent : {1}".format(lineNum,line))
        else:
            #输出的屏幕
            if not bFirstFound:
                print("\n########################################################################################################################\n")
                print("Found result of ==> {0}\n".format(filepath))
            print("lineNumber [{0}]\nlineContent : {1}".format(lineNum,line))
        




# 用于测试
if __name__ == "__main__":
    # 输出到控制台
    # scanner = FileScanner("C:/Users/smallpi/Desktop/Linux笔记/运维基础/","""系统""")
    # scanner.scan()

    scanner = FileScanner("C:/Users/smallpi/Desktop/NCUtilTest/20160306/","""^POLYLINE""",True,"C:/Users/smallpi/Desktop/scan_result.txt")
    scanner.scan()