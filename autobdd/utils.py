
import socket
from contextlib import closing

import behave
from behave import parser

#---------------------------------------------------------------#
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
        
#---------------------------------------------------------------#
def isSameID(file1, file2):
    
    if not file1.is_file():
        return False
        
    if not file2.is_file():
        return False
    
    uid1 = file1.read_text()
    uid2 = file2.read_text()
    
    return uid1 == uid2
    

#---------------------------------------------------------------#
def build_feature_index(feature_text):
    line_index = {}
    p = parser.Parser()
    feature = p.parse(feature_text)
    line_index[feature.line] = ('feature', feature)
    for scenario in feature.scenarios:
        line_index[scenario.line] = ('scenario', scenario)
        for step in scenario.steps:
            line_index[step.line] = ('step', step)
    return line_index
    