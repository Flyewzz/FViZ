class SystemGroup:
    """Системная группа (например, этаж в доме)"""
    def __init__(self, name, color, G, k):
        self.name = name
        self.color = color
        self.G = G  # Уникальный идентификатор
        self.k = k  # Второй уникальный идентификатор
        self.cells = {}  # 🔹 Мапа (L, T) -> PhysicalQuantity

    def add_quantity(self, quantity):
        """Добавляет физическую величину в карту LT"""
        self.cells[(quantity.L, quantity.T)] = quantity

    def remove_quantity(self, L, T):
        """Удаляет физическую величину из LT карты"""
        if (L, T) in self.cells:
            del self.cells[(L, T)]

    def get_quantity(self, L, T):
        """Быстро ищет физическую величину по LT"""
        return self.cells.get((L, T))

    def get_next_quantity(self, exclude_L, exclude_T):
        """Ищет любую другую физ. величину в группе"""
        for (L, T), quantity in self.cells.items():
            if (L, T) != (exclude_L, exclude_T):
                return quantity
        return None  # Если нет других величин

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "G": self.G,
            "k": self.k
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            color=data["color"],
            G=data["G"],
            k=data["k"]
        )