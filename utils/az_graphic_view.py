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
    points_state = 9  # добавляем центр-точку для автоматического формирования границ


# ----------------------------------------------------------------------------------------------------------------------
class PointState(Enum):
    """
    Вариант состояния ViewState.point_state
    """
    add = 0
    move = 1
    delete = 2


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
        self.line.setPen(QtGui.QPen(color, 1, QtCore.Qt.SolidLine))

        self.line2 = QtWidgets.QGraphicsLineItem(self)  # диагональная линия 2
        self.line2.setLine(draw_line(point, crop_size, False))
        self.line2.setPen(QtGui.QPen(color, 1, QtCore.Qt.SolidLine))

        rect = QtCore.QRectF(point.x() - crop_size / 2, point.y() - crop_size / 2, crop_size, crop_size)
        self.setRect(rect)
        self.setPen(QtGui.QPen(color, 2, QtCore.Qt.SolidLine))
        self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def mouseMoveEvent(self, event):
        self.moveBy(event.pos().x() - event.lastPos().x(), event.pos().y() - event.lastPos().y())

    def repaint_border(self, new_crop_size):
        if self.crop_size == new_crop_size:
            return
        else:
            self.crop_size = new_crop_size
            rect = QtCore.QRectF(self.point.x() - new_crop_size / 2, self.point.y() - new_crop_size / 2,
                                 new_crop_size, new_crop_size)
            self.setRect(rect)
            self.setPen(QtGui.QPen(self.color, 2, QtCore.Qt.SolidLine))


def draw_line(point, crop_size, left_one=True):
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
        self.view_state_before_mid_click = None  # слот для сохранения текущего состояния виджета
        self.drag_state = DragState.no  # состояние перетаскивания
        self.scan_size = 1280

        self.drag = False  # FIRE
        self.prev_pos = None  # FIRE

    def crop_scan_size_changed(self, size):  # изменение рамок у границ объектов кадрирования
        self.scan_size = size
        pass
        # TODO: сделать при передаче scan_size'a пересчёт данных

    def mousePressEvent(self, event):
        # if event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.AltModifier:
        #     self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        #     self.drag = True
        #     self.prev_pos = event.pos()
        #     self.setCursor(QtCore.Qt.SizeAllCursor)
        # elif event.button() == QtCore.Qt.LeftButton:
        #     self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        #
        # # This does not work as i wanted, it is only changing the mouse icon
        # elif event.button() == QtCore.Qt.MiddleButton:
        #     # set hand icon..
        #     self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        #     # print selected item position in scene.
        #     for x in self.scene().selectedItems():
        #         print(x.scenePos())
        super(AzImageViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # if self.drag:
        #     new_scale = self.matrix().m11()
        #     delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prev_pos)) * -1.0 * new_scale
        #     center = QtCore.QPoint(self.viewport().width() / 2 + delta.x(), self.viewport().height() / 2 + delta.y())
        #     new_center = self.mapToScene(center)
        #     self.centerOn(new_center)
        #     self.prev_pos = event.pos()
        #     return
        super(AzImageViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # if self.drag:
        #     self.drag = False
        #     self.setCursor(QtCore.Qt.ArrowCursor)
        super(AzImageViewer, self).mouseReleaseEvent(event)
        #
        # if event.button() == QtCore.Qt.RightButton:
        #     # Context Menu
        #     menu = QtWidgets.QMenu()
        #     save = menu.addAction('save')
        #     load = menu.addAction('load')
        #     selectedAction = menu.exec_(event.globalPos())
        #
        #     if selectedAction == save:
        #         common.scene_save(self)
        #     if selectedAction == load:
        #         common.scene_load(self)

    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #     # modifierPressed = QtWidgets.QApplication.keyboardModifiers()
    #     modifierName = ''
    #
    #     # определяем модификаторы нажатия мыши
    #     if event.buttons() == QtCore.Qt.RightButton:
    #         modifierName += " Right Click"
    #     elif event.buttons() == QtCore.Qt.LeftButton:
    #         modifierName += " Left Click"
    #     elif event.buttons() == QtCore.Qt.MidButton:
    #         # Сохраняем предыдущее состояние view_state
    #         # Меняем временно, до MouseRelease состояние на hand_move
    #         modifierName += " Mid Click"
    #         self.is_mid_click = True
    #         self.view_state_before_mid_click = self.view_state
    #         self.view_state = ViewState.hand_move
    #
    #         if not self.hand_start_point:
    #             self.hand_start_point = event.pos()
    #             self.drag_state = DragState.start
    #             self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
    #         return
    #
    #     if self.view_state == ViewState.hand_move:
    #         if not self.hand_start_point:
    #             self.hand_start_point = event.pos()
    #             self.drag_state = DragState.start
    #             self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
    #         return
    #     elif self.view_state == ViewState.points_state:  # режим добавления точек
    #         if 'Right Click' in modifierName:  # проверка на правую кнопку мыши
    #             return  # добавление только левой кнопкой мыши, иначе выходим
    #         sp = self.mapToScene(event.pos())
    #         lp = self.pixmap_item.mapFromScene(sp)
    #         point_mc = AzPointWithRect(lp, QtGui.QColor(the_color_crop), self.scan_size)
    #         self.scene().addItem(point_mc)  # добавляем объект на сцену
    #
    # def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
    #     # sp = self.mapToScene(event.pos())
    #     # lp = self.pixmap_item.mapFromScene(sp)
    #     if self.view_state == ViewState.hand_move:  # and self.drag_state == DragState.in_process:
    #         lp = event.pos()
    #         dx = int(lp.x() - self.hand_start_point.x())
    #         dy = int(lp.y() - self.hand_start_point.y())
    #
    #         hpos = self.horizontalScrollBar().value()
    #         self.horizontalScrollBar().setValue(hpos - dx)
    #
    #         vpos = self.verticalScrollBar().value()
    #         self.verticalScrollBar().setValue(vpos - dy)
    #
    #         self.hand_start_point = None
    #         self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
    #
    #         self.drag_state = DragState.no
    #
    #         if self.is_mid_click:
    #             # Если была нажата средняя кнопка мыши - режим hand_move вызван разово.
    #             # Возвращаем состояние обратно
    #             self.is_mid_click = False
    #             self.set_view_state(self.view_state_before_mid_click)
    #
    #         return

    def set_view_state(self, state=ViewState.normal):
        self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if state == ViewState.hand_move:
            self.view_state = state
            self.hand_start_point = None
            self.drag_state = DragState.no
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            return
        if state == ViewState.points_state:
            self.view_state = state
            self.hand_start_point = None
            # self.drag_state = DragState.no
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
            return
        self.view_state = ViewState.normal

    def clear_scene(self):
        """
        Очистить сцену
        """
        self.set_view_state()
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
        self.fitInView(self.pixmap_item, QtCore.Qt.KeepAspectRatio)
        # self.fitInView(self.scene().sceneRect())
        # self.image_widget.fitInView(QtCore.QRectF(0, 0, 400, 300), QtCore.Qt.KeepAspectRatio)

    # def scaleView(self, scaleFactor):
    #     factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
    #     if factor < 0.5 or factor > 10:
    #         return
    #     self.scale(scaleFactor, scaleFactor)

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
        brush = QtGui.QBrush(pcol, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(QtGui.QColor(the_color), 1, QtCore.Qt.SolidLine)
        graph_poly.setPen(pen)
        graph_poly.setBrush(brush)
        graph_poly.setPolygon(poly)
        self.scene().addItem(graph_poly)
