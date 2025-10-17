from PyQt5 import QtWidgets, QtGui, QtCore

class FrameWithLines(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.border_radius = 28  # 圆角半径

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)

        # 设置裁剪区域，带圆角的矩形
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.rect())  # 将 QRect 转换为 QRectF
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        painter.setClipPath(path)

        # 设置遮罩画笔
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 90))  # 半透明黑色
        pen.setWidth(int(1.3))  # 横线宽度
        painter.setPen(pen)

        # 绘制横线，确保在圆角矩形内
        line_spacing = int(3.0)  # 横线间距
        y = 0
        while y < self.height():
            painter.drawLine(0, y, self.width(), y)
            y += line_spacing

        # 绘制右下角的直角标志
        marker_color = QtGui.QColor(140, 140, 140)
        marker_pen = QtGui.QPen(marker_color)
        marker_pen.setWidth(int(2.6))  # 设置线条宽度
        painter.setPen(marker_pen)

        # 设置直角的起点和终点
        line_length = 13  # 直角标志的长度
        margin = 20
        x_start = self.width() - margin - line_length  # 水平线起点
        y_start = self.height() - margin - line_length  # 垂直线起点

        # 水平线
        painter.drawLine(x_start, self.height() - margin,
                         self.width() - margin, self.height() - margin)
        # 垂直线
        painter.drawLine(self.width() - margin, y_start,
                         self.width() - margin, self.height() - margin)

        painter.end()