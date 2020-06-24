import logging
import shutil
import tempfile
import unittest

from hotmarkup.file_connection import YamlConnection, JsonConnection, PickleConnection


class TestFileConnection(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.dir_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def _test_dict_file_connection(self, connection_type):
        path = tempfile.NamedTemporaryFile(dir=self.dir_path).name
        connection_type(path, name='test_1', default={'a': 'b'})
        connection = connection_type(path, name='test_2')
        self.assertEqual(connection.a, 'b')
        connection.a = 'c'
        del connection
        connection = connection_type(path, name='test_3')
        self.assertEqual(connection.a, 'c')

    def _test_empty_file(self, connection_type):
        connection = connection_type(tempfile.NamedTemporaryFile(dir=self.dir_path)
                                     .name, name='test_1', default={})
        self.assertEqual(connection.to_basic(), {})
        connection = connection_type(tempfile.NamedTemporaryFile(dir=self.dir_path)
                                     .name, name='test_2', default=[])
        self.assertEqual(connection.to_basic(), [])

    def _test_override_file(self, connection_type):
        path = tempfile.NamedTemporaryFile(dir=self.dir_path).name
        connection = connection_type(path, default={'a': 'b'}, override={'a': 'c'})
        self.assertEqual(connection.a, 'c')
        del connection
        connection = connection_type(path, override={'c': 'e'})
        self.assertEqual(connection.to_basic(), {'c', 'e'})

    def test_yaml(self):
        self._test_dict_file_connection(YamlConnection)
        self._test_empty_file(YamlConnection)

    def test_json(self):
        self._test_dict_file_connection(JsonConnection)
        self._test_empty_file(JsonConnection)

    def test_pickle(self):
        self._test_dict_file_connection(PickleConnection)
        self._test_empty_file(PickleConnection)
