"""
Tests for the character response utility functions.
"""

import unittest

from app.utils.character_response_utils import build_resource_list
from app.grpc_services.proto import marvel_pb2


class TestBuildResourceList(unittest.TestCase):
    def test_build_resource_list_comics(self):
        resource_data = {
            "available": 2,
            "returned": 2,
            "collectionURI": "http://example.com/comics",
            "items": [
                {
                    "resourceURI": "http://example.com/comics/1",
                    "name": "Comic 1",
                },
                {
                    "resourceURI": "http://example.com/comics/2",
                    "name": "Comic 2",
                },
            ],
        }
        resource_list = build_resource_list(resource_data, "comics")
        self.assertEqual(resource_list.available, 2)
        self.assertEqual(resource_list.returned, 2)
        self.assertEqual(resource_list.collectionURI, "http://example.com/comics")
        self.assertEqual(len(resource_list.comics), 2)
        self.assertEqual(resource_list.comics[0].name, "Comic 1")
        self.assertEqual(resource_list.comics[1].name, "Comic 2")

    def test_build_resource_list_stories(self):
        resource_data = {
            "available": 1,
            "returned": 1,
            "collectionURI": "http://example.com/stories",
            "items": [
                {
                    "resourceURI": "http://example.com/stories/1",
                    "name": "Story 1",
                    "type": "cover",
                }
            ],
        }
        resource_list = build_resource_list(resource_data, "stories")
        self.assertEqual(resource_list.available, 1)
        self.assertEqual(resource_list.returned, 1)
        self.assertEqual(resource_list.collectionURI, "http://example.com/stories")
        self.assertEqual(len(resource_list.stories), 1)
        self.assertEqual(resource_list.stories[0].name, "Story 1")
        self.assertEqual(resource_list.stories[0].type, "cover")

    def test_build_resource_list_events(self):
        resource_data = {
            "available": 1,
            "returned": 1,
            "collectionURI": "http://example.com/events",
            "items": [
                {
                    "resourceURI": "http://example.com/events/1",
                    "name": "Event 1",
                }
            ],
        }
        resource_list = build_resource_list(resource_data, "events")
        self.assertEqual(resource_list.available, 1)
        self.assertEqual(resource_list.returned, 1)
        self.assertEqual(resource_list.collectionURI, "http://example.com/events")
        self.assertEqual(len(resource_list.events), 1)
        self.assertEqual(resource_list.events[0].name, "Event 1")

    def test_build_resource_list_series(self):
        resource_data = {
            "available": 1,
            "returned": 1,
            "collectionURI": "http://example.com/series",
            "items": [
                {
                    "resourceURI": "http://example.com/series/1",
                    "name": "Series 1",
                }
            ],
        }
        resource_list = build_resource_list(resource_data, "series")
        self.assertEqual(resource_list.available, 1)
        self.assertEqual(resource_list.returned, 1)
        self.assertEqual(resource_list.collectionURI, "http://example.com/series")
        self.assertEqual(len(resource_list.series), 1)
        self.assertEqual(resource_list.series[0].name, "Series 1")

    def test_empty_resource_data(self):
        resource_data = {}
        resource_list = build_resource_list(resource_data, "comics")
        self.assertEqual(resource_list.available, 0)
        self.assertEqual(resource_list.returned, 0)
        self.assertEqual(resource_list.collectionURI, "")
        self.assertEqual(len(resource_list.comics), 0)

    def test_invalid_resource_type(self):
        resource_data = {
            "available": 1,
            "returned": 1,
            "collectionURI": "http://example.com/unknown",
            "items": [
                {
                    "resourceURI": "http://example.com/unknown/1",
                    "name": "Unknown 1",
                }
            ],
        }
        resource_list = build_resource_list(resource_data, "unknown")
        self.assertEqual(resource_list.available, 0)
        self.assertEqual(resource_list.returned, 0)
        self.assertEqual(resource_list.collectionURI, "")
