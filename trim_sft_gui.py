import json
import struct
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class SafetensorsEditor(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Safetensors Metadata Editor")
        self.setGeometry(100, 100, 700, 500)
        
        mainLayout = QtWidgets.QVBoxLayout()
        font = QtGui.QFont("Arial", 12)
        self.setFont(font)

        self.loadButton = QtWidgets.QPushButton("Select a Safetensors")
        self.loadButton.setFont(QtGui.QFont("Arial", 14))
        self.loadButton.setStyleSheet("padding: 10px;")
        self.loadButton.clicked.connect(self.loadFile)
        mainLayout.addWidget(self.loadButton)
        
        self.metadataList = QtWidgets.QListWidget()
        self.metadataList.setFont(QtGui.QFont("Arial", 12))
        self.metadataList.setStyleSheet("padding: 10px;")
        mainLayout.addWidget(self.metadataList)
        
        self.saveButton = QtWidgets.QPushButton("Save to New Safetensors")
        self.saveButton.setFont(QtGui.QFont("Arial", 14))
        self.saveButton.setStyleSheet("padding: 10px;")
        self.saveButton.clicked.connect(self.saveFile)
        self.saveButton.setEnabled(False)
        mainLayout.addWidget(self.saveButton)
        
        self.setLayout(mainLayout)

    def loadFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a Safetensors", "", "Safetensors Files (*.safetensors)", options=options)
        
        if fileName:
            self.fileName = fileName
            self.loadSafetensorsFile(fileName)
    
    def loadSafetensorsFile(self, filename):
        try:
            with open(filename, "rb") as f:
                header_length_bytes = f.read(8)
                header_length = struct.unpack("<Q", header_length_bytes)[0]
                header_bytes = f.read(header_length)
                header = json.loads(header_bytes.decode("utf-8"))
                
                self.metadata = header.get("__metadata__", {})
                if not self.metadata:
                    QMessageBox.information(self, "Warning", "No __metadata__ found")
                    return
                
                self.metadataList.clear()
                
                sorted_metadata = sorted(self.metadata.items(), key=lambda item: len(str(item[1])), reverse=True)
                
                for key, value in sorted_metadata:
                    item_text = f"{key} - Length: {len(str(value))}"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setFont(QtGui.QFont("Arial", 12))

                    if len(str(value)) > 100 * 1024 * 1024:  # 100 MB
                        item.setBackground(QtGui.QColor(255, 102, 102)) 
                        item.setForeground(QtGui.QColor(0, 0, 0))  

                    item.setCheckState(QtCore.Qt.Unchecked)
                    self.metadataList.addItem(item)

                # 启用保存按钮
                self.saveButton.setEnabled(True)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Can not load file: {e}")

    def saveFile(self):
        keys_to_delete = [item.text().split(" - ")[0] for item in self.metadataList.findItems("*", QtCore.Qt.MatchWildcard) if item.checkState() == QtCore.Qt.Checked]
        
        with open(self.fileName, "rb") as f:
            header_length_bytes = f.read(8)
            header_length = struct.unpack("<Q", header_length_bytes)[0]
            header_bytes = f.read(header_length)
            header = json.loads(header_bytes.decode("utf-8"))
        
        if "__metadata__" in header:
            for key in keys_to_delete:
                header["__metadata__"].pop(key, None)
        
        new_header_bytes = json.dumps(header, separators=(',', ':')).encode("utf-8")
        new_header_length = len(new_header_bytes)
        offset_delta = new_header_length - header_length
        
        for tensor_info in header.values():
            if isinstance(tensor_info, dict) and "data_offsets" in tensor_info:
                start_offset, end_offset = tensor_info["data_offsets"]
                tensor_info["data_offsets"] = [start_offset + offset_delta, end_offset + offset_delta]
        
        options = QFileDialog.Options()
        new_file_name, _ = QFileDialog.getSaveFileName(self, "Save to New Safetensors", "", "Safetensors Files (*.safetensors)", options=options)
        
        if new_file_name:
            with open(new_file_name, "wb") as f:
                f.write(struct.pack("<Q", new_header_length))
                f.write(new_header_bytes) 
                
                with open(self.fileName, "rb") as original_file:
                    original_file.seek(8 + header_length)
                    bin_data = original_file.read()
                    f.write(bin_data)
            
            QMessageBox.information(self, "Success", "Successfully saved")

app = QtWidgets.QApplication(sys.argv)

app.setStyle("Fusion")
palette = app.palette()
palette.setColor(QtGui.QPalette.Button, QtGui.QColor(70, 130, 180))
palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
app.setPalette(palette)

editor = SafetensorsEditor()
editor.show()
sys.exit(app.exec_())
