# backend/bridge.py
class JSBridge:
    def __init__(self, webView):
        self.webView = webView

    def create_cell(self, cell):
        js = f"field.createCell({cell.L}, {cell.T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');"
        self.webView.page().runJavaScript(js)

    def update_cell(self, cell):
        js = f"field.updateCell({cell.L}, {cell.T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');"
        self.webView.page().runJavaScript(js)