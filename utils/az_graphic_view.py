from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import config
from enum import Enum
from shapely import Polygon

the_color = config.UI_COLORS.get("line_color")
the_color_crop = config.UI_COLORS.get("crop_color")


# Реализация Романа Хабарова

# ----------------------------------------------------------------------------------------------------------------------
class ViewState(Enum):
    """
    Общее состояние поля View
    """
    normal = 1  # ожидаем клик по полигону
    draw = 2  # в процессе отрисовки
    rubber_band = 3  # выделение области изображения
    ruler = 4  # рулетка
    drag = 5  # перемещение полигона
    vertex_move = 6  # перемещение вершины полигона
    hand_move = 7  # перемещение области изображения "рукой"
    hide_polygons = 8  # скрываем полигоны
    point_add = 9  # добавляем центр-точку ручного кадрирования (РК)
    point_move = 10  # перемещаем центр-точку РК
    point_delete = 11  # удаляем центр-точку РК


# ----------------------------------------------------------------------------------------------------------------------
class DragState(Enum):
    """
    Вариант состояния ViewState.drag поля View
    """
    no = 0
    start = 1
    in_process = 2
    end = 3


# ----------------------------------------------------------------------------------------------------------------------
class AzPointWithRect(QtWidgets.QGraphicsRectItem):
    """
    Класс для хранения точки-центра с рамкой вокруг по значению Crop-size'а
    Принимает точку (QPointF) и величину кадрирования (int)
    """

    def __init__(self, point: QtCore.QPointF, color: QtGui.QColor, crop_size: int = 1280):
        super().__init__()
        self.point = point  # сохраняем значение центральной точки
        self.color = color
        self.crop_size = crop_size  # значение величины кадрирования, например 1280, или 256

        self.line = QtWidgets.QGraphicsLineItem(self)  # диагональная линия
        self.line.setLine(draw_line(point, crop_size, True))
        self.line.setPen(QtGui.QPen(color, 1, QtCore.Qt.PenStyle.SolidLine))

        self.line2 = QtWidgets.QGraphicsLineItem(self)  # диагональная линия 2
        self.line2.setLine(draw_line(point, crop_size, False))
        self.line2.setPen(QtGui.QPen(color, 1, QtCore.Qt.PenStyle.SolidLine))

        rect = QtCore.QRectF(point.x() - crop_size / 2, point.y() - crop_size / 2, crop_size, crop_size)
        self.setRect(rect)
        self.setPen(QtGui.QPen(color, 2, QtCore.Qt.PenStyle.SolidLine))
        self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def repaint_border(self, new_crop_size):
        if self.crop_size == new_crop_size:
            return
        else:
            self.crop_size = new_crop_size
            rect = QtCore.QRectF(self.point.x() - new_crop_size / 2, self.point.y() - new_crop_size / 2,
                                 new_crop_size, new_crop_size)
            self.setRect(rect)
            self.setPen(QtGui.QPen(self.color, 2, QtCore.Qt.PenStyle.SolidLine))

    def apply_offset(self, offset_x, offset_y):  # смещение центральной точки на дельту (может быть и отрицательной)
        self.point.setX(self.point.x() + offset_x)
        self.point.setY(self.point.y() + offset_y)


def draw_line(point, crop_size, left_one=True):
    # рисование внутренних перекрестных линий; left_one = True: 7 -> 3; left_one = False: 1 -> 9
    x = point.x()
    y = point.y()
    if left_one:
        left_line = QtCore.QLineF()
        left_line.setLine(x - crop_size / 2.5, y - crop_size / 2.5, x + crop_size / 2.5, y + crop_size / 2.5)
        return left_line
    else:
        right_line = QtCore.QLineF()
        right_line.setLine(x + crop_size / 2.5, y - crop_size / 2.5, x - crop_size / 2.5, y + crop_size / 2.5)
        return right_line


# ----------------------------------------------------------------------------------------------------------------------
class AzImageViewer(QtWidgets.QGraphicsView):  # Реализация Романа Хабарова
    """
    Виджет для отображения изображений и меток/разметки (*.jpg, *.png и т.д.)
    """
    list_mc_changed = QtCore.pyqtSignal(list)  # сигнал об изменении объекта self.points_mc

    def __init__(self, parent=None, active_color=None, fat_point_color=None, on_rubber_band_mode=None):
        super().__init__(parent)
        scene = QtWidgets.QGraphicsScene(self)  # Графический контейнер
        self.setScene(scene)  # Устанавливаем сцену
        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()  # Создаём растровый элемент (картинка)
        scene.addItem(self._pixmap_item)  # добавляем растровый элемент к сцене

        self._zoom = 0  # увеличение
        self.view_state = ViewState.normal  # состояние виджета
        self.hand_start_point = None  # начальная точка для перемещения
        self.is_mid_click = False  # флаг использования средней клавиши
        self.click_point = None  # сохранение для перемещения точек
        self.points_mc = list()  # набор точек РК для данного снимка
        self.view_state_before_mid_click = None  # слот для сохранения текущего состояния виджета
        self.scan_size = 0  # по умолчанию ставим 0

        # self.drag = False  # FIRE
        # self.prev_pos = None  # FIRE

    def crop_scan_size_changed(self, size):  # изменение рамок у границ объектов кадрирования
        self.scan_size = size
        pass
        # TODO: сделать при передаче scan_size'a пересчёт данных

    # def mousePressEvent(self, event):
    #     sp = self.mapToScene(event.pos())
    #     lp = self.pixmap_item.mapFromScene(sp)
    #     if event.button() == QtCore.Qt.LeftButton:
    #         rect_item = QtWidgets.QGraphicsRectItem(lp.x(), lp.y(), 50, 50)
    #         rect_item.setFlags(QtWidgets.QGraphicsRectItem.ItemIsSelectable | QtWidgets.QGraphicsRectItem.ItemIsMovable)
    #         self.scene().addItem(rect_item)
    #     elif event.button() == QtCore.Qt.RightButton:
    #         items = self.scene().items(lp.__pos__())
    #         for item in items:
    #             if isinstance(item, QtWidgets.QGraphicsRectItem):
    #                 if item.isSelected():
    #                     item.setSelected(False)
    #                 else:
    #                     self.scene().clearSelection()
    #                     item.setSelected(True)
    #                 break
    #         else:
    #             self.scene().clearSelection()
    # lp = self.pixmap_item.mapFromScene(sp)  # конвертация в координаты снимка

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print("==========")
        items = self.scene().items()
        for item in items:
            if isinstance(item, AzPointWithRect):
                print(item.point)

        sp = self.mapToScene(event.pos())  # точка по клику, переведенная в координаты сцены
        lp = self.pixmap_item.mapFromScene(sp)  # конвертация в координаты снимка

        modifierName = ''
        # определяем модификаторы нажатия мыши
        if event.buttons() == QtCore.Qt.MouseButton.RightButton:
            modifierName += " Right Click"
        elif event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            modifierName += " Left Click"
        elif event.buttons() == QtCore.Qt.MouseButton.MidButton:
            # Сохраняем предыдущее состояние view_state
            # Меняем временно, до MouseRelease состояние на hand_move
            modifierName += " Mid Click"
            self.is_mid_click = True
            self.view_state_before_mid_click = self.view_state
            self.view_state = ViewState.hand_move

            if not self.hand_start_point:  # стартовая точка не свободна, значит используем её
                self.hand_start_point = event.pos()
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ClosedHandCursor))
            return

        # режим перемещения "ручкой"
        if self.view_state == ViewState.hand_move:
            if not self.hand_start_point:
                self.hand_start_point = event.pos()
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ClosedHandCursor))
            return

        # режим добавления точек
        elif self.view_state == ViewState.point_add:
            if 'Right Click' in modifierName:  # проверка на правую кнопку мыши
                return  # добавление только левой кнопкой мыши, иначе выходим
            point_mc = AzPointWithRect(sp, QtGui.QColor(the_color_crop), self.scan_size)
            self.scene().addItem(point_mc)  # добавляем объект на сцену
            self.points_mc.append(point_mc)  # сохраняем объект в памяти
            self.list_mc_changed.emit(self.points_mc)  # сигнализируем об изменении перечня точек РК
            return

        # режим перемещения точек
        elif self.view_state == ViewState.point_move:
            if 'Right Click' in modifierName:
                return
            super(AzImageViewer, self).mousePressEvent(event)  # инициируем событие для класса QGraphicsView
            self.click_point = lp  # запоминаем точку старта
            return

        # режим удаления точек
        elif self.view_state == ViewState.point_delete:
            if 'Right Click' in modifierName:
                return
            # items = self.scene().items(lp.__pos__())
            # for item in items:
            #     if isinstance(item, QtWidgets.QGraphicsRectItem):
            #         if item.isSelected():
            #             item.setSelected(False)
            #         else:
            #             self.scene().clearSelection()
            #             item.setSelected(True)
            #         break
            # else:
            #     self.scene().clearSelection()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        sp = self.mapToScene(event.pos())  # точка по клику, переведенная в координаты сцены
        lp = self.pixmap_item.mapFromScene(sp)  # конвертация в координаты снимка

        # перемещение "ручкой"
        if self.view_state == ViewState.hand_move:
            dx = int(event.pos().x() - self.hand_start_point.x())
            dy = int(event.pos().y() - self.hand_start_point.y())

            hpos = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(hpos - dx)

            vpos = self.verticalScrollBar().value()
            self.verticalScrollBar().setValue(vpos - dy)

            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

            if self.is_mid_click:
                # Если была нажата средняя кнопка мыши - режим hand_move вызван разово.
                # Возвращаем состояние обратно
                self.is_mid_click = False
                self.set_view_state(self.view_state_before_mid_click)
            return

        # режим перемещения точек
        elif self.view_state == ViewState.point_move:
            super(AzImageViewer, self).mouseReleaseEvent(event)
            dx = lp.x() - self.click_point.x()
            dy = lp.y() - self.click_point.y()
            # print(f"dx = {delta_x}; dy = {delta_y}")
            items = self.scene().selectedItems()
            for item in items:
                if isinstance(item, AzPointWithRect):  # объект класса точка с прямоугольником
                    for point_mc in self.points_mc:
                        if point_mc == item:  # где этот объект в перечне point_mc
                            point_mc.apply_offset(dx, dy)  # применяем смещение точки выделенного объекта-в-памяти
                            # item.apply_offset(dx, dy)  # применяем смещение точки выделенного объекта-на-сцене
                            # self.points_mc.append(item)  # добавляем новый
                    # TODO: заменить объект в списке
                break
            return
            # super(AzImageViewer, self).mousePressEvent(event)

    # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    #     if self.view_state == ViewState.point_move:
    #         super().mouseMoveEvent(event)

    def set_view_state(self, state=ViewState.normal):
        self.view_state = state
        # TODO: переделать self.hand_start_point = None
        print(self.view_state)
        if state == ViewState.hand_move:
            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            return
        if state == ViewState.point_add:
            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
            return
        if state == ViewState.point_move:
            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return
        if state == ViewState.point_delete:
            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            return
        self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))  # если вариант normal

    def clear_scene(self):
        """
        Очистить сцену
        """
        self.set_view_state()
        self.points_mc.clear()
        scene = QtWidgets.QGraphicsScene(self)
        self.setScene(scene)
        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self._pixmap_item)

    @property
    def pixmap_item(self):
        return self._pixmap_item

    def set_pixmap(self, pixmap):
        """
        Задать новую картинку
        """
        self.scene().clear()
        self._zoom = 0  # Test
        # self.sceneRect().setRect(0, 0, 0, 0)
        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._pixmap_item)
        self.pixmap_item.setPixmap(pixmap)
        self.fitInView(self.pixmap_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        # self.fitInView(self.scene().sceneRect())
        # self.image_widget.fitInView(QtCore.QRectF(0, 0, 400, 300), QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Колесо прокрутки для изменения масштаба"""
        modifier_press = QtWidgets.QApplication.keyboardModifiers()
        modifier_name = ''
        if (modifier_press & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier:
            modifier_name += 'Ctrl'
        if 'Ctrl' in modifier_name:
            sp = self.mapToScene(event.pos())  # начальная точка мыши, при уменьшении картинки
            lp = self.pixmap_item.mapFromScene(sp)
            factor = 1.0
            if event.angleDelta().y() > 0:  # угол отклонения: -120 отдаление; +120 приближение
                if self._zoom < config.MAXIMUM_ZOOM:
                    factor = 1.25
                    self._zoom += 1
            else:
                if self._zoom > config.MINIMUM_ZOOM:
                    factor = 0.8
                    self._zoom -= 1
            self.scale(factor, factor)
            if event.angleDelta().y() > 0:
                self.centerOn(lp)

    def add_polygon_to_scene(self, cls_name, color, polygon):  # добавление меток (полигонов SAMA на сцену)
        poly = QtGui.QPolygonF()
        for p in polygon:
            poly.append(QtCore.QPointF(p[0], p[1]))

        graph_poly = QtWidgets.QGraphicsPolygonItem()
        pcol = QtGui.QColor(color)
        pcol.setAlpha(config.ALPHA)
        brush = QtGui.QBrush(pcol, QtCore.Qt.BrushStyle.SolidPattern)
        pen = QtGui.QPen(QtGui.QColor(the_color), 1, QtCore.Qt.PenStyle.SolidLine)
        graph_poly.setPen(pen)
        graph_poly.setBrush(brush)
        graph_poly.setPolygon(poly)
        self.scene().addItem(graph_poly)
