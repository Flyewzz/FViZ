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
                const scale = field.stage.scaleX();
                const stagePos = field.stage.position();

                const localX = ({pos.x()} - stagePos.x) / scale;
                const localY = ({pos.y()} - stagePos.y) / scale;

                const cell = field.computeLT(localX, localY);

                if (window.pyqtObject && cell) {{
                    const L = parseInt(cell.L);
                    const T = parseInt(cell.T);
                    window.pyqtObject.showContextMenu(L, T, cell.group_name, {global_pos.x()}, {global_pos.y()});
                }}
            }})();
        """)