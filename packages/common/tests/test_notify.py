import importlib
from unittest.mock import patch

notify = importlib.import_module("mcp_stash_common.notify")


@patch("mcp_stash_common.notify.subprocess.run")
@patch("mcp_stash_common.notify.platform.system", return_value="Linux")
@patch("mcp_stash_common.notify.shutil.which", return_value="/usr/bin/notify-send")
def test_notify_linux(mock_which, mock_system, mock_run):
    assert notify.notify("Title", "Message") is True
    mock_run.assert_called_once()


@patch("mcp_stash_common.notify.platform.system", return_value="Linux")
@patch("mcp_stash_common.notify.shutil.which", return_value=None)
def test_notify_linux_no_backend(mock_which, mock_system):
    assert notify.notify("Title", "Message") is False
