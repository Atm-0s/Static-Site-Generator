import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_url(self):
        node = TextNode("This is a link", TextType.LINK, "http://example.com")
        node2 = TextNode("This is a link", TextType.LINK, "http://example.com")
        self.assertEqual(node, node2)

    def test_no_url(self):
        node = TextNode("No URL text", TextType.TEXT)
        self.assertIsNone(node.url)

    def test_url_eq(self):
        node = TextNode("A link", TextType.LINK)
        node2 = TextNode("A link", TextType.LINK)
        self.assertEqual(node, node2)

    def test_url_not_eq(self):
        node = TextNode("A link", TextType.LINK , "http://example.com")
        node2 = TextNode("A link", TextType.LINK)
        self.assertNotEqual(node, node2)

if __name__ == "__main__":
    unittest.main()