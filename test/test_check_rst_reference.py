"""
    pytest: tests the functioning of rst_rename.check_rst_references()
"""
import pathlib
from rst_rename import check_rst_references

####################################################################################################

def test_when_part_of_a_word():
    """ The stem of src appears as a part of a word but it is not a real reference """
    contents = ["something that contains objects", "but not the stem alone"]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
    expected = { 'result': False }
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']

def test_when_part_of_a_regular_sentence():
    """ src is part of a regular sentence in contents but it is not a real reference """
    contents = ["something that contains the exact objects.png but", "it is not a real reference"]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
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
    dst = pathlib.Path('itdoesntmatter')
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
    dst = pathlib.Path('renamed.png')
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
    dst = pathlib.Path('renamed.png')
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
    dst = pathlib.Path('renamed.png')
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
    dst = pathlib.Path('renamed.png')
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
    dst = pathlib.Path('renamed.png')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': '.. image:: object.png', 'dst': '.. image:: renamed.png' },
        { 'line': 5, 'src': '.. figure:: /object.png', 'dst': '.. figure:: /renamed.png' }
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']

####################################################################################################

def test_when_looking_in_a_toctree_for_non_rst_src():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      object.rst",
                "      otherobject.rst",
                "",
                "other things",
                ]
    src = pathlib.Path('object.txt')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_when_looking_in_a_toctree_for_non_rst_dst():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      object.rst",
                "      otherobject.rst",
                "",
                "other things",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.txt')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_when_first_in_a_toctree():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      object.rst",
                "      otherobject.rst",
                "",
                "other things",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 5, 'src': '      object.rst', 'dst': '      renamed.rst' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_first_in_a_toctree_without_extension():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      object",
                "      otherobject.rst",
                "",
                "other things",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 5, 'src': '      object', 'dst': '      renamed' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_nth_a_toctree():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      otherobject.rst",
                "      object.rst",
                "      otherobject.rst",
                "",
                "other things",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 6, 'src': '      object.rst', 'dst': '      renamed.rst' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_when_out_of_the_toctree():
    contents = ["some contents",
                "   .. toctree::  ",
                "      :titlesonly:",
                "      :maxdepth: 1",
                "",
                "      otherobject.rst",
                "      otherobject.rst",
                "",
                "Do not count the next::",
                "",
                "      object.rst",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


####################################################################################################


def test_ref_when_not_the_target_src():
    contents = ["some contents",
                "and a :ref:`toanothercontent` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_ref_when_not_the_target_src_with_caption():
    contents = ["some contents",
                "and a :ref:`with caption <toanothercontent>` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_ref_when_the_target_src():
    contents = ["some contents",
                "and a :ref:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :ref:`object` that', 'dst': 'and a :ref:`renamed` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_doc_when_not_the_target_src():
    contents = ["some contents",
                "and a :doc:`toanothercontent` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_doc_when_not_the_target_src_with_caption():
    contents = ["some contents",
                "and a :doc:`with caption <toanothercontent>` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']



def test_doc_when_the_target_src():
    contents = ["some contents",
                "and a :doc:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :ref:`object` that', 'dst': 'and a :ref:`renamed` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']

def test_ref_when_the_target_src_with_caption():
    contents = ["some contents",
                "and a :ref:`with caption <object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :ref:`with caption <object>` that', 'dst': 'and a :ref:`with caption <renamed>` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']



def test_ref_when_the_target_src_with_caption_different_line():
    contents = ["some contents",
                "and a :ref:`with ",
                "caption ",
                "<object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :ref:`<object>` that', 'dst': 'and a :ref:`<renamed>` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_ref_when_the_target_src_with_caption_different_indented_line():
    contents = ["some contents",
                "* and a :ref:`with ",
                "  caption ",
                "  <object>` that",
                "  should change",
                "",
                "* another point",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :ref:`<object>` that', 'dst': 'and a :ref:`<renamed>` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_ref_when_two_targets_and_one_with_caption_different_indented_line():
    contents = ["some contents",
                "* and a :ref:`with ",
                "  caption ",
                "  <object>` and :ref:`object` that",
                "  should change",
                "",
                "* another point",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': '  <object>` and :ref:`object` that', 'dst': '  <renamed>` and :ref:`renamed` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_doc_when_not_a_rst_in_src():
    contents = ["some contents",
                "and a :doc:`object` that",
                "should not change"]
    src = pathlib.Path('object.txt')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']


def test_doc_when_not_a_rst_in_dst():
    contents = ["some contents",
                "and a :doc:`object` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.txt')
    expected = { 'result': False,}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']



def test_doc_when_the_target_src_with_caption():
    contents = ["some contents",
                "and a :doc:`with caption<object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :doc:`with caption <object>` that', 'dst': 'and a :doc:`with caption <renamed>` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']


def test_doc_when_two_refs_on_same_line():
    contents = ["some contents",
                "and a :doc:`with caption<object>` and :ref:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = { 'result': True, 'changes': [
        { 'line': 2, 'src': 'and a :doc:`with caption <object>` and :ref:`object` that', 'dst': 'and a :doc:`with caption <renamed>` and :ref:`renamed` that' },
    ]}
    obtained = check_rst_references(contents, src, dst)
    assert expected['result'] == obtained['result']
    assert expected['changes'] == obtained['changes']

