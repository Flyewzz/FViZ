from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

class PhysicalWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        print(f"[JS console] {msg} (line {line})")

    def contextMenuEvent(self, event):
        event.accept()

        pos = event.pos()
        global_pos = self.mapToGlobal(pos)

        self.page().runJavaScript(f"""
            (function() {{
                const x = {pos.x()} + window.scrollX;
                const y = {pos.y()} + window.scrollY;

                const point = computeLT(x, y);

                if (window.pyqtObject && point) {{
                    const L = parseInt(point.L);
                    const T = parseInt(point.T);

                    const globalX = {global_pos.x()};
                    const globalY = {global_pos.y()};

                    window.pyqtObject.showContextMenu(L, T, globalX, globalY);
                }}
            }})();
        """)