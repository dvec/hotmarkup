import os

from hotmarkup.conenction import RootConnection, BASIC_TYPE


class FileConnection(RootConnection):
    """
    All file connection types must inherit FileConnection.
    This class implements stamp function
    """
    def __init__(self, path: str, default: BASIC_TYPE = None, override: BASIC_TYPE = None, **kwargs):
        """
        :param path path to file with data
        :param default default data which will be used if file is empty or does not exists
        :param override data that will dumped to file while creating FileConnection.
               If passed then default will be ignored
        """
        self._path: str = path
        if default is not None and override is None and \
                (not os.path.exists(path) or os.stat(path).st_size == 0):
            self.dump(default)
        if override is not None:
            self.dump(override)
        self._default: BASIC_TYPE = default
        self._override: BASIC_TYPE = override
        super().__init__(name=path, **kwargs)

    def load(self) -> BASIC_TYPE:
        return super(FileConnection, self).load()

    def dump(self, data: BASIC_TYPE):
        return super(FileConnection, self).dump(data)

    def stamp(self):
        stamp = int(os.stat(self._path).st_mtime * 10000000)
        return stamp


try:
    import yaml
except ImportError as e:
    yaml = None


class YamlConnection(FileConnection):
    """Yaml File Connection via PyYAML backend"""
    def __init__(self, *args, **kwargs):
        if yaml is None:
            raise RuntimeError('You need to install PyYAML to use YamlConnection')
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path) as file:
            data: BASIC_TYPE = yaml.safe_load(file)
        if not data:  # For case if file is empty
            if self._override is not None:
                data: BASIC_TYPE = self._override
            elif self._default is not None:
                data: BASIC_TYPE = self._default
            else:
                data: BASIC_TYPE = {}
        return data

    def dump(self, data: BASIC_TYPE):
        with open(self._path, 'w') as file:
            yaml.safe_dump(data, file, allow_unicode=True)


try:
    import json
except ImportError as e:
    json = None


class JsonConnection(FileConnection):
    """Json File Connection via json backend"""
    def __init__(self, *args, **kwargs):
        if json is None:
            raise RuntimeError('You need to install json to use JsonConnection')
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path) as file:
            data = json.load(file)
        if not data:  # For case if file is empty
            if self._override is not None:
                data = self._override
            elif self._default is not None:
                data = self._default
            else:
                data = {}
        return data

    def dump(self, data: BASIC_TYPE):
        with open(self._path, 'w') as file:
            json.dump(data, file)


try:
    import pickle
except ImportError as e:
    pickle = None


class PickleConnection(FileConnection):
    """Pickle File Connection"""
    def __init__(self, *args, **kwargs):
        if pickle is None:
            raise RuntimeError('You need to install pickle to use JsonConnection')
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path, 'rb') as file:
            return pickle.load(file)

    def dump(self, data: BASIC_TYPE):
        with open(self._path, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
