"""Foreign pin lookup must not inherit the committing checkout's Git environment."""
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PinHookTest(unittest.TestCase):
    def test_foreign_pin_with_inherited_git_dir_and_unknown_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            campaign, fork = base / 'campaign', base / 'faer'
            for repo in (campaign, fork):
                subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            subprocess.run(['git', '-C', str(fork), '-c', 'user.name=Test', '-c',
                            'user.email=test@example.invalid', '-c', 'commit.gpgsign=false',
                            '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty',
                            '-m', 'pin source'], check=True)
            sha = subprocess.check_output(['git', '-C', str(fork), 'rev-parse', 'HEAD'], text=True).strip()
            (campaign / 'pins').mkdir()
            pin = campaign / 'pins/fork.rev'
            env = dict(os.environ, GIT_DIR=str(campaign / '.git'), GIT_WORK_TREE=str(campaign))
            hook = ROOT / '.githooks/pre-commit'
            for value, expected in ((sha, 0), ('0' * 40, 1)):
                with self.subTest(pin=value):
                    pin.write_text(value + '\n')
                    subprocess.run(['git', '-C', str(campaign), 'add', 'pins/fork.rev'], check=True)
                    result = subprocess.run(['sh', str(hook)], cwd=campaign, env=env,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    if expected:
                        self.assertIn('no local checkout can resolve', result.stderr)


if __name__ == '__main__':
    unittest.main()
