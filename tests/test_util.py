import unittest
import os
from controllers.utils import split_list


class TestListSplitter(unittest.TestCase):
    def setUp(self):
        self.list = [str(i) for i in range(100)]
        self.short_list = [1, 2]

    def test_list_splitter_3(self):
        splitted_lists = split_list(self.list, 3)

        self.assertEqual(len(splitted_lists), 3)
        self.assertEqual(splitted_lists[0][1], 0)
        self.assertEqual(splitted_lists[1][1], 1)
        self.assertEqual(splitted_lists[2][1], 2)

    def test_list_splitter_4(self):
        splitted_lists = split_list(self.list, 4)

        self.assertEqual(len(splitted_lists), 4)
        self.assertEqual(splitted_lists[0][1], 0)
        self.assertEqual(splitted_lists[1][1], 1)
        self.assertEqual(splitted_lists[2][1], 2)

    def test_list_splitter_7(self):
        splitted_lists = split_list(self.list, 7)

        self.assertEqual(len(splitted_lists), 7)
        self.assertEqual(splitted_lists[0][1], 0)
        self.assertEqual(splitted_lists[1][1], 1)
        self.assertEqual(splitted_lists[6][1], 6)

    def test_split_number(self):
        splitted_list = split_list(self.list)

        self.assertEqual(len(splitted_list), os.cpu_count())

    def test_short_list(self):
        """Non splitted short list"""
        splitted_lists = split_list(self.short_list, 7)

        self.assertEqual(len(splitted_lists), 1)