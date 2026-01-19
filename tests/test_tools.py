import pytest
from unittest.mock import patch, MagicMock
from pr_review_agent.tools.terminal import SecurityManager, run_command
from pr_review_agent.tools.git import git_diff

class TestSecurityManager:
    def test_safe_command(self):
        is_valid, _ = SecurityManager.validate("ls -la")
        assert is_valid

    def test_unsafe_operators(self):
        unsafe_cmds = ["ls | grep foo", "echo hello > file.txt", "ls ; rm -rf"]
        for cmd in unsafe_cmds:
            is_valid, reason = SecurityManager.validate(cmd)
            assert not is_valid
            assert "Forbidden pattern" in reason

    def test_unsafe_commands(self):
        unsafe_cmds = ["rm -rf /", "sudo apt-get install", "dd if=/dev/zero"]
        for cmd in unsafe_cmds:
            is_valid, reason = SecurityManager.validate(cmd)
            assert not is_valid
            assert "Forbidden pattern" in reason

class TestRunCommand:
    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        
        result = run_command.invoke({"command": "echo hello"})
        
        assert result["exit_code"] == 0
        assert result["stdout"] == "output"
        mock_run.assert_called_once()
    
    def test_run_command_security_block(self):
        result = run_command.invoke({"command": "rm -rf /"})
        assert "Security Error" in result["error"]

    @patch("subprocess.run")
    def test_run_command_unsafe_override(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="deleted", stderr="")
        
        # Should proceed because unsafe_mode=True
        result = run_command.invoke({"command": "rm -rf /", "unsafe_mode": True})
        
        assert result["exit_code"] == 0
        mock_run.assert_called_once()

class TestGitDiff:
    @patch("subprocess.run")
    def test_staged_diff(self, mock_run):
        mock_run.return_value = MagicMock(stdout="diff content")
        
        git_diff.invoke({"repo_root": ".", "mode": "staged"})
        
        args = mock_run.call_args[0][0]
        assert "diff" in args
        assert "--cached" in args

    @patch("subprocess.run")
    def test_branch_diff(self, mock_run):
        mock_run.return_value = MagicMock(stdout="diff content")
        
        git_diff.invoke({"repo_root": ".", "mode": "branch", "base_ref": "feature-branch"})
        
        args = mock_run.call_args[0][0]
        assert "feature-branch" in args
