"""
    pytest: tests the functioning of rst_rename.expand_changes_on_contents()
"""
import pathlib
from rst_rename import expand_changes_on_contents, _HIGHLIGHT_ESCAPE, _STANDARD_SCAPE

def test_when_no_changes():
    """ This can't happen since expand_changes_on_contents() is only called when there's at least one change
        Anyway, it is an easy way to start testing """
    contents = ["line1", "line2", "line3"]
    changes = []
    src = pathlib.Path('object.png')
    dst = pathlib.Path('renamed.png')
    expected = []
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert expected == obtained

def test_basic_change():
    contents = ["line :download:`object.png` and so on"]
    changes = [(0, 16)]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('renamed.png')
    expected = [{
        "linenr": 0,
        "src": "line :download:`object.png` and so on",
        "dst": "line :download:`renamed.png` and so on",
        "repr": "line :download:`%srenamed.png%s` and so on" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']
