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
    add_point = 9  # добавляем центр-точку для автоматического формирования границ


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
class RectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, qrectf):
        super().__init__()

        self.qrectf = qrectf
        self.setRect(self.qrectf)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self.line = QtWidgets.QGraphicsLineItem(self)
        self.line.setPen(QtGui.QPen(QtGui.QColor(the_color_crop), 2, QtCore.Qt.SolidLine))
        self.line.setLine(0, 0, 50, 50)
        self.line2 = QtWidgets.QGraphicsLineItem(self)
        self.line2.setPen(QtGui.QPen(QtGui.QColor(the_color), 2, QtCore.Qt.SolidLine))
        self.line2.setLine(QtCore.QLineF(0, 50, 50, 0))

    def mouseMoveEvent(self, event):
        self.moveBy(event.pos().x() - event.lastPos().x(),
                    event.pos().y() - event.lastPos().y())


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
        scene.addItem(self._pixmap_item) # добавляем растровый элемент к сцене

        self._zoom = 0  # увеличение
        self.view_state = ViewState.normal  # состояние виджета
        self.hand_start_point = None  # начальная точка для перемещения
        self.is_mid_click = False  # флаг использования средней клавиши
        self.view_state_before_mid_click = None  # слот для сохранения текущего состояния виджета
        self.drag_state = DragState.no  # состояние перетаскивания

    # реализация ПРОПАН
    def add_qrectf(self, qrectf):
        self.qrectf = qrectf

    #Реализация ПРОПАН
    def add_rect(self, num):  # добавление квадратов
        if num == 0:  # очистить сцену
            self.clear()
        elif num > self.num_old:
            for i in range(self.num_old, num):
                rect = RectItem(self.qrectf)
                rect.moveBy(self.qrectf.width() * i, 100)
                self.list_rect.append(rect)
                self.addItem(rect)
        elif num < self.num_old:
            for i in range(num, self.num_old):
                self.removeItem(self.list_rect[-1])
                self.list_rect.pop()
        else:
            pass
        self.num_old = num

    def crop_scan_size_changed(self, size):  # изменение рамок у границ объектов кадрирования
        pass
        # TODO: сделать при передаче scan_size'a пересчёт данных

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # modifierPressed = QtWidgets.QApplication.keyboardModifiers()
        modifierName = ''

        if event.buttons() == QtCore.Qt.MidButton:
            # Сохраняем предыдущее состояние view_state
            # Меняем временно, до MouseRelease состояние на hand_move
            modifierName += " Mid Click"
            self.is_mid_click = True
            self.view_state_before_mid_click = self.view_state
            self.view_state = ViewState.hand_move

            if not self.hand_start_point:
                self.hand_start_point = event.pos()
                self.drag_state = DragState.start
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            return

        if self.view_state == ViewState.hand_move:
            if not self.hand_start_point:
                self.hand_start_point = event.pos()
                self.drag_state = DragState.start
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            return
        elif self.view_state == ViewState.add_point:
            sp = self.mapToScene(event.pos())
            lp = self.pixmap_item.mapFromScene(sp)
            print(lp)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        # sp = self.mapToScene(event.pos())
        # lp = self.pixmap_item.mapFromScene(sp)
        if self.view_state == ViewState.hand_move:  # and self.drag_state == DragState.in_process:
            lp = event.pos()
            dx = int(lp.x() - self.hand_start_point.x())
            dy = int(lp.y() - self.hand_start_point.y())

            hpos = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(hpos - dx)

            vpos = self.verticalScrollBar().value()
            self.verticalScrollBar().setValue(vpos - dy)

            self.hand_start_point = None
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

            self.drag_state = DragState.no

            if self.is_mid_click:
                # Если была нажата средняя кнопка мыши - режим hand_move вызван разово.
                # Возвращаем состояние обратно
                self.is_mid_click = False
                print(self.view_state_before_mid_click)
                print(self.view_state)
                self.set_view_state(self.view_state_before_mid_click)

            return

    def set_view_state(self, state=ViewState.normal):
        self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if state == ViewState.hand_move:
            self.view_state = state
            self.hand_start_point = None
            self.drag_state = DragState.no
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            return
        if state == ViewState.add_point:
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

    def add_point_to_scene(self, x, y, color):
        graph_poly = QtWidgets.QGraphicsPolygonItem()
        pcol = QtGui.QColor(color)
        self.scene().addItem(graph_poly)
        #
        # double rad = 1;
        # scene->addEllipse(x - rad, y - rad, rad * 2.0, rad * 2.0, QPen(), QBrush(Qt::SolidPattern));

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
