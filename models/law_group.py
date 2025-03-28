from models.law import Law


class LawGroup:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.laws = []  # список Law

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "laws": [law.to_dict() for law in self.laws]
        }

    @classmethod
    def from_dict(cls, data):
        group = cls(name=data["name"], color=data["color"])
        for law_data in data.get("laws", []):
            law = Law.from_dict(law_data, group)
            group.laws.append(law)
        return group