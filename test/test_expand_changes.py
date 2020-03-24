"""
    pytest: tests the functioning of rst_rename.expand_changes_on_contents()
"""
from rst_rename import expand_changes_on_contents, create_representation, _HIGHLIGHT_ESCAPE, _STANDARD_SCAPE

####################################################################################################

def test_create_repr_when_basic():
    srcline = "object.png"
    dstline = "renamed.png"
    src = "object.png"
    dst = "renamed.png"
    expected = "%srenamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE)
    obtained = create_representation(srcline, dstline, src, dst)
    assert expected == obtained

def test_create_repr_when_same_folder():
    srcline = "_img/object.png"
    dstline = "_img/renamed.png"
    src = "_img/object.png"
    dst = "_img/renamed.png"
    expected = "_img/%srenamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE)
    obtained = create_representation(srcline, dstline, src, dst)
    assert expected == obtained

def test_create_repr_when_different_folder():
    srcline = "_img/object.png"
    dstline = "_imgage/renamed.png"
    src = "_img/object.png"
    dst = "_imgage/renamed.png"
    expected = "_img%sage/renamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE)
    obtained = create_representation(srcline, dstline, src, dst)
    assert expected == obtained

def test_create_repr_when_different_folder_same_name():
    srcline = "_img/object.png"
    dstline = "_imgage/object.png"
    src = "_img/object.png"
    dst = "_imgage/object.png"
    expected = "_img%sage%s/object.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE)
    obtained = create_representation(srcline, dstline, src, dst)
    assert expected == obtained


####################################################################################################

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
        "repr": "%srenamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']

def test_basic_change_with_shorter_renamed():
    contents = ["objectwithlongname.png"]
    changes = [(0, 0)]
    src = 'objectwithlongname.png'
    dst = 'renamed.png'
    expected = [{
        "linenr": 0,
        "src": "objectwithlongname.png",
        "dst": "renamed.png",
        "repr": "%srenamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
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
        "repr": "line :download:`%srenamed%s.png` and so on" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
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


def test_rst_ref_with_caption():
    contents = ["And this is :ref:`caption <object>` witout caption"]
    changes = [(0, 27)]
    src = 'object.rst'
    dst = 'renamed.rst'
    expected = [{
        "linenr": 0,
        "src":  "And this is :ref:`caption <object>` witout caption",
        "dst":  "And this is :ref:`caption <renamed>` witout caption",
        "repr": "And this is :ref:`caption <%srenamed%s>` witout caption" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


def test_basic_change_with_same_path():
    contents = ["_resources/object.png"]
    changes = [(0, 0)]
    src = '_resources/object.png'
    dst = '_resources/renamed.png'
    expected = [{
        "linenr": 0,
        "src": "_resources/object.png",
        "dst": "_resources/renamed.png",
        "repr": "_resources/%srenamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


def test_basic_change_with_different_path():
    contents = ["_resources/object.png"]
    changes = [(0, 0)]
    src = '_resources/object.png'
    dst = '_images/renamed.png'
    expected = [{
        "linenr": 0,
        "src": "_resources/object.png",
        "dst": "_images/renamed.png",
        "repr": "_%simages/renamed%s.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']


def test_basic_change_with_different_path_but_same_name():
    contents = ["_resources/object.png"]
    changes = [(0, 0)]
    src = '_resources/object.png'
    dst = '_images/object.png'
    expected = [{
        "linenr": 0,
        "src": "_resources/object.png",
        "dst": "_images/object.png",
        "repr": "_%simag%ses/object.png" % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE),
    }]
    obtained = expand_changes_on_contents(contents, changes, src, dst)
    assert 1 == len(obtained)
    assert expected[0]['linenr'] == obtained[0]['linenr']
    assert expected[0]['src'] == obtained[0]['src']
    assert expected[0]['dst'] == obtained[0]['dst']
    assert expected[0]['repr'] == obtained[0]['repr']

