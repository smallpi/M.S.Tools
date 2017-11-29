# -*- coding:utf-8 -*-

__author__ = "smallpi"

"""
将三角网格文件格式转成.UFO文件格式
目的是为了加快三角网格文件的读取
.UFO Unified Formated Object
自己定义的一种二进制的三角网格文件格式
格式如下：
36 Bytes    保留
4 Bytes     保留
4 Bytes     文件包含的数据内容
4 Bytes     三角网格顶点数
12 Bytes    一个顶点的X坐标、Y坐标、Z坐标分别占用4个字节，float类型
12 Bytes    一个顶点的颜色R、G、B分别占用4个字节，float类型
...
12 Bytes    重复一个顶点的X坐标、Y坐标、Z坐标分别占用4个字节，float类型
12 Bytes    重复一个顶点的颜色R、G、B分别占用4个字节，float类型
...
"""

import os
import re
import struct

class UFOConverter:

    def __init__(self, file, targetFile):
        self._file = file
        self._targetFile = targetFile
        self._objName = ""
        self._vertices = []
        self._normals = []
        self._textures = []
        self._colors = []
        self._colorMap = {}
        self._vertexIndexes = []
        self._normalIndexes = []
        self._textureIndexes = []
        self._hasTexture = False
        self._hasNormal = False


    def convertOBJ(self):
        if not os.path.exists(self._file) or not os.path.isfile(self._file):
            return False
        dirName,fileName = os.path.split(self._file)
        fileName,extName = os.path.splitext(fileName)
        print(dirName,fileName,extName,os.sep)

        # 解析MTL文件
        mtlFileName = dirName + os.sep + fileName + ".mtl"
        if os.path.exists(mtlFileName):
            mtlFile = open(mtlFileName)
            colorName = ""
            for line in mtlFile:
                if line.startswith("newmtl"):
                    m = re.search('''newmtl\s+(\w+)''',line)
                    colorName = m.group(1)
                elif line.startswith("Kd"):
                    m = re.search('''Kd\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)''',line)
                    self._colorMap[colorName] = ( float(m.group(1)), float(m.group(2)), float(m.group(3)) )
        
        vertices = []
        normals = []
        textures = []

        # 解析OBJ文件
        objFile = open(self._file)
        mtlName = ""
        for line in objFile:
            if line.startswith("vt"):
                # 纹理坐标
                m = re.search('''vt\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)''',line)
                textures.append(( float(m.group(1)), float(m.group(2)), float(m.group(3))))
                self._hasTexture = True
            elif line.startswith("vn"):
                # 法向量
                m = re.search('''vn\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)''',line)
                normals.append(( float(m.group(1)), float(m.group(2)), float(m.group(3)) ))
                self._hasNormal = True
            elif line.startswith("v"):
                # 顶点坐标
                m = re.search('''v\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)''',line)
                vertices.append(( float(m.group(1)), float(m.group(2)), float(m.group(3)) ))
            elif line.startswith("usemtl"):
                # 材质名称
                m = re.search('''usemtl\s+(\w+)''',line)
                mtlName = m.group(1)
            elif line.startswith("f"):
                # 面信息
                m = re.search('''f\s+(\d+)/(\d*)/(\d*)\s+\s+(\d+)/(\d*)/(\d*)\s+(\d+)/(\d*)/(\d*)''',line)
                vIndex = (m.group(1),m.group(4),m.group(7))
                vtIndex = (m.group(2),m.group(5),m.group(8))
                vnIndex = (m.group(3),m.group(6),m.group(9))
                self._vertices.append( vertices[int(vIndex[0])-1] )
                self._vertices.append( vertices[int(vIndex[1])-1] )
                self._vertices.append( vertices[int(vIndex[2])-1] )
                self._normals.append( normals[int(vnIndex[0])-1] )
                self._normals.append( normals[int(vnIndex[1])-1] )
                self._normals.append( normals[int(vnIndex[2])-1] )
                self._colors.append( self._colorMap[mtlName] )
                self._colors.append( self._colorMap[mtlName] )
                self._colors.append( self._colorMap[mtlName] )
        # 输出UFO文件
        self.writeToTarget()


    def convertSTL(self):
        pass

    def writeToTarget(self):
        if len(self._targetFile) == 0:
            dirName,fileName = os.path.split(self._file)
            fileName,extName = os.path.splitext(fileName)
            self._targetFile = dirName + os.sep + fileName + ".ufo"
        # 存储的数据种类
        typeInt = 0
        if len(self._normals) > 0:
            typeInt |= int("0001",base=2)
        if len(self._colors) > 0:
            typeInt |= int("0010",base=2)
        if len(self._textures) > 0:
            typeInt |= int("0100",base=2)

        # 存储的数据个数
        vertexLen = len(self._vertices)

        print(typeInt,vertexLen)

        targetFile = open(self._targetFile,"wb+")
        targetFile.write(struct.pack("IIIIIIIIIIII",0,0,0,0,0,0,0,0,0,0,typeInt,vertexLen))

        for i in range(vertexLen):
            targetFile.write(struct.pack("fff",*self._vertices[i]))
        for i in range(vertexLen):
            targetFile.write(struct.pack("fff",*self._normals[i]))
        for i in range(vertexLen):
            targetFile.write(struct.pack("fff",*self._colors[i]))



if __name__ == "__main__":
    ufo = UFOConverter("C:/Users/smallpi/Desktop/NCUtilTest/custom4.obj","")
    ufo.convertOBJ()