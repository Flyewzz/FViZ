class Law:
    def __init__(self, name, formula, description, variables, group):
        self.name = name
        self.formula = formula
        self.description = description
        self.variables = variables  # список из 4 названий физ. величин
        self.group = group  # ссылка на SystemGroup