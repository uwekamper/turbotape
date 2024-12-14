import json
import os

from turbotape.helpers import (
    iterate_array,
    iterate_resource,
    intersection,
    union,
)


class TestIterateArray:

    def test_iterate_array(self):
        pass


class TestIterateResource:

    def test_iterate_resource(self):
        pass


class TestSetOpsResource:

    def test_intersection(self):
        res = intersection([1, 2], [2, 3], [2, 4, 5])
        self.assertEqual(1, len(res))
        self.assertEqual(2, res[0])

    def test_union(self):
        res = union([1, 2], [2, 3], [2, 4, 5])
        self.assertEqual(5, len(res))
        self.assertEqual(1, res[0])