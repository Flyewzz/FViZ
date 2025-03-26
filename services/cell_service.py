# services/cell_service.py
from models.law_group import LawGroup
from models.system_group import SystemGroup
from models.physical_value import PhysicalQuantity

class CellService:
    def __init__(self, webView):
        self.webView = webView
        self.system_groups = [
            SystemGroup("Группа 1", "#73ecfa", G=1, k=1),
            SystemGroup("Группа 2", "#fa73ec", G=2, k=2),
            SystemGroup("Группа 3", "#ecfa73", G=3, k=3)
        ]
        self.cells = {}
        self.selected = []

        self.law_groups = [
            LawGroup("Механика", "#ffaaaa"),
            LawGroup("Электродинамика", "#aaffaa"),
            LawGroup("Термодинамика", "#aaaaff"),
        ]

        self._fill_cells()
        self.send_all_to_webview()

    def _fill_cells(self):
        # Инициализация cells с тестовыми значениями — как в старом коде
        # 🔹 Заполняем сотами (примерные тестовые данные)
        self.cells = {
            (-2, -2): PhysicalQuantity("Частота", "f", "Гц", "T^{-1}", self.system_groups[0], -2, -2),
            (-2, -1): PhysicalQuantity("Ускорение", "a", "м/с²", "L T^{-2}", self.system_groups[0], -2, -1),
            (-2, 0): PhysicalQuantity("Давление", "p", "Па", "M L^{-1} T^{-2}", self.system_groups[0], -2, 0),
            (-2, 1): PhysicalQuantity("Мощность", "P", "Вт", "M L^2 T^{-3}", self.system_groups[0], -2, 1),
            (-2, 2): PhysicalQuantity("Магнитный поток", "Φ", "Вб", "M L^2 T^{-2} A^{-1}", self.system_groups[0], -2,
                                      2),

            (-1, -2): PhysicalQuantity("Вязкость", "η", "Па·с", "M L^{-1} T^{-1}", self.system_groups[0], -1, -2),
            (-1, -1): PhysicalQuantity("Сила", "F", "Н", "M L T^{-2}", self.system_groups[0], -1, -1),
            (-1, 0): PhysicalQuantity("Плотность", "ρ", "кг/м³", "M L^{-3}", self.system_groups[0], -1, 0),
            (-1, 1): PhysicalQuantity("Работа", "A", "Дж", "M L^2 T^{-2}", self.system_groups[0], -1, 1),
            (-1, 2): PhysicalQuantity("Поток энергии", "q", "Вт/м²", "M T^{-3}", self.system_groups[0], -1, 2),

            (0, -2): PhysicalQuantity("Скорость", "v", "м/с", "L T^{-1}", self.system_groups[1], 0, -2),
            (0, -1): PhysicalQuantity("Угловая скорость", "ω", "рад/с", "T^{-1}", self.system_groups[1], 0, -1),
            (0, 0): PhysicalQuantity("Масса", "m", "кг", "M", self.system_groups[1], 0, 0),
            (0, 1): PhysicalQuantity("Энергия", "E", "Дж", "M L^2 T^{-2}", self.system_groups[1], 0, 1),
            (0, 2): PhysicalQuantity("Сила тока", "I", "А", "I", self.system_groups[1], 0, 2),

            (1, -2): PhysicalQuantity("Импульс", "p", "кг·м/с", "M L T^{-1}", self.system_groups[2], 1, -2),
            (1, -1): PhysicalQuantity("Момент импульса", "L", "кг·м²/с", "M L^2 T^{-1}", self.system_groups[2], 1, -1),
            (1, 0): PhysicalQuantity("Объём", "V", "м³", "L^3", self.system_groups[2], 1, 0),
            (1, 1): PhysicalQuantity("Эл. напряжение", "U", "В", "M L^2 T^{-3} A^{-1}", self.system_groups[2], 1, 1),
            (1, 2): PhysicalQuantity("Электр. заряд", "q", "Кл", "A T", self.system_groups[2], 1, 2),

            (2, -2): PhysicalQuantity("Сопротивление", "R", "Ом", "M L^2 T^{-3} A^{-2}", self.system_groups[2], 2, -2),
            (2, -1): PhysicalQuantity("Электр. ёмкость", "C", "Ф", "M^{-1} L^{-2} T^4 A^2", self.system_groups[2], 2,
                                      -1),
            (2, 0): PhysicalQuantity("Длина", "l", "м", "L", self.system_groups[2], 2, 0),
            (2, 1): PhysicalQuantity("Температура", "T", "K", "Θ", self.system_groups[2], 2, 1),
            (2, 2): PhysicalQuantity("Кол-во вещества", "n", "моль", "N", self.system_groups[2], 2, 2),
        }

        for coords, cell in self.cells.items():
            cell.group.add_quantity(cell)

    def find_quantities_in_other_groups(self, L, T, current_group_name):
        result = []
        for group in self.system_groups:
            if group.name != current_group_name:
                q = group.get_quantity(L, T)
                if q:
                    result.append(q)
        return result

    def delete_cell(self, L, T, group_name):
        for group in self.system_groups:
            if group.name == group_name:
                quantity = group.get_quantity(L, T)
                if quantity:
                    group.remove_quantity(L, T)
                    other_quantities = self.find_quantities_in_other_groups(L, T, group_name)
                    if len(other_quantities) > 0:
                        self.update_web_cell(L, T, other_quantities[0])
                    else:
                        self.remove_web_cell(L, T)
                break

    def replace_cell(self, L, T, quantity):
        self.update_web_cell(L, T, quantity)

    def apply_edit(self, L, T, name, symbol, unit, value_c, new_group):
        if (L, T) not in self.cells:
            return
        current = self.cells[L, T]
        if current.group != new_group:
            del self.cells[L, T]
            current.group.remove_quantity(L, T)
            new = PhysicalQuantity(name, symbol, unit, value_c, new_group, L, T)
            new_group.add_quantity(new)
            self.cells[L, T] = new
        else:
            current.name = name
            current.symbol = symbol
            current.unit = unit
            current.value_c = value_c
        self.update_web_cell(L, T, self.cells[L, T])

    def create_cell(self, cell, group):
        self.cells[(cell.L, cell.T)] = cell
        group.add_quantity(cell)

        self.create_web_cell(cell.L, cell.T, cell)

    def create_web_cell(self, L, T, cell):
        """Создает соту в WebView"""
        self.webView.page().runJavaScript(f"""
            field.createCell({L}, {T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');
        """)

    def update_web_cell(self, L, T, cell):
        self.webView.page().runJavaScript(
            f"field.updateCell({L}, {T}, '{cell.name}', '{cell.symbol}', '{cell.value_c}', '{cell.group.name}', '{cell.group.color}');")

    def remove_web_cell(self, L, T):
        self.webView.page().runJavaScript(f"field.removeCell({L}, {T});")

    def get_all_groups(self):
        return self.system_groups

    def get_all_cells(self):
        return self.cells

    def get_cell_by_coords(self, L, T, group_name):
        for group in self.system_groups:
            if group.name == group_name:
                return group.cells.get((L, T))
        return None

    def toggle_selection(self, cell):
        if cell in self.selected:
            self.selected.remove(cell)
        else:
            print('selected', cell)
            self.selected.append(cell)

    def check_parallelogram(self):
        if len(self.selected) not in (3, 4):
            print("❌ Недостаточно выделенных элементов")
            return None

        items = self.selected.copy()

        # 1. Сортировка по L убыванию, затем T убыванию — для e1
        items.sort(key=lambda q: (-q.L, -q.T))
        e1 = items[0]

        # 2. Остальные сортируем по L и T по возрастанию
        rest = items[1:]
        rest.sort(key=lambda q: (q.L, q.T))

        if len(rest) < 2:
            print("❌ Недостаточно оставшихся для параллелограмма")
            return None

        e2, e3 = rest[0], rest[1]
        e4 = rest[2] if len(items) == 4 else e3  # как в оригинале

        def log_and_check(attr_name, fn):
            a = fn(e1) + fn(e2)
            b = fn(e3) + fn(e4)
            result = a == b
            print(f"⚖️  Проверка {attr_name}: {fn(e1)}+{fn(e2)} == {fn(e3)}+{fn(e4)} -> {'✅' if result else '❌'}")
            return result

        if all([
            log_and_check("G", lambda q: q.group.G),
            log_and_check("k", lambda q: q.group.k),
            log_and_check("L", lambda q: q.L),
            log_and_check("T", lambda q: q.T),
        ]):
            print("✅ Параллелограмм найден — передаём [e1, e3, e2, e4]")
            return [e1, e3, e2, e4]

        print("❌ Условия не выполнены")
        return None

    def send_all_to_webview(self):
        script = "\n".join(
            [
                f"field.createCell({L}, {T}, '{c.name}', '{c.symbol}', '{c.value_c}', '{c.group.name}', '{c.group.color}');"
                for (L, T), c in self.cells.items()
            ]
        )
        self.webView.page().runJavaScript(f"ensureFieldExists(() => {{ {script} }});")
