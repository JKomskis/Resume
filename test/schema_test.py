import unittest
import json
import pprint

from jschon import create_catalog, JSON, JSONSchema


class SchemaTests(unittest.TestCase):
    def test_schema_is_valid(self):
        schema_file = "schema/resume.schema.json"

        create_catalog("2020-12")
        with open(schema_file) as s:
            schema_contents = json.load(s)
            schema: JSONSchema = JSONSchema(schema_contents)

            validate_result = schema.validate()
            print(validate_result)
            self.assertTrue(
                validate_result.valid, pprint.pformat(validate_result.output("basic"))
            )
