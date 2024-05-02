from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

import dn_crop
import json
import copy

if __name__ == '__main__':
    Path = 'D:/Beatls/NIR_S/Крамола/2024/Progs/DataForProgs/cutter_prj'
    JsonFile = 'res.json'
    jsonObj = dn_crop.DNjson(Path + '/' + JsonFile)
    NumImg = 70
    Pols = jsonObj.ReadPolygons(NumImg)
    Img = Image.open(Path + '/' + jsonObj.ImgsName[NumImg])
    Img = dn_crop.DNjson.PrintPolys(Pols['Polys'], Img)
    #
    plt.imshow(Img)
    plt.show()

    # PathData='D:/Beatls/NIR_S/Крамола/2024/Progs/DataForProgs/cutter_prj'
    # JsonNameFile='cut_prj.json'
    # ImgCutObj=dn_crop.DNImgCut(PathData,JsonNameFile)
    # ImgCutObj.CutAllImgs(1280,[0.5,0.5,0.5,0.5,0.5,0.5],0.5,'res.json')

    # JsonNameFileWrite='proba.json'
    # JsonObj=dn_crop.DNjson(PathData+'/'+JsonNameFile)
    # JsonObj.WriteDataJson(PathData,JsonNameFileWrite,DataForJson['ImgNames'],DataForJson['Pols'],DataForJson['ClsNums'])


# Функция вывода контуров полигонов на изображение
@classmethod
def PrintPolys(cls, Polys: [], Img: Image):
    RGBMAss = np.array(Img).astype("uint8")
    for Poly in Polys:
        for i in range(len(Poly)):
            j = i + 1
            if j == len(Poly): j = 0
            p1 = [int(Poly[i][0]), int(Poly[i][1])]
            p2 = [int(Poly[j][0]), int(Poly[j][1])]
            cv.line(RGBMAss, p1, p2, (255, 255, 0), 2)
    return RGBMAss