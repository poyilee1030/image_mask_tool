import glob
from PyQt5.QtWidgets import *
from sys import exit, argv
from mainui import *
from custom_widget import *
from image_util_encode import ImageUtilEncode


class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.btnSelectSrcFolder.clicked.connect(self.onSelectSrcFolderClicked)
        self.btnSave.clicked.connect(self.onSaveClicked)
        self.btnPrev.clicked.connect(self.onPrevClicked)
        self.btnNext.clicked.connect(self.onNextClicked)
        self.tableWidget.setEditTriggers(QAbstractItemView.CurrentChanged)
        self.tableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.itemSelectionChanged.connect(self.onRowSelected)
        self.button_delete = None
        self.vSlider.valueChanged.connect(self.valuechange)

        # src_path = self.read_last_folder_path()
        # self.lineEditSrc.setText(src_path)

        self.src_path_list = []
        self.cur_index = 0

        self.mouse_tracker = MouseTracker(self.lblOutputMsg, self.update_table_view, self.update_scroll_bar)
        self.oxLayout.addWidget(self.mouse_tracker)

    def update_scroll_bar(self, y):
        print("main:: y = ", y)
        y = y // 10
        slider_pos = self.vSlider.value()
        slider_pos -= y
        if slider_pos < 0:
            slider_pos = 0
        elif slider_pos > 100:
            slider_pos = 100

        self.vSlider.setValue(slider_pos)

    def valuechange(self):
        slider_pos = self.vSlider.value()
        new_pos = 100 - slider_pos
        self.mouse_tracker.set_cur_offset_y(new_pos)
        self.mouse_tracker.update()

    def updateCurTotalLabel(self):
        self.lblCurTotal.setText("{} / {}".format(self.cur_index+1, len(self.src_path_list)))

    def onRowSelected(self):
        selected_row = -1
        items = self.tableWidget.selectedItems()

        count = len(items)
        if count > 0:
            selected_row = items[0].row()
        print(selected_row)
        self.mouse_tracker.set_selected_idx(selected_row)

    def onSaveClicked(self):

        self.saveType()

        src_path = self.src_path_list[self.cur_index]
        basename_ext = os.path.basename(src_path)
        basename = os.path.splitext(basename_ext)[0]

        src_folder = os.path.dirname(src_path)
        dst_folder = os.getcwd() + "/output"
        if not os.path.exists(dst_folder):
            os.mkdir(dst_folder)

        dst_path = dst_folder + "/" + basename + ".png"

        json_path = src_folder + "/" + basename + ".json"
        data = {"src": basename_ext,
                'units': []}
        sd_list = self.mouse_tracker.get_saved_draw_list()
        for sd in sd_list:
            unit = {"model_type": sd[0],
                    "x1": sd[1],
                    "y1": sd[2],
                    "x2": sd[3],
                    "y2": sd[4]}
            data['units'].append(unit)
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        self.lblOutputMsg.setText("{} saved success.".format(basename))

        sd_list = self.mouse_tracker.get_saved_draw_list()
        iue = ImageUtilEncode(src_path, sd_list)
        iue.encode(dst_path)

    def onPrevClicked(self):
        self.onSaveClicked()
        self.cur_index -= 1
        if self.cur_index < 0:
            self.cur_index = len(self.src_path_list) - 1
        self.mouse_tracker.set_image(self.src_path_list[self.cur_index])
        self.mouse_tracker.update()
        self.updateCurTotalLabel()

    def onNextClicked(self):
        self.onSaveClicked()
        self.cur_index += 1
        if self.cur_index >= len(self.src_path_list):
            self.cur_index = 0
        self.mouse_tracker.set_image(self.src_path_list[self.cur_index])
        self.mouse_tracker.update()
        self.updateCurTotalLabel()

    def onScanSrcClicked(self):
        src_folder = self.lineEditSrc.text()
        self.src_path_list = glob.glob(src_folder + "/*.*g")
        self.mouse_tracker.set_image(self.src_path_list[self.cur_index])
        self.mouse_tracker.update()
        # self.write_last_folder_path()
        self.updateCurTotalLabel()

    def onSelectSrcFolderClicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.DirectoryOnly)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.lineEditSrc.setText(filenames[0])
            self.cur_index = 0
            self.onScanSrcClicked()

    def saveType(self):
        row_count = self.tableWidget.rowCount()
        saved_draw_count = row_count
        model_type_list = []
        for i in range(saved_draw_count):
            item = self.tableWidget.item(i, 0)
            t = item.text()
            model_type_list.append(t)

        self.mouse_tracker.update_model_type(model_type_list)

    def update_table_view(self, saved_draw_list):

        saved_draw_count = len(saved_draw_list)

        self.tableWidget.setRowCount(saved_draw_count)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['type', 'position', ''])
        hheader = self.tableWidget.horizontalHeader()
        hheader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hheader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hheader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        #hheader.setDefaultSectionSize(200)

        vheader = self.tableWidget.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(45)

        for i in range(saved_draw_count):
            sd_item = saved_draw_list[i]
            self.button_delete = QPushButton('delete', self)

            item = QTableWidgetItem(sd_item[0])
            self.tableWidget.setItem(i, 0, item)
            str_pos = "(x,y,w,h)=({:.2f},{:.2f},{:.2f},{:.2f})".format(sd_item[1], sd_item[2], sd_item[3], sd_item[4])
            item = QTableWidgetItem(str_pos)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 1, item)
            self.tableWidget.setCellWidget(i, 2, self.button_delete)

            self.button_delete.clicked.connect(
                lambda state, r=i: self.button_delete_pushed(r)
            )

    def button_delete_pushed(self, row):
        self.mouse_tracker.remove_saved_draw(row)


if __name__ == "__main__":
    app = QApplication(argv)
    myWin = MyMainWindow()
    myWin.setWindowTitle("Mask Image Tool 1.0.2")
    myWin.show()
    exit(app.exec_())
