# -*- coding: utf-8 -*-

import os, sys, time, re
import logging
import subprocess
from pathlib import Path

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
from PyQt5.QtWebEngineWidgets import *

from .utils import *
from .manager import *
from .editor import *

#---------------------------------#
class ProcessOutThread(QThread):
    output = pyqtSignal([str])
    stoped = pyqtSignal([int])

    def __init__(self, process):
        QThread.__init__(self)
        self.process = process
        
    def run(self):
        while True:
            time.sleep(0.2)
            try:
                out, err = self.process.communicate(timeout=1)
                if out:
                    self.output.emit(f'OUT: {out.decode("GBK")}')
                if err:    
                    self.output.emit(f'ERROR: {err.decode("GBK")}')
            except subprocess.TimeoutExpired:
                #self.output.emit('TimeoutExpired')
                pass
            ret = self.process.poll()
            if ret != None:
                break
                
            '''
            text = self.process.stderr.readline().decode('GBK')
            if text:
                self.output.emit(f'ERROR: {text}')
            text = self.process.stdout.readline().decode('GBK')
            if text:
                self.output.emit(f'OUT: {text}')
            else:
                break
            '''    
        self.stoped.emit(ret)
        
#---------------------------------#
class CmdExecView(QDockWidget):
    def __init__(self, parent):
        super().__init__('进程输出')
        self.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.parent = parent
        
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(12)
        
        self.textInfo = QTextEdit()
        self.textInfo.setReadOnly(True)        
        self.textInfo.setFont(font)
        self.textInfo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textInfo.customContextMenuRequested.connect(self.onContextMenu)
        self.setWidget(self.textInfo)
    
    def append(self, text):
        self.textInfo.append(text)    
    
    def clear(self):
        self.textInfo.clear()
    
    def onContextMenu(self, pos):
        
        menu = QMenu()
        
        self.clearAction = menu.addAction("Clear")
        self.clearAction.triggered.connect(self.clear)
        
        menu.exec_(self.textInfo.viewport().mapToGlobal(pos))
        
#---------------------------------#


#---------------------------------#
class FeatureView(QDockWidget):
    def __init__(self, parent):
        super().__init__('')
        
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.parent = parent
        
        '''
        # 3. Place a button
        self.newFeatureBtn = QPushButton("+")
        self.newFeatureBtn.setFlat(True)
        self.delFeatureBtn = QPushButton("-")
        self.delFeatureBtn.setFlat(True)
        self.enableFeatureBtn = QPushButton("En")
        self.enableFeatureBtn.setFlat(True)
        self.disableFeatureBtn = QPushButton("Dis")
        self.disableFeatureBtn.setFlat(True)
        
        hbox.addWidget(self.newFeatureBtn)
        hbox.addWidget(self.delFeatureBtn)
        hbox.addWidget(self.enableFeatureBtn)
        hbox.addWidget(self.disableFeatureBtn)
        hbox.addStretch(1)
        ''' 
        
        self.manager = None
        
        #self.features=QStringListModel()
        self.featureModel = QStandardItemModel(self)
        self.featureModel.itemChanged.connect(self.onFeatureNameChanged)
        
        self.featureView = QListView()
        self.featureView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.featureView.setModel(self.featureModel)
        self.featureView.clicked.connect(self.onViewClicked)
        self.featureView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.featureView.customContextMenuRequested.connect(self.onContextMenu)
        
        self.freeFiles = QStringListModel()
        
        self.freeView = QListView()
        self.freeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.freeView.setModel(self.freeFiles)
        self.freeView.clicked.connect(self.onFreeViewClicked)
        self.freeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.freeView.customContextMenuRequested.connect(self.onFreeFilesContextMenu)
        
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        
        splitter.addWidget(self.featureView)
        splitter.addWidget(self.freeView)
        splitter.setStretchFactor(0, 80)
        splitter.setStretchFactor(1, 20)

        self.setWidget(splitter)
        
    def setManager(self, manager):
        
        self.manager = manager
        
        self.manager.testcase_opened.connect(self.onOpenedTestCase)
        self.manager.testcase_closed.connect(self.onClosedTestCase)
        
        self.manager.feature_created.connect(self.onFeatureCreated)
        self.manager.feature_changed.connect(self.onFeatureChanged)
        self.manager.feature_deleted.connect(self.onFeatureDeleted)
        self.manager.feature_renamed.connect(self.onFeatureRenamed)
        
        self.manager.file_deleted.connect(self.onFileDeleted)
        
    def loadView(self):
        
        self.featureModel.clear()
        
        for key in sorted(list(self.manager.features.keys())):
            feature = self.manager.features[key]
            #print(feature.name, feature.is_enabled)
            item = QStandardItem(feature.name)
            if not feature.is_enabled :
                item.setEnabled(False)
            self.featureModel.appendRow(item)
            
        self.freeFiles.setStringList([ str(it) for it in self.manager.free_py_files ])
        
        self.show()
    
    def onOpenedTestCase(self, path):
        self.loadView()
        
    def onClosedTestCase(self):
        self.clear()
        self.show()
        
    def clear(self):
        self.featureModel.clear()
        self.show()
        
    def onViewClicked(self, index):
        
        item = self.featureModel.itemFromIndex(index)
        feature = self.manager.features[item.text()]
        self.parent.editFeature(feature)
    
    def onContextMenu(self, pos):
        
        if not self.manager.path: 
            return
            
        self.selText = None
        self.selIndex = None
        
        index = self.featureView.indexAt(pos)
        if index != None:
            self.selIndex = index
            item = self.featureModel.itemFromIndex(index)
            #feature = self.manager.features[item.text()]
            self.selText = item.text() if item else None
            
        menu = QMenu()
        
        self.newAction = menu.addAction("New")
        self.newAction.triggered.connect(self.parent.onNewFeature)
        self.deleteAction = menu.addAction("Delete")
        self.deleteAction.triggered.connect(self.onDeleteFeature)
        
        self.renameAction = menu.addAction("Rename")
        self.renameAction.triggered.connect(self.onRenameFeature)
        
        self.changeNameAction = menu.addAction("Change Name")
        self.changeNameAction.triggered.connect(self.onChangeNameFeature)
        
        if self.selText:
            menu.addSeparator()
            if item.isEnabled():
                self.ableAction = menu.addAction("Disable")
            else:    
                self.ableAction = menu.addAction("Enable")
            self.ableAction.triggered.connect(self.onChangeFeatureStatus)
        else:
            self.deleteAction.setEnabled(False)
            self.renameAction.setEnabled(False)
            self.changeNameAction.setEnabled(False)
            
        menu.addSeparator() 
        self.editEnvAction = menu.addAction("编辑环境文件")
        self.editEnvAction.triggered.connect(self.onEditEnvFile)
                
        menu.exec_(self.featureView.viewport().mapToGlobal(pos))
    
    def onFreeViewClicked(self, index):
        py_file = self.freeFiles.stringList()[index.row()]
        self.parent.editPython(Path(py_file))
    
    def onFreeFilesContextMenu(self, pos):
        
        if not self.manager.path: 
            return
        
        self.selText = None
        self.selIndex = None
        
        index = self.freeView.indexAt(pos)
        if index != None:
            self.selIndex = index
            if self.selIndex.row() >= 0:
                self.selText = self.freeFiles.stringList()[self.selIndex.row()]
            else :
                self.selText = None
                
        menu = QMenu()
                
        #self.renameFreeAction = menu.addAction("Rename")
        #self.renameFreeAction.triggered.connect(self.onRenamePython)
        self.deleteFreeAction = menu.addAction("Delete")
        self.deleteFreeAction.triggered.connect(self.onDeletePython)
        
        if not self.selText:
            self.deleteFreeAction.setEnabled(False)
        
        menu.addSeparator()    
        self.editEnvAction = menu.addAction("编辑环境文件")
        self.editEnvAction.triggered.connect(self.onEditEnvFile)
        self.openFolderAction = menu.addAction("打开目录位置")
        self.openFolderAction.triggered.connect(self.onOpenFolder)
                
        menu.exec_(self.freeView.viewport().mapToGlobal(pos))
    
    def onRenameFeature(self):
        self.featureView.edit(self.selIndex)
        
    def onChangeNameFeature(self):
        pass
    
    def onFeatureNameChanged(self, item):
        #print("onFeatureNameChanged", item.text())
        self.manager.renameFeature(self.selText, item.text())
        
    def onDeleteFeature(self):
        YesNo = QMessageBox.question(self, '删除确认', f'您确定要删除 {self.selText} 文件!', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if YesNo == QMessageBox.Yes:
            self.manager.deleteFeature(self.selText)

    def onChangeFeatureStatus(self):
        try:
            self.manager.changeFeatureStatus(self.selText)
        except Exception as e:
            QMessageBox.information(self,"操作失败", str(e), QMessageBox.Yes)
            
    def onEditEnvFile(self):
        self.parent.editPython(Path(PY_ENV_FILE))
    
    def onOpenFolder(self):
        #os.system(f'start "{self.manager.path}"')
        print(self.manager.path)
        os.system(f'explorer "{self.manager.path}"')
    
    def onRenamePython(self):
        pass
        
    def onDeletePython(self):
        YesNo = QMessageBox.question(self, '删除确认', f'您确定要删除 {self.selText} 文件!', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if YesNo == QMessageBox.Yes:
            self.manager.deleteFreePython(Path(self.selText))

    def onFeatureCreated(self, feature):
        self.loadView()
        
    def onFeatureChanged(self, feature):
        self.loadView()
        
    def onFeatureDeleted(self, feature):
        self.loadView()
        
    def onFeatureRenamed(self, feature, new_feature):
        self.loadView()
        
    def onFileDeleted(self, path, py_file):
        self.loadView()
        
#---------------------------------#

class FeaturePanel(QWidget):
    
    split_pos = None
    
    def __init__(self, parent):
        super().__init__()
        
        
        self.parent = parent
        self.textChanged = [False, False]
        
        self.featureFile = None
        self.pythonFile = None
        
        self.featureEditor = FeatureEditor(panel = self)
        self.featureEditor.textChanged.connect(self.onFeatureChanged)
        
        self.pythonEditor = PythonEditor(panel = self)
        self.pythonEditor.textChanged.connect(self.onStepChanged)
        
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.splitterMoved.connect(self.onSplitterMoved)
        
        splitter.addWidget(self.featureEditor)
        splitter.addWidget(self.pythonEditor)
        splitter.setStretchFactor(0, 50)
        splitter.setStretchFactor(1, 50)
        
        if self.split_pos:
            splitter.moveSplitter(self.split_pos, 1)
        
        hbox=QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)
    
    def onFeatureChanged(self):
        self.textChanged[0] = True
        #print('onFeatureChanged')
        
    def onStepChanged(self):
        self.textChanged[1] = True
        #print('onStepChanged')
        
    def readFile(self, file_path):
        codings = ['utf-8', 'GB18030']
        
        text = None
        for coding in codings:
            try:
                with file_path.open(encoding=coding) as f:
                    text = f.read()
                    break
            except UnicodeDecodeError:
                pass
                
        return text
        
    def editFeature(self, feature):
       
        self.featureFile = feature.feature_file
        self.pythonFile = feature.py_file
        
        if not self.featureFile.is_file():
            return
        
        if not self.pythonFile.is_file():
            ok = QMessageBox.question(self, '文件不存在', f'文件[{feature.py_file}]不存在，是否需要生成一个默认文件？', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ok == QMessageBox.Yes:
                print('Creating python file', feature.py_file)
                self.pythonFile.touch()
            else:
                return
                
        print(f"Editing Feature File:{self.featureFile}")                
        
        text = self.readFile(self.featureFile)        
        if text:
            self.featureEditor.setText(text)
        
        print(f"Editing Python File:{self.pythonFile}")                
        text = self.readFile(self.pythonFile)        
        if text:
            self.pythonEditor.setText(text)
        
        self.textChanged = [False, False]
                
    def editPython(self, python_file):
        
        self.featureFile = None
        self.pythonFile = python_file
        
        self.featureEditor.hide()
                        
        print(f"Editing Python File:{self.pythonFile}")                
        text = self.readFile(self.pythonFile)        
        if text:
            self.pythonEditor.setText(text)
        
        self.textChanged = [False, False]
    
    def reload(self, file_path):
        
        if file_path == self.featureFile:
            text = self.readFile(self.featureFile)        
            if text:
                self.featureEditor.setText(text)
        elif file_path == self.pythonFile:
            text = self.readFile(self.pythonFile)        
            if text:
                self.pythonEditor.setText(text)
              
    def isFileChanged(self):
        return self.textChanged[0] or self.textChanged[1]
        
    def onSplitterMoved(self, pos, index):
        self.split_pos = pos
        #print(pos, index)
    
    def isCodeExist(self, code_str):
        match = re.search(code_str, self.pythonEditor.text())
        return True if match else False
    
    def appendCode(self, code_str):
        self.pythonEditor.append(code_str)
        text = self.pythonEditor.text()
        #find("os",case_sensitive=False,search_forward=True,window_name="Main")      
        line_pos = len(text.split("\n"))
        self.pythonEditor.setCursorPosition(line_pos, 0) #linefocus, colfocus)
        self.pythonEditor.ensureCursorVisible()
        self.pythonEditor.setFocus()
        
    def locateCode(self, code_str, show = False):
        text = self.pythonEditor.text()
        match = re.findall(code_str, text)
        if match:
            pos = text.find(match[0]) + len(match[0])
            line_pos = len(text[:pos].split("\n"))
            print("Matched", line_pos)
            if show:
                self.pythonEditor.setCursorPosition(line_pos, 0) #linefocus, colfocus)
                self.pythonEditor.ensureCursorVisible()
                self.pythonEditor.setFocus()
            return True
            
        else:
            return self.parent.locateCode(code_str, show)
            
    def onSave(self):
        if self.textChanged[0]:
            self.featureFile.write_text(self.featureEditor.text(), encoding='utf-8')
            print(f"Writed File: {self.featureFile}")
            self.textChanged[0] = False
            
        if self.textChanged[1]:
            self.pythonFile.write_text(self.pythonEditor.text(), encoding='utf-8')
            print(f"Writed File: {self.pythonFile}")
            self.textChanged[1] = False
        
    def onCopy(self):
        if self.featureEditor.isFocus:
            self.featureEditor.copy()
        if self.pythonEditor.isFocus:
            self.pythonEditor.copy()
            
    def onCut(self):
        if self.featureEditor.isFocus:
            self.featureEditor.cut()
        if self.pythonEditor.isFocus:
            self.pythonEditor.cut()
        
    def onPaste(self):
        if self.featureEditor.isFocus:
            self.featureEditor.paste()
        if self.pythonEditor.isFocus:
            self.pythonEditor.paste()
        
    def onUndo(self):
        if self.featureEditor.isFocus:
            self.featureEditor.undo()
        if self.pythonEditor.isFocus:
            self.pythonEditor.undo()
        
    def onRedo(self):
        if self.featureEditor.isFocus:
            self.featureEditor.redo()
        if self.pythonEditor.isFocus:
            self.pythonEditor.redo()

