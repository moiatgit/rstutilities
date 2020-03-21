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

