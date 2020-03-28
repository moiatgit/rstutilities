"""
    pytest: tests the functioning of rst_ls_unref.deepest_common_path()
"""
import pathlib
from rstutils import deepest_common_path
from rstutils import pathlib

####################################################################################################

def test_empty_list_of_paths():
    paths = []
    expected = pathlib.Path('/')
    obtained = deepest_common_path(paths)
    assert expected == obtained


def test_just_one_dir(monkeypatch):
    paths = [pathlib.Path('/a/b/c')]
    monkeypatch.setattr(pathlib.Path, 'is_dir', lambda _: True)
    expected = pathlib.Path('/a/b/c')
    obtained = deepest_common_path(paths)
    assert expected == obtained

def test_just_one_file(monkeypatch):
    paths = [pathlib.Path('/a/b/c/file.txt')]
    monkeypatch.setattr(pathlib.Path, 'is_dir', lambda _: False)
    expected = pathlib.Path('/a/b/c')
    obtained = deepest_common_path(paths)
    assert expected == obtained

def test_two_files_with_exactly_the_same_parent(monkeypatch):
    paths = [pathlib.Path('/a/b/c/file1.txt'),
             pathlib.Path('/a/b/c/file2.txt'),
             ]
    monkeypatch.setattr(pathlib.Path, 'is_dir', lambda _: False)
    expected = pathlib.Path('/a/b/c')
    obtained = deepest_common_path(paths)
    assert expected == obtained

def test_two_files_with_common_grandparent(monkeypatch):
    paths = [pathlib.Path('/a/b/c/file1.txt'),
             pathlib.Path('/a/b/d/file2.txt'),
             ]
    monkeypatch.setattr(pathlib.Path, 'is_dir', lambda _: False)
    expected = pathlib.Path('/a/b')
    obtained = deepest_common_path(paths)
    assert expected == obtained


def test_a_file_and_a_dir_that_is_its_parent(monkeypatch):
    def fake_is_dir(path):
        return str(path) == '/a/b/c'

    paths = [pathlib.Path('/a/b/c/file1.txt'),
             pathlib.Path('/a/b/c'),
             ]
    monkeypatch.setattr(pathlib.Path, 'is_dir', fake_is_dir)
    expected = pathlib.Path('/a/b/c')
    obtained = deepest_common_path(paths)
    assert expected == obtained

def test_a_dir_and_a_file_directly_contained(monkeypatch):
    def fake_is_dir(path):
        return str(path) == '/a/b/c'

    paths = [pathlib.Path('/a/b/c'),
             pathlib.Path('/a/b/c/file1.txt'),
             ]
    monkeypatch.setattr(pathlib.Path, 'is_dir', fake_is_dir)
    expected = pathlib.Path('/a/b/c')
    obtained = deepest_common_path(paths)
    assert expected == obtained

def test_a_bunch_of_dirs_and_files(monkeypatch):
    def fake_is_dir(path):
        return not str(path).endswith(".txt")

    paths = [pathlib.Path('/a/b/c'),
             pathlib.Path('/a/b/c/file1.txt'),
             pathlib.Path('/a/b/d/e'),
             pathlib.Path('/a/b/f/g/file2.txt'),]
    monkeypatch.setattr(pathlib.Path, 'is_dir', fake_is_dir)
    expected = pathlib.Path('/a/b')
    obtained = deepest_common_path(paths)
    assert expected == obtained

