import os
import unittest
from pathlib import Path

import scubatrace


class TestProject(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "c"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.C
        )

    def test_project_create(self):
        self.assertIsNotNone(self.project)
        self.assertEqual(self.project.language, scubatrace.language.C)
        self.assertEqual(self.project.path, str(self.project_path))
        self.assertTrue(Path(self.project.path).exists())

    def test_project_parser(self):
        parser = self.project.parser
        self.assertIsNotNone(parser)

    def test_project_files(self):
        files = self.project.files
        self.assertGreater(len(files), 0)
        for _, file in files.items():
            self.assertIsNotNone(file.name)

    def test_project_functions(self):
        functions = self.project.functions
        self.assertGreater(len(functions), 0)
        for func in functions:
            self.assertIsNotNone(func.name)

    def test_project_callgraph(self):
        callgraph = self.project.callgraph
        self.assertIsNotNone(callgraph)
        self.assertGreater(len(callgraph.nodes), 0)
        self.assertGreater(len(callgraph.edges), 0)

    def test_files_keys_are_relative(self):
        c_project = scubatrace.Project.create(
            str(self.samples_dir / "c") + os.sep,
            language=scubatrace.language.C,
            enable_lsp=False,
        )
        for key in c_project.files.keys():
            self.assertFalse(
                Path(key).is_absolute(),
                f"Expected relative path key, got absolute path: {key}",
            )


class TestGitProject(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent.parent
        self.project_path = self.test_dir
        self.project = scubatrace.GitProject.create(
            str(self.project_path), language=scubatrace.language.PYTHON
        )

    def test_git_project_create(self):
        self.assertIsNotNone(self.project)
        self.assertEqual(self.project.language, scubatrace.language.PYTHON)
        self.assertEqual(self.project.path, str(self.project_path))
        self.assertTrue(Path(self.project.path).exists())

    def test_git_project_current_branch(self):
        branch = self.project.current_branch
        self.assertIsInstance(branch, str)
        self.assertGreater(len(branch), 0)

    def test_git_project_current_commit(self):
        commit = self.project.current_commit
        self.assertIsInstance(commit, str)
        self.assertEqual(len(commit), 40)

    def test_git_project_remote_url(self):
        remote = self.project.remote_url
        self.assertTrue(isinstance(remote, str))

    def test_git_project_is_dirty(self):
        self.assertIsInstance(self.project.is_dirty, bool)

    def test_git_project_untracked_files(self):
        untracked = self.project.untracked_files
        self.assertIsInstance(untracked, list)
        for path in untracked:
            self.assertIsInstance(path, str)

    def test_git_project_head_commit_message(self):
        message = self.project.get_commit_message()
        self.assertIsInstance(message, str)
        self.assertGreater(len(message.strip()), 0)

    def test_git_project_get_file_at_commit(self):
        head_sha = self.project.current_commit
        file = self.project.get_file_at_commit("README.md", head_sha)
        self.assertGreater(len(file.text), 0)

    def test_git_project_get_commits(self):
        commits = self.project.get_commits(max_count=5)
        self.assertIsInstance(commits, list)
        self.assertLessEqual(len(commits), 5)
        for sha in commits:
            self.assertIsInstance(sha, str)
            self.assertEqual(len(sha), 40)
