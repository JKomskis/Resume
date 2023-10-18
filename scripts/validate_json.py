import argparse
import json

from jschon import create_catalog, JSON, JSONSchema


def validate_file(input_file: str, schema_file: str):
    create_catalog("2020-12")
    with open(schema_file) as s, open(input_file) as f:
        schema_contents = json.load(s)
        schema: JSONSchema = JSONSchema(schema_contents)

        validate_result = schema.validate()
        if not validate_result.valid:
            raise Exception(
                f"{json.dumps(validate_result.output('detailed'), indent=4)}\nSchema file provided is not valid, please check schema file."
            )

        input_data = JSON(json.load(f))
        evaluate_result = schema.evaluate(input_data)
        if not evaluate_result.valid:
            raise Exception(
                f"{json.dumps(evaluate_result.output('detailed'), indent=4)}\nInput file is not valid, please check input file."
            )
        print("Input file is valid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "schema",
        help="Schema file against which to validate data, e.g. schema/resume.schema.json",
    )
    parser.add_argument("input", help="Input file to validate, e.g. resume.json")
    args = parser.parse_args()

    validate_file(args.input, args.schema)
