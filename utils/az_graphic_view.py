from PyQt5 import QtCore, QtWidgets, QtGui
from utils import config
from enum import Enum
from shapely import Polygon

the_color = config.UI_COLORS.get("line_color")
the_color_crop = config.UI_COLORS.get("crop_color")


# Часть класса - реализация Романа Хабарова
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
    point_universal = 12  # универсальный инструмент РК: левой переместить, правой добавить, shift+click - удалить


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
        self.setPen(QtGui.QPen(color, 4, QtCore.Qt.PenStyle.SolidLine))
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

            self.line.setLine(draw_line(self.point, new_crop_size, True))
            # self.line.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.PenStyle.SolidLine))
            self.line2.setLine(draw_line(self.point, new_crop_size, False))
            # self.line2.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.PenStyle.SolidLine))

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
    signal_list_mc_changed = QtCore.pyqtSignal(bool)  # сигнал об изменении объекта self.points_mc

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

    def crop_scan_size_changed(self, size: int):  # изменение рамок у границ объектов кадрирования
        self.scan_size = size  # при изменении...
        if self.points_mc:  # перерисовываем все границы объектов
            for item in self.points_mc:
                if isinstance(item, AzPointWithRect):
                    item.repaint_border(size)

    def add_mc_point(self, point, scan_size, color=the_color_crop):
        point_mc = AzPointWithRect(point, QtGui.QColor(color), scan_size)
        self.scene().addItem(point_mc)  # добавляем объект на сцену
        self.points_mc.append(point_mc)  # сохраняем объект в памяти

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        sp = self.mapToScene(event.pos())  # точка по клику, переведенная в координаты сцены
        lp = self.pixmap_item.mapFromScene(sp)  # конвертация в координаты снимка

        modifierName = ''
        modifier_key = QtWidgets.QApplication.keyboardModifiers()  # Модификаторы клавиш
        if (modifier_key & QtCore.Qt.KeyboardModifier.ShiftModifier) == QtCore.Qt.KeyboardModifier.ShiftModifier:
            modifierName += 'Shift'

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
            self.add_mc_point(sp, self.scan_size)
            if self.points_mc:
                self.signal_list_mc_changed.emit(True)  # сигнализируем об изменении перечня точек РК
            return

        # режим перемещения точек
        elif self.view_state == ViewState.point_move:
            if 'Right Click' in modifierName:
                return
            super(AzImageViewer, self).mousePressEvent(event)  # инициируем событие для класса QGraphicsView
            self.click_point = lp  # запоминаем точку старта
            return

        elif self.view_state == ViewState.point_universal:
            if 'Shift' in modifierName and "Left Click" in modifierName:
                self.delete_one_point(lp)
                return

            if 'Right Click' in modifierName:
                self.add_mc_point(sp, self.scan_size)
                if self.points_mc:
                    self.signal_list_mc_changed.emit(True)  # сигнализируем об изменении перечня точек РК
                return

            if 'Left Click' in modifierName:
                super(AzImageViewer, self).mousePressEvent(event)  # инициируем событие для класса QGraphicsView
                self.click_point = lp  # запоминаем точку старта
                return

        # лист переменных
        # режим удаления точек
        elif self.view_state == ViewState.point_delete:
            if 'Right Click' in modifierName:
                return
            self.delete_one_point(lp)

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

        # режим перемещения точек универсальный
        elif self.view_state == ViewState.point_universal:
            super(AzImageViewer, self).mouseReleaseEvent(event)
            self.move_point_finish(self.click_point, lp)

        # режим перемещения точек
        elif self.view_state == ViewState.point_move:
            super(AzImageViewer, self).mouseReleaseEvent(event)
            self.move_point_finish(self.click_point, lp)

    def delete_one_point(self, map_point):
        """Удаление одной точки"""
        items = self.scene().items(map_point)  # выбираем по клику объекты
        if items:  # нас есть объекты
            for item in items:
                if isinstance(item, AzPointWithRect):  # нас интересуют только объекты с точкой
                    for point in self.points_mc:
                        if item == point:  # искомый объект найден
                            self.scene().removeItem(item)  # удаляем объект со сцены
                            self.points_mc.remove(point)  # удаляем объект из массива
                            if self.points_mc:  # сигнализируем об изменении
                                self.signal_list_mc_changed.emit(True)
                            else:  # если список совсем пустой - шлем сигнал
                                self.signal_list_mc_changed.emit(False)  # False - лист пуст
                            return  # хватит и одного удаления

    def move_point_finish(self, click_point, map_point):
        if click_point is None or map_point is None:
            return
        dx = map_point.x() - click_point.x()
        dy = map_point.y() - click_point.y()
        # print(f"dx = {delta_x}; dy = {delta_y}")
        items = self.scene().selectedItems()
        for item in items:
            if isinstance(item, AzPointWithRect):  # объект класса точка с прямоугольником
                item.apply_offset(dx, dy)  # применяем смещение точки выделенного объекта
                if self.points_mc:
                    self.signal_list_mc_changed.emit(True)  # сигнализируем об изменении перечня точек РК
            break
        return

    def set_view_state(self, state=ViewState.normal):
        self.view_state = state
        if state != ViewState.normal:
            self.hand_start_point = None
        if state == ViewState.normal:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))  # если вариант normal
        elif state == ViewState.hand_move:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        elif state == ViewState.point_add:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        elif state == ViewState.point_move:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        elif state == ViewState.point_delete:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        elif state == ViewState.point_universal:
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        else:
            print(self.view_state)  # какой-то неизвестный ViewState

    def clear_scene(self):
        """
        Очистить сцену
        """
        self.points_mc.clear()
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
        self.points_mc.clear()  # удаляем информацию о точках РК
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
        pen = QtGui.QPen(QtGui.QColor(the_color), 2, QtCore.Qt.PenStyle.SolidLine)
        graph_poly.setPen(pen)
        graph_poly.setBrush(brush)
        graph_poly.setPolygon(poly)
        self.scene().addItem(graph_poly)
