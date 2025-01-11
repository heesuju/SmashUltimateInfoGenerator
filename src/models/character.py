class Character():
    def __init__(self, **kwargs):
        self.custom:str = ""
        self.key:str = ""
        self.group:str = ""
        self.series:str = ""
        self.slots:list[int] = []
        self.update(**kwargs)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key.lower()):
                setattr(self, key.lower(), value)