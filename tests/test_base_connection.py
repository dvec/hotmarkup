import logging
import unittest

from hotmarkup.base_connection import BaseConnection


class BaseConnectionMock(BaseConnection):
    def __init__(self, data, **kwargs):
        self._data = data
        self._stamp = 0
        self._dumps = []
        super().__init__(name='mock', **kwargs)

    def load(self):
        return self._data

    def stamp(self):
        return self._stamp

    def dump(self, data):
        self._dumps.append(data)


class TestBaseConnection(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_dict(self):
        mock = BaseConnectionMock({'a': 'b'})
        self.assertEqual(mock['a'], 'b')

    def test_list(self):
        mock = BaseConnectionMock([0, 2, 1])
        self.assertEqual(mock[1], 2)

    def test_reload(self):
        mock = BaseConnectionMock({'a': 'b'})
        mock._stamp = 1
        mock._data = {'a': 'c'}
        self.assertEqual(mock['a'], 'c')

    def test_reload_false(self):
        mock = BaseConnectionMock({'a': 'b'}, reload=False)
        mock._stamp = 1
        mock._data = {'a': 'c'}
        self.assertEqual(mock['a'], 'b')

    def test_dump(self):
        mock = BaseConnectionMock({'a': 'b'})
        mock['a'] = 'c'
        self.assertEqual(mock._dumps, [{'a': 'c'}])

    def test_dump_false(self):
        mock = BaseConnectionMock({'a': 'b'}, dump=False)
        mock['a'] = 'c'
        self.assertEqual(mock._dumps, [])

    def test_mutable_false(self):
        mock = BaseConnectionMock({'a': 'b'}, mutable=False)
        with self.assertRaises(RuntimeError):
            mock.a = 'c'

    def test_iter(self):
        mock = BaseConnectionMock(list(range(10)))
        expected = iter(range(10))
        for i in mock:
            self.assertEqual(i, next(expected))

    def test_slice(self):
        mock = BaseConnectionMock(list(range(10)))
        expected = iter(range(2, 7, 2))
        for i in mock[2:7:2]:
            self.assertEqual(i, next(expected))

    def test_func(self):
        mock = BaseConnectionMock(list(reversed(range(10))))
        mock.sort()
        self.assertEqual(mock._dumps, [list(range(10))])

    def test_item_get(self):
        mock = BaseConnectionMock({'a': 'b'})
        self.assertEqual(mock['a'], 'b')

    def test_item_set(self):
        mock = BaseConnectionMock({'a': 'b'})
        mock['a'] = 'c'
        self.assertEqual(mock['a'], 'c')

    def test_attr_get(self):
        mock = BaseConnectionMock({'a': 'b'})
        self.assertEqual(mock.a, 'b')

    def test_attr_set(self):
        mock = BaseConnectionMock({'a': 'b'})
        mock.a = 'c'
        self.assertEqual(mock.a, 'c')
