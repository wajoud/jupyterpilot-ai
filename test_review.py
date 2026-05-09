import unittest
from unittest.mock import MagicMock, patch
import sys

# Add src to path so we can import jupyterpilot_ai
sys.path.insert(0, "./src")

from jupyterpilot_ai.extension import JupyterPilotMagics

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.history import HistoryAccessorBase

class MockHistory(HistoryAccessorBase):
    def end_session(self):
        pass
    def reset(self, new_session=True):
        pass

class TestReviewMagic(unittest.TestCase):
    def setUp(self):
        # Use a real IPython shell to satisfy Traitlets validation
        self.shell = InteractiveShell.instance()
        self.shell.history_manager = MockHistory()
        self.shell.history_manager.input_hist_raw = [
            "import pandas as pd",
            "df = pd.DataFrame({'a': [1,2,3]})",
            "for i in range(len(df)): df.loc[i, 'b'] = df.loc[i, 'a'] * 2" # Inefficient code to review
        ]
        
        self.magics = JupyterPilotMagics(self.shell)
        
        # Mock the LLM provider and introspector
        self.magics.provider = MagicMock()
        self.magics.introspector = MagicMock()
        self.magics.introspector.get_context.return_value = "\n--- Data Schema Context ---\nMocked Context"
        
    @patch('IPython.display.display')
    @patch('IPython.display.Markdown')
    def test_review(self, mock_markdown, mock_display):
        # Set the mock return value for the LLM
        self.magics.provider.generate.return_value = "### Review\nThe loop is inefficient. Use vectorized operations instead:\n```python\ndf['b'] = df['a'] * 2\n```"
        
        # Trigger the %review magic
        self.magics.review("")
        
        # Verify the LLM was called with correct arguments
        self.magics.provider.generate.assert_called_once()
        args, kwargs = self.magics.provider.generate.call_args
        
        prompt = args[0]
        context = args[1]
        
        self.assertIn("Review the following code", prompt)
        self.assertIn("for i in range(len(df)): df.loc[i, 'b'] = df.loc[i, 'a'] * 2", prompt)
        
        self.assertIn("Mocked Context", context)
        self.assertIn("import pandas as pd", context)
        
        self.assertEqual(kwargs['raw'], True)
        self.assertEqual(kwargs['system_prompt'], "You are JupyterPilot, an expert code reviewer. Provide constructive feedback, point out potential bugs or inefficiencies, and offer an optimized version of the code. You can use markdown.")
        
        # Verify it formats and displays the markdown
        mock_markdown.assert_called_once_with("### Review\nThe loop is inefficient. Use vectorized operations instead:\n```python\ndf['b'] = df['a'] * 2\n```")
        mock_display.assert_called_once()

if __name__ == '__main__':
    unittest.main()
