class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

def find_longest_chain_leaf(node):
    if not node.children:  # If node has no children, it is a leaf
        return node, 1  # Return the leaf and its chain length 1
    else:
        max_child_length = 0
        longest_chain_leaf = None
        for child in node.children:
            child_leaf, child_length = find_longest_chain_leaf(child)
            if child_length > max_child_length:
                max_child_length = child_length
                longest_chain_leaf = child_leaf
        return longest_chain_leaf, max_child_length + 1  # Add 1 for the current node