import unittest
from conversions import *
from blocktype import BlockType
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

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is a text with a link [to boot.dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot.dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.link1.com) attached and a second [link](https://www.link2.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.link1.com"),
                TextNode(" attached and a second ", TextType.TEXT),
                TextNode(
                    "link", TextType.LINK, "https://www.link2.com"
                )
            ],
            new_nodes
        )

    def test_split_images_start_with_image(self):
        node = TextNode(
            "![image](https://www.catpics/cat.png) a cat picture.",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://www.catpics/cat.png"),
                TextNode(" a cat picture.", TextType.TEXT)
            ],
            new_nodes
        )

    def test_split_links_start_with_link(self):
        node = TextNode(
            "[link](https://www.google.com) a link to google.",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" a link to google.", TextType.TEXT)
            ],
            new_nodes
        )

    def test_text_to_textnodes(self):
        node = text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            node
        )

        def test_markdown_to_blocks(self):
            md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                [
                    "This is **bolded** paragraph",
                    "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                    "- This is a list\n- with items",
                ],
            )


    def test_block_to_block_types(self):
        # Test a heading
        block = "# This is a Heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

        # Test a code block
        block = "```\nprint('Hello, World!')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

        # Test a quote block
        block = "> This is a quote.\n> It spans multiple lines."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

        # Test an unordered list
        block = "- Item one\n- Item two"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST) # Note: The solution file uses BlockType.ULIST

        # Test an ordered list
        block = "1. First item\n2. Second item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST) # Note: The solution file uses BlockType.OLIST

        # Test a paragraph
        block = "This is a regular paragraph of text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title(self):
        md = """
# Hello World!
This is a test
to see if I extract only the title
properly
        """
        title = extract_title(md)
        self.assertEqual(title, "Hello World!")

    def test_extract_title_error(self):
        md = """
## Hello World!
This is a test
to see if I raise an error
properly
"""
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_extract_title_whitespace(self):
        md = """
#       Hello World!
This is a test
to see if
all the whitespace is stripped
properly
"""
        title = extract_title(md)
        self.assertEqual(title, "Hello World!")
