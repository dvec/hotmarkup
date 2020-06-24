import logging
import unittest

from hotmarkup.conenction import RootConnection


class RootConnectionMock(RootConnection):
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
        mock = RootConnectionMock({'a': 'b'})
        self.assertEqual(mock['a'], 'b')

    def test_list(self):
        mock = RootConnectionMock([0, 2, 1])
        self.assertEqual(mock[1], 2)

    def test_multiple_level(self):
        mock = RootConnectionMock({'a': {'b': {'c': 'd'}}})
        mock.a.b.c = 'e'
        self.assertEqual(mock.a.b.c, 'e')

    def test_reload(self):
        mock = RootConnectionMock({'a': 'b'})
        mock._stamp = 1
        mock._data = {'a': 'c'}
        self.assertEqual(mock['a'], 'c')

    def test_reload_false(self):
        mock = RootConnectionMock({'a': 'b'}, reload=False)
        mock._stamp = 1
        mock._data = {'a': 'c'}
        self.assertEqual(mock['a'], 'b')

    def test_dump(self):
        mock = RootConnectionMock({'a': 'b'})
        mock['a'] = 'c'
        self.assertEqual(mock._dumps, [{'a': 'c'}])

    def test_dump_false(self):
        mock = RootConnectionMock({'a': 'b'}, dump=False)
        mock['a'] = 'c'
        self.assertEqual(mock._dumps, [])

    def test_mutable_false(self):
        mock = RootConnectionMock({'a': 'b'}, mutable=False)
        with self.assertRaises(RuntimeError):
            mock.a = 'c'

    def test_iter(self):
        mock = RootConnectionMock(list(range(10)))
        expected = iter(range(10))
        for i in mock:
            self.assertEqual(i, next(expected))

    def test_slice(self):
        mock = RootConnectionMock(list(range(10)))
        expected = iter(range(2, 7, 2))
        for i in mock[2:7:2]:
            self.assertEqual(i, next(expected))

    def test_func(self):
        mock = RootConnectionMock(list(reversed(range(10))))
        mock.sort()
        self.assertEqual(mock._dumps, [list(range(10))])

    def test_iadd(self):
        mock = RootConnectionMock([0, 1])
        mock += [2, 3]
        self.assertEqual(mock.to_basic(), [0, 1, 2, 3])

    def test_set_empty_basic(self):
        mock = RootConnectionMock({'a': 'b'})
        mock.c = {}
        mock.c.d = 'e'
        self.assertEqual(mock._dumps, [{'a': 'b', 'c': {}}, {'a': 'b', 'c': {'d': 'e'}}])

    def test_set_basic(self):
        mock = RootConnectionMock({'a': 'b'})
        mock.c = {'d': 'e'}
        self.assertEqual(mock._dumps, [{'a': 'b', 'c': {'d': 'e'}}])

    def test_item_get(self):
        mock = RootConnectionMock({'a': 'b'})
        self.assertEqual(mock['a'], 'b')

    def test_item_set(self):
        mock = RootConnectionMock({'a': 'b'})
        mock['a'] = 'c'
        self.assertEqual(mock['a'], 'c')

    def test_attr_get(self):
        mock = RootConnectionMock({'a': 'b'})
        self.assertEqual(mock.a, 'b')

    def test_attr_set(self):
        mock = RootConnectionMock({'a': 'b'})
        mock.a = 'c'
        self.assertEqual(mock.a, 'c')

    def test_to_basic(self):
        basic = {'a': 'b'}
        mock = RootConnectionMock(basic)
        self.assertEqual(mock.to_basic(), basic)

    def test_partly_immutable(self):
        mock = RootConnectionMock({'a': {'b': {'c': 'd'}}, 'e': {'f': 'g'}})
        mock.a.mutable = False
        with self.assertRaises(RuntimeError):
            mock.a.b.c = 'e'
        mock.a.mutable = True
        mock.a.b.c = 'e'
        self.assertEqual(mock.a.b.c, 'e')

    def test_add_log(self):
        mock = RootConnectionMock({})
        with self.assertLogs('mock', level=logging.INFO) as log:
            mock.a = 'b'
            self.assertEqual(log.output, ['INFO:mock:Mutation ADD mock.a=b'])

    def test_delete_log(self):
        mock = RootConnectionMock({'a': 'b'})
        with self.assertLogs('mock', level=logging.INFO) as log:
            del mock.a
            self.assertEqual(log.output, ['INFO:mock:Mutation DELETE mock.a'])

    def test_update_log(self):
        mock = RootConnectionMock({'a': 'b'})
        with self.assertLogs('mock', level=logging.INFO) as log:
            mock.a = 'c'
            self.assertEqual(log.output, ['INFO:mock:Mutation UPDATE mock.a=c'])

    def test_func_log(self):
        mock = RootConnectionMock({'a': [2, 3, 1, 0]})
        with self.assertLogs('mock', level=logging.INFO) as log:
            mock.a.sort()
            self.assertEqual(log.output, ['INFO:mock:Mutation FUNC mock.sort; new value: [0, 1, 2, 3]'])
