
import os
import logging
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
from PyQt5.QtWebEngineWidgets import *

from .utils import *

class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class MyHTTPServer(HTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""
    def __init__(self, base_path, server_address):
        self.base_path = base_path
        super().__init__(server_address, RequestHandlerClass=HTTPHandler)

#--------------------------------------------------------------#
class HttpDaemon(QThread):
    def __init__(self, base_path, port=5566):
        super().__init__()
        self.base_path = base_path
        self.port = port
        self._server = None

    def run(self):
        
        print("Server Thread Started.")
        self._server = MyHTTPServer(self.base_path, ('127.0.0.1', self.port))
        self._server.serve_forever()

    def stop(self):
        
        if not self._server:
            return
            
        self._server.shutdown()
        self._server.socket.close()
        self.wait()
        self._server = None
        
        print("Server Thread Stoped.")

#--------------------------------------------------------------#
class WebPage(QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)

#--------------------------------------------------------------#
class ReportView(QDockWidget):
    def __init__(self, parent):
        super().__init__('查看报表')
        
        self.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        
        self.parent = parent
        
        self.webView = QWebEngineView(self)    
        self.setWidget(self.webView)
        
        self.resize(800,600)
        
        self.server = None
        
        self.visibilityChanged.connect(self.onVisibilityChanged)
    
    def onVisibilityChanged(self, visible):
        if visible: 
            if self.server:
                self.server.start()
        else:
            if self.server:
                self.server.stop()
            
    #def closeEvent(self, event):
    #    super().closeEvent(event)
    #    print("closeEvent")
    #    event.skip()
        
    def openReport(self, path):
        
        port = find_free_port()
        
        self.server = HttpDaemon(path, port)
        self.server.start()
        self.page = WebPage(f"http://127.0.0.1:{port}")
        self.page.home()
        self.webView.setPage(self.page)
        self.show()
        