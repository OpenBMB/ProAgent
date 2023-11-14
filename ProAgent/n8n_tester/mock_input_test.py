import unittest
from unittest import mock
from ProAgent.n8n_tester.mock_input import *
from ProAgent.n8n_parser.node import n8nPythonNode, n8nNodeMeta

class MockInputTest(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test case by initializing the `mock_interface` attribute with a `MockInput` object.

        Parameters:
            self (TestClass): The current instance of the test class.

        Returns:
            None
        """
        self.mock_interface = MockInput(persist_on_destruction=True)
        

    def create_test_node(self, integration_name, resource_name, operation_name):
        """
        Create a test node for mock input test.

        Args:
            integration_name (str): The name of the integration.
            resource_name (str): The name of the resource.
            operation_name (str): The name of the operation.

        Returns:
            n8nPythonNode: The created test node.
        """
        custom_meta = n8nNodeMeta(
            integration_name=integration_name,
            resource_name=resource_name,
            operation_name=operation_name
        )

        # Create an instance of n8nPythonNode and associate it with the custom n8nNodeMeta
        node = n8nPythonNode(
            # node_id=1,
            node_meta=custom_meta,
            node_comments="Test node for mock_input_test",
            # Other attributes as needed
        )
        return node

    def test_basic_fetch(self):
        """
        Test basic fetch function.

        Set the persist_on_destruction attribute of the mock_interface object to False.
        Assert that the mock_data attribute of the mock_interface object is not None.
        Create a test node with the given parameters: 'blah', 'blahh', 'blahhhh'.
        Assert that the result of the get_node_example_input method of the 
        mock_interface object, with the mock_node as input, is equal to [{}].

        Parameters:
        - self: The object instance.

        Returns:
        - None
        """
        self.mock_interface.persist_on_destruction = False
        self.assertIsNotNone(self.mock_interface.mock_data)
        mock_node = self.create_test_node('blah', 'blahh', 'blahhhh')
        self.assertEqual(self.mock_interface.get_node_example_input(mock_node), [{}])

    def test_register_mock_input(self):
        """
        Test the 'register_mock_input' method of the class.
        
        This method is used to test the functionality of the 'register_mock_input' method of the class 'MockInterface'.
        
        Parameters:
        - self: The object instance.
        
        Returns:
        - None
        
        Raises:
        - AssertionError: If the assertion fails.
        """
        mock_node = self.create_test_node('A', 'B', 'C')
        self.mock_interface.persist_on_destruction = False
        target_input = {'A': 'a', 'B': {'C': 'c'}}
        self.mock_interface.register_node_example_input(mock_node, target_input)
        self.assertEqual(self.mock_interface.get_node_example_input(mock_node), [target_input])
