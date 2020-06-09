import os

from hotmarkup.base_connection import BaseConnection

try:
    import json
except ImportError as e:
    json = None

try:
    import pickle
except ImportError as e:
    pickle = None

try:
    import yaml
except ImportError as e:
    yaml = None


# noinspection PyAbstractClass
class FileConnection(BaseConnection):
    """All file connection types must inherit FileConnection.
    This class implements stamp function
    """
    def __init__(self, path, default=None, **kwargs):
        """Create new FileConnection

        Keyword arguments:
        path -- path to file with data
        default -- default data which will be used if file is empty or does not exists
        """
        self._path = path
        if default is not None and (not os.path.exists(path) or os.stat(path).st_size == 0):
            self.dump(default)
        super().__init__(name=path, **kwargs)

    def stamp(self):
        stamp = int(os.stat(self._path).st_mtime * 10000000)
        return stamp


class YamlConnection(FileConnection):
    """Yaml File Connection via PyYAML backend"""
    def __init__(self, *args, **kwargs):
        if yaml is None:
            raise RuntimeError('You need to install PyYAML to use YamlConnection')
        super().__init__(*args, **kwargs)

    def load(self):
        with open(self._path) as file:
            return yaml.safe_load(file)

    def dump(self, data):
        with open(self._path, 'w') as file:
            yaml.safe_dump(data, file, allow_unicode=True)


class JsonConnection(FileConnection):
    """Json File Connection via json backend"""
    def __init__(self, *args, **kwargs):
        if json is None:
            raise RuntimeError('You need to install json to use JsonConnection')
        super().__init__(*args, **kwargs)

    def load(self):
        with open(self._path) as file:
            return json.load(file)

    def dump(self, data):
        with open(self._path, 'w') as file:
            json.dump(data, file)


class PickleConnection(FileConnection):
    """Pickle File Connection"""
    def __init__(self, *args, **kwargs):
        if pickle is None:
            raise RuntimeError('You need to install pickle to use JsonConnection')
        super().__init__(*args, **kwargs)

    def load(self):
        with open(self._path, 'rb') as file:
            return pickle.load(file)

    def dump(self, data):
        with open(self._path, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
