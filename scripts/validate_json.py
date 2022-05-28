import argparse
import json

from jschon import Catalogue, JSON, JSONSchema, URI

def validate_file(input_file: str, schema_file: str):
    catalogue: Catalogue = Catalogue.create_default_catalogue("2020-12")
    with open(schema_file) as s, open(input_file) as f:
        schema_mapping = json.load(s)
        schema: JSONSchema = JSONSchema(schema_mapping)

        validate_scope = schema.validate()
        if not validate_scope.valid:
            raise Exception(f"{json.dumps(validate_scope.output('detailed'), indent=4)}\nSchema file provided is not valid, please check schema file.")
        
        input_data = JSON(json.load(f))
        evaluate_scope = schema.evaluate(input_data)
        if not evaluate_scope.valid:
            raise Exception(f"{json.dumps(schema.evaluate(input_data).output('detailed'), indent=4)}\nInput file is not valid, please check input file.")
        print("Input file is valid.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", help="Schema file against which to validate data, e.g. schema/resume.schema.json")
    parser.add_argument("input", help="Input file to validate, e.g. resume.json")
    args = parser.parse_args()
    
    validate_file(args.input, args.schema)