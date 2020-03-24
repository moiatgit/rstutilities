"""
    pytest: tests the functioning of rst_rename.expand_changes_on_contents()
"""
from rst_rename import expand_changes_on_contents, _HIGHLIGHT_ESCAPE, _STANDARD_SCAPE

def test_when_no_changes():
    """ This can't happen since expand_changes_on_contents() is only called when there's at least one change
        Anyway, it is an easy way to start testing """
    contents = ["line1", "line2", "line3"]
    changes = []
    src = 'object.png'
    dst = 'renamed.png'
    expected = []
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert expected == obtained

def test_basic_change():
    contents = ["object.png"]
    changes = [(0, 0)]
    src = 'object.png'
    dst = 'renamed.png'
    expected = [{
        "linenr": 0,
        "src": "object.png",
        "dst": "renamed.png",
        "repr": "%srenamed.png%s" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']

def test_download_change():
    contents = ["line :download:`object.png` and so on"]
    changes = [(0, 16)]
    src = 'object.png'
    dst = 'renamed.png'
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

def test_rst_with_extension():
    contents = ["   object.rst"]
    changes = [(0, 3)]
    src = 'object.rst'
    dst = 'renamed.rst'
    expected = [{
        "linenr": 0,
        "src":  "   object.rst",
        "dst":  "   renamed.rst",
        "repr": "   %srenamed%s.rst" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


def test_rst_without_extension():
    contents = ["   object"]
    changes = [(0, 3)]
    src = 'object.rst'
    dst = 'renamed.rst'
    expected = [{
        "linenr": 0,
        "src":  "   object",
        "dst":  "   renamed",
        "repr": "   %srenamed%s" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


def test_rst_ref_without_caption():
    contents = ["And this is :ref:`object` witout caption"]
    changes = [(0, 18)]
    src = 'object.rst'
    dst = 'renamed.rst'
    expected = [{
        "linenr": 0,
        "src":  "And this is :ref:`object` witout caption",
        "dst":  "And this is :ref:`renamed` witout caption",
        "repr": "And this is :ref:`%srenamed%s` witout caption" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


