import logging
from enum import Enum
from typing import Union, Callable, Any

BASIC_TYPE = Union[dict, list]


class MutationType(Enum):
    ADD = 'ADD'
    DEL = 'DEL'
    SET = 'SET'


class Connection(object):
    """
    Connection class
    It implements base hotmarkup connection functionality
    """
    # noinspection PyProtectedMember
    def __init__(self, name: str, basic: BASIC_TYPE, parent,
                 change_callback: Callable[[str, MutationType, Any], None], check_actual: Callable[[], None]):
        """
        :param name: Connection name used for logging configuration (defaults to __name__)
        :param basic: Data for connection
        :param parent: Connection parent. If connection is root parent equals to self
        :param change_callback: Function that will be called on data change
        :param check_actual: Function that will be called to check if data is actual. If not function must reload data
        """
        self._parent: Connection = parent
        if parent is parent._parent:
            self._name: str = parent._name
        else:
            self._name: str = self._parent._name + '.' + name
            while parent is not parent._parent:
                parent: Connection = parent._parent
        self._root: RootConnection = parent
        self._logger: logging.Logger = self._root._logger
        self._mutable: bool = self._parent._mutable

        self._change_callback: Callable[[str, MutationType, Any], None] = change_callback
        self._check_actual: Callable[[], None] = check_actual

        self._load_from_basic(basic)

    def __setitem__(self, key, value):
        if (isinstance(self._children, list) and self._children[key] == value) or \
                (isinstance(self._children, dict) and key in self._children and self._children[key] == value):
            return
        if not self.mutable:
            raise RuntimeError(f'Value {self._name + "." + key} is immutable')
        existed: bool = key in self._children
        if isinstance(value, (list, dict)):
            self._children[key] = Connection(key, value, self, self._change_callback, self._check_actual)
        else:
            self._children[key] = value
        self._change_callback(self._name + '.' + key, MutationType.SET if existed else MutationType.ADD, value)

    def __getitem__(self, item):
        self._check_actual()
        return self._children[item]

    def __delitem__(self, key):
        del self._children[key]
        self._change_callback(self._name + '.' + key, MutationType.DEL, None)

    def __setattr__(self, key, value):
        if key.startswith('_') or key in dir(self) or key in dir(self.__class__):
            super(Connection, self).__setattr__(key, value)
            return
        self[key] = value

    def __getattr__(self, item):
        if item in dir(self) or item in dir(self.__class__):
            return super(Connection, self).__getattribute__(item)
        if item in self._children.__dir__():
            self._check_actual()

            def children_hash():
                return hash(tuple(self._children))

            def func(*args, **kwargs):
                before = children_hash()
                value = getattr(self._children, item)(*args, **kwargs)
                for child_index in range(len(self._children)):
                    if isinstance(self._children[child_index], BASIC_TYPE.__args__):
                        self._children[child_index] = Connection(str(child_index), self._children[child_index],
                                                                 self, self._change_callback, self._check_actual)
                if before != children_hash():
                    if not self.mutable:
                        raise RuntimeError(
                            f'Called {type(self._children).__name__}.{item} for non-mutable instance')
                    self._change_callback(self._name, MutationType.SET, self._children)
                return value

            return func
        return self[item]

    def __delattr__(self, item):
        del self[item]

    def __len__(self):
        return self._children.__len__()

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, item):
        return self._children.__contains__(item)

    def __iadd__(self, other):
        self._children.__iadd__(other)
        return self

    def _get_all_children(self):
        all_children = []
        for child in self._children:
            all_children.append(child)
            all_children.extend(child._get_all_children())
        return all_children

    def _load_from_basic(self, basic: BASIC_TYPE):
        if isinstance(basic, dict):
            self._children = {}
            for k, v in basic.items():
                if any(isinstance(v, x) for x in BASIC_TYPE.__args__):
                    self._children[k] = Connection(k, v, self, self._change_callback, self._check_actual)
                else:
                    self._children[k] = v
        elif isinstance(basic, list):
            self._children = []
            for e, v in enumerate(basic):
                if any(isinstance(v, x) for x in BASIC_TYPE.__args__):
                    self._children.append(Connection(str(e), v, self, self._change_callback, self._check_actual))
                else:
                    self._children.append(v)
        else:
            raise TypeError(f'Unknown basic {type(basic)}')

    def to_basic(self) -> BASIC_TYPE:
        """Convert Connection to basic type
        :return: dict or list
        """
        self._check_actual()
        if isinstance(self._children, dict):
            result = {}
            for name, value in self._children.items():
                if isinstance(value, Connection):
                    result[name] = value.to_basic()
                else:
                    result[name] = value
        elif isinstance(self._children, list):
            result = []
            for value in self._children:
                if isinstance(value, Connection):
                    result.append(value.to_basic())
                else:
                    result.append(value)
        else:
            raise TypeError(f'Unknown children type: {type(self._children)}')
        return result

    @property
    def mutable(self) -> bool:
        """
        mutable property
        When mutable.setter is called, change repeats for every child
        """
        return self._mutable

    @mutable.setter
    def mutable(self, value: bool):
        self._mutable = value
        for child in self._children:
            if isinstance(child, Connection):
                child.mutable = value


class RootConnection(Connection):
    """
    RootConnection class
    It implements
    """
    def __init__(self, name: str = None, logger: logging.Logger = None,
                 mutable: bool = True, dump: bool = True, reload: bool = True):
        """
        :param name: connection name used for logging configuration (defaults to __name__)
        :param logger: logger for connection. If logger is set passing name is not necessary
        :param mutable: if set to False connection will raise RuntimeError when __setattr__ or __setitem__ called
        :param dump: if set to False connection will not call dump function
        :param reload: if set to False connection will not check for stamp update
        """
        self._name: str = name or __name__
        self._logger: logging.Logger = logger or logging.getLogger(name)
        self._cached_stamp: int = self.stamp()
        self._mutable: bool = mutable
        self._dump: bool = dump
        self._reload: bool = reload
        super().__init__(name, self.load(), self, self._change_callback, self._check_actual)

    def _change_callback(self, name: str, mutation_type: MutationType, new_value):
        log_value = new_value.to_basic() if isinstance(new_value, Connection) else new_value
        self._logger.info(f'Registered {mutation_type.name} '
                          f'{f"{name}" if mutation_type == MutationType.DEL else f"{name}={log_value}"}')
        if self._dump is False:
            return
        self._logger.debug(f'Saving config')
        self.dump(self.to_basic())
        self._cached_stamp: int = self.stamp()

    def _check_actual(self):
        if self._reload is False:
            return
        new_stamp: int = self.stamp()
        self._root._logger.debug(f'Cached stamp: {self._cached_stamp} Current stamp: {new_stamp}')

        if self._cached_stamp != new_stamp:
            self._logger.debug(f'Loading config')
            self._load_from_basic(self.load())

    def load(self) -> BASIC_TYPE:
        """Returns parsed data e.g. list or dict. Calls when stamp changes"""
        raise NotImplementedError(f'Function \'load\' in {self.__class__.__name__} not implemented')

    def dump(self, data: BASIC_TYPE):
        """Function called on data change if dump is True"""
        raise NotImplementedError(f'Function \'dump\' in {self.__class__.__name__} not implemented')

    def stamp(self) -> int:
        """Function called on every request if reload is True.
        If stamp does not equals previously saved stamp load function calls
        """
        raise NotImplementedError(f'Function \'stamp\' in {self.__class__.__name__} not implemented')
