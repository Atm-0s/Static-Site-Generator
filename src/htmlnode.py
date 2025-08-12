

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props == None or self.props == {}:
            return ""
        prop_list = []
        for key, value in self.props.items():
            prop_list.append(f'{key}="{value}"')
        result = " ".join(prop_list)
        return f" {result}"

    def __repr__(self):
        return f" tag = {self.tag}, value = {self.value}, children = {self.children}, props = {self.props}"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf nodes must have a value")
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"



class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Tag is required")
        if self.children is None or self.children == []:
            raise ValueError("Parent nodes must have children")

        results = ""
        for child in self.children:
            if not isinstance(child, HTMLNode):
                raise ValueError("Child is not a valid HTMLNode")
            results = results + child.to_html()

        return f"<{self.tag}>{results}</{self.tag}>"