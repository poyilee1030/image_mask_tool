import os
import json
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt


class MouseTracker(QWidget):
    distance_from_center = 0

    def __init__(self, lblmsg, update_table_view, update_scroll_bar):
        super().__init__()
        self.label = lblmsg
        self.update_table_view = update_table_view
        self.update_scroll_bar = update_scroll_bar
        self.pixmap = None
        self.mouse_start_x = -1
        self.mouse_start_y = -1
        self.mouse_end_x = -1
        self.mouse_end_y = -1
        self.setMouseTracking(True)
        self.pixmap_start_x = -1
        self.pixmap_start_y = -1
        self.pixmap_end_x = -1
        self.pixmap_end_y = -1
        self.selected_idx = -1
        self.saved_draw_list = []
        self.cur_offset_y = 0
        self.max_offset_y = 9999
        self.cur_widget_width = 1280
        self.cur_widget_height = 720
        self.cur_img_path = ""
        self.show()

    def set_cur_offset_y(self, slide_pos):
        offset_y = self.max_offset_y * (slide_pos/100)
        self.cur_offset_y = offset_y

    def set_selected_idx(self, selected_idx):
        self.selected_idx = selected_idx
        self.update()

    def set_image(self, image_path):
        self.cur_img_path = image_path

        # try load json
        dirname = os.path.dirname(image_path)
        image_basename_ext = os.path.basename(image_path)
        image_basename = os.path.splitext(image_basename_ext)[0]
        json_path = dirname + "/" + image_basename + ".json"

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding="utf-8") as data_file:
                data = json.loads(data_file.read())
                units = data['units']
                self.saved_draw_list.clear()
                for unit in units:
                    model_type = unit['model_type']
                    x1 = unit['x1']
                    y1 = unit['y1']
                    x2 = unit['x2']
                    y2 = unit['y2']
                    self.saved_draw_list.append([model_type, x1, y1, x2, y2])
        else:
            self.saved_draw_list.clear()

        self.pixmap = QPixmap(self.cur_img_path)
        image_w = self.pixmap.width()
        image_h = self.pixmap.height()
        new_image_w = self.width()
        scale_ratio = new_image_w / image_w
        new_image_h = round(scale_ratio * image_h)
        self.pixmap = QPixmap(self.cur_img_path).scaled(new_image_w, new_image_h)
        self.cur_widget_width = self.width()
        self.cur_widget_height = self.height()
        self.max_offset_y = new_image_h - self.cur_widget_height

        self.cur_offset_y = 0
        self.update_table_view(self.saved_draw_list)

    def update_model_type(self, model_type_list):
        for i in range(len(model_type_list)):
            model_type = model_type_list[i]
            draw_item = self.saved_draw_list[i]
            draw_item[0] = model_type

    def paintEvent(self, event):
        if self.pixmap is not None:
            widget_width = self.width()
            widget_height = self.height()
            if widget_width != self.cur_widget_width or widget_height != self.cur_widget_height:
                self.pixmap = QPixmap(self.cur_img_path)
                image_w = self.pixmap.width()
                image_h = self.pixmap.height()
                new_image_w = self.width()
                scale_ratio = new_image_w / image_w
                new_image_h = round(scale_ratio * image_h)
                self.pixmap = QPixmap(self.cur_img_path).scaled(new_image_w, new_image_h)
                self.cur_widget_width = widget_width
                self.cur_widget_height = widget_height
                self.max_offset_y = new_image_h - self.cur_widget_height
                print("width or height changed, resize image and set")

            offset_x = 0
            offset_y = self.cur_offset_y
            image_width = self.pixmap.width()
            image_height = self.pixmap.height()

            st_painter = QPainter(self)
            st_painter.drawPixmap(QRect(offset_x, -offset_y, image_width, image_height), self.pixmap)
            self.pixmap_start_x = offset_x / image_width
            self.pixmap_start_y = offset_y / image_height
            self.pixmap_end_x = (offset_x + widget_width) / image_width
            self.pixmap_end_y = (offset_y + widget_height) / image_height

            #print(offset_x, offset_y, image_width, image_height)

            for i in range(len(self.saved_draw_list)):
                draw_item = self.saved_draw_list[i]
                draw_type = draw_item[0]
                restore_sx = (draw_item[1] * image_width) - offset_x
                restore_sy = (draw_item[2] * image_height) - offset_y
                restore_ex = (draw_item[3] * image_width) - offset_x
                restore_ey = (draw_item[4] * image_height) - offset_y

                if i == self.selected_idx:
                    st_painter.setPen(Qt.red)
                else:
                    st_painter.setPen(Qt.green)

                st_painter.drawRect(restore_sx, restore_sy, restore_ex-restore_sx, restore_ey-restore_sy)

        if not (self.mouse_start_x == -1 or self.mouse_start_y == -1):
            dy_painter = QPainter(self)
            dy_painter.setPen(Qt.blue)
            dy_painter.begin(self)
            dy_painter.drawRect(self.mouse_start_x, self.mouse_start_y,
                                self.mouse_end_x - self.mouse_start_x, self.mouse_end_y - self.mouse_start_y)
            dy_painter.end()

    def mousePressEvent(self, event):
        cursor = QtGui.QCursor()
        self.mouse_start_x = event.x()
        self.mouse_start_y = event.y()
        print("Press cursor = ", cursor.pos())
        print("Press event pos = ", event.pos())

    def wheelEvent(self, event):
        if self.pixmap is not None:
            y = event.angleDelta().y()
            print("widget::y = ", y)
            self.update_scroll_bar(y)

    def clamp(self, value, low, high):
        if value < low:
            value = low
        elif value >= high:
            value = high
        # value = (value - low) / (high - low)
        return value

    def find_left_top_right_bottom(self):
        left = min(self.mouse_start_x, self.mouse_end_x)
        right = max(self.mouse_start_x, self.mouse_end_x)
        top = min(self.mouse_start_y, self.mouse_end_y)
        bottom = max(self.mouse_start_y, self.mouse_end_y)
        top += self.cur_offset_y
        bottom += self.cur_offset_y
        return left, top, right, bottom

    def mouseReleaseEvent(self, event):
        cursor = QtGui.QCursor()
        print("Release cursor = ", cursor.pos())
        print("Release event pos = ", event.pos())
        left, top, right, bottom = self.find_left_top_right_bottom()
        if (right - left) < 10 or (bottom - top) < 10:
            self.mouse_start_x = -1
            self.mouse_start_y = -1
            self.mouse_end_x = -1
            self.mouse_end_y = -1
            return

        if self.pixmap is not None:
            new_sx = self.clamp(left / self.pixmap.width(), self.pixmap_start_x, self.pixmap_end_x)
            new_sy = self.clamp(top / self.pixmap.height(), self.pixmap_start_y, self.pixmap_end_y)
            new_ex = self.clamp(right / self.pixmap.width(), self.pixmap_start_x, self.pixmap_end_x)
            new_ey = self.clamp(bottom / self.pixmap.height(), self.pixmap_start_y, self.pixmap_end_y)
            self.saved_draw_list.append(["0", new_sx, new_sy, new_ex, new_ey])

        self.mouse_start_x = -1
        self.mouse_start_y = -1
        self.mouse_end_x = -1
        self.mouse_end_y = -1
        self.update_table_view(self.saved_draw_list)

    def mouseMoveEvent(self, event):
        self.mouse_end_x = event.x()
        self.mouse_end_y = event.y()
        self.update()

    def get_saved_draw_list(self):
        return self.saved_draw_list

    def remove_saved_draw(self, row):
        draw_item = self.saved_draw_list[row]
        self.saved_draw_list.remove(draw_item)
        self.update_table_view(self.saved_draw_list)
        self.update()
