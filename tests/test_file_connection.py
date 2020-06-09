import os
import tempfile
import shutil
import unittest

from hotmarkup.file_connection import YamlConnection, JsonConnection, PickleConnection


class TestFileConnection(unittest.TestCase):
    def setUp(self):
        self.dir_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def _test_file_connection(self, connection_type, filename):
        path = os.path.join(self.dir_path, filename)
        connection_type(path, default={'test_ok': False})
        connection = connection_type(path)
        self.assertEqual(connection.test_ok, False)
        connection.test_ok = True
        del connection
        connection = connection_type(path)
        self.assertEqual(connection.test_ok, True)

    def test_yaml_connection(self):
        self._test_file_connection(YamlConnection, 'test.yaml')

    def test_json_connection(self):
        self._test_file_connection(JsonConnection, 'test.json')

    def test_pickle_connection(self):
        self._test_file_connection(PickleConnection, 'test.pickle')
