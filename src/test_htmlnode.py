import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_multi(self):
        node = HTMLNode("a", "link text", None, {"href": "https://www.google.com", "target": "_blank"})
        result = node.props_to_html()
        self.assertEqual(result, ' href="https://www.google.com" target="_blank"')


    def test_props_to_None(self):
        node = HTMLNode("p", "paragraph text", None, None)
        result = node.props_to_html()
        self.assertEqual(result, "")

    def test_props_to_empty_dict(self):
        node = HTMLNode("p", "paragraph text", None, {})
        result = node.props_to_html()
        self.assertEqual(result, "")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_glink(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_bold(self):
        node = LeafNode("b", "Bold text!")
        self.assertEqual(node.to_html(), "<b>Bold text!</b>")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_to_html_none_child(self):
        child_node = None
        parent_node = ParentNode("div", [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_to_html_invalid_str_child(self):
        child_node = "not a valid child"
        parent_node = ParentNode("p", [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_to_html_invalid_tag(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_to_html_multi_child(self):
        child_node1 = LeafNode("a", "https://www.link.com")
        child_node2 = LeafNode("b", "Bold Text")
        parent_node = ParentNode("p", [child_node1, child_node2])
        self.assertEqual(
            parent_node.to_html(),
            "<p><a>https://www.link.com</a><b>Bold Text</b></p>"
        )
