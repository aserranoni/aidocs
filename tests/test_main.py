import unittest
import os
import json
from unittest.mock import patch, mock_open, call, Mock
from aidocs_pkg.main import setup, init, edit, check, AIDOCS_DIR, CONFIG_FILE, TEMPLATE_FILE, REAL_FILENAME, DEFAULT_CONFIG, DEFAULT_TEMPLATE

class TestAidocs(unittest.TestCase):

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_setup(self, mock_open_func, mock_exists, mock_makedirs):
        # Test when config and template files do not exist
        mock_exists.side_effect = [False, False] # config.json does not exist, template.md does not exist
        
        # Create separate mock file handles for each open call
        mock_config_file_handle = mock_open().return_value
        mock_template_file_handle = mock_open().return_value
        mock_open_func.side_effect = [mock_config_file_handle, mock_template_file_handle]

        setup()
        mock_makedirs.assert_called_once_with(AIDOCS_DIR, exist_ok=True)
        self.assertEqual(mock_exists.call_count, 2)
        self.assertEqual(mock_open_func.call_count, 2)
        
        # Check config file creation
        mock_open_func.assert_any_call(CONFIG_FILE, "w")
        written_config_content = "".join([c.args[0] for c in mock_config_file_handle.write.call_args_list])
        self.assertEqual(json.loads(written_config_content), DEFAULT_CONFIG)
        
        # Check template file creation
        mock_open_func.assert_any_call(TEMPLATE_FILE, "w")
        written_template_content = "".join([c.args[0] for c in mock_template_file_handle.write.call_args_list])
        self.assertEqual(written_template_content, DEFAULT_TEMPLATE)

        # Reset mocks for the next test case
        mock_makedirs.reset_mock()
        mock_exists.reset_mock()
        mock_open_func.reset_mock()

        # Test when config and template files already exist
        mock_exists.side_effect = [True, True] # config.json exists, template.md exists
        setup()
        mock_makedirs.assert_called_once_with(AIDOCS_DIR, exist_ok=True)
        self.assertEqual(mock_exists.call_count, 2)
        mock_open_func.assert_not_called()

    @patch('os.symlink')
    @patch('os.remove')
    @patch('os.path.islink')
    @patch('os.path.lexists')
    @patch('os.path.exists')
    @patch('os.chdir')
    @patch('os.getcwd', return_value='/current/dir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_init(self, mock_json_load, mock_open_func, mock_getcwd, mock_chdir, mock_exists, mock_lexists, mock_islink, mock_remove, mock_symlink):
        project_path = "/test/project"
        real_file_path = os.path.join(project_path, REAL_FILENAME)
        
        # Mock config file content
        mock_json_load.return_value = DEFAULT_CONFIG

        # Mock template file content
        mock_template_read_handle = mock_open(read_data=DEFAULT_TEMPLATE).return_value

        # --- Scenario 1: aidocs.md does not exist, no existing symlinked files ---
        mock_exists.side_effect = lambda path: {
            TEMPLATE_FILE: True,
            CONFIG_FILE: True,
            real_file_path: False,
        }.get(path, False)
        mock_lexists.return_value = False
        mock_islink.return_value = False

        # Mock open calls for template and aidocs.md
        mock_aidocs_md_write_handle_s1 = mock_open().return_value
        mock_open_func.side_effect = [
            mock_open(read_data=json.dumps(DEFAULT_CONFIG)).return_value, # For reading CONFIG_FILE (first time)
            mock_template_read_handle, # For reading TEMPLATE_FILE
            mock_aidocs_md_write_handle_s1, # For writing REAL_FILENAME
            mock_open(read_data=json.dumps(DEFAULT_CONFIG)).return_value, # For reading CONFIG_FILE (second time)
        ]

        init(project_path)

        # Assertions for Scenario 1
        mock_exists.assert_any_call(real_file_path)
        mock_open_func.assert_any_call(real_file_path, "w")
        mock_aidocs_md_write_handle_s1.write.assert_called_once_with(DEFAULT_TEMPLATE)
        mock_symlink.assert_any_call(REAL_FILENAME, "GEMINI.md")
        mock_symlink.assert_any_call(REAL_FILENAME, "CLAUDE.md")
        self.assertEqual(mock_symlink.call_count, len(DEFAULT_CONFIG["symlinks"]))
        mock_remove.assert_not_called()
        mock_chdir.assert_any_call(project_path)
        mock_chdir.assert_any_call('/current/dir')

        # Reset mocks for Scenario 2
        mock_exists.reset_mock()
        mock_lexists.reset_mock()
        mock_islink.reset_mock()
        mock_remove.reset_mock()
        mock_symlink.reset_mock()
        mock_chdir.reset_mock()
        mock_getcwd.reset_mock()
        mock_open_func.reset_mock()
        mock_json_load.reset_mock()

        # --- Scenario 2: aidocs.md exists, existing symlinked files with content ---
        existing_gemini_content = "Content from GEMINI.md"
        existing_claude_content = "Content from CLAUDE.md"
        existing_aidocs_md_content = "Existing aidocs.md content."

        gemini_path = os.path.join(project_path, "GEMINI.md")
        claude_path = os.path.join(project_path, "CLAUDE.md")

        mock_exists.side_effect = lambda path: {
            TEMPLATE_FILE: True,
            CONFIG_FILE: True,
            real_file_path: True,
            gemini_path: True,
            claude_path: True,
        }.get(path, False)
        mock_lexists.side_effect = lambda path: {
            gemini_path: True,
            claude_path: True,
        }.get(path, False)
        mock_islink.return_value = False # Indicate they are not symlinks

        mock_json_load.return_value = DEFAULT_CONFIG

        mock_config_read_handle_s2 = mock_open(read_data=json.dumps(DEFAULT_CONFIG)).return_value
        mock_gemini_read_handle_s2 = mock_open(read_data=existing_gemini_content).return_value
        mock_claude_read_handle_s2 = mock_open(read_data=existing_claude_content).return_value
        mock_aidocs_md_read_handle_s2 = mock_open(read_data=existing_aidocs_md_content).return_value
        mock_aidocs_md_write_handle_s2 = mock_open().return_value

        mock_open_func.side_effect = [
            mock_config_read_handle_s2, 
            mock_gemini_read_handle_s2, 
            mock_claude_read_handle_s2, 
            mock_aidocs_md_read_handle_s2, 
            mock_aidocs_md_write_handle_s2,
            mock_open(read_data=json.dumps(DEFAULT_CONFIG)).return_value, # For reading CONFIG_FILE (second time)
        ]

        init(project_path)

        # Assertions for Scenario 2
        mock_exists.assert_any_call(real_file_path)
        mock_open_func.assert_any_call(real_file_path, "w")
        expected_combined_content = existing_aidocs_md_content + \
                                    "\n\n--- Content from GEMINI.md ---\n\n" + existing_gemini_content + \
                                    "\n\n--- Content from CLAUDE.md ---\n\n" + existing_claude_content
        mock_aidocs_md_write_handle_s2.write.assert_called_once_with(expected_combined_content)
        mock_remove.assert_any_call(gemini_path)
        mock_remove.assert_any_call(claude_path)
        self.assertEqual(mock_remove.call_count, len(DEFAULT_CONFIG["symlinks"]))
        self.assertEqual(mock_symlink.call_count, len(DEFAULT_CONFIG["symlinks"]))
        mock_chdir.assert_any_call(project_path)
        mock_chdir.assert_any_call('/current/dir')

    @patch('os.path.exists')
    @patch('os.environ.get', return_value=None)
    @patch('sys.platform', 'darwin')
    @patch('subprocess.Popen')
    @patch('sys.exit', side_effect=SystemExit)
    def test_edit_darwin(self, mock_sys_exit, mock_popen, mock_environ_get, mock_exists):
        project_path = "/test/project"
        real_file_path = os.path.join(project_path, REAL_FILENAME)

        # Test case 1: aidocs.md does not exist
        mock_exists.return_value = False
        with self.assertRaises(SystemExit):
            edit(project_path)
        mock_sys_exit.assert_called_once_with(1)
        mock_popen.assert_not_called()
        mock_sys_exit.reset_mock()
        mock_popen.reset_mock()

        # Test case 2: aidocs.md exists, macOS
        mock_exists.return_value = True
        mock_popen.return_value.wait.return_value = 0 # Corrected mocking
        edit(project_path)
        mock_popen.assert_called_once_with(['open', '-W', '-t', real_file_path])
        mock_popen.return_value.wait.assert_called_once()
        mock_sys_exit.assert_not_called()
        mock_popen.reset_mock()

    @patch('os.path.exists')
    @patch('os.environ.get', return_value=None)
    @patch('sys.platform', 'win32')
    @patch('subprocess.Popen')
    @patch('sys.exit', side_effect=SystemExit)
    def test_edit_win32(self, mock_sys_exit, mock_popen, mock_environ_get, mock_exists):
        project_path = "/test/project"
        real_file_path = os.path.join(project_path, REAL_FILENAME)

        # Test case 1: aidocs.md does not exist
        mock_exists.return_value = False
        with self.assertRaises(SystemExit):
            edit(project_path)
        mock_sys_exit.assert_called_once_with(1)
        mock_popen.assert_not_called()
        mock_sys_exit.reset_mock()
        mock_popen.reset_mock()

        # Test case 2: aidocs.md exists, Windows
        mock_exists.return_value = True
        mock_popen.return_value.wait.return_value = 0 # Corrected mocking
        edit(project_path)
        mock_popen.assert_called_once_with(['notepad', real_file_path])
        mock_popen.return_value.wait.assert_called_once()
        mock_sys_exit.assert_not_called()
        mock_popen.reset_mock()

    @patch('os.path.exists')
    @patch('os.environ.get', return_value=None)
    @patch('sys.platform', 'linux')
    @patch('subprocess.Popen')
    @patch('sys.exit', side_effect=SystemExit)
    def test_edit_linux(self, mock_sys_exit, mock_popen, mock_environ_get, mock_exists):
        project_path = "/test/project"
        real_file_path = os.path.join(project_path, REAL_FILENAME)

        # Test case 1: aidocs.md does not exist
        mock_exists.return_value = False
        with self.assertRaises(SystemExit):
            edit(project_path)
        mock_sys_exit.assert_called_once_with(1)
        mock_popen.assert_not_called()
        mock_sys_exit.reset_mock()
        mock_popen.reset_mock()

        # Test case 2: aidocs.md exists, Linux, xdg-open found
        mock_exists.return_value = True
        mock_popen.return_value.wait.return_value = 0 # Corrected mocking
        edit(project_path)
        mock_popen.assert_called_once_with(['xdg-open', real_file_path])
        mock_popen.return_value.wait.assert_called_once()
        mock_sys_exit.assert_not_called()
        mock_popen.reset_mock()

        # Test case 3: aidocs.md exists, Linux, xdg-open not found, nano found
        mock_second_popen_instance = Mock()
        mock_second_popen_instance.wait.return_value = 0
        mock_popen.side_effect = [FileNotFoundError, mock_second_popen_instance] # Corrected mocking
        edit(project_path)
        mock_popen.assert_called_with(['nano', real_file_path])
        mock_second_popen_instance.wait.assert_called_once()
        mock_sys_exit.assert_not_called()
        mock_popen.reset_mock()

        # Test case 4: aidocs.md exists, Linux, no editor found
        mock_popen.side_effect = FileNotFoundError
        with self.assertRaises(SystemExit):
            edit(project_path)
        mock_sys_exit.assert_called_once_with(1)

    @patch('os.path.exists')
    @patch('os.environ.get')
    @patch('subprocess.Popen')
    @patch('sys.exit', side_effect=SystemExit)
    def test_edit_editor_env_var(self, mock_sys_exit, mock_popen, mock_environ_get, mock_exists):
        project_path = "/test/project"
        real_file_path = os.path.join(project_path, REAL_FILENAME)
        mock_exists.return_value = True
        mock_environ_get.return_value = "myeditor"
        mock_popen.return_value.wait.return_value = 0 # Corrected mocking

        edit(project_path)
        mock_environ_get.assert_called_once_with('EDITOR')
        mock_popen.assert_called_once_with(["myeditor", real_file_path])
        mock_popen.return_value.wait.assert_called_once()
        mock_sys_exit.assert_not_called()
        mock_popen.reset_mock()
        mock_environ_get.reset_mock()

    @patch('os.walk')
    @patch('os.path.islink')
    @patch('os.path.lexists')
    @patch('os.path.exists')
    @patch('os.readlink')
    @patch('builtins.open')
    @patch('json.load')
    def test_check(self, mock_json_load, mock_open_func, mock_readlink, mock_exists, mock_lexists, mock_islink, mock_walk):
        search_path = "/test/search"