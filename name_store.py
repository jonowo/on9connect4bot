import json
import os.path


class NameStore:
    def __init__(self, path: str) -> None:
        self.path = path
        if os.path.exists(path):
            with open(path) as f:
                self.data = json.load(f)
            self.data = {int(k): v for k, v in self.data.items()}
        else:
            self.data = {}

    def get(self, key) -> str:
        return self.data[key]

    def set(self, key, val) -> None:
        self.data[key] = val

    @staticmethod
    def load_from(cls, path: str) -> None:
        with open(path) as f:
            data = json.load(f)
        return cls(data)

    def save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.data, f)
