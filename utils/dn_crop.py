# Реализация Жукова Дениса, некоторые доработки: Az
from PyQt5 import QtCore
from shapely import Polygon, MultiPolygon, GeometryCollection, Point
import cv2 as cv
import numpy as np
import codecs
import copy
import json
import os

# Библиотечички для отладочки
# import matplotlib.pyplot as plt
# from PIL import Image

DEBUG = True  # активатор режима отладки


# ----------------------------------------------------------------------------------------------------------------------
class DNjson:
    """ Класс работы с исходными данными (результатами НС), записанными в формате json"""

    def __init__(self, FullNameJsonFile: str, init_mc_file=False):
        self.input_file_exists = os.path.exists(FullNameJsonFile)
        self.good_file = None  # флаг "порядка" файла SAMA JSON
        self.good_mc_file = None  # флаг "порядка" файла ручного кадрирования JSON_MC
        self.FullNameJsonFile = FullNameJsonFile

        # Параметры для ручного кадрирования (ручной нарезки), теперь перед процедурой выполняем
        # метод hand_cut_init, далее без изменений
        self.IsHandCutImgs = False
        self.FullNameMCJsonFile = None  # путь к файлу
        self.DataMCDict = None
        self.SizeWinMC = None
        self.WinPosPtMC = None
        self.PathToImgMC = None
        self.ImgsNameMC = None

        if self.input_file_exists:  # файл исходных данных есть
            # Получаем данные из файла в виде формата json
            self.DataDict = self.ReadDataJson()
            if self.DataDict:  # выполняем проверку
                # Читаем имена всех изображений, записанных в json
                self.ImgsName = self.ReadNamesImgs()

                self.PathToImg = self.DataDict["path_to_images"]

                # Формируем перечень имен классов (меток)
                self.labels = (self.DataDict['labels'])

                # Узнаем максимальный номер класса
                self.MaxClsNum = len(self.labels)  # print("Максимальный номер класса: ", self.MaxClsNum)

            # Если по умолчанию стоит проверка инициализации MC-файла:
            if init_mc_file:
                self.hand_cut_init()

    # Функции, использующиеся при инициализации класса
    def ReadDataJson(self):
        """ Функция чтения данных из файла Json"""
        file = open(self.FullNameJsonFile, "r")
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

    def ReadDataMCJson(self):
        # Читаем файл Json для ручной нарезки
        file = open(self.FullNameMCJsonFile, "r")
        # Читаем одну строчку, т.к. предполагается, что все данные в файле записаны в одну строчку
        data = file.readline()
        file.close()

        if self.check_mc_json(data):  # выполняем проверку
            self.good_mc_file = True
            # Переделываем строку в json словарь
            data_mc_dict = json.loads(data)
            return data_mc_dict
        else:
            self.good_mc_file = False
            return None

    def check_json(self, json_project_data):  # примитивная проверка на наличие нужных параметров
        for field in ["path_to_images", "images", "labels", "labels_color"]:
            if field not in json_project_data:
                return False
        return True

    def check_mc_json(self, json_mc_project_data):  # примитивная проверка на наличие нужных параметров
        for field in ["filename", "path_to_images", "scan_size", "images"]:
            if field not in json_mc_project_data:
                return False
        return True

    # Обновляем объект, проверяя есть ли данные для ручного кадрирования
    def hand_cut_init(self):
        PathToJsonFile = os.path.dirname(self.FullNameJsonFile)
        BaseNameJsonFile = os.path.splitext(os.path.basename(self.FullNameJsonFile))[0]
        NameMCJsonFile = BaseNameJsonFile + '.json_mc'
        # Проверяем, есть ли файл для ручной нарезки
        self.FullNameMCJsonFile = os.path.join(PathToJsonFile, NameMCJsonFile)
        self.IsHandCutImgs = os.path.exists(self.FullNameMCJsonFile)
        # Если есть файл для ручной нарезки
        if self.IsHandCutImgs:
            self.DataMCDict = self.ReadDataMCJson()
            if self.DataMCDict:
                # Читаем имена всех изображений в Json-файле для ручной разметки
                self.ImgsNameMC = [NameImg for NameImg in self.DataMCDict["images"].keys()]
                self.PathToImgMC = self.DataMCDict['path_to_images']

                # Читаем точки позиций окон
                self.WinPosPtMC = [self.DataMCDict['images'][NameImg] for NameImg in self.ImgsNameMC]
                self.SizeWinMC = self.DataMCDict['scan_size']

    @classmethod
    def ReadJsonKeys(cls, DataDict):
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

        # Создаем файл json
        # FullNameJsonFile=PathToJsonFile+'/'+NameJsonFile
        # with codecs.open(FullNameJsonFile,'w','utf-8') as file:
        #
        #     file.write(str(self.DataDict))
        #     file.write()

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


# Отладочная функция вывода контуров полигонов на изображение
# @classmethod
# def PrintPolys(cls,Polys:[],Img:Image):
#     RGBMAss=np.array(Img).astype("uint8")
#     for Poly in Polys:
#         for i in range(len(Poly)):
#             j = i + 1
#             if j == len(Poly): j = 0
#             p1 = [int(Poly[i][0]),int(Poly[i][1])]
#             p2 = [int(Poly[j][0]),int(Poly[j][1])]
#             cv.line(RGBMAss, p1, p2, (255, 255, 0), 5)
#     return RGBMAss


# ----------------------------------------------------------------------------------------------------------------------

class DNImgCut(QtCore.QObject):
    """ Класс работы с изображениями:
        PathToImg - каталог входной файла json
        NameJsonFile - наименования входного файла json
        init_mc_file - флаг инициализации данных для ручного кадрирования
        """
    signal_progress = QtCore.pyqtSignal(str)  # Az+: сигнал об изменении работы алгоритма

    def __init__(self, PathToJsonFile: str, NameJsonFile: str, init_mc_file=False):
        super().__init__()
        self.FullNamesImgsMCFile = None
        self.FullNamesImgsFile = None
        self.cut_images_count = 0  # счетчик нарезанных изображений, в случае ошибки возвращает None

        # Создаем объект json
        FullNameJsonFile = PathToJsonFile + '/' + NameJsonFile
        self.JsonObj = DNjson(FullNameJsonFile, init_mc_file)
        self.update_images_data()  # пробуем загрузить данные об изображениях

    def update_images_data(self):
        # Заполнение данных об изображениях в каталогах для *.json и *.json_mc
        if self.JsonObj.good_file:  # если файл подходит, заполняем
            self.FullNamesImgsFile = []
            for ImgName in self.JsonObj.ImgsName:
                self.FullNamesImgsFile.append(os.path.join(self.JsonObj.PathToImg, ImgName))
        else:  # иначе сообщаем о неприятности
            print("Исходный файл *.json не содержит требуемых данных")

        # Получение картинок для файла json_mc:
        if self.JsonObj.IsHandCutImgs:
            self.FullNamesImgsMCFile = []
            for ImgName in self.JsonObj.ImgsNameMC:
                self.FullNamesImgsMCFile.append(os.path.join(self.JsonObj.PathToImgMC, ImgName))
        else:
            print("Связанный файл *.json_mc не содержит требуемых данных")

    @classmethod
    def PolsIntersection(cls, Pol1, Pol2):
        """Ищет пересечение полигонов.
           Возвращает ТОЛЬКО список полигонов"""

        Res = []  # Конечный список полигонов
        AreaPol = []  # Площади пересечений
        IsAllObjPols = False
        if Pol1.intersects(Pol2):
            ResInter = Pol1.intersection(Pol2)
        else:
            ResInter = Polygon()

        if type(ResInter) == Polygon:
            IsAllObjPols = True
            # Оказывается бывают полигоны с нулевой площадью. Это пиздец
            if ResInter.area > 0.01:
                Res.append(ResInter)
                AreaPol.append(ResInter.area)
            else:
                Res.append(Polygon())
                AreaPol.append(0)

        elif type(ResInter) == MultiPolygon:
            IsAllObjPols = True
            for Pol in ResInter.geoms:
                if Pol.area > 0.01:
                    Res.append(Pol)
                    AreaPol.append(Pol.area)
                else:
                    Res.append(Polygon())
                    AreaPol.append(0)

        elif type(ResInter) == GeometryCollection:
            for Pol in ResInter.geoms:
                if type(Pol) == Polygon:
                    if Pol.area > 0.01:
                        Res.append(Pol)
                        AreaPol.append(Pol.area)
                    else:
                        Res.append(Polygon())
                        AreaPol.append(0)
        else:
            Res.append(Polygon())
            AreaPol.append(ResInter.area)
            if DEBUG:
                print("Пересечение полигонов не является полигоном, а каким-то другим геометрическим говном")

        SumArea = sum(AreaPol)
        AreaCrudePol = Pol2.area

        return {"PolsSHP": Res, "ValidTypes": IsAllObjPols, "AreaIntesPols": AreaPol,
                "SumArea": SumArea, "AreaCrudePol": AreaCrudePol}

    @classmethod
    def PolsDifference(cls, Pol1: Polygon, Pol2: Polygon):
        """Ищет вычитание полигонов,
           возвращает ТОЛЬКО список полигонов"""

        Res = []
        Area = []
        IsAllObjPols = False
        ResDiff = Pol1.difference(Pol2)

        if type(ResDiff) == Polygon:
            if ResDiff.area > 0.01:
                Res.append(ResDiff)
                Area.append(ResDiff.area)
            else:
                Res.append(Polygon())
                Area.append(Polygon().area)

            IsAllObjPols = True
        elif type(ResDiff) == MultiPolygon:
            IsAllObjPols = True
            for Pol in ResDiff.geoms:
                if Pol.area > 0.01:
                    Res.append(Pol)
                    Area.append(Pol.area)
                else:
                    Res.append(Polygon())
                    Area.append(Polygon().area)

        elif type(ResDiff) == GeometryCollection:
            for Pol in ResDiff.geoms:
                if type(Pol) == Polygon:
                    if Pol.area > 0.01:
                        Res.append(Pol)
                        Area.append(Pol.area)
                    else:
                        Res.append(Polygon())
                        Area.append(Polygon().area)

        else:
            Res.append(Polygon())
            Area.append(ResDiff.area)
            if DEBUG:
                print("Вычитание полигонов не является полигоном, а каким-то другим геометрическим говном")

        return {"PolsSHP": Res, "Area": Area, "ValidTypes": IsAllObjPols}

    @classmethod
    def PolsListIntersection(cls, Pol1: Polygon, PolsList: []):
        """Ищет пересечение окна со списком полигонов,
        возвращает список списков полигонов, длинной равной списку входных полигонов.
        Список списков нужен для варианта, когда один полигон пересекает другой в нескольких местах"""
        ResPol = []
        IsAllPoly = []
        SumArea = []
        PartArea = []
        for Pol2 in PolsList:
            A = cls.PolsIntersection(Pol1, Pol2)
            ResPol.append(A['PolsSHP'])
            if DEBUG:
                if len(A['PolsSHP']) == 0:
                    print("Это очень не хорошо, PolsIntersection возвращает пустоту")

            IsAllPoly.append(A['ValidTypes'])
            SumArea.append(A['SumArea'])
            if A['AreaCrudePol'] == 0:
                PartArea.append(0)
            else:
                PartArea.append(A['SumArea'] / A['AreaCrudePol'])

        return {"PolsSHP": ResPol, "ValidTypes": IsAllPoly, "SumArea": SumArea,
                "PartArea": PartArea}

    @classmethod
    def FinedMinAreaOVWinPos(cls, pnWinProb: [], pnOldWin: [], WW, HW):
        """Функция возвращает номера позиций окон с минимальным перекрытием со старыми окнами"""
        WsPolSHPOld = [cls.CreateWPolSHP(p, WW, HW) for p in pnOldWin]
        WsPolSHP = [cls.CreateWPolSHP(p, WW, HW) for p in pnWinProb]
        AreaMass = []
        for WPolSHP in WsPolSHP:
            AreaOVW = []
            for WPolSHPOld in WsPolSHPOld:
                if WPolSHP.intersects(WPolSHPOld):
                    AreaOVW.append(WPolSHP.intersection(WPolSHPOld).area)
                else:
                    AreaOVW.append(0)
            AreaMass.append(sum(AreaOVW))

        # Индексы позиций окон с минимальным перекрытием
        InxMinArea = [i for i, v in enumerate(AreaMass) if v == min(AreaMass)]
        return InxMinArea

    @classmethod
    def CreateWPolSHP(cls, pn: [], WW, HW):
        """Функция построения shp полигона из сканирующего окна"""
        xn = pn[0]
        yn = pn[1]
        xk = xn + WW
        yk = yn + HW
        Pol = [[xn, yn], [xk, yn], [xk, yk], [xn, yk]]
        PolSHP = Polygon(Pol)
        return PolSHP

    @classmethod
    def PointPolyPosWin(cls, WPShp: Polygon, PolsShp: []):

        # Выделяем точки полигонов, не принадлежащие окну
        PtsPols = []
        for Pol in PolsShp:
            PtsPols += list(Pol.exterior.coords)
        PtsPolsOutW = [Pt for Pt in PtsPols if not WPShp.contains(Point(Pt))]
        xp = np.array(PtsPolsOutW)[:, 0]
        yp = np.array(PtsPolsOutW)[:, 1]

        # Узнаем габариты окна
        PtsWin = list(WPShp.exterior.coords)
        x = np.array(PtsWin)[:, 0]
        y = np.array(PtsWin)[:, 1]
        xMinW = min(x)
        xMaxW = max(x)
        yMinW = min(y)
        yMaxW = max(y)

        if min(xp) <= xMinW and max(xp) >= xMaxW:
            return False

        elif min(yp) <= yMinW and max(yp) >= yMaxW:
            return False

        return True

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
        pn = [int(pn[0]), int(pn[1])]
        dx = WW - int(WW * ProcOverlapW)
        dy = HW - int(HW * ProcOverlapW)

        pk = pn.copy()
        pnList = []  # Список удовлетворительных значений сканирующего окна
        while 1:
            # Генерируем из окна SHP полигон
            WPolSHP = cls.CreateWPolSHP(pk, WW, HW)

            # Проверяем полигоны на пересечение с окном сканирования
            Pols = cls.FindPolyOverload(WPolSHP, PolsSHP, ProcOverlapPol, NumClsPols)

            # Если найдены пересекающиеся полигоны
            if not Pols == None:
                # Запоминаем позицию окна
                pnList.append(pk.copy())

            # Если сканирующее окно при смещении на dx,dy перейдет за край изображения, корректируем dx,dy
            if pk[0] + dx + WW > WImg:
                dx = int(WImg - WW - pk[0])
            if pk[1] + dy + HW > HImg:
                dy = int(HImg - HW - pk[1])

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
                dx = WW - int(WW * ProcOverlapW)

    @classmethod
    def GetPosWindShp2(cls, WW: int, HW: int, WImg: int, HImg: int, ProcOverlapPol: [], D: int, ProcOverlapW: float,
                       PolsSHP: [], NumClsPols: []):
        """Интеллектуальная функция перемещения сканирующего окна по картинке. Разбиваем полигоны на кластеры согласно
        положению их центров масс (по территориальному признаку)
            eps - минимальное расстояние между центрами масс полигонов, чтобы их можно было отнести в один кластер
            считаем, что если центры масс укладываются в размеры сканирующего окна, то это - один кластер """

        # Копируем массив полигонов, чтобы с исходным ни дай бог ничего не случилось
        PolsSHPCop = copy.copy(PolsSHP)
        NumClsPolsCop = copy.copy(NumClsPols)

        pnList = []  # Список удовлетворительных значений сканирующего окна

        # Открываем цикл, который повторяется до тех пор пока все полигоны не будут учтены
        Count = 0
        while 1:
            # Если полигонов не осталось, выходим из цикла
            if len(PolsSHPCop) == 0:
                break
            # Переводим SHP полигоны в обычные
            PolsPt = [np.array(PolSHP.exterior.coords, float) for PolSHP in PolsSHPCop]

            # Определяем размеры всех полигонов
            PolsPtMinMax = {'MinX': [], 'MaxX': [], 'MinY': [], 'MaxY': []}  # Координаты рамки каждого полигона

            # Разделяем весь список полигонов на те, которые целиком умещаются в окно, и те, которые в окно не умещаются
            IndxPolW = []  # Индексы полигонов, которые полностью помещаются в окно
            IndxPolBig = []  # Индексы полигонов, которые в окно не помещаются
            for i in range(len(PolsPt)):
                x = np.array(PolsPt[i])[:, 0]
                y = np.array(PolsPt[i])[:, 1]
                xMin = min(x)
                xMax = max(x)
                yMin = min(y)
                yMax = max(y)

                PolsPtMinMax['MinX'].append(xMin)
                PolsPtMinMax['MaxX'].append(xMax)
                PolsPtMinMax['MinY'].append(yMin)
                PolsPtMinMax['MaxY'].append(yMax)

                WPol = xMax - xMin
                HPol = yMax - yMin

                if WPol < WW - 2 * D and HPol < HW - 2 * D:
                    IndxPolW.append(i)
                else:
                    IndxPolBig.append(i)

            # Определяем зону пробегания окна
            xMin = min(PolsPtMinMax['MinX'])
            xMax = max(PolsPtMinMax['MaxX'])
            yMin = min(PolsPtMinMax['MinY'])
            yMax = max(PolsPtMinMax['MaxY'])

            # Расширяем зону кластера таким образом, чтобы было как можно меньше пересечений одинаковых объектов
            xMinD = xMin - WW + D
            if xMinD < 0: xMinD = 0

            xMaxD = xMax + WW - D
            if xMaxD > WImg: xMaxD = WImg

            yMinD = yMin - HW + D
            if yMinD < 0: yMinD = 0

            yMaxD = yMax + HW - D
            if yMaxD > HImg: yMaxD = HImg

            WZone = xMaxD - xMinD
            HZone = yMaxD - yMinD

            # Вычисляем шаг перемещения окна и количество шагов с учетом заданного интервала
            dx = WW - int(WW * ProcOverlapW)
            dy = HW - int(HW * ProcOverlapW)

            IterX = int((WZone) / dx)
            IterY = int((HZone) / dy)

            if (WZone - dx) % dx > 0: IterX += 1
            if (HZone - dy) % dy > 0: IterY += 1

            # Перемещаем окно в пределах рабочей зоны с заданным интервалом
            WPosProp = {'pn': [], 'PolsObj': []}

            for iy in range(IterY):
                for ix in range(IterX):

                    # Расчитываем позицию сканирующего окна
                    pnX = xMinD + ix * dx
                    pnY = yMinD + iy * dy
                    if pnX + WW > xMaxD: pnX = xMaxD - WW
                    if pnY + HW > yMaxD: pnY = yMaxD - HW
                    if pnX < 0: pnX = 0
                    if pnY < 0: pnY = 0

                    # Генерируем из окна SHP полигон
                    WPolSHP = cls.CreateWPolSHP([pnX, pnY], WW, HW)

                    # Проверяем полигоны на пересечение с окном сканирования
                    PolsOV = cls.FindPolyOverload(WPolSHP, PolsSHPCop, ProcOverlapPol, NumClsPols)

                    # Ставим соответствие положение сканирующего окна и пересекающихся полигонов
                    # только для непустых окон
                    if not PolsOV == None:
                        WPosProp['pn'].append([int(pnX), int(pnY)])
                        WPosProp['PolsObj'].append(PolsOV)

            # Если по пробеганию окна по всей зоне кластера не нашлось ни одного полигона, то выходим из цикла
            if len(WPosProp['pn']) == 0:
                break

            # Выбираем оптимальную позицию
            IndxOV = [WPosProp['PolsObj'][i]['IndxGood'] for i in range(len(WPosProp['pn']))]
            IndxOun = [WPosProp['PolsObj'][i]['IndxOun'] for i in range(len(WPosProp['pn']))]
            IndxBad = [WPosProp['PolsObj'][i]['IndxBad'] for i in range(len(WPosProp['pn']))]

            # 1. Узнаем позиции окна, где все полигоны попадают полностью
            IndxWPosPOun = [i for i in range(len(WPosProp['pn'])) if len(IndxBad[i]) == 0 and len(IndxOV[i]) == 0
                            and not len(IndxOun) == 0]

            # 2. Узнаем позиции окна, где нет полигонов, которые плохо нарезались (с маленькими остатками от нарезания)
            IndxWPosPNoBad = [i for i in range(len(WPosProp['pn'])) if len(IndxBad[i]) == 0 and not len(IndxOV[i]) == 0]

            # 3. Узнаем позиции окна, где есть и плохо нарезаные полигоны
            IndxWPosPBad = [i for i in range(len(WPosProp['pn'])) if not len(IndxBad[i]) == 0]

            IndxWPosRes = -1  # Результирующий индекс выгодного положения окна

            # 1. Если найдены позиции окна, где все полигоны попадают полностью
            if not len(IndxWPosPOun) == 0:
                # 1.1 Узнаем позицию окна с максимальным количеством таких полигонов
                NumbOunPol = [len(IndxOun[i]) for i in IndxWPosPOun]
                IndxMaxNumbPol = [i for i, v in enumerate(NumbOunPol) if v == max(NumbOunPol)]
                IndxWOun = [IndxWPosPOun[i] for i in IndxMaxNumbPol]

                # 1.2 Из отобранных позиций, выбираем такие, которые имеют минимальную площадь пересечения со старыми окнами
                if not len(pnList) == 0:
                    pnWinList = [WPosProp['pn'][i] for i in range(len(WPosProp['pn'])) if i in IndxWOun]
                    Indx = cls.FinedMinAreaOVWinPos(pnWinList, pnList, WW, HW)
                    IndxWOun = [IndxWOun[i] for i in Indx]

                # 1.3 Выбираем такую позицию окна, где большинство полигонов расположены ближе к центру окна
                DMass = []
                for i in IndxWOun:
                    WPolSHP = cls.CreateWPolSHP(WPosProp['pn'][i], WW, HW)
                    pWc = WPolSHP.centroid
                    psPolsc = [Pol.centroid for Pol in WPosProp['PolsObj'][i]['Polys']]
                    Dist = [pWc.distance(pP) for pP in psPolsc]
                    DMean = np.mean(Dist)
                    DMass.append(DMean)

                IndxRes = DMass.index(min(DMass))
                IndxWPosRes = IndxWOun[IndxRes]

            # 2. Если при любой позиции окна полигоны режутся, но нет плохо нарезаных полигонов
            elif len(IndxWPosPOun) == 0 and not len(IndxWPosPNoBad) == 0:
                # 2.1 Выбираем позицию окна, где точки полигонов лежат по одну сторону от окна
                # (полигоны не должны пересекать противоположные стороны окна)
                IndxWPos = IndxWPosPNoBad.copy()
                ValidPos = []
                for i in IndxWPos:
                    WPolSHP = cls.CreateWPolSHP(WPosProp['pn'][i], WW, HW)
                    ValidPos.append(cls.PointPolyPosWin(WPolSHP, WPosProp['PolsObj'][i]['Polys']))

                IndxWPos = [IndxWPos[i] for i, v in enumerate(IndxWPos) if ValidPos[i]]
                if len(IndxWPos) == 0: IndxWPos = IndxWPosPNoBad.copy()

                # 2.2 Узнаем позицию окна с максимальным количеством целых полигонов
                NumbOunPol = [len(IndxOun[i]) for i in IndxWPos]
                IndxMaxNumbPol = [i for i, v in enumerate(NumbOunPol) if v == max(NumbOunPol)]
                IndxWPos = [IndxWPos[i] for i in IndxMaxNumbPol]

                # 2.3 Из отобранных позиций, выбираем такие,
                # которые имеют минимальную площадь пересечения со старыми окнами
                if not len(pnList) == 0:
                    pnWinList = [WPosProp['pn'][i] for i in range(len(WPosProp['pn'])) if i in IndxWPos]
                    Indx = cls.FinedMinAreaOVWinPos(pnWinList, pnList, WW, HW)
                    IndxWPos = [IndxWPos[i] for i in Indx]

                # 2.4 Выбираем позицию окна, где в среднем захватывается обльшая часть площадей полигонов
                # (больше всего целыхполигонов без учета размера самих полигонов)
                PartAreaMean = []
                for i in IndxWPos:
                    PartAreaMean.append(np.mean(WPosProp['PolsObj'][i]['PartArea']))

                # Здесь можно еще доделать проверку на максимальную площадь полигонов попадающих в окно

                IndxRes = PartAreaMean.index(max(PartAreaMean))
                IndxWPosRes = IndxWPos[IndxRes]

            # 3. Если при любой позиции окна полигоны режутся так, что есть плохо нарезаные полигоны
            elif len(IndxWPosPOun) == 0 and len(IndxWPosPNoBad) == 0 and not len(IndxWPosPBad) == 0:
                IndxWPos = IndxWPosPBad.copy()
                # 3.1 Узнаем позиции окон с максимальным количеством хорошо нарезанных полигонов
                NumbNoBadPol = [len(IndxOV[i]) + len(IndxOun[i]) for i in IndxWPos]
                IndxMaxNumbGoodPol = [i for i, v in enumerate(NumbNoBadPol) if v == min(NumbNoBadPol)]
                IndxWPos = [IndxWPos[i] for i in IndxMaxNumbGoodPol]

                # 3.1 Узнаем позицию окна с минимальным количеством плохо нарезанных полигонов
                NumbBadPol = [len(IndxBad[i]) for i in IndxWPos]
                IndxMinNumbBadPol = [i for i, v in enumerate(NumbBadPol) if v == min(NumbBadPol)]
                IndxWPos = [IndxWPos[i] for i in IndxMinNumbBadPol]

                # 3.2 Выбираем позицию окна со значимыми значениями площадей (так, чтобы пересечение с окном давали результыты)
                AreasList = [WPosProp['PolsObj'][i]['AreaOV'] for i in range(len(WPosProp['pn'])) if i in IndxWPos]
                NumbIndx = []
                for i in range(len(AreasList)):
                    NumbIndx.append(len([j for j, v in enumerate(AreasList[i]) if v > 0.1]))

                if DEBUG:
                    if max(NumbIndx) == 0:
                        print("Произошла поебень. Нет окон в которых полигоны бы нормально резались,"
                              "т.е. пересечение полигонов с окном были бы значимыми")

                Indx = [i for i, v in enumerate(NumbIndx) if v > 0]
                if not len(Indx) == 0:
                    IndxWPos = [IndxWPos[i] for i in Indx]

                # 3.3 Выбираем позицию окна с минимальным перекрытием с другими окнами
                if not len(pnList) == 0:
                    pnWinList = [WPosProp['pn'][i] for i in range(len(WPosProp['pn'])) if i in IndxWPos]
                    Indx = cls.FinedMinAreaOVWinPos(pnWinList, pnList, WW, HW)
                    IndxWPos = [IndxWPos[i] for i in Indx]

                # Выбираем позицию окна, где в среднем захватывается обльшая часть полигонов
                PartAreaMean = []
                for i in IndxWPos:
                    PartAreaMean.append(np.mean(WPosProp['PolsObj'][i]['PartArea']))

                IndxRes = PartAreaMean.index(max(PartAreaMean))
                IndxWPosRes = IndxWPos[IndxRes]

                if DEBUG:
                    print("Следует уменьшить шаг смещения окна, есть полигоны, которые плохо режутся")

            if DEBUG:
                if IndxWPosRes == -1:
                    print("Произошла поебень. Не найдена оптимальная позиция окна при существовании полигонов")
            if IndxWPosRes >= 0:
                pnList.append(WPosProp['pn'][IndxWPosRes])
            # Режем полигоны, попадающие в окно
            # Ищим пересечение полигонов с окном
            WPolSHP = cls.CreateWPolSHP(pnList[-1], WW, HW)
            if DEBUG:
                IndxPolEmpty = [i for i, v in enumerate(PolsSHPCop) if v.is_empty]
                if not len(IndxPolEmpty) == 0:
                    print("Произошла поебень, пустой полигон в списке полигонов")

            PolsListW = cls.PolsListIntersection(WPolSHP, PolsSHPCop)

            # Ищем индексы полигонов с непустым пересечением
            IndxPolsOW = [i for i, v in enumerate(PolsListW["PolsSHP"]) if not v[0].is_empty]

            if DEBUG:
                if len(IndxPolsOW) == 0:
                    print("Произошла поебень, не может IndxPolsOW быть пустым")
                    return pnList

            # Для каждого индекса вычитаем часть полигона, находящегося в окне
            NumClsApp = []
            PolApp = []
            for i in IndxPolsOW:
                # Вычитаем из из полигона окно
                PolListDif = cls.PolsDifference(PolsSHPCop[i], WPolSHP)['PolsSHP']

                # Добавляем данные вычитания
                for Pol in PolListDif:
                    if not Pol.is_empty:
                        NumClsApp.append(NumClsPolsCop[i])
                        PolApp.append(Pol)

            # Удаляем старые данные
            PolsSHPCop = [v for i, v in enumerate(PolsSHPCop) if not i in IndxPolsOW]
            NumClsPolsCop = [v for i, v in enumerate(NumClsPolsCop) if not i in IndxPolsOW]

            # Добавляем в конец новые
            if not len(PolApp) == 0:
                PolsSHPCop += PolApp
                NumClsPolsCop += NumClsApp

            Count += 1

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
            Indx_OV = [j[0] for j in Indx]

            # Получаем площади полигонов
            AreaP = [P_OV[j].area for j in range(len(P_OV))]

            # Получаем площади пересечения полигонов с окном
            AreaOV = [WPolSHP.intersection(P_OV[j]).area for j in range(len(P_OV))]

            # Процент площади пересечения

            if DEBUG:
                IndxDeb = [i for i, v in enumerate(AreaP) if v < 0.0001]
                if not len(IndxDeb) == 0:
                    print(
                        "Произошла поебень, в списке исходных полигонов есть полигоны с нулевой площадью. Такого быть не должно")

            ProcAreaOverlap = np.array(AreaOV) / np.array(AreaP)

            # Проветяем удовлетворение условию площади пересечения сканирующей рамки с полигонами для разных классов
            PolSHP = []
            ClsNumsPol = []
            PartArea = []

            GoodIndxOV = []
            GoodIndxOunOV = []
            BadIndxOV = []
            for i in range(len(P_OV)):
                ClsNum = Cls_OV[i]
                PolSHP.append(P_OV[i])
                ClsNumsPol.append(ClsNum)
                PartArea.append(ProcAreaOverlap[i])

                # В хорошие индексы полигонов записываем те, площадь которых:
                # 1. В сканирующем окне больше пороговой
                # 2. За пределами сканирующего окна больше пороговой
                if ProcAreaOverlap[i] >= ProcOverlapPols[ClsNum] and \
                        ProcAreaOverlap[i] < 1 - ProcOverlapPols[ClsNum]:
                    GoodIndxOV.append(Indx_OV[i])

                # Если полигон целиком попадает в сканирующее окно (записываем отдельным индексом)
                elif ProcAreaOverlap[i] > 0.999:
                    GoodIndxOunOV.append(Indx_OV[i])

                else:
                    BadIndxOV.append(Indx_OV[i])

            return {'ClsNums': ClsNumsPol, 'Polys': PolSHP, 'AreaOV': AreaOV, 'PartArea': PartArea,
                    'IndxGood': GoodIndxOV, 'IndxOun': GoodIndxOunOV, 'IndxBad': BadIndxOV}

    def CutImg(self, NumImg: int, SizeWind: int, ProcOverlapPol: [], ProcOverlapW: float, output_image_dir: str,
               DKray: int,
               IsSmartCut: bool):
        """Функция нарезки картинки
        ProcOverlapPol - пороговое значение части площади пересечения полигона со сканирующим окном
        с которого считается, что полигон попадает в окно"""
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

        # AZ
        if IsSmartCut:
            WPos = DNImgCut.GetPosWindShp2(WW, HW, W, H, ProcOverlapPol, DKray, ProcOverlapW, PolsSHP, Pols['ClsNums'])
        else:
            WPos = DNImgCut.GetPosWindShp(pWind, WW, HW, WObl, HObl, ProcOverlapPol, ProcOverlapW, PolsSHP,
                                          Pols['ClsNums'])

        # if DEBUG:
        #     Count=0
        #     ContWind = []
        #     ContWind+=Pols['Polys']
        #     for Pos in WPos:
        #         ContWind.append(np.array(self.CreateWPolSHP(Pos, WW, HW).exterior.coords, int))
        #
        #
        #         Prob=self.JsonObj.PrintPolys(ContWind,Img)
        #         plt.imshow(Prob)
        #         plt.show()

        # Для каждой позиции сканирующего окна режем полигоны, площадь пересечения которых больше порогового значения
        i = 0  # счетчик имён нарезанных картинок (в пределах обрабатываемого исходного снимка)
        NameCropImgs = []
        PolsImg = []
        ClsNumsImg = []
        IndxNoCutPol = []  # Индексы полигонов, которые не были разрезаны (нужно для статистики)
        for pW in WPos:
            # Строим SHP полигон из сканирующего окна
            WPolSHP = DNImgCut.CreateWPolSHP(pW, WW, HW)

            # Находим валидные полигоны
            PolsOvSHP = DNImgCut.FindPolyOverload(WPolSHP, PolsSHP, ProcOverlapPol, Pols['ClsNums'])
            if not PolsOvSHP == None:
                IndxNoCutPol += PolsOvSHP['IndxGood']

            # Режем каждый полигон по границе сканирующего окна
            ListPolsCutSHP = self.PolsListIntersection(WPolSHP, PolsOvSHP['Polys'])
            PolsCut = []
            ClsNums = []

            for j in range(len(ListPolsCutSHP['PolsSHP'])):
                for PolSHP in ListPolsCutSHP['PolsSHP'][j]:
                    if not PolSHP.is_empty:
                        ClsNums.append(PolsOvSHP['ClsNums'][j])
                        PolsCut.append(np.array(PolSHP.exterior.coords, float))

            PolsCut = self.JsonObj.CoordGlobToLocal(PolsCut, pW)

            # Режем изображение согласно координатам сканирующего окна
            ImgCrop = Img[pW[1]:pW[1] + HW, pW[0]:pW[0] + WW]

            # Генерим имя сохраняемого изображения
            NameImg = os.path.splitext(os.path.basename(path))[0]
            NameImg += "_{:0>3}.jpg".format(i)
            i += 1  # увеличиваем счетчик
            FullFileName = os.path.join(output_image_dir, NameImg)
            # Записываем картинки
            success, ImgCropArr = cv.imencode('.jpg', ImgCrop)
            ImgCropArr.tofile(FullFileName)
            if success:
                self.cut_images_count += 1

            NameCropImgs.append(NameImg)
            PolsImg.append(PolsCut)
            ClsNumsImg.append(ClsNums)

        # Для статистики и статьи
        PolsPt = [np.array(PolSHP.exterior.coords, float) for PolSHP in PolsSHP]
        NumbSmollPol = 0
        for PolPt in PolsPt:
            x = np.array(PolPt)[:, 0]
            y = np.array(PolPt)[:, 1]
            xMin = min(x)
            xMax = max(x)
            yMin = min(y)
            yMax = max(y)

            WPol = xMax - xMin
            HPol = yMax - yMin

            if WPol < WW and HPol < HW:
                NumbSmollPol += 1

        # if DEBUG:
        #     print("\nКоличество картинок:", len(WPos))
        #     print("Доля нерезанных полигонов:", len(np.unique(IndxNoCutPol)) / NumbSmollPol)

        return {'ImgNames': NameCropImgs, 'Pols': PolsImg, 'ClsNums': ClsNumsImg}

    # Функция нарезки всех картинок в json файле и генерация нового json-файла
    def CutAllImgs(self, SizeWind: int, ProcOverlapPol: [], ProcOverlapW: float,
                   NameJsonFile: str, DKray: int, IsSmartCut: bool, IsHandCut: bool):
        """Функция нарезки изображений, записанных в json (проверка на наличие изображений отсутствует)
        SizeWind - размер сканирующего окна,
        ProcOverlapPol - пороговое значение процента площади перекрытия полигона окном,
        при котором часть полигона записывается на вырезанное изображение
        ProcOverlapW - шаг сканирующего окна в процентаже площади перекрытия
        NameJsonFile - полное имя (без разширения) записываемого json-файла
        DKray:int - минимальное расстояние от края сканирующего окна до полигона (чтоб не впритычечку), в пикселях
        IsSmartCut - выбор между хитрожопой функцией нарезки и тупой
        IsHandCut - выбор между ручной нарезкой и автоматической"""

        # Если нарезка в автоматическом режиме
        if not IsHandCut:
            JsonAllData = {}
            # Добавляем путь к файлам-картинкам
            JsonAllData['path_to_images'] = os.path.dirname(NameJsonFile)
            if not os.path.isdir(JsonAllData['path_to_images']):
                os.mkdir(JsonAllData['path_to_images'])

            # Перебор по всем картинкам в Json-файле
            JsonAllData['images'] = {}

            # Az+: функция для расчета статистики и ориентировочного времени работы
            overall_size, images_count = az_calc_stats(self.JsonObj.PathToImg, self.JsonObj.ImgsName)
            sum_size = 0  # прогресс по объему (весу файлов)

            for i in range(len(self.JsonObj.ImgsName)):
                # Az: пропускаем несуществующие файлы
                if not os.path.exists(os.path.join(self.JsonObj.PathToImg, self.JsonObj.ImgsName[i])):
                    print(f"[!] error: no file {os.path.join(self.JsonObj.PathToImg, self.JsonObj.ImgsName[i])}")
                    continue
                # if i < 139:  # Закончил на 421.
                #     continue
                bad_files = ["447_USA_2011-10.jpg", "447_USA_2016-05.jpg", "447_USA_2017-07.jpg", "447_USA_2018-08.jpg",
                             "447_USA_2019-02.jpg", "447_USA_2020-08.jpg", "447_USA_2020-10.jpg", "447_USA_2021-09.jpg",
                             "447_USA_2021-11.jpg", "447_USA_2022-09.jpg", "126_FRA_2016-03.jpg", "126_FRA_2018-03.jpg",
                             "129c_FRA_2016-08.jpg"]
                # bad_files = ["128_FRA_2014-06-13.jpg", "128_FRA_2017-06.jpg", "128_FRA_2018-06.jpg",
                #              "189_IRL_2006-06.jpg", "421_USA_2018-01.jpg", "446s_USA_2012-11-06.jpg"
                #              "446s_USA_2014-10.jpg", "446s_USA_2016-04.jpg", "446s_USA_2018-05.jpg",
                #              "446s_USA_2019-06.jpg", "446s_USA_2020-10.jpg", "446s_USA_2022-04.jpg",
                #              "446s_USA_2022-06.jpg"]
                if self.JsonObj.ImgsName[i] in bad_files:
                    continue

                # Az+: немного статистики, для понимания процесса
                sum_size += az_calc_size(os.path.join(self.JsonObj.PathToImg, self.JsonObj.ImgsName[i]))
                stats = (f"{(i + 1)} из {images_count}: ~{(i + 1) * 100 / images_count:.2f}%; объем: "
                         f"~{sum_size * 100 / overall_size:.2f}% (всего: {overall_size:.0f} Mb), "
                         f"обрабатываю: {self.JsonObj.ImgsName[i]}")
                self.signal_progress.emit(stats)

                if DEBUG:
                    print(stats)
                CutData = self.CutImg(i, SizeWind, ProcOverlapPol, ProcOverlapW,
                                      os.path.dirname(NameJsonFile), DKray, IsSmartCut)

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
            with codecs.open(NameJsonFile, 'w', 'utf-8') as file:
                file.write(str(JsonAllDataStr))

        # Если есть файл для ручной нарезки
        elif self.JsonObj.IsHandCutImgs:
            JsonAllData = {}
            # Формируем путь для записи файлов
            JsonAllData['path_to_images'] = os.path.join(os.path.dirname(NameJsonFile), 'MCImgs')
            print(NameJsonFile)
            NameOutputMCJsonFile = os.path.splitext(os.path.basename(NameJsonFile))[0] + "_mc"  # Az: выход - файл json
            NameOutputMCJsonFile = NameOutputMCJsonFile + '.json'  # "mc" должна относится к имени файла, не расширения!

            # Если нет каталога для хранения нарезанных картинок
            if not os.path.isdir(JsonAllData['path_to_images']):
                os.mkdir(JsonAllData['path_to_images'])

            JsonAllData['images'] = {}
            # Перебор по всем картинкам для ручной нарезки
            for i in range(len(self.JsonObj.ImgsNameMC)):
                if not self.JsonObj.WinPosPtMC[i] == None:
                    CutData = self.CutImgHand(self.JsonObj.SizeWinMC, i, self.JsonObj.WinPosPtMC[i],
                                              JsonAllData['path_to_images'])

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
            NameJsonMCFile = os.path.join(JsonAllData['path_to_images'], NameOutputMCJsonFile)
            with codecs.open(NameJsonMCFile, 'w', 'utf-8') as file:
                file.write(str(JsonAllDataStr))

        if DEBUG:
            print("Нарезка завершена")
        return self.cut_images_count

    def CutImgHand(self, SizeWind: int, NumImg: int, PtC: [], output_image_dir: str):
        """Функция нарезки изображений в ручном режиме"""
        # Читаем все полигоны с картинки
        Pols = self.JsonObj.ReadPolygons(NumImg)

        # Преобразуем полигоны в SHP
        PolsSHP = DNjson.PolysToShp(Pols['Polys'])

        # Читаем картинку (обходим проблему русских букв в названиях каталогов для open cv)
        path = self.FullNamesImgsMCFile[NumImg]
        Img = open(path, 'rb')
        data = Img.read()
        data_arr = np.frombuffer(data, dtype=np.uint8)
        Img = cv.imdecode(data_arr, cv.IMREAD_COLOR)

        # Определяем размеры картинки
        H = Img.shape[0]
        W = Img.shape[1]

        # Определяем позиции окна исходя из координат центральных точек
        dW = int(SizeWind / 2)
        dH = int(SizeWind / 2)
        WW = SizeWind
        HW = SizeWind

        WPos = []
        for Pt in PtC:
            xn = int(Pt[0] - dW)
            yn = int(Pt[1] - dH)

            if xn < 0: xn = 0
            if xn + SizeWind > W: xn = W - SizeWind

            if yn < 0: yn = 0
            if yn + SizeWind > H: yn = H - SizeWind

            WPos.append([xn, yn])

        # Режем изображение
        NameCropImgs = []
        PolsImg = []
        ClsNumsImg = []
        i = 0  # Счетчик изображений
        for pW in WPos:
            # Строим SHP полигон из сканирующего окна
            WPolSHP = DNImgCut.CreateWPolSHP(pW, WW, HW)

            # Находим валидные полигоны
            ClsNumsMax = max(Pols['ClsNums'])
            ProcOverlapPol = [0] * (ClsNumsMax + 1)
            PolsOvSHP = DNImgCut.FindPolyOverload(WPolSHP, PolsSHP, ProcOverlapPol, Pols['ClsNums'])
            if DEBUG:
                if PolsOvSHP == None:
                    print("Произошла ебань. При нарезке изображения в ручном режиме,"
                          "есть картинки, которые не включают в себя полигонов")

            if not PolsOvSHP == None:
                # Режем каждый полигон по границе сканирующего окна
                ListPolsCutSHP = self.PolsListIntersection(WPolSHP, PolsOvSHP['Polys'])
                PolsCut = []
                ClsNums = []

                for j in range(len(ListPolsCutSHP['PolsSHP'])):
                    for PolSHP in ListPolsCutSHP['PolsSHP'][j]:
                        if not PolSHP.is_empty:
                            ClsNums.append(PolsOvSHP['ClsNums'][j])
                            PolsCut.append(np.array(PolSHP.exterior.coords, float))

                PolsCut = self.JsonObj.CoordGlobToLocal(PolsCut, pW)

                # Режем изображение согласно координатам сканирующего окна
                ImgCrop = Img[pW[1]:pW[1] + HW, pW[0]:pW[0] + WW]

                # Генерим имя сохраняемого изображения
                NameImg = os.path.splitext(os.path.basename(path))[0]
                NameImg += "_mc_{:0>3}.jpg".format(i)  # Az: Денис, такая запись проще и быстрее
                i += 1  # увеличиваем счетчик
                FullFileName = os.path.join(output_image_dir, NameImg)
                # Записываем картинки
                success, ImgCropArr = cv.imencode('.jpg', ImgCrop)
                ImgCropArr.tofile(FullFileName)
                if success:
                    self.cut_images_count += 1

                NameCropImgs.append(NameImg)
                PolsImg.append(PolsCut)
                ClsNumsImg.append(ClsNums)

        return {'ImgNames': NameCropImgs, 'Pols': PolsImg, 'ClsNums': ClsNumsImg}


def az_calc_stats(path_to_dir, images):
    """Az: Расчет статистики обрабатываемых данных и ориентировочного времени работы"""
    count = 0  # количество реальных файлов
    summ_size = 0  # их суммарный размер в Mb
    for image in images:
        if not os.path.exists(os.path.join(path_to_dir, image)):
            continue  # переходим к следующему, т.к. этого файла не существует
        summ_size += az_calc_size(os.path.join(path_to_dir, image))  # получаем сумму...
        count += 1  # ...и реальное количество объектов
    return summ_size, count


def az_calc_size(file, degree=2):
    """Az: Расчет размера файла и перевод его в нужную размерность. degree: 1 - Килобайты; 2 - Мб; 3 - Гб и т.д."""
    size = os.path.getsize(file) / (1024 ** degree)
    return size
