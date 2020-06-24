import logging
import shutil
import tempfile
import unittest

from hotmarkup.file_connection import YamlConnection, JsonConnection, CsvConnection, PickleConnection


class TestFileConnection(unittest.TestCase):
    TO_DICT_TEST = [YamlConnection, JsonConnection, PickleConnection]
    TO_LIST_TEST = [CsvConnection]

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.dir_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def _test_dict_file_connection(self, connection_type):
        path = tempfile.NamedTemporaryFile(dir=self.dir_path).name
        connection_type(path, default={'test_ok': False})
        connection = connection_type(path)
        self.assertEqual(connection.test_ok, False)
        connection.test_ok = True
        del connection
        connection = connection_type(path)
        self.assertEqual(connection.test_ok, True)

    def _test_list_file_connection(self, connection_type):
        path = tempfile.NamedTemporaryFile(dir=self.dir_path).name
        connection_type(path, default=[['field_1', 'field_2'], ['value_1', 'value_2']])
        connection = connection_type(path, as_dict=True)
        self.assertEqual(connection.to_basic(), [{'field_1': 'value_1', 'field_2': 'value_2'}])
        connection[0]['field_1'] = 'value_3'
        connection.append(['value_4', 'value_5'])
        del connection
        connection = connection_type(path, as_dict=True)
        print(connection.to_basic())
        self.assertEqual(connection[0]['field_1'], 'value_3')
        self.assertEqual(connection[1]['field_2'], 'value_5')

    def _test_empty_file(self, connection_type):
        connection = connection_type(tempfile.NamedTemporaryFile(dir=self.dir_path)
                                     .name, default={})
        self.assertEqual(connection.to_basic(), {})
        connection = connection_type(tempfile.NamedTemporaryFile(dir=self.dir_path)
                                     .name, default=[])
        self.assertEqual(connection.to_basic(), [])

    def _test_override_file(self, connection_type):
        path = tempfile.NamedTemporaryFile(dir=self.dir_path).name
        connection = connection_type(path, default={'a': 'b'}, override={'a': 'c'})
        self.assertEqual(connection.a, 'c')
        del connection
        connection = connection_type(path, override={'c': 'e'})
        self.assertEqual(connection.to_basic(), {'c', 'e'})

    def test(self):
        for connection_type in self.TO_DICT_TEST:
            self._test_dict_file_connection(connection_type)
            self._test_empty_file(connection_type)
        for connection_type in self.TO_LIST_TEST:
            self._test_list_file_connection(connection_type)
