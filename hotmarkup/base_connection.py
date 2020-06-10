import logging
from collections import Iterable


class BaseConnection:
    """All connection types must inherit BaseConnection.
    This class implements all connection functionality except
    functions load, dump and stamp
    """
    def __init__(self, name=None, root=None, logger: logging.Logger = None, mutable=True, dump=True, reload=True):
        """Create new BaseConnection

        Keyword arguments:
        name -- connection name used for logging configuration (defaults to __name__)
        root -- root of connection. To create root connection use root=None
        logger -- logger for connection. If logger is set passing name is not necessary
        mutable -- if set to False connection will raise RuntimeError when __setattr__ or __setitem__ called
        dump -- if set to False connection will not call dump function
        reload -- if set to False connection will not check for stamp update
        """
        self._initialized = False
        self._root: BaseConnection = self if root is None else root
        if self._root is self:
            self._name = name or __name__
            self._mutable = mutable
            self._dump = dump
            self._reload = reload
            if logger is None:
                self._logger: logging.Logger = logging.getLogger(self._name)
            else:
                self._logger: logging.Logger = logger
            self._children = BaseConnection._from_basic(self.load(), self)._children
            self._cached_stamp = self.stamp()
            self._initialized = True
            self._logger.info(f'Loaded {name} config: {self.to_basic()}')

    @classmethod
    def _from_basic(cls, basic: Iterable, root):
        result = BaseConnection(root=root)
        if isinstance(basic, dict):
            result._children = {}
            for k, v in basic.items():
                if isinstance(v, dict) or isinstance(v, list):
                    result._children[k] = BaseConnection._from_basic(v, root)
                else:
                    result._children[k] = v
        elif isinstance(basic, Iterable):
            result._children = []
            for v in basic:
                if isinstance(v, dict) or isinstance(v, list):
                    result._children.append(BaseConnection._from_basic(v, root))
                else:
                    result._children.append(v)

        else:
            raise RuntimeError(f'Unknown basic {type(basic)}')
        result._initialized = True
        return result

    def __setitem__(self, key, value):
        if (isinstance(self._children, list) and self._children[key] == value) or \
                (isinstance(self._children, dict) and key in self._children and self._children[key] == value):
            return
        if self._initialized and not self._root._mutable:
            raise RuntimeError(f'Config {self._root._name} is immutable')
        self._root._logger.info(f'Setting \'{key}\' to \'{value}\'')
        self._children[key] = value
        if self._root._initialized:
            self._root._safe_dump()

    def __getitem__(self, item):
        if self._initialized and self._root is self and self._needs_reload():
            self._safe_load()
        return self._children[item]

    def __delitem__(self, key):
        del self._children[key]
        if self._root._initialized:
            self._root._safe_dump()

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
            return
        self[key] = value

    def __getattr__(self, item):
        if item.startswith('_') and not item.startswith('__'):
            return self.__dict__[item]
        if item in self._children.__dir__():
            if self._initialized and self._root is self and self._needs_reload():
                self._safe_load()

            def children_hash():
                return hash(tuple(self._children))

            def func(*args, **kwargs):
                before = children_hash()
                value = getattr(self._children, item)(*args, **kwargs)
                if self._root._initialized and before != children_hash():
                    if not self._root._mutable:
                        raise RuntimeError(
                            f'Called {type(self._children).__name__}.{item} for non-mutable instance')
                    self._root._safe_dump()
                return value

            return func
        return self[item]

    def __delattr__(self, item):
        del self[item]

    def __len__(self):
        if self._root is self and self._needs_reload():
            self._safe_load()
        return self.__getattr__('__len__')()

    def __iter__(self):
        if self._root is self and self._needs_reload():
            self._safe_load()
        return self.__getattr__('__iter__')()

    def __contains__(self, item):
        if self._root is self and self._needs_reload():
            self._safe_load()
        return self.__getattr__('__contains__')(item)

    def _needs_reload(self) -> bool:
        if not self._initialized:
            raise RuntimeError('Called _needs_reload for not initialized instance')
        if self._root is not self:
            raise RuntimeError('Called _needs_reload for not-root instance')
        if not self._reload:
            return False
        new_stamp = self.stamp()
        if self._initialized:
            self._root._logger.debug(f'Cached stamp: {self._cached_stamp} Current stamp: {new_stamp}')
        return self._cached_stamp != new_stamp

    def _safe_load(self):
        if self._root is not self:
            raise RuntimeError('Called _safe_load for non-root instance')
        self._root._logger.debug(f'Loading config')
        self._initialized = False
        self._children = BaseConnection._from_basic(self.load(), self)._children
        self._initialized = True

    def _safe_dump(self):
        if self._root is not self:
            raise RuntimeError('Called _safe_dump for non-root instance')
        if not self._root._mutable:
            raise RuntimeError(f'Called _safe_dump for non-mutable instance')
        if not self._root._dump:
            return
        self._root._logger.debug(f'Saving config')
        new_data = self.to_basic()
        self.dump(new_data)
        self._cached_stamp = self.stamp()

    def load(self) -> Iterable:
        """Returns parsed data e.g. list or dict. Calls when stamp changes"""
        raise NotImplementedError(f'Function \'load\' in {self.__class__.__name__} not implemented')

    def dump(self, data: Iterable):
        """Function called on data change if dump is True"""
        raise NotImplementedError(f'Function \'dump\' in {self.__class__.__name__} not implemented')

    def stamp(self) -> int:
        """Function called on every request if reload is True.
        If stamp does not equals previously saved stamp load function calls
        """
        raise NotImplementedError(f'Function \'stamp\' in {self.__class__.__name__} not implemented')

    def to_basic(self) -> Iterable:
        """Convert Connection to basic type (e.g. dict or list)"""
        if self._initialized and self._root is self and self._needs_reload():
            self._safe_load()
        if isinstance(self._children, dict):
            result = {}
            for name, value in self._children.items():
                if isinstance(value, BaseConnection):
                    result[name] = value.to_basic()
                else:
                    result[name] = value
        elif isinstance(self._children, Iterable):
            result = []
            for value in self._children:
                if isinstance(value, BaseConnection):
                    result.append(value.to_basic())
                else:
                    result.append(value)
        else:
            raise RuntimeError(f'Unknown children type: {type(self._children)}')
        return result
