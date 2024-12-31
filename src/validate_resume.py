import json
import argparse
import logging
from pathlib import Path
from jsonschema import Draft202012Validator, SchemaError

from util.schema_validation import get_schema_format_checker


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description="Validate a JSON data file against a JSON schema."
    )
    parser.add_argument("data_file", help="Input data JSON file")
    parser.add_argument("schema_file", help="JSON schema file")
    args = parser.parse_args()

    data_file = Path(args.data_file)
    schema_file = Path(args.schema_file)

    if not data_file.exists():
        logging.error(f"Data file {data_file} does not exist.")
        exit(1)
    if not schema_file.exists():
        logging.error(f"Schema file {schema_file} does not exist.")
        exit(1)

    try:
        with data_file.open("r") as df:
            data = json.load(df)
        with schema_file.open("r") as sf:
            schema = json.load(sf)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        exit(1)

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as e:
        logging.error(f"Invalid schema: {e}")

    validator = Draft202012Validator(schema, format_checker=get_schema_format_checker())
    has_errors = False
    for err in validator.iter_errors(data):
        has_errors = True
        path_str = ""
        for path_segment in err.path:
            path_str += f"['{path_segment}']"

        formatted_instance = json.dumps(err.instance, indent=2)
        formatted_instance = "\n".join(
            "  " + line for line in formatted_instance.splitlines()
        )

        message = f"instance{path_str}:\n{formatted_instance}\n{err.message}"

        logging.error(f"Validation error:\n{message}\n")

    if has_errors:
        exit(1)
    else:
        logging.info("JSON data is valid according to the schema.")


if __name__ == "__main__":
    main()
