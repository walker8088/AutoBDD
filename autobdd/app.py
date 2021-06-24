# -*- coding: utf-8 -*-

import os, sys, time
import logging
import shutil
import uuid
from pathlib import Path
from subprocess import Popen, PIPE
import traceback

from behave import parser

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

import xlrd
import xlwt
import pyexcel

from .utils import *
from .manager import *
from .editor import *
from .views import *
from .report import *

#---------------------------------------------------------------#
APP_NAME = 'AutoBDD'
APP_SHOW = 'AutoBDD测试用例管理'
UID_FILE = 'uid'

#---------------------------------------------------------------#
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.root_folder = Path.cwd()
        self.templates_folder = Path(self.root_folder, 'templates')
        
        self.testManager = TestCaseManager(self.templates_folder)
        
        self.setWindowTitle(APP_SHOW)
        self.setWindowIcon(QIcon('images\\app.ico'))

        self.tabView = QTabWidget(self)
        self.tabView.setTabsClosable(True)
        self.tabView.tabCloseRequested.connect(self.onTabCloseRequest)
        #self.tabView.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.tabView.customContextMenuRequested.connect(self.openMenu)
        self.setCentralWidget(self.tabView)
        
        self.logView = LogView(self)
        self.logView.hide()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logView)
        
        self.reportView = ReportView(self)
        self.reportView.hide()
        #self.addDockWidget(Qt.BottomDockWidgetArea, self.reportView)
        
        self.createActions()
        self.createMenus()
        self.createToolBars()
        
        self.resize(1000,800)
        
        self.featureView = FeatureView(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.featureView)
        
        self.config = {
            'allure_log_path' : Path('allure', 'test_log'),
            'allure_report_path' : Path('allure', 'report'),
        }
        
        self.featureView.setManager(self.testManager)
        
        self.testManager.testcase_opened.connect(self.onTestCaseOpened)
        self.testManager.testcase_closed.connect(self.onTestCaseClosed)
        #self.testManager.file_created.connect(self.onFileCreated)
        
        #self.testManager.file_deleted.connect(self.onFileDeleted)
        #self.testManager.file_renamed.connect(self.onFileRenamed)
        #self.testManager.file_content_changed.connect(self.onFileContentChanged)
        
        self.testManager.feature_deleted.connect(self.onFeatureDeleted)
        self.testManager.feature_renamed.connect(self.onFeatureRenamed)
        self.testManager.file_deleted.connect(self.onFileDeleted)
        self.testManager.file_content_changed.connect(self.onFileContentChanged)
        
        self.onCloseTestCase()
        
        self.initActionStatus()

        self.readSettings()
    
    def initActionStatus(self):    
        self.featureView.clear()
        self.features = []
        self.tabView.clear()
        self.setWindowTitle(APP_SHOW)
        
        self.newTestAction.setEnabled(True)
        self.openTestAction.setEnabled(True)
        self.closeTestAction.setEnabled(False)
        self.importExcelAction.setEnabled(False)
        self.exportExcelAction.setEnabled(False)
        self.importMultiCaseAction.setEnabled(True)
        
        self.tbEdit.setEnabled(False)
        self.tbRun.setEnabled(False)
        
        self.showLogView(False)
        self.showFeatureView(True)
        
    def getPanels(self):
        panels = [] 
        for i in range(self.tabView.count()):
            panels.append(self.tabView.tabText(i))
        return panels
    
    def showLogView(self, show):
        self.logView.setVisible(show)
        self.showLogViewAction.setChecked(show)

    def showFeatureView(self, show):
        self.featureView.setVisible(show)
        self.showFeatureViewAction.setChecked(show)
            
    def editFeature(self, feature):
        
        file_name = str(feature.feature_file)
        panels = self.getPanels()
        
        #Close Edited Py Files
        py_file = str(feature.py_file) 
        if py_file in panels:
            index = panels.index(py_file)
            panel = self.tabView.widget(index)
            panel.onSave()
            self.tabView.removeTab(index)
            panels.pop(index)
            
        if file_name not in panels:
            panel = FeaturePanel(self)
            panel.editFeature(feature)
            panels.append(file_name)    
            self.tabView.addTab(panel, file_name)
            
        self.tabView.setCurrentIndex(panels.index(file_name))
        return self.tabView.currentWidget()
        
    def editPython(self, file_name):
        
        if not file_name.is_file():
            return None
            
        panels = self.getPanels()
        if str(file_name) not in panels:
            panel = FeaturePanel(self)
            panel.editPython(file_name)
            panels.append(str(file_name)) 
            self.tabView.addTab(panel, str(file_name))
            
        self.tabView.setCurrentIndex(panels.index(str(file_name)))
        return self.tabView.currentWidget()
        
    def onTabCloseRequest(self, index):
        panel = self.tabView.widget(index)
        if panel.isFileChanged():
            YesNo = QMessageBox.question(self, '确认', '文件内容已经修改, 要保存后关闭吗?', 
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            
            if YesNo == QMessageBox.Cancel:
                return
           
            if YesNo == QMessageBox.Yes:
                self.testManager.stopWatch()
                panel.onSave()
                self.testManager.startWatch()
        
        self.tabView.removeTab(index)
        
    def onNewTestCase(self):
        
        folder = QFileDialog.getExistingDirectory(self, "新建测试集目录", "")
        if folder == '': 
            return
        
        folder = Path(folder)
        files = os.listdir(folder)
        if files:
            QMessageBox.information(self, '提示', f'[{folder}]不是空目录, 不能在此目录下建立测试集.')
            return  
        
        self.onCloseTestCase()
        self.testManager.newTestCase(Path(folder))
    
    def onOpenTestCase(self):
        
        folder = QFileDialog.getExistingDirectory(self, "打开测试集目录", "")
        if folder == '': 
            return
            
        folder = Path(folder)
        steps_path = Path(folder, STEPS_PATH)
        if not steps_path.is_dir(): 
            QMessageBox.information(self, '提示', f'由于不存在[{steps_path}]目录, 不能打开[{folder}]目录的测试集.')
            return  
       
        self.onCloseTestCase()
        self.testManager.openTestCase(Path(folder))
        
    def onCloseTestCase(self):        
        self.testManager.closeTestCase()
        
    def onTestCaseOpened(self, folder):
        self.setWindowTitle(f'{APP_SHOW}-[{folder}]')
        
        self.newTestAction.setEnabled(False)
        self.openTestAction.setEnabled(False)
        self.closeTestAction.setEnabled(True)
        self.importExcelAction.setEnabled(True)
        self.exportExcelAction.setEnabled(True)
        self.importMultiCaseAction.setEnabled(False)
        
        self.tbEdit.setEnabled(True)
        self.tbRun.setEnabled(True)
        
        print(f"TestCase Opened: [{folder}]")
        
    def onTestCaseClosed(self):
        self.initActionStatus()
        print(f"TestCase Closed.")
         
    def onRunTestCase(self):
        
        dlg = CmdExecDialog(self.config)
        ok = dlg.exec_()
        if not ok:
            return
        

        cmd = dlg.cmd.text()
        
        self.config['allure_cmd'] = dlg.report.text()

        self.writeSettings()
        self.onSaveAllFiles()
        
        allure_report_path = self.config['allure_report_path']
        allure_log_path = self.config['allure_log_path']
        
        if allure_report_path.is_dir():
            shutil.rmtree(allure_report_path, ignore_errors=True)
        
        if allure_log_path.is_dir():
            shutil.rmtree(allure_log_path, ignore_errors=True)
        
        self.logView.clear()
        
        try:
            self.runCmd(cmd) 
        except Exception as e:
            self.logView.append(str(e)+'\n')
            self.process = None
            return

        while None != self.process :
            qApp.processEvents()
    
        #TODO empty folder test
        
        
        if not dlg.report_check.isChecked():
            return

        #if not allure_report_path.is_dir():
        #    allure_report_path.mkdir()
        
        uid = str(uuid.uuid1())

        Path(allure_log_path, UID_FILE).write_text(uid)
        print(f'Writed uid file [{Path(allure_log_path, UID_FILE)}]')
            
        allure_cmd = self.config['allure_cmd']
        
        try:
            self.runCmd(f'{allure_cmd}  generate -c "{allure_log_path}" -o "{allure_report_path}"') 
        except Exception as e:
            self.logView.append(str(e)+'\n')
            self.process = None
            return
        
        while None != self.process :
            qApp.processEvents()
            
        Path(allure_report_path, UID_FILE).write_text(uid)
        
        self.onViewReport()

    def onViewReport(self):
        
        allure_report_path = self.config['allure_report_path']
        allure_log_path = self.config['allure_log_path']
        
        if not allure_log_path.is_dir():
            QMessageBox.information(self, '提示', '请先运行测试集.')
            return
        
        if not Path(allure_log_path, UID_FILE).is_file():
            QMessageBox.information(self, '提示', '运行结果不完整, 请重新运行测试集.')
            return
        '''
        if not allure_report_path.is_dir():
            allure_report_path.mkdir()
              
        if not isSameID(Path(allure_log_path, UID_FILE), Path(allure_report_path, UID_FILE)):
            uid = Path(allure_log_path, UID_FILE).read_text()
            
            allure_cmd = self.config['allure_cmd']
            
            try:
                self.runCmd(f'{allure_cmd}  generate -c "{allure_log_path}" -o "{allure_report_path}"') 
            except Exception as e:
                self.logView.append(str(e)+'\n')
                self.process = None
                return
            
            while None != self.process :
                qApp.processEvents()
                 
            Path(allure_report_path, UID_FILE).write_text(uid)
        '''     
        self.reportView.openReport(allure_report_path)
        
    def onCheckTestCase(self):
        self.onSaveAllFiles()
        try:
            self.runCmd(f'behave -d') 
        except Exception as e:
            self.logView.append(str(e)+'\n')
            self.process = None    
        else:    
            while None != self.process :
                qApp.processEvents()
    
    def onCodeDebug(self):
        pass

    def onProcessOut(self, text):
        self.logView.append(text)
    
    def onProcessStoped(self, ret_code):
        self.process = None
        self.processThread = None
        self.logView.append(f'RUN: Process Stoped with exit code {ret_code}\n')
        
    def runCmd(self, cmd):    
        
        self.showLogView(True)
        self.logView.append(f'RUN: {cmd}\n')
        self.process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.processThread = ProcessOutThread(self.process)
        self.processThread.output.connect(self.onProcessOut)
        self.processThread.stoped.connect(self.onProcessStoped)
        self.processThread.start()
    
    def locateCode(self, code_str, show = True):
        def match_str(match_str, text):
            match = re.findall(match_str, text)
            if match:
                pos = text.find(match[0]) + len(match[0])
                line_pos = len(text[:pos].split("\n"))
                #print(f"Matched {name}", match[0], pos, line_pos)
                return line_pos
            return None
            
        #Find in Features    
        for name,feature in self.testManager.features.items():
            #print(f'Matching: {name}')
            text = feature.py_file.read_text(encoding = 'utf-8')             
            line_pos = match_str(code_str, text)
            if line_pos:
                print(f"Matched {name}", line_pos)
                if show :
                    panel = self.editFeature(feature)
                    panel.pythonEditor.setCursorPosition(line_pos, 0) #linefocus, colfocus)
                    panel.pythonEditor.ensureCursorVisible()
                    panel.pythonEditor.setFocus()
                return True
                
        #Find in Free Python Files        
        for py_file in self.testManager.free_py_files:
            #print(f'Matching: {py_file}')
            text = py_file.read_text(encoding = 'utf-8')             
            line_pos = match_str(code_str, text)
            if line_pos:
                print(f"Matched {py_file}", line_pos)
                if show :
                    panel = self.editPython(py_file)
                    panel.pythonEditor.setCursorPosition(line_pos, 0) #linefocus, colfocus)
                    panel.pythonEditor.ensureCursorVisible()
                    panel.pythonEditor.setFocus()
                return True
        
        return False
        
    def onImportMultiCase(self):
    
        file_name, _ = QFileDialog.getOpenFileName(self,
                            "导入Excel文件选择",
                            "",
                            "Excel Files (*.xlsx;*.xls);;")
        
        if file_name == '':
            return
        
        folder = QFileDialog.getExistingDirectory(self, "选择导入目录", "")
        if folder == '': 
            return
            
        self.importExcelToMultiCase(file_name, folder)
    
    def onImportExcel(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                            "导入Excel文件", "", "Excel Files (*.xlsx;*.xls);;")
        
        if file_name == '':
            return
        
        self.importExcel(file_name)
    
    def onExportExcel(self):
        file_name, _ = QFileDialog.getSaveFileName(self,
                            "导出Excel文件", "", "Excel Files (*.xlsx;*.xls);;")
        
        if file_name == '':
            return
        try:
            self.exportExcel(file_name)
        except Exception as e:
            QMessageBox.information(self, '导出失败', str(e))
        else:    
            QMessageBox.information(self, '提示', f'成功导出到 [{file_name}]')
            
    def importExcel(self, file_name):
        records = pyexcel.get_records(file_name = file_name)
        if len(records) == 0:
            QMessageBox.information(self, '文件内容为空')
            return

        headers = records[1].keys()

        dlg = HeaderChoiceDialog(headers, self)
        headers_map = dlg.do_choice()
        if not headers_map:
            return
        
        self.newFeatureFromData(records, headers_map, self.testManager)
    
    def exportExcel(self, file_name):

        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        
        def write_row(sheet, row_no, row_values, style):
            for col_no, value in enumerate(row_values):
                sheet.write(row_no, col_no, value, style)
                
        book = xlwt.Workbook(encoding = 'utf-8')
        sheet = book.add_sheet('sheet1')
        
        head = ['功能', '场景', '操作步骤', '期望结果', '前置条件', '测试结果']
        write_row(sheet, 0, head, style)
        
        row = 1
        p = parser.Parser()
        for name, feature in self.testManager.features.items():
            items = ['' for i in range(6)]
            text = feature.feature_file.read_text(encoding = 'utf-8')
            model = p.parse(text)
            #items[0] = model.name
            for scenario in model.scenarios:
                items[1] = scenario.name
                op_names = []
                results = []
                for step in scenario.steps:
                    if step.step_type in ['given', 'when']:
                        op_names.append(step.name)
                    elif step.step_type == 'then':
                        results.append(step.name)
                items[4] = op_names.pop(0)
                items[2] = '\n'.join(op_names)
                items[3] = '\n'.join(results)     
                write_row(sheet, row, items, style)
                row += 1
            
        book.save(file_name)    
            
    def importExcelToMultiCase(self, file_name, folder):

        self.showLogView(True)
        
        '''
        headers = records[1].keys()

        dlg = HeaderChoiceDialog(headers, self)
        headers_map = dlg.do_choice()
        if not headers_map:
            return
        '''
        
        book = xlrd.open_workbook(file_name)
        self.logView.append(f"Opend: {file_name} ok.\n")
        for testcase_name in book.sheet_names():
            if testcase_name.startswith('Sheet'):
                print(f"Skiped default sheet : {testcase_name}")
                self.logView.append(f"Skiped default sheet : {testcase_name}")
                continue
            
            sheet = book.sheet_by_name(testcase_name)
            if sheet.nrows == 0:
                print(f"Skiped empty sheet : {testcase_name}")
                self.logView.append(f"Skiped empty sheet : {testcase_name}")
                continue
                
            print(f"Creating TestCase [{testcase_name}]")
            self.logView.append(f"Creating TestCase [{testcase_name}]")
                
            testcase_folder = Path(folder, testcase_name)
            if not testcase_folder.is_dir():
                testcase_folder.mkdir()
            
            manager = TestCaseManager(self.templates_folder)
            
            if not manager.isTestCaseFolder(testcase_folder):
                manager.newTestCase(testcase_folder)
            else:
                manager.openTestCase(testcase_folder)
            
            qApp.processEvents()
            
            self.newFeatureFromData(sheet, headers_map, manager)

    def newFeatureFromData(self, records, header_map, manager):
        
        count = 0
        hdr = header_map

        def is_empty_line(line):
            for it in line:
                if str(it).strip() != '':
                    return False
            return Trues
            
        def clean_steps(items):
            ll = list(filter(lambda x : len(str(x).strip()) > 0, items))
            print(ll)
            return [str(x) for x in ll]

        def build_scenario_from_record(record):
            scenario_name = record[hdr['scenario_name']]
            givens = clean_steps(record[hdr['given_steps']].split('\n'))
            given_steps = [f'前置_{it}' for it in givens]
            when_steps = clean_steps(record[hdr['when_steps']].split('\n'))
            then_steps = record[hdr['then_steps']].strip().split('\n')
            step_data = record[hdr['sample_data']] if 'sample_data' in hdr else ''
            tag_val = record[hdr['tag_name']] if 'tag_name' in hdr else None
            
            if tag_val:
                tag = f'{hdr["tag_name"]}.{tag_val}'
            else:
                tag = None    

            return Scenario(scenario_name, given_steps, when_steps, then_steps, step_data, tag)
        
        def newFeatureFor(name, scenarios, all_sets):
             nonlocal count
             count += 1
             feature_name = f'{count:03d}.{name}'
             if feature_name in manager.features:
                 #print(f"Skiping {feature_name}.")
                 self.logView.append(f"Skiping {feature_name}.")
             else:
                 manager.newFeatureWith(feature_name, scenarios, all_sets)
                 #print(f'Feature {feature_name} commited.')
                 self.logView.append(f'Feature {feature_name} commited.')
                
        all_sets = [set(), set(), set()]
        feature_name = None
        scenarios = []
        
        for line_no, record in enumerate(records):
            
            qApp.processEvents()
            
            name = record[hdr['feature_name']]
            
            try:
                scenario = build_scenario_from_record(record)
            except Exception as e:
                self.logView.append(f'第{line_no}行, {record}, {str(e)}')
                tb = traceback.format_exc()
                self.logView.append(tb)
                break
            
            scenarios.append(scenario)
                    
            #新的Feature
            if not feature_name: 
                feature_name = name
                #print(f"Found New Feature {feature_name}")
                self.logView.append(f"Found New Feature {feature_name}")
                    
            #老Feature的新场景
            elif name == feature_name: 
                print(f"    Feature {feature_name} append scenario {scenario.name}")
                
            #遇到新feature,先把老Feature的数据提交处理
            else:
                newFeatureFor(feature_name, scenarios, all_sets)
                name = None
                feature_name = None
                scenarios = []
            
            #遇到最后一行, 把老Feature的数据提交处理    
            if line_no == (len(records) - 1): 
                if feature_name and scenarios:
                    newFeatureFor(feature_name, scenarios, all_sets)
                break
        self.logView.append('导入完成。')
                
    def onNewFeature(self):
        feature_name, ok = QInputDialog.getText(self, "输入", "请输入新建Feature名:", QLineEdit.Normal, "")
        if ok and feature_name != '':
            self.testManager.newFeature(feature_name)
            self.editFeature(self.testManager.features[feature_name])
            
    def onFeatureRenamed(self, feature, new_feature):
        file_name = str(feature.feature_file)
        new_file_name = str(new_feature.feature_file)
        
        panels = self.getPanels()
        if file_name in panels:
            index = panels.index(file_name)
            self.tabView.setTabText(index, new_file_name)
            panel = self.tabView.widget(index)
            panel.featureFile = new_feature.feature_file
            panel.pythonFile = new_feature.py_file
            
    def onFeatureDeleted(self, feature):
        file_name = feature.feature_file
        self.onFileDeleted(feature.path, feature.feature_file)
        
    def onFileRenamed(self, path, file_name, new_file_name):
        
        print(f"File [{file_name}] renamed to [{new_file_name}]")
        
        panels = self.getPanels()
        if str(file_name) in panels:
            index = panels.index(str(file_name))
            panel = self.tabView.widget(index)
            self.tabView.setTabText(index, str(new_file_name))
            panel.feature_file = Path(path, new_file_name)
        elif file_name.suffix.lower() in ['.py', '.py_']:
            print("got py file")
            
    
    def onFileDeleted(self, path, file_name):
        #print(f"onFileDeleted: {file_name}")
        name = str(file_name)
        panels = self.getPanels()
        if name in panels:
            index = panels.index(name)
            self.tabView.removeTab(index) 
    
    def onFileContentChanged(self, target_path):
        for index in range(self.tabView.count()):
            panel = self.tabView.widget(index)
            if (panel.featureFile == target_path) or (panel.pythonFile == target_path):
                print(f"File Content Changed [{target_path}].")
                continue
                YesNo = QMessageBox.question(self, '确认', f'打开编辑的文件{target_path}内容已经被外部程序修改, 要重新加载么?', 
                        QMessageBox.Yes | QMessageBox.No , QMessageBox.Yes)
                if YesNo == QMessageBox.Yes:
                    panel.reload(target_path)
    
    def onShowMaxFeatureWin(self):
        self.showLogView(False)
        curr_panel = self.tabView.currentWidget()
        curr_panel.showSplit(99)
    
    def onShowMaxCodeWin(self):
        self.showLogView(False)
        curr_panel = self.tabView.currentWidget()
        curr_panel.showSplit(0)
        
    def onSaveAllFiles(self):
        self.testManager.stopWatch()
        
        for index in range(self.tabView.count()):
            panel = self.tabView.widget(index)
            panel.onSave()
        
        self.testManager.startWatch()
            
    def onSaveFile(self):
        panel = self.tabView.currentWidget()
        self.testManager.stopWatch()
        panel.onSave()
        self.testManager.startWatch()
        
    def onUndo(self):
        panel = self.tabView.currentWidget()
        panel.onUndo()
        
    def onRedo(self):
        panel = self.tabView.currentWidget()
        panel.onRedo()
        
    def onCut(self):
        panel = self.tabView.currentWidget()
        panel.onCut()
        
    def onCopy(self):
        panel = self.tabView.currentWidget()
        panel.onCopy()
        
    def onPaste(self):
        panel = self.tabView.currentWidget()
        panel.onPaste()
    
    def onSearch(self):
        panel = self.tabView.currentWidget()
        #panel.onPaste()
        
    def createActions(self):
            
        self.newTestAction = QAction(
            "新建测试集目录", 
            self, 
            statusTip="新建测试集", 
            triggered=self.onNewTestCase)
        
        self.openTestAction = QAction(
            "打开测试集目录", 
            self, 
            statusTip="打开测试集", 
            triggered=self.onOpenTestCase)
        
        self.closeTestAction = QAction(
            "关闭测试集", 
            self, 
            statusTip="关闭测试集", 
            triggered=self.onCloseTestCase)
        
        self.closeTestAction.setEnabled(False)

        self.saveTestAction = QAction(
            "保存测试集",
            self,
            statusTip="保存测试集",
            triggered=self.onSaveAllFiles)
        
        self.runTestAction = QAction(
            "运行测试集",
            self,
            statusTip="运行测试集",
            triggered=self.onRunTestCase)
        
        self.viewReportAction = QAction(
            "查看报告",
            self,
            statusTip="查看报告",
            triggered=self.onViewReport)
        
        self.checkTestAction = QAction(
            "检查",
            self,
            statusTip="检查测试集",
            triggered=self.onCheckTestCase)
        
        self.codeDebugAction = QAction(
            "调试",
            self,
            statusTip="代码调试",
            triggered=self.onCodeDebug)
        
        '''    
        self.newFileAction = QAction(
            "New File",
            self,
            statusTip="新建Feature",
            triggered=self.onNewFile)
        
        self.removeFileAction = QAction(
            "Remove File",
            self,
            statusTip="删除Feature文件",
            triggered=self.onRemoveFile)
        '''
        
        self.saveFileAction = QAction(
            "Save File",
            self,
            statusTip="保存文件",
            triggered=self.onSaveFile)
        
        self.importExcelAction = QAction(
            "导入Excel测试用例",
            self,
            statusTip="导入Excel文件到当前目录",
            triggered=self.onImportExcel)
        
        self.exportExcelAction = QAction(
            "导出Excel测试用例",
            self,
            statusTip="导出到Excel文件",
            triggered=self.onExportExcel)
        
        self.importMultiCaseAction = QAction(
            "导入目录",
            self,
            statusTip="导入Excel文件到多个目录",
            triggered=self.onImportMultiCase)
        
        self.showFeatureViewAction = QAction(
            "显示Feature窗口",
            self,
            statusTip = "显示Feature", 
            checkable = True,
            triggered = self.showFeatureView)
        
        self.showLogViewAction = QAction(
            "显示Log窗口",
            self,
            statusTip = "显示Log窗口",
            checkable = True,
            triggered = self.showLogView)
        
        self.showMaxFeatureWinAction = QAction(
            "Feature",
            self,
            statusTip="最大化Feature窗口",
            triggered=self.onShowMaxFeatureWin)
        
        self.showMaxCodeWinAction = QAction(
            "Code",
            self,
            statusTip="最大化Code窗口",
            triggered=self.onShowMaxCodeWin)
        
        self.searchAction = QAction(
            "搜索",
            self,
            statusTip="搜索",
            triggered=self.onSearch)
                
        self.aboutAction = QAction(
            "&About",
            self,
            statusTip="Show the application's About box",
            triggered=self.about)
            
    def createEditActions(self):
    
        ids = ["undo", "redo", "cut", "copy", "paste", 'save', 'saveall']
        icons = [
            "edit-undo.png", "edit-redo.png", "edit-cut.png", "edit-copy.png",
            "edit-paste.png", "save.png", "save-all.png"
        ]
        shortcuts = [
            'Ctrl+Z', 'Ctrl+Y', 'Ctrl+X', 'Ctrl+C',
            'Ctrl+V', 'Ctrl+S','Ctrl+Shift+S'
        ]
        connects = [
            self.onUndo, self.onRedo, self.onCut, self.onCopy, self.onPaste, self.onSaveFile, self.onSaveAllFiles
        ]

        l = []
        for i in range(len(ids)):
            a = QAction(QIcon("images/" + icons[i]), ids[i], self)
            a.setShortcut(shortcuts[i])
            a.triggered.connect(connects[i])
            l.append(a)

        return l
        
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addSeparator()
        #self.fileMenu.addAction(self.closeAction)
        #self.fileMenu.addAction(self.exitAction)

        #self.menuBar().addSeparator()
        self.editMenu = self.menuBar().addMenu("&Edit")
        
        self.winMenu = self.menuBar().addMenu("&Windows")
        self.winMenu.addAction(self.showFeatureViewAction)
        self.winMenu.addAction(self.showLogViewAction)
        
        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAction)

    def createToolBars(self):

        self.tb1 = self.addToolBar("TestCase")
        self.tb1.addAction(self.newTestAction)
        self.tb1.addAction(self.openTestAction)
        self.tb1.addAction(self.closeTestAction)
        
        self.tb2 = self.addToolBar("Import")
        self.tb2.addAction(self.importExcelAction)
        self.tb2.addAction(self.exportExcelAction)
        self.tb2.addAction(self.importMultiCaseAction)
        
        l = self.createEditActions() 
        self.tbEdit = self.addToolBar("Edit")
        for i in l:
            self.tbEdit.addAction(i)
        self.tbEdit.addAction(self.showMaxFeatureWinAction)
        self.tbEdit.addAction(self.showMaxCodeWinAction)

        self.tbEdit.addAction(self.searchAction)
        
        self.addToolBar(self.tbEdit)
        
        self.tbRun = self.addToolBar("Run")
        self.tbRun.addAction(self.runTestAction)
        self.tbRun.addAction(self.viewReportAction)
        self.tbRun.addAction(self.checkTestAction)
        self.tbRun.addAction(self.codeDebugAction)
        
        #self.tbShowWin = self.addToolBar("ShowWin")
        #self.tbShowWin.addAction(self.showMaxCodeWinAction)
        
        
        #self.toolbar.addAction(self.exitAction)
    
        self.statusBar().showMessage("Ready")
    
    def closeEvent(self, event):
        changed = False
        
        for index in range(self.tabView.count()):
            panel = self.tabView.widget(index)
            if panel.isFileChanged():
                feature = self.tabView.tabText(index)
                YesNo = QMessageBox.question(self, '确认', f'文件[{feature}]内容已经修改, 要保存吗?', 
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            
                if YesNo == QMessageBox.Cancel:
                    event.ignore()
                    return
                if YesNo == QMessageBox.Yes:
                    panel.onSave()
                
        event.accept()
        self.writeSettings()
        
    def readSettings(self):

        settings = QSettings('WalkerLi', APP_NAME)

        pos = settings.value('pos', QPoint(200, 50))
        size = settings.value('size', QSize(600, 600))
        test_path = Path(settings.value('last_test_path', ''))
        opened = settings.value('opened',[])
        active = settings.value('active_tab', None)
        is_win_max = settings.value('win_maxed', False)
        
        self.move(pos)
        if is_win_max:
            print('is_win_max', is_win_max)
            self.showMaximized()
        else:
            self.resize(size)
        
        self.config['allure_cmd'] = settings.value('allure_cmd', 'allure.bat')

        if test_path.is_dir():
            if not self.testManager.openTestCase(test_path):
                return
            for name in opened:
                file_name = Path(name)
                ext = file_name.suffix.lower() 
                if ext in ['.py', '.py_']:
                    self.editPython(file_name)
                elif (ext in ['.feature', 'feature_']) and (file_name.stem in self.testManager.features):
                    feature = self.testManager.features[file_name.stem]
                    self.editFeature(feature)
        
            panels = self.getPanels()   
            if active and active in panels:
                index = panels.index(active)
                self.tabView.setCurrentIndex(index)
            
    def writeSettings(self):

        settings = QSettings('WalkerLi', APP_NAME)

        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
        settings.setValue('win_maxed', self.isMaximized())
        
        settings.setValue('last_test_path', str(self.testManager.path)) 
        settings.setValue('opened', self.getPanels()) 
        settings.setValue('active_tab', self.tabView.tabText(self.tabView.currentIndex())) 
        
        settings.setValue('allure_cmd', self.config['allure_cmd'])
        
    def about(self):
        pass
                
#---------------------------------------------------------------#
class AutoHaveApp(QApplication):
    def __init__(self, argv):
        super().__init__([])
        self.argv = argv
        self.mainWin = MainWindow()
        self.mainWin.show()
        
#---------------------------------------------------------------#
def run():
    app = AutoHaveApp(sys.argv)
    sys.exit(app.exec_())
    