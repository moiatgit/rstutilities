"""
    pytest: tests the functioning of rst_rename.check_rst_references()
"""
import pathlib
from rstutils import check_rst_references

####################################################################################################

def test_when_part_of_a_word():
    """ The stem of src appears as a part of a word but it is not a real reference """
    contents = ["something that contains objects", "but not the stem alone"]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

def test_when_part_of_a_regular_sentence():
    """ src is part of a regular sentence in contents but it is not a real reference """
    contents = ["something that contains the exact objects.png but", "it is not a real reference"]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_when_not_referenced_by_an_image_because_prefix():
    contents = ["A reference with image to another file",
                "",
                ".. image:: anotherobject.png",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

def test_when_not_referenced_by_an_image_because_suffix():
    contents = ["A reference with image to another file",
                "",
                ".. image:: object.pngX",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.png')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(2, 11)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(2, 12)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(2, 12)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(2, 12)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_when_not_referenced_by_an_image_because_prefix():
    contents = ["A reference with image to another file",
                "",
                ".. literalinclude:: anotherobject.java",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.java')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

def test_when_not_referenced_by_an_image_because_suffix():
    contents = ["A reference with image to another file",
                "",
                ".. literalinclude:: object.javaX",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.java')
    dst = pathlib.Path('itdoesntmatter')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_when_referenced_by_an_image():
    contents = ["A real reference with image",
                "",
                ".. literalinclude:: object.java",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.java')
    dst = pathlib.Path('renamed.png')
    expected = [(2, 20)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_when_referenced_by_an_absolute_literalinclude():
    contents = ["A real reference with image",
                "",
                ".. literalinclude:: /object.java",
                "   :align: center",
                "",
                "And other things",
                ]
    src = pathlib.Path('object.java')
    dst = pathlib.Path('renamed.java')
    expected = [(2, 21)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

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
    expected = [(2, 11), (5, 13)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)



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
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(5, 6)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(5, 6)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(6, 6)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_when_on_a_second_toctree():
    contents = ["some contents",
                "     .. toctree::  ",
                "        :titlesonly:",
                "        :maxdepth: 1",
                "",
                "       otherobject.rst",
                "       otherobject.rst",
                "",
                "End of first toctree",
                "",
                "Something that requires indentation",
                "  .. toctree::",
                "",
                "      object.rst",
                ]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(13, 6)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


####################################################################################################


def test_ref_when_not_the_target_src():
    contents = ["some contents",
                "and a :ref:`toanothercontent` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_ref_when_not_the_target_src_with_caption():
    contents = ["some contents",
                "and a :ref:`with caption <toanothercontent>` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_ref_when_the_target_src():
    contents = ["some contents",
                "and a :ref:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 12)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_not_the_target_src():
    contents = ["some contents",
                "and a :doc:`toanothercontent` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_not_the_target_src_with_caption():
    contents = ["some contents",
                "and a :doc:`with caption <toanothercontent>` that",
                "should not change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_the_target_src():
    contents = ["some contents",
                "and a :doc:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 12)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_ref_when_the_target_src_with_caption():
    contents = ["some contents",
                "and a :ref:`with caption <object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 26)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)



def test_ref_when_the_target_src_with_caption_different_line():
    contents = ["some contents",
                "and a :ref:`with ",
                "caption ",
                "<object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 1)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(3, 3)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


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
    expected = [(3, 3), (3, 22)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_not_a_rst_in_src():
    contents = ["some contents",
                "and a :doc:`object` that",
                "should not change"]
    src = pathlib.Path('object.txt')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_the_target_src_with_caption():
    contents = ["some contents",
                "and a :doc:`with caption<object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 25)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

def test_doc_when_two_refs_on_same_line():
    contents = ["some contents",
                "and a :ref:`with caption<object>` and :doc:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 25), (1, 44)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_doc_when_two_refs_on_same_line():
    contents = ["some contents",
                "and a :doc:`with caption<object>` and :ref:`object` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 25), (1, 44)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_ref_when_the_target_src_with_three_refs_with_splitted():
    contents = ["some contents",
                "and a :ref:`with ",
                "caption ",
                "<object>` that :doc:`object` and :ref:`another",
                "splitted caption <object>` that",
                "should change"]
    src = pathlib.Path('object.rst')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 1), (3, 21), (4, 18)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

####################################################################################################


def test_download_when_not_the_target_src():
    contents = ["some contents",
                "and a :dowload:`toanothercontent` that",
                "should not change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_download_when_not_the_target_src_with_caption():
    contents = ["some contents",
                "and a :download:`with caption <toanothercontent>` that",
                "should not change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = list()
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_download_when_the_target_src():
    contents = ["some contents",
                "and a :download:`object.tar.gz` that",
                "should change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 17)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_download_when_the_target_src_with_caption():
    contents = ["some contents",
                "and a :download:`with caption <object.tar.gz>` that",
                "should change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(1, 31)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)



def test_download_when_the_target_src_with_caption_different_line():
    contents = ["some contents",
                "and a :download:`with ",
                "caption ",
                "<object.tar.gz>` that",
                "should change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 1)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_download_when_the_target_src_with_caption_different_indented_line():
    contents = ["some contents",
                "* and a :download:`with ",
                "  caption ",
                "  <object.tar.gz>` that",
                "  should change",
                "",
                "* another point",
                ]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 3)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)


def test_download_when_two_targets_and_one_with_caption_different_indented_line():
    contents = ["some contents",
                "* and a :download:`with ",
                "  caption ",
                "  <object.tar.gz>` and :download:`object.tar.gz` that",
                "  should change",
                "",
                "* another point",
                ]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 3), (3, 34)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

def test_download_when_the_target_src_with_three_refs_with_splitted():
    contents = ["some contents",
                "and a :download:`with ",
                "caption ",
                "<object.tar.gz>` that :doc:`anotherobject` and :download:`another",
                "splitted caption <object.tar.gz>` that",
                "should change"]
    src = pathlib.Path('object.tar.gz')
    dst = pathlib.Path('renamed.rst')
    expected = [(3, 1), (4, 18)]
    obtained = check_rst_references(contents, src)
    assert set(expected) == set(obtained)

