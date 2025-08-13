import unittest
from conversions import text_node_to_html_node, split_nodes_delimiter
from textnode import TextNode, TextType

class TestConversionFunctions(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_italics(self):
        node = TextNode("italics", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italics")

    def test_image(self):
        node = TextNode("An image", TextType.IMAGE, "https://image.com/cat.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["src"], "https://image.com/cat.png")
        self.assertEqual(html_node.props["alt"], "An image")

    def test_link(self):
        node = TextNode("A link", TextType.LINK, "https://google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "A link")
        self.assertEqual(html_node.props["href"], "https://google.com")

    def test_split_nodes_code(self):
        node = TextNode("This is a text with a `code` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
        TextNode("This is a text with a ", TextType.TEXT),
        TextNode("code", TextType.CODE),
        TextNode(" word", TextType.TEXT),
        ])

    def test_split_nodes_plain_text(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("This is plain text", TextType.TEXT)])

    def test_split_nodes_error(self):
        node = TextNode("This is not **correct", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)