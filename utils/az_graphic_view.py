from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import config
from shapely import Polygon

the_color = config.UI_COLORS.get("line_color")


# ----------------------------------------------------------------------------------------------------------------------
class AzImageViewer(QtWidgets.QGraphicsView):  # Реализация Романа Хабарова
    """
    Виджет для отображения изображений и меток/разметки (*.jpg, *.png и т.д.)
    """

    def __init__(self, parent=None, active_color=None, fat_point_color=None, on_rubber_band_mode=None):
        super().__init__(parent)
        self.line_width = 1  # толщина линии по умолчанию
        scene = QtWidgets.QGraphicsScene(self)
        self.setScene(scene)

        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self._pixmap_item)

        self._zoom = 0

    def clear_scene(self):
        """
        Очистить сцену
        """
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

    def add_polygon_to_scene(self, cls_name, color, polygon):
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