"""
    pytest: tests the functioning of rst_rename.check_rst_references()
"""
import pathlib
from rst_rename import check_rst_references


def test_when_part_of_a_word():
    """ The stem of src appears as a part of a word but it is not a real reference """
    contents = ["something that contains objects", "but not the stem alone"]
    src = pathlib.Path('object.png')
    dst = 'itdoesntmatter'
    expected = { 'result': False }
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']

def test_when_part_of_a_regular_sentence():
    """ src is part of a regular sentence in contents but it is not a real reference """
    contents = ["something that contains the exact objects.png but", "it is not a real reference"]
    src = pathlib.Path('object.png')
    dst = 'itdoesntmatter'
    expected = { 'result': False }
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_when_not_referenced_by_an_image():
    contents = ["A reference with image to another file",
                "",
                ".. image:: anotherobject.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'itdoesntmatter'
    expected = { 'result': False, }
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_when_referenced_by_an_image():
    contents = ["A real reference with image",
                "",
                ".. image:: object.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'renamed.png'
    expected = { 'result': True, 'changes': [ { 'line': 2, 'src': '.. image:: object.png', 'dst': '.. image:: renamed.png' } ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_referenced_by_an_absolute_image():
    contents = ["A real reference with image",
                "",
                ".. image:: /object.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'renamed.png'
    expected = { 'result': True, 'changes': [ { 'line': 2, 'src': '.. image:: /object.png', 'dst': '.. image:: /renamed.png' } ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_referenced_by_a_figure():
    contents = ["A real reference with figure",
                "",
                ".. figure:: object.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'renamed.png'
    expected = { 'result': True, 'changes': [ { 'line': 2, 'src': '.. figure:: object.png', 'dst': '.. figure:: renamed.png' } ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_referenced_by_a_figure_with_path():
    contents = ["A real reference with image and figure",
                "",
                ".. figure:: object.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'renamed.png'
    expected = { 'result': True, 'changes': [ { 'line': 2, 'src': '.. figure:: object.png', 'dst': '.. figure:: renamed.png' } ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_referenced_by_image_and_figure():
    contents = ["A real reference with figure",
                "",
                ".. image:: object.png",
                "   :align: center",
                "",
                ".. figure:: /object.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = 'renamed.png'
    expected = { 'result': True, 'changes': [ 
        { 'line': 2, 'src': '.. image:: object.png', 'dst': '.. image:: renamed.png' },
        { 'line': 5, 'src': '.. figure:: /object.png', 'dst': '.. figure:: /renamed.png' } 
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']

