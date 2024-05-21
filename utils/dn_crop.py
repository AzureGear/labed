from shapely import Polygon, MultiPolygon
from sklearn.cluster import DBSCAN
import numpy as np
import cv2 as cv
import copy
import codecs
import json
import os


class DNjson:
    """ Класс работы с исходными данными (результатами НС), записанными в формате json"""

    def __init__(self, json_file: str):
        self.json_file = json_file

        # Получаем данные из файла в виде формата json
        self.DataDict = self.ReadDataJson()

        if self.DataDict:  # выполняем проверку

            # Читаем имена всех изображений, записанных в json
            self.ImgsName = self.ReadNamesImgs()

            # Формируем перечень имен классов (меток)
            self.labels = (self.DataDict['labels'])

            # Узнаем максимальный номер класса
            self.MaxClsNum = len(self.labels)  # print("Максимальный номер класса: ", self.MaxClsNum)

    # Функции, использующиеся при инициализации класса
    # Функция чтения данных из файла Json
    def ReadDataJson(self):
        # Читаем файл Json
        file = open(self.json_file, "r")
        # Читаем одну строчку, т.к. предполагается, что все данные в файле записаны в одну строчку
        data = file.readline()
        file.close()

        if self.check_json(data):  # выполняем проверку
            self.good_file = True
            # Переделываем строку в json словарь
            data_dict = json.loads(data)
            return data_dict
        else:
            self.good_file = False
            return None

    def check_json(self, json_project_data):  # примитивная проверка на наличие нужных параметров
        for field in ["path_to_images", "images", "labels", "labels_color"]:
            if field not in json_project_data:
                return False
        return True

    @classmethod
    def ReadJsonKeys(cls, DataDict):  # код для отладки
        Keys1 = DataDict.keys()
        for Key1 in Keys1:
            print(Key1, type(DataDict[Key1]))

            if Key1 == 'images':
                Keys2 = DataDict[Key1].keys()
                for Key2 in Keys2:
                    print("\t", Key2, type(DataDict[Key1][Key2]))

                    Keys3 = DataDict[Key1][Key2].keys()
                    for Key3 in Keys3:
                        print("\t\t", Key3, type(DataDict[Key1][Key2][Key3]))

                        if Key3 == 'shapes':
                            for i in range(len(DataDict[Key1][Key2][Key3])):
                                print("\t\t\t", i, type(DataDict[Key1][Key2][Key3][i]))

                                Keys4 = DataDict[Key1][Key2][Key3][i].keys()
                                for Key4 in Keys4:
                                    print("\t\t\t\t", Key4, type(DataDict[Key1][Key2][Key3][i][Key4]))

            if Key1 == 'labels_color':
                Keys2 = DataDict[Key1].keys()
                for Key2 in Keys2:
                    print("\t", Key2, type(DataDict[Key1][Key2]))

            if Key1 == 'labels':
                for i in range(len(DataDict[Key1])):
                    print("\t", i, type(DataDict[Key1][i]), DataDict[Key1][i])

    # Создание словаря для отдельной картинки
    def PolsToDict(self, NumCrudeImg: int, Pols: [], ClsNums: []):
        PropsImg = self.ReadImgProp(NumCrudeImg)
        shapes = []
        for i in range(len(Pols)):
            # Перевод из numpy в list двумерного массива
            PolList = list(Pols[i])
            PolList = [list(PolList[j]) for j in range(len(PolList))]

            # Перевод из int32 в просто int
            xList = [float(p[0]) for p in PolList]
            yList = [float(p[1]) for p in PolList]
            PolList = [[xList[j], yList[j]] for j in range(len(xList))]

            dict = {'cls_num': ClsNums[i], 'points': PolList, 'id': i + 1}
            shapes.append(dict)

        return {'shapes': shapes, 'lrm': PropsImg['lrm'], 'status': PropsImg['status'],
                'last_user': PropsImg['last_user']}

    # Функция записи в файл json
    def WriteDataJson(self, PathToJsonFile: str, NameJsonFile: str, NamesImg: [], Polys: [], NumsCls: []):
        # Формируем словарь, который будет записан
        # 1. Формируем путь к изображениям
        PathToImgs = PathToJsonFile
        PathToImgs.replace('/', '\/')
        self.ReadJsonKeys()

    # # Функция чтения имен классов (меток), содержащихся в json
    # def read_labels_names(self):
    #     labels_names = []
    #     # Получение наименований всех изображений
    #     values = list(self.DataDict["labels"].values())
    #     for NameImg in self.DataDict["images"].keys():
    #         NamesImgs.append(NameImg)
    #     return NamesImgs

    # Функция чтения имен файлов - изображений, содержащихся в json
    def ReadNamesImgs(self):
        NamesImgs = []
        # Получение наименований всех изображений
        for NameImg in self.DataDict["images"].keys():
            NamesImgs.append(NameImg)
        return NamesImgs

    # Функции, использующиеся во внешней программе, относящиеся к отдельному изображению
    # Функция чтения всех полигонов на конкретном изображении
    def ReadPolygons(self, NumImg: int):
        # Если номер изображения больше чем количество изображений, содержащихся в json-файле, выходим из программы
        if NumImg >= len(self.ImgsName):
            print("Заданный номер изображения некорректен")
            return None

        # Перебор всех полигонов на изображении
        ClsNums = []
        Polys = []
        for Pol in self.DataDict["images"][self.ImgsName[NumImg]]["shapes"]:
            ClsNums.append(Pol['cls_num'])
            Polys.append(Pol['points'])
        return {'ClsNums': ClsNums, 'Polys': Polys}

    # Функция чтения свойств изображения
    def ReadImgProp(self, NumImg: int):
        # Если номер изображения больше чем количество изображений, содержащихся в json-файле, выходим из программы
        if NumImg >= len(self.ImgsName):
            print("Заданный номер изображения некорректен")
            return None

        LRM = self.DataDict["images"][self.ImgsName[NumImg]]["lrm"]
        Stat = self.DataDict["images"][self.ImgsName[NumImg]]["status"]
        LastUser = self.DataDict["images"][self.ImgsName[NumImg]]["last_user"]

        return {"lrm": LRM, "status": Stat, "last_user": LastUser}

    # Функция преобразования полигонов точечных в полигоны Shp
    @classmethod
    def PolysToShp(cls, Polys: []):
        PolysShp = []
        for Pol in Polys:
            PolysShp.append(Polygon(Pol))
        return PolysShp

    # Функция преобразования координат полигона из исходных в локальные (для порезанных картинок)
    @classmethod
    def CoordGlobToLocal(cls, Polys: [], np: []):
        for Pol in Polys:
            Pol[:, 0] = Pol[:, 0] - np[0]
            Pol[:, 1] = Pol[:, 1] - np[1]
        return Polys


# ----------------------------------------------------------------------------------------------------------------------
class DNImgCut:
    """ Класс работы с изображениями"""

    def __init__(self, PathToImg: str, NameJsonFile: str):

        self.PathToImg = PathToImg

        # Создаем объект json
        json_file = PathToImg + '/' + NameJsonFile
        self.JsonObj = DNjson(json_file)

        # Получение имен всех картинок в папке
        self.FullNamesImgsFile = []
        for ImgName in self.JsonObj.ImgsName:
            self.FullNamesImgsFile.append(PathToImg + '/' + ImgName)

    @classmethod
    def create_poly_from_shp(cls, pn: [], WW, HW):
        """Функция построения shp полигона из сканирующего окна"""
        xn = pn[0]
        yn = pn[1]
        xk = xn + WW
        yk = yn + HW
        Pol = [[xn, yn], [xk, yn], [xk, yk], [xn, yk]]
        PolSHP = Polygon(Pol)
        return PolSHP

    @classmethod
    def GetPosWindShp(cls, pn: [], WW: int, HW: int, WImg: int, HImg: int, ProcOverlapPol: [], ProcOverlapW: float,
                      PolsSHP: [], NumClsPols: []):
        """
        Функция перемещения сканирующего окна по картинке (возвращает массив значений всех удовлетворительных
        положений сканирующего окна). Параметры:
            pn - начальная точка перемещения окна;
            WW, HW - размеры окна;
            WImg, HImg - размеры информативной области изображения, в пределах которой следует вести скольжение окна;
            ProcOverlapPol - значение границы (%) перекрытия площади полигонов (устанавливается для каждого класса
                отдельно);
            ProcOverlapW - процент перекрытия окна для смежных кадров.
        """
        # В начале алгоритма перемещение окна идет по одному пикселю
        dx = int(WW * ProcOverlapW)
        dy = int(HW * ProcOverlapW)
        pk = pn.copy()
        pnList = []  # Список удовлетворительных значений сканирующего окна
        while 1:
            # Генерируем из окна SHP полигон
            WPolSHP = cls.create_poly_from_shp(pk, WW, HW)

            # Проверяем полигоны на пересечение с окном сканирования
            Pols = cls.FindPolyOverload(WPolSHP, PolsSHP, ProcOverlapPol, NumClsPols)

            # Если найдены пересекающиеся полигоны
            if not Pols == None:
                # Запоминаем позицию окна
                pnList.append(pk.copy())

            # Если сканирующее окно при смещении на dx,dy перейдет за край изображения, корректируем dx,dy
            if pk[0] + dx + WW > WImg:
                dx = WImg - WW - pk[0]
            if pk[1] + dy + HW > HImg:
                dy = HImg - HW - pk[1]

            # Смещаем окно по горизонтали
            pk[0] += dx

            # Если достигли конца картинки
            if dx == 0 and dy == 0:
                return pnList

            # Если достигли только вертикального края картинки
            elif dx == 0:
                # Перескакиваем на строчку ниже
                pk[0] = pn[0]
                pk[1] += dy
                dx = int(WW * ProcOverlapW)

    @classmethod
    def GetPosWindShp2(cls, WW: int, HW: int, WImg: int, HImg: int, ProcOverlapPol: [], D: int, ProcOverlapW: float,
                       PolsSHP: [], NumClsPols: []):
        """Интеллектуальная функция перемещения сканирующего окна по картинке. Разбиваем полигоны на кластеры согласно
        положению их центров масс (по территориальному признаку)
            eps - минимальное расстояние между центрами масс полигонов, чтобы их можно было отнести в один кластер
            считаем, что если центры масс укладываются в размеры сканирующего окна, то это - один кластер """

        PolsC = []
        for Pol in PolsSHP:
            P = Pol.centroid
            PolsC.append([P.x, P.y])

        ClastModel = DBSCAN(eps=(WW + HW) / 2, min_samples=1)
        ClastModel.fit_predict(PolsC)

        pnList = []  # Список удовлетворительных значений сканирующего окна
        # Дальнейшая обработка изображения идет по кластерам, на которые разбиты полигоны
        for NCl in np.unique(ClastModel.labels_):
            print("Номер обрабатываемого кластера: ", NCl)
            # Выбираем все полигоны, принадлежащие одному кластеру
            Index = np.column_stack(np.where(np.array(ClastModel.labels_) == NCl))
            PolsSHPClast = [PolsSHP[i[0]] for i in Index]
            NumClsPolsClast = [NumClsPols[i[0]] for i in Index]
            IndexClast = [i[0] for i in Index]

            # Открываем цикл, который повторяется до тех пор пока все полигоны в кластере не будут учтены
            while 1:
                # Переводим SHP полигоны в обычные
                PolsPtClast = [np.array(PolSHP.exterior.coords, float) for PolSHP in PolsSHPClast]

                # Определяем размеры всех полигонов в кластере
                PolsClastMinMax = {'MinX': [], 'MaxX': [], 'MinY': [], 'MaxY': []}  # Координаты рамки каждого полигона

                # Разделяем весь список полигонов на те, которые целиком умещаются в окно, и те, которые в окно не умещаются
                IndxPolW = []  # Индексы полигонов, которые полностью помещаются в окно
                IndxPolBig = []  # Индексы полигонов, которые в окно не помещаются
                for i in range(len(PolsPtClast)):
                    x = np.array(PolsPtClast[i])[:, 0]
                    y = np.array(PolsPtClast[i])[:, 1]
                    xMin = min(x)
                    xMax = max(x)
                    yMin = min(y)
                    yMax = max(y)

                    PolsClastMinMax['MinX'].append(xMin)
                    PolsClastMinMax['MaxX'].append(xMax)
                    PolsClastMinMax['MinY'].append(yMin)
                    PolsClastMinMax['MaxY'].append(yMax)

                    WPol = xMax - xMin
                    HPol = yMax - yMin

                    if WPol < WW - 2 * D and HPol < HW - 2 * D:
                        IndxPolW.append(i)
                    else:
                        IndxPolBig.append(i)

                # Определяем зону всего кластера
                xMinClsat = min(PolsClastMinMax['MinX'])
                xMaxClsat = max(PolsClastMinMax['MaxX'])
                yMinClsat = min(PolsClastMinMax['MinY'])
                yMaxClsat = max(PolsClastMinMax['MaxY'])

                # Учитываем отступ
                xMinClsatD = xMinClsat - D
                if xMinClsatD < 0: xMinClsatD = 0

                yMinClsatD = yMinClsat - D
                if yMinClsatD < 0: yMinClsatD = 0

                xMaxClsatD = xMaxClsat + D
                if xMaxClsatD > WImg: xMaxClsatD = WImg

                yMaxClsatD = yMaxClsat + D
                if yMaxClsatD > HImg: yMaxClsatD = HImg

                WClast = xMaxClsatD - xMinClsatD
                HClast = yMaxClsatD - yMinClsatD

                # Вычисляем шаг перемещения окна и количество шагов с учетом заданного интервала
                dx = WW - int(WW * ProcOverlapW)
                dy = HW - int(HW * ProcOverlapW)

                IterX = int((WClast - dx) / dx)
                IterY = int((HClast - dx) / dy)

                if (WClast - dx) % dx > 0: IterX += 1
                if (HClast - dy) % dy > 0: IterY += 1

                # Перемещаем окно в пределах кластерной зоны с заданным интервалом
                WPosProp = {'pn': [], 'IndxPolsClast': [], 'PartArea': [], 'PolsSHP': []}
                for iy in range(IterY):
                    for ix in range(IterX):

                        # Расчитываем позицию сканирующего окна
                        pnX = xMinClsatD + ix * dx
                        pnY = yMinClsatD + iy * dy
                        if pnX + WW > xMaxClsatD: pnX = xMaxClsatD - WW
                        if pnY + HW > yMaxClsatD: pnY = yMaxClsatD - HW
                        if pnX < 0: pnX = 0
                        if pnY < 0: pnY = 0

                        # Генерируем из окна SHP полигон
                        WPolSHP = cls.CreateWPolSHP([pnX, pnY], WW, HW)

                        # Проверяем полигоны на пересечение с окном сканирования
                        PolsClast = cls.FindPolyOverload(WPolSHP, PolsSHPClast, ProcOverlapPol, NumClsPolsClast)

                        # Ставим соответствие положение сканирующего окна и пересекающихся полигонов
                        # с процентажем площади
                        if not PolsClast == None:
                            WPosProp['pn'].append([int(pnX), int(pnY)])
                            WPosProp['IndxPolsClast'].append(PolsClast['Indx'])
                            WPosProp['PartArea'].append(PolsClast['PartArea'])
                            WPosProp['PolsSHP'].append(PolsClast['Polys'])

                # Если по пробеганию окна по всей зоне кластера не нашлось ни одного полигона то выходим из цикла
                if len(WPosProp['PolsSHP']) == 0:
                    print("Возможно, не все полигоны обработались")
                    break

                # Выбираем оптимальную позицию сканирующего окна по максимуму попадания в него объектов
                # При этом, в приоритете находятся позиции, в которых объект попадает целиком в сканирущее окно
                IndxWPosRes = 0  # По умолчанию, номер оптимальной позиции окна - 0

                # Узнаем позиции окна, где все полигоны попадают полностью (средняя площадь пересечения полигонов с окном равна единице)
                KofArea = [np.mean(PartAreaPols) for PartAreaPols in WPosProp['PartArea']]
                IndxPolsAreaAll = [i for i, v in enumerate(KofArea) if v > 0.99]

                # Если найдены позиции окна, где все полигоны попадают полностью, выбираем максимальное количество полигонов
                if not len(IndxPolsAreaAll) == 0:
                    NumbPol = [len(WPosProp['IndxPolsClast'][i]) for i in IndxPolsAreaAll]
                    IndxMaxNumbPols = NumbPol.index(max(NumbPol))
                    IndxWPosRes = IndxPolsAreaAll[IndxMaxNumbPols]

                    IndxsMaxNumbPols = [i for i, v in enumerate(NumbPol) if v == max(NumbPol)]
                    IndxsWPosRes = [IndxPolsAreaAll[i] for i in IndxsMaxNumbPols]


                # Если для всех позиций окна какие-то из полигонов режутся, выбираем позицию окна
                # так, чтобы было максимальное количество нерезанных объектов
                else:
                    # Узнаем количество нерезанных полигонов для каждой позиции окна
                    NumbPolsAreaAll = []
                    for PartAreaPols in WPosProp['PartArea']:
                        NumbPolsAreaAll.append(len([i for i, v in enumerate(PartAreaPols) if v > 0.99]))

                    # Узнаем все индексы позиций окна, где полигоны не разрезаны
                    IndxMaxNumbPolsAreaAll = [i for i, v in enumerate(NumbPolsAreaAll) if v == max(NumbPolsAreaAll)]
                    # Из них выбираем позицию с мксиммальным усредненным коэффициентом по площади
                    KofArea = [KofArea[i] for i in IndxMaxNumbPolsAreaAll]
                    IndxMaxKofArea = KofArea.index(max(KofArea))
                    IndxWPosRes = IndxMaxNumbPolsAreaAll[IndxMaxKofArea]

                    IndxsMaxKofArea = [i for i, v in enumerate(KofArea) if v == max(KofArea)]
                    IndxsWPosRes = [IndxMaxNumbPolsAreaAll[i] for i in IndxsMaxKofArea]

                # Если позиций окон удовлетворяющих условию много, то выбираем из всех позиций
                # с минимальным пересечением с ранее занесенными в список окнами
                SummArea = []
                for IndxWPosRes in IndxsWPosRes:
                    WPolSHP = cls.CreateWPolSHP(WPosProp['pn'][IndxWPosRes], WW, HW)
                    Ws = [cls.CreateWPolSHP(pn, WW, HW) for pn in pnList]
                    AreaW = [WPolSHP.intersection(W).area for W in Ws]
                    SummArea.append(sum(AreaW))

                IndxMaxSumArea = SummArea.index(min(SummArea))
                IndxWPosRes = IndxsWPosRes[IndxMaxSumArea]

                # print(IndxWPosRes,'\t',IndxsWPosRes)

                # Узнаем текущее количество полигонов для каждой позиции окна
                # NumbPols=[len(IndxPos) for IndxPos in WPosProp['IndxPolsClast']]

                # Узнаем все номера позиций окна, где количество полигонов максимально
                # MaxNumbPols=max(NumbPols)
                # IndxMaxNumbPols=[index for index,value in enumerate(NumbPols) if value==MaxNumbPols]

                # Формируем массив bool для всех позиций окна:
                # True - количество пересекающихся полигонов максимально,
                # False - меньше максимального
                # ChoisePosW=[NumbPol==MaxNumbPols for NumbPol in NumbPols]

                # Узнаем сколько полигонов перекрываются полностью для каждой позиции окна
                # (расчет ведется только для положений окна с максимальным количеством пересечений полигонов)
                # NumbPolsAreaAll=[]
                # IndxPolsAreaAll=[]
                # for j in range(len(WPosProp['PartArea'])):
                #     if ChoisePosW[j]:
                #         NumbPolsAreaAll.append(len([i for i,v in enumerate(WPosProp['PartArea'][j]) if v>0.99]))
                #         IndxPolsAreaAll.append([i for i,v in enumerate(WPosProp['PartArea'][j]) if v>0.99])
                #     else:
                #         NumbPolsAreaAll.append(0)
                #         IndxPolsAreaAll.append(None)

                # Узнаем первый индекс максимального количества полигонов перекрывающихся полностью окном
                # MaxNumbPolsAreaAll=max(NumbPolsAreaAll)
                # IndxMaxNumbPolsAreaAll=NumbPolsAreaAll.index(MaxNumbPolsAreaAll)

                # Добавляем положение окна в список хороших положений окон
                pnList.append(WPosProp['pn'][IndxWPosRes])

                # Режем полигоны, попадающие в окно
                WPolSHP = cls.CreateWPolSHP(pnList[-1], WW, HW)
                PolsCutSHP = [WPolSHP.intersection(PolsSHPClast[j]) for j in WPosProp['IndxPolsClast'][IndxWPosRes]]

                # Вычитаем из полигонов кластера все перекрывающиеся полигоны
                for j in range(len(PolsCutSHP)):
                    CurIndx = WPosProp['IndxPolsClast'][IndxWPosRes][j]
                    if type(PolsCutSHP[j]) == Polygon:
                        PolDif = PolsSHPClast[CurIndx].difference(PolsCutSHP[j])
                    elif type(PolsCutSHP[j]) == MultiPolygon:
                        for PolSHP in PolsCutSHP[j].geoms:
                            PolDif = PolsSHPClast[CurIndx].difference(PolSHP)

                    # Если результат вычитания - это один полигон, то записываем его на место старого
                    if type(PolDif) == Polygon:
                        PolsSHPClast[CurIndx] = copy.copy(PolDif)

                    # Если результат - мультиполигон, то удаляем исходный полигон, и записываем новые
                    elif type(PolDif) == MultiPolygon:
                        PolsSHPClast.pop(CurIndx)
                        for Pol in PolDif.geoms:
                            PolsSHPClast.append(Pol)

                # Удаляем из списка полигонов все пустые
                PolsSHPClast = [Pol for Pol in PolsSHPClast if not Pol.is_empty]

                # Если список полигонов пуст, выходим из цикла
                if len(PolsSHPClast) == 0:
                    break

        return pnList

    @classmethod
    def FindPolyOverload(cls, WPolSHP, PolsSHP: [], ProcOverlapPols: [], NumClsPols: []):
        """Функция поиска пересекающихся с рамкой полигонов"""
        # Получаем индексы полигонов, пересекающихся со сканирующим окном
        Ov = WPolSHP.intersects(PolsSHP)
        Indx = np.column_stack(np.where(Ov))

        if len(Indx) == 0:
            return None
        # Если какие-то полигоны пересекаются с окном
        elif len(Indx) > 0:
            # Получаем пересекающиеся полигоны и номера их классов
            P_OV = [PolsSHP[j[0]] for j in Indx]
            Cls_OV = [NumClsPols[j[0]] for j in Indx]

            # Получаем площади полигонов
            AreaP = [P_OV[j].area for j in range(len(P_OV))]

            # Получаем площади пересечения полигонов с окном
            AreaOV = [WPolSHP.intersection(P_OV[j]).area for j in range(len(P_OV))]

            # Процент площади пересечения
            ProcAreaOverlap = np.array(AreaOV) / np.array(AreaP)

            # Проветяем удовлетворение условию площади пересечения сканирующей рамки с полигонами для разных классов
            GoodPolSHP = []
            ClsNumsGoodPol = []
            for i in range(len(P_OV)):
                ClsNum = Cls_OV[i]
                if ProcAreaOverlap[i] >= ProcOverlapPols[ClsNum]:
                    GoodPolSHP.append(P_OV[i])
                    ClsNumsGoodPol.append(ClsNum)

            if len(GoodPolSHP) > 0:
                return {'ClsNums': ClsNumsGoodPol, 'Polys': GoodPolSHP}

            elif len(GoodPolSHP) == 0:
                return None

    # Функция нарезки картинки
    # ProcOverlapPol - пороговое значение части площади пересечения полигона со сканирующим окном
    # с которого считается, что полигон попадает в окно
    def CutImg(self, NumImg: int, SizeWind: int, ProcOverlapPol: [], ProcOverlapW: float):
        # Определяем координаты рамки, в которую вмещается вся разметка
        # Читаем все полигоны с картинки
        Pols = self.JsonObj.ReadPolygons(NumImg)

        # Определяем минимум, максимум координату по всем полигонам
        xMin = Pols['Polys'][0][0][0]
        yMin = Pols['Polys'][0][0][1]
        xMax = Pols['Polys'][0][0][0]
        yMax = Pols['Polys'][0][0][1]

        for Pol in Pols['Polys']:
            x = np.array(Pol)[:, 0]
            y = np.array(Pol)[:, 1]

            if min(x) < xMin: xMin = min(x)
            if min(y) < yMin: yMin = min(y)
            if max(x) > xMax: xMax = max(x)
            if max(y) > yMax: yMax = max(y)

        # Читаем картинку (обходим проблему русских букв в названиях каталогов для open cv)
        path = self.FullNamesImgsFile[NumImg]
        Img = open(path, 'rb')
        data = Img.read()
        data_arr = np.frombuffer(data, dtype=np.uint8)
        Img = cv.imdecode(data_arr, cv.IMREAD_COLOR)

        # Определяем размеры картинки
        H = Img.shape[0]
        W = Img.shape[1]

        # Определяем координаты стартовой позиции сканирующего окна
        # По умолчанию, стартовая позиция: 0,0
        pWind = [0, 0]

        # Перемещаем сканирующее окно к рамке полигонов
        if xMin > SizeWind: pWind[0] = xMin - SizeWind
        if yMin > SizeWind: pWind[1] = yMin - SizeWind

        # Определяем размер сканирующего окна, если изображение меньше заданного размера окна
        WW = SizeWind
        HW = SizeWind
        if W - pWind[0] < WW: WW = W - pWind[0]
        if H - pWind[1] < HW: HW = H - pWind[1]

        # Определяем размеры значащей области изображения, с полигонами
        WObl = xMax - pWind[0] + WW
        HObl = yMax - pWind[1] + HW

        if WObl > W: WObl = W
        if HObl > H: HObl = H

        # Преобразуем полигоны в SHP
        PolsSHP = DNjson.PolysToShp(Pols['Polys'])

        # Получаем все валидные значения сканирующего окна
        # WPos=DNImgCut.GetPosWindShp(pWind,WW,HW,WObl,HObl,ProcOverlapPol,ProcOverlapW,PolsSHP,Pols['ClsNums'])
        # AZ
        WPos = DNImgCut.GetPosWindShp2(WW, HW, W, H, ProcOverlapPol, 5, ProcOverlapW, PolsSHP, Pols['ClsNums'])

        # Для каждой позиции сканирующего окна режем полигоны, площадь пересечения которых больше порогового значения
        i = 0
        NameCropImgs = []
        PolsImg = []
        ClsNumsImg = []
        for pW in WPos:
            # Строим SHP полигон из сканирующего окна
            WPolSHP = DNImgCut.create_poly_from_shp(pW, WW, HW)

            # Находим валидные полигоны
            PolsOvSHP = DNImgCut.FindPolyOverload(WPolSHP, PolsSHP, ProcOverlapPol, Pols['ClsNums'])

            # Режем каждый полигон по границе сканирующего окна
            PolsCutSHP = [WPolSHP.intersection(PolsOvSHP['Polys'][j]) for j in range(len(PolsOvSHP['Polys']))]

            # Определяем индексы, где результаты нарезки являются полигонами
            PolsCut = []
            ClsNums = []
            for j in range(len(PolsCutSHP)):
                if type(PolsCutSHP[j]) == Polygon:
                    PolsCut.append(np.array(PolsCutSHP[j].exterior.coords, float))
                    ClsNums.append(PolsOvSHP['ClsNums'][j])

                elif type(PolsCutSHP[j]) == MultiPolygon:
                    for PolSHP in PolsCutSHP[j].geoms:
                        PolsCut.append(np.array(PolSHP.exterior.coords, float))
                        ClsNums.append(PolsOvSHP['ClsNums'][j])

            PolsCut = self.JsonObj.CoordGlobToLocal(PolsCut, pW)

            # Режем изображение согласно координатам сканирующего окна
            ImgCrop = Img[pW[1]:pW[1] + HW, pW[0]:pW[0] + WW]

            # Генерим имя сохраняемого изображения
            NameImg = os.path.splitext(os.path.basename(path))[0]
            NameImg += '_'
            if i < 10: NameImg += '0'
            NameImg += str(i)
            NameImg += '.jpg'
            FullFileName = self.PathToImg + '/' + NameImg

            # Записываем картинки
            success, ImgCropArr = cv.imencode('.jpg', ImgCrop)
            ImgCropArr.tofile(FullFileName)

            i += 1

            NameCropImgs.append(NameImg)
            PolsImg.append(PolsCut)
            ClsNumsImg.append(ClsNums)

        return {'ImgNames': NameCropImgs, 'Pols': PolsImg, 'ClsNums': ClsNumsImg}

    # Функция нарезки всех картинок в json файле и генерация нового json-файла
    def CutAllImgs(self, SizeWind: int, ProcOverlapPol: [], ProcOverlapW: float, NameJsonFile: str):
        """
        1 - размер сканирующего окна;
        ProcOverlapPol - какой процент площади полигонов надо перекрыть окном, чтобы считать возможным
                зафиксировать позицию окна;
        ProcOverlapW - процент перекрытия окна для смежных кадров
            """
        # TODO: все сокращения дениса переправить: Wind - ветер; Proc - сокращение от процесс, обработка;
        JsonAllData = {}

        # Добавляем путь к файлам-картинкам
        JsonAllData['path_to_images'] = self.PathToImg

        # Перебор по всем картинкам в Json-файле
        JsonAllData['images'] = {}
        for i in range(len(self.JsonObj.ImgsName)):
            CutData = self.CutImg(i, SizeWind, ProcOverlapPol, ProcOverlapW)

            # Перебор по нарезанным картинкам одного исходного изображения
            for j in range(len(CutData['ImgNames'])):
                Dict = self.JsonObj.PolsToDict(i, CutData['Pols'][j], CutData['ClsNums'][j])
                JsonAllData['images'][CutData['ImgNames'][j]] = Dict.copy()

        # Записываем оконцовку json без изменений, к картинкам отношение не имеет
        JsonAllData['labels'] = self.JsonObj.DataDict['labels']
        JsonAllData['labels_color'] = self.JsonObj.DataDict['labels_color']

        # Перевод json в строку
        JsonAllDataStr = json.dumps(JsonAllData, ensure_ascii=False, sort_keys=False)

        # Запись строки в файл
        json_file = self.PathToImg + '/' + NameJsonFile
        with codecs.open(json_file, 'w', 'utf-8') as file:
            file.write(str(JsonAllDataStr))

        print("Нарезка завершена")
        return 0
