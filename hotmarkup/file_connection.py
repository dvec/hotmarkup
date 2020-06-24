import os

from hotmarkup.conenction import RootConnection, BASIC_TYPE


class FileConnection(RootConnection):
    """
    All file connection types must inherit FileConnection.
    This class implements stamp function
    """
    def __init__(self, path: str, name: str = None, default: BASIC_TYPE = None, override: BASIC_TYPE = None, **kwargs):
        """
        :param path path to file with data
        :param name connection name. Defaults to path
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
        super().__init__(name=name or path, **kwargs)

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
    def __init__(self, *args, loader=yaml.SafeLoader, dumper=yaml.SafeDumper, dumper_kwargs: dict = None, **kwargs):
        """
        :param loader: loader used to load data
        :param dumper: dumper used to dump data
        :param dumper_kwargs: kwargs for data dumper
        """
        if yaml is None:
            raise RuntimeError('You need to install PyYAML to use YamlConnection')
        self._loader = loader
        self._dumper = dumper
        self._dumper_kwargs = dumper_kwargs or {}
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path) as file:
            data: BASIC_TYPE = yaml.load(file, self._loader)
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
            yaml.dump(data, file, self._dumper, **self._dumper_kwargs)


try:
    import json
except ImportError as e:
    json = None


class JsonConnection(FileConnection):
    """Json File Connection via json backend"""
    def __init__(self, *args, parser_kwargs: dict = None, dumper_kwargs: dict = None, **kwargs):
        """
        :param parser_kwargs: kwargs for data parser
        :param dumper_kwargs: kwargs for data dumper
        """
        if json is None:
            raise RuntimeError('You need to install json to use JsonConnection')
        self._parser_kwargs = parser_kwargs or {}
        self._dumper_kwargs = dumper_kwargs or {}
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path) as file:
            data = json.load(file, **self._parser_kwargs)
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
            json.dump(data, file, **self._dumper_kwargs)


try:
    import pickle
except ImportError as e:
    pickle = None


class PickleConnection(FileConnection):
    """Pickle File Connection"""
    def __init__(self, *args, parser_kwargs: dict = None, dumper_kwargs: dict = None, **kwargs):
        """
        :param parser_kwargs: kwargs for data parser
        :param dumper_kwargs: kwargs for data dumper
        """
        if pickle is None:
            raise RuntimeError('You need to install pickle to use JsonConnection')
        self._parser_kwargs = parser_kwargs or {}
        self._dumper_kwargs = dumper_kwargs or {'protocol': pickle.HIGHEST_PROTOCOL}
        super().__init__(*args, **kwargs)

    def load(self) -> BASIC_TYPE:
        with open(self._path, 'rb') as file:
            return pickle.load(file, **self._parser_kwargs)

    def dump(self, data: BASIC_TYPE):
        with open(self._path, 'wb') as file:
            pickle.dump(data, file, **self._dumper_kwargs)
