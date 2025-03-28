class Law:
    def __init__(self, name, formula, description, variables, group):
        self.name = name
        self.formula = formula
        self.description = description
        self.variables = variables  # список из 4 названий физ. величин
        self.group = group  # ссылка на SystemGroup

        def to_dict(self):
            return {
                "name": self.name,
                "formula": self.formula,
                "description": self.description,
                "variables": self.variables  # список имён
            }

        @classmethod
        def from_dict(cls, data, group):
            return cls(
                name=data["name"],
                formula=data.get("formula", ""),
                description=data.get("description", ""),
                variables=data.get("variables", []),
                group=group
            )