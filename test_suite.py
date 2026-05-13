import unittest
from unittest.mock import MagicMock, patch
import sys
import json

# Add src to path so we can import jupyterpilot_ai
sys.path.insert(0, "./src")

from jupyterpilot_ai.introspector import SchemaIntrospector
from jupyterpilot_ai.extension import JupyterPilotMagics
from jupyterpilot_ai.provider import LLMProvider

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.history import HistoryAccessorBase

class MockHistory(HistoryAccessorBase):
    def end_session(self):
        pass
    def reset(self, new_session=True):
        pass

class TestIntrospector(unittest.TestCase):
    def setUp(self):
        self.shell = MagicMock()
        self.shell.user_ns = {}
        self.introspector = SchemaIntrospector(self.shell)

    def test_mongo_introspection(self):
        # Mock PyMongo Database
        mock_db = MagicMock()
        # Ensure isinstance checks pass by patching _is_mongodb_db
        self.introspector._is_pandas_df = lambda x: False
        self.introspector._is_sqlalchemy_engine = lambda x: False
        self.introspector._is_mongodb_db = lambda x: x is mock_db
        
        mock_db.list_collection_names.return_value = ["userData"]
        
        # Mock cursor for find().sort().limit()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = [
            {"_id": "1", "name": "Alice", "age": 25},
            {"_id": "2", "name": "Bob", "role": "admin"}
        ]
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_collection.index_information.return_value = {
            "_id_": {"key": [("_id", 1)]},
            "name_idx": {"key": [("name", 1)]}
        }
        
        mock_db.__getitem__.return_value = mock_collection
        
        self.shell.user_ns = {"my_db": mock_db}
        
        context = self.introspector.get_context()
        
        self.assertIn("MongoDB Database 'my_db'", context)
        self.assertIn("Collection 'userData'", context)
        self.assertIn("_id", context)
        self.assertIn("age", context)
        self.assertIn("name", context)
        self.assertIn("role", context)
        self.assertIn("_id_(_id)", context)
        self.assertIn("name_idx(name)", context)

class TestProvider(unittest.TestCase):
    def setUp(self):
        self.provider = LLMProvider()

    def test_clean_code(self):
        markdown_code = "```python\nprint('hello')\n```"
        clean = self.provider._clean_code(markdown_code)
        self.assertEqual(clean, "print('hello')")

class TestMagics(unittest.TestCase):
    def setUp(self):
        self.shell = InteractiveShell.instance()
        self.shell.history_manager = MockHistory()
        self.shell.history_manager.input_hist_raw = [
            "x = 10"
        ]
        self.magics = JupyterPilotMagics(self.shell)
        self.magics.provider = MagicMock()
        self.magics.introspector = MagicMock()
        self.magics.introspector.get_context.return_value = ""

    def test_do_magic(self):
        self.magics.provider.generate.return_value = "print(x)"
        with patch.object(self.shell, 'set_next_input') as mock_set_input:
            self.magics.do("print the variable")
            mock_set_input.assert_called_once_with("print(x)")

    @patch('sys.last_traceback', True, create=True)
    @patch('sys.last_type', Exception, create=True)
    @patch('sys.last_value', Exception("Test error"), create=True)
    def test_fix_magic(self):
        self.magics.provider.generate.return_value = "x = 10"
        with patch.object(self.shell, 'set_next_input') as mock_set_input:
            with patch('traceback.format_exception', return_value=["Error trace"]):
                self.magics.fix("")
                mock_set_input.assert_called_once_with("x = 10")
                
                # Check provider was called with error context
                args, _ = self.magics.provider.generate.call_args
                self.assertIn("Code:", args[0])
                self.assertIn("Error:", args[0])

if __name__ == '__main__':
    unittest.main()
