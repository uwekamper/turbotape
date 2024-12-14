import os
import json
import datetime
from pathlib import Path

import pytest

from turbotape.records import (
    fetch_field,
    Record,
    CategoryMediator,
)


@pytest.fixture
def test_record():
    """
    Fixture for anything that needs test_record.json to be tested.
    """
    json_path = Path(__file__).parent / 'test_record.json'
    with open(json_path, mode='r') as fh:
        test_record = json.load(fh)
        return test_record


class TestCategoryMediator:

    @pytest.fixture()
    def my_field(self, test_record) -> dict:
        field = test_record['fields'][2]
        return field

    @pytest.fixture()
    def my_mediator(self) -> CategoryMediator:
        mediator = CategoryMediator()
        return mediator

    def test_update_category_str(self, my_field, my_mediator):
        value = 'Complete'
        res = my_mediator.update(my_field, value)
        assert res == [{ "value": \
            {
              "id": 48993,
              "text": "Complete",
              "color": "00866A",
              "means_completed": True
            }
        }]

    def test_fetch_category(self, my_mediator):
        assert \
            [(1, "Entered"), (2, "Accepted"), (3, "Rejected")] == \
            my_mediator.fetch(self.field, field_param='choices')
        assert \
            "Accepted" == \
            my_mediator.fetch(self.field)
        assert \
            "Accepted" == \
            my_mediator.fetch(self.field, field_param='active')['text']
        assert \
            2 == \
            my_mediator.fetch(self.field, field_param='active')['id']
        assert \
            "DCBD8" == \
            my_mediator.fetch(self.field, field_param='active')['color']


    def test_as_podio_dict(self, my_mediator):
        res = my_mediator.as_podio_dict(self.field)
        self.assertEqual([2], res)


class TestFetchField:

    def test_get_field_not_found(self):
        self.assertEqual(
            None,
            fetch_field('does_not_exist', self.test_item)
        )

    def test_get_field_with_underscore(self):
        self.assertEqual(
            'Go',
            fetch_field('do_it', self.test_item)
        )

    def test_get_text_field(self):
        self.assertEqual(
            "Bow of boat",
            fetch_field('name', self.test_item)
        )

    def test_get_text_field_multiline(self):
        self.assertEqual(
            "<p>There's something about knowing the bow from the stern that "
            "makes sense in regard to this project.</p>",
            fetch_field('description', self.test_item)
        )

    def test_fetch_category_field(self):
        self.assertEqual(
            [(1, "Entered"), (2, "Accepted"), (3, "Rejected")],
            fetch_field('status2__choices', self.test_item)
        )
        self.assertEqual(
            "Accepted",
            fetch_field('status2', self.test_item)
        )
        self.assertEqual(
            "Accepted",
            fetch_field('status2__active', self.test_item)['text']
        )
        self.assertEqual(
            2,
            fetch_field('status2__active', self.test_item)['id']
        )
        self.assertEqual(
            "DCEBD8",
            fetch_field('status2__active', self.test_item)['color']
        )

    def test_fetch_app_field(self):
        self.assertEqual(
            [503454054],
            fetch_field('projects', self.test_item)
        )
        # self.assertEqual(
        #     503454054,
        #    fetch_field('projects__first', self.test_item)
        #)
        #self.assertEqual(
        #    503454054,
        #    fetch_field('projects__last', self.test_item)
        #)

    def test_fetch_calculation_field(self):
        self.assertEqual(
            "Hello,  John Doe",
            fetch_field('calc', self.test_item)
        )

    def test_fetch_date_field(self):
        self.assertEqual(
            '2018-07-27 01:00:00',
            fetch_field('date', self.test_item)
        )
        self.assertEqual(
            datetime.datetime(2018, 7, 27, 1, 0),
            fetch_field('date__datetime', self.test_item)
        )
        
        self.assertEqual(
            '2018-07-27 01:00:00',
            fetch_field('date__start', self.test_item)
        )
        # item[‘date__start_datetime’]
        self.assertEqual(
            datetime.datetime(2018, 7, 27, 1, 0),
            fetch_field('date__start_datetime', self.test_item)
        )
        self.assertEqual(
            datetime.datetime(2018, 7, 28, 1, 0),
            fetch_field('date__end_datetime', self.test_item)
        )

    def test_fetch_embed_field(self):
        self.assertEqual(
            "http://www.newsletter-webversion.de/?c=0-v0yw-0-11xa&utm_source=newsletter&utm_medium=email&utm_campaign=02%2F2017+DT&newsletter=02%2F2017+DT",
            fetch_field('embed', self.test_item)
        )


class TestRecord:

    @pytest.fixture
    def my_record(self, test_record: dict) -> Record:
        return Record(test_record)

    def test__getitem__(self, my_record):
        self.assertEqual(
            "Bow of boat",
            my_record['name']
        )

    def test__setitem__(self, my_record):
        self.assertEqual(0, len(my_record._tainted))
        my_record['name'] = 'Bow of ship'
        # after setting the value, the number of tainted fields should go up.
        self.assertEqual(1, len(my_record._tainted))
        res = my_record.as_podio_dict(fields=my_record._tainted)
        self.assertEqual("Bow of ship", res['name'])

    def test__setitem__textfield_none(self, my_record):
        self.assertEqual(0, len(my_record._tainted))
        my_record['name'] = None
        # after setting the value, the number of tainted fields should go up.
        self.assertEqual(1, len(my_record._tainted))
        res = my_record.as_podio_dict(fields=my_record._tainted)
        self.assertEqual([], res['name'])

    def test_as_podio_dict(self, my_record):
        res = my_record.as_podio_dict(fields=['name'])
        self.assertEqual("Bow of boat", res['name'])

