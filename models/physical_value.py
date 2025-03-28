class PhysicalQuantity:
    """Класс для представления физической величины"""

    def __init__(self, name, symbol, unit, value_c, group, L, T):
        """
        :param name: Название величины (например, "Сила")
        :param symbol: Условное обозначение (например, "F")
        :param unit: Единица измерения (например, "Н")
        :param value_c: Размерность в СИ (например, "M L T^{-2}")
        :param group: Системная группа, к которой принадлежит
        :param L: Координата L на сетке
        :param T: Координата T на сетке
        """
        self.name = name
        self.symbol = symbol
        self.unit = unit
        self.value_c = value_c
        self.group = group  # Ссылка на системную группу
        self.L = L
        self.T = T

    def __repr__(self):
        return f"PhysicalQuantity({self.name}, {self.symbol}, {self.unit}, {self.value_c}, Group={self.group.name}, L={self.L}, T={self.T})"

    def to_dict(self, visible=False):
        return {
            "name": self.name,
            "symbol": self.symbol,
            "unit": self.unit,
            "value_c": self.value_c,
            "L": self.L,
            "T": self.T,
            "group": self.group.name,
            "visible": visible  # только для экспорта
        }

    @classmethod
    def from_dict(cls, data, group):
        return cls(
            name=data["name"],
            symbol=data["symbol"],
            unit=data["unit"],
            value_c=data["value_c"],
            group=group,
            L=data["L"],
            T=data["T"]
        )