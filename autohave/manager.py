# -*- coding: utf-8 -*-

import os, sys
import shutil
import copy
from pathlib import Path
import collections
from dataclasses import dataclass

#from jinja2 import Template
from mako.template import Template

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#---------------------------------------------------------------#
STEPS_PATH = 'steps'
PY_ENV_FILE = 'environment.py'
DEFAULT_ENV_FILE = 'default_environment.py'
FEATURE_TEMPLATE_FILE = 'template.feature'
#FEATURE_JINJA2_TEMPLATE_FILE = 'template.feature.jinja2'
FEATURE_MAKO_TEMPLATE_FILE = 'template.feature.mako'

PY_TEMPLATE_FILE = 'template_steps.py'
#PY_JINJA2_TEMPLATE_FILE = 'template_steps.py.jinja2'
PY_MAKO_TEMPLATE_FILE = 'template_steps.py.mako'

#---------------------------------------------------------------#
@dataclass
class Scenario:
    name: str
    given_steps: list
    when_steps:  list
    then_steps:  list
    step_data: str

#---------------------------------------------------------------#
class FeatureItem:
    def __init__(self, path, name, is_enabled = True):
        self.path = path
        self.name = name
        self.enable() if is_enabled else self.disable() 
        
    def enable(self):
        self.feature_file = Path(f'{self.name}.feature') 
        self.py_file = Path(STEPS_PATH, f'{self.name}_steps.py')  
        self.is_enabled = True
    
    def disable(self):
        self.feature_file = Path(f'{self.name}.feature_') 
        self.py_file = Path(STEPS_PATH, f'{self.name}_steps.py_')  
        self.is_enabled = False
    
    def clone(self):
        return copy.deepcopy(self)
    
    def copy_from(self, other):
        self.path =  other.path
        self.name =  other.name
        self.enable() if other.is_enabled else self.disable() 
        
    def __str__(self):
        return self.name
    
    #def full_feature_file(self):
    #    return Path(self.path, self.feature_file)
    
    #def full_py_file(self):
    #    return Path(self.path, self.py_file)
    
    def get_opposition_name(self):
        if self.is_enabled:
            return Path(f'{self.name}.feature_') 
        else:
            return Path(f'{self.name}.feature') 
            
#---------------------------------------------------------------#
class MyEventHandler(FileSystemEventHandler):
    def __init__(self, parent):
        self.parent = parent
        
    def on_modified(self, event):
        self.parent.onFileModified(event)
        
#---------------------------------------------------------------#
class TestCaseManager(QObject):
    
    testcase_opened = pyqtSignal([Path])
    testcase_closed = pyqtSignal([])
    
    feature_created = pyqtSignal([FeatureItem])
    feature_deleted = pyqtSignal([FeatureItem])
    feature_changed = pyqtSignal([FeatureItem])
    feature_renamed = pyqtSignal([FeatureItem, FeatureItem])
    
    file_renamed = pyqtSignal([Path, Path, Path])
    file_deleted = pyqtSignal([Path, Path])
    
    file_content_changed = pyqtSignal([Path])
    
    def __init__(self, templates_dir):
        super().__init__()
        
        self.path = None
        self.path_templates = Path(templates_dir).resolve()
        self.eventHandler = MyEventHandler(self)
        self.fileObserver = None
            
        self.clear()
        
    def clear(self):
        
        self.features = collections.OrderedDict()
        
        self.feature_files = {}
        self.py_files = {}
        
        self.free_py_files = []
    
    def getFeatureNames(self):
        return [ (self.features[key], self.features[key].is_enabled) for key in self.features ]
    
    def isTestCaseFolder(self, path):
        
        if not path.is_dir():
            return False 
        
        if not Path(path, STEPS_PATH).is_dir():
            return False
        
        return True    
        
    def newTestCase(self, path):
        
        #建立steps目录
        Path(path, STEPS_PATH).mkdir()
        
        #建立默认环境文件       
        full_env_file = Path(path, PY_ENV_FILE)
        env_template_file = Path(self.path_templates, DEFAULT_ENV_FILE)
        if env_template_file.is_file():
            shutil.copyfile(env_template_file, full_env_file)
        else:
            full_env_file.touch()
        
        return self.openTestCase(path)
    
    def openTestCase(self, path):
        
        if not path.is_dir():
            return False 
        
        steps_path = Path(path, STEPS_PATH)
        if not steps_path.is_dir(): 
            return False
            
        if  self.path != None:
            self.closeTestCase() 
        
        self.clear()
        self.path = Path(path).resolve()
       
        os.chdir(self.path)
        
        for filename in self.path.iterdir():
            ext = filename.suffix.lower()
            if ext == '.feature':
                self.__appendFeature(filename.stem)
            elif ext == '.feature_':
                self.__appendFeature(filename.stem, False)
        
        #未与Feature绑定的pyfile单独管理
        self.__reload_free_files()
        
        self.testcase_opened.emit(self.path)
        self.startWatch()
        
        return True
         
    def startWatch(self):    
        
        if self.path and self.path.is_dir():
            self.fileObserver = Observer()
            self.fileObserver.schedule(self.eventHandler, str(self.path), recursive=True)
            self.fileObserver.start()
        
        return True
        
    def stopWatch(self):    
    
        if None == self.fileObserver:
            return
            
        self.fileObserver.stop()
        self.fileObserver.join()
        self.fileObserver = None
    
    def onFileModified(self, event):    
        #print(f"{event.src_path} has been modified")
        target = Path(event.src_path)
        if target.is_file():
            self.file_content_changed.emit(target)
            
    def closeTestCase(self):
        
        if not self.path:
            return
            
        self.stopWatch()
        
        self.path = None
        self.clear()
        
        self.testcase_closed.emit()
    
    def __appendFeature(self, name, enabled = True):
        
        feature = FeatureItem(self.path, name, enabled)
        #print(f"__appendFeature {name} Enabled:{enabled}")
        self.features[name] = feature
        self.feature_files[feature.feature_file] = feature
        self.py_files[feature.py_file] = feature
        
        if feature.py_file in self.free_py_files:
            self.free_py_files.remove(feature.py_file)
            
        return feature
    
    def __removeFeature(self, feature):
        
        del self.features[feature.name]
        del self.feature_files[feature.feature_file]
        del self.py_files[feature.py_file]
        
    def __reload_free_files(self):
        self.free_py_files = []
        for filename in Path(self.path, STEPS_PATH).iterdir():
            if filename.suffix.lower() in ['.py', '.py_']:
                py_file = Path(STEPS_PATH, filename.name)
                if py_file not in self.py_files:               
                    self.free_py_files.append(py_file) 
        
    def newFeature(self, name):
        
        if name in self.features:
            return False
        
        feature = self.__appendFeature(name)
        
        feature_template_file = Path(self.path_templates, FEATURE_TEMPLATE_FILE)
        #full_feature_file = feature.full_feature_file()
        
        if feature_template_file.is_file():
            shutil.copyfile(feature_template_file, feature.feature_file)
        else:
            feature.feature_file.touch()
        
        print(f"Created File [{feature.feature_file}]")
        
        #full_python_file = feature.full_py_file()
        if feature.py_file.is_file():
            print(f"Binded Python File to feature [{feature.py_file}]")
        else:    
            python_template_file = Path(self.path_templates, PY_TEMPLATE_FILE)
            if python_template_file.is_file():
                shutil.copyfile(python_template_file, feature.py_file)
            else:
                feature.py_file.touch()
            print(f"Created File [{feature.py_file}]")
        
        self.feature_created.emit(feature)
        
        return True
    
    
    def newFeatureWith(self, name, scenarios, all_sets):
        
        if name in self.features: 
            return False
        
        feature = self.__appendFeature(name)
        
        feature_template_file = Path(self.path_templates, FEATURE_MAKO_TEMPLATE_FILE)
        
        template = Template(feature_template_file.read_text(encoding = 'utf-8') )
        text = template.render(name = name, scenarios = scenarios)
        
        #full_feature_file = feature.full_feature_file()
        #full_feature_file.write_text(text, encoding = 'utf-8')
        feature.feature_file.write_text(text, encoding = 'utf-8')
        print(f"Created File [{feature.feature_file}]")
        
        clean_scenarios = self.__merge(scenarios, all_sets)
        
        py_template_file = Path(self.path_templates, PY_MAKO_TEMPLATE_FILE)
        template = Template(py_template_file.read_text(encoding = 'utf-8') )
        text = template.render(scenarios = clean_scenarios)
        
        #full_py_file = feature.full_py_file()
        #full_py_file.write_text(text, encoding = 'utf-8')
        feature.py_file.write_text(text, encoding = 'utf-8')
        
        print(f"Created File [{feature.py_file}]")
        
        self.feature_created.emit(feature)
   
        return True
        
    def deleteFeature(self, name):    
        
        if name not in self.features:
            return False
            
        feature = self.features[name]
        feature.feature_file.unlink()        
        print(f"Deleted File: [{feature.feature_file}]")
        
        self.__removeFeature(feature)
        self.__reload_free_files()
        
        self.feature_deleted.emit(feature)
        
        return True
        
    def renameFeature(self, name, new_name):
        
        if name not in self.features:
            return False
        
        feature = self.features[name]
        new_feature = FeatureItem(self.path, new_name)
        
        self.__doRenameFeature(feature, new_feature)
        
        return True
        
    def changeFeatureStatus(self, name):
        
        if name not in self.features:
            return False 
        
        feature = self.features[name]
        new_feature = feature.clone()
        new_feature.disable() if new_feature.is_enabled else new_feature.enable() 
        #print('changeFeatureStatus to :', new_feature.name, new_feature.is_enabled)
        self.__doRenameFeature(feature, new_feature)
        
        #self.feature_changed.emit(new_feature)
        
        return True
        
    def __doRenameFeature(self, feature, new_feature):
        
        #feature_file = feature.feature_file
        #full_feature_file = feature.full_feature_file()
        #py_file = feature.py_file
        #full_py_file = feature.full_py_file()
            
        #new_feature_file = new_feature.feature_file
        #new_full_feature_file = new_feature.full_feature_file()
        
        if new_feature.feature_file.is_file():
            raise Exception(f'[{feature.feature_file}]改名为[{new_feature.feature_file}]失败，目标文件已经存在。')
        
        #new_py_file = new_feature.py_file
        #new_full_py_file = new_feature.full_py_file()
        
        if new_feature.py_file.is_file():
            raise Exception(f'[{feature.py_file}]改名为[{new_feature.py_file}]失败，目标文件已经存在。')
        
        feature.feature_file.rename(new_feature.feature_file)
        print(f'[{feature.feature_file}] 改名为 [{new_feature.feature_file}]')
        feature.py_file.rename(new_feature.py_file)
        print(f'[{feature.py_file}] 改名为 [{new_feature.py_file}]')
        
        self.__removeFeature(feature)
        self.__appendFeature(new_feature.name, new_feature.is_enabled)
        self.__reload_free_files()
        
        self.feature_renamed.emit(feature, new_feature)
        
    def deleteFreePython(self, py_file):
        real_file = Path(self.path, py_file)
        real_file.unlink()
        self.free_py_files.remove(py_file)
        print(f"Deleted File: [{real_file}]")
        
        self.file_deleted.emit(self.path, py_file)
    
    def __merge(self, scenarios, all_sets):
        
        def clean_add(steps, all_set):
            clean_steps = []
            for step in steps:
                if step not in all_set:
                    clean_steps.append(step)
                    all_set.add(step)
            return clean_steps
            
        all_given_set = all_sets[0]
        all_then_set = all_sets[1]
        all_when_set = all_sets[2]
        
        clean_scenarios = []
        
        for scen in scenarios:
            clean_given_steps = clean_add(scen.given_steps, all_given_set)
            clean_when_steps = clean_add(scen.when_steps, all_when_set)
            clean_then_steps = clean_add(scen.then_steps, all_then_set)
            
            clean_scenarios.append(Scenario(scen.name, clean_given_steps, clean_when_steps, clean_then_steps, scen.step_data))
        
        return clean_scenarios   