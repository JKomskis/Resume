import unittest
import json
from typing import List
from pathlib import Path
from jsonschema import Draft202012Validator, Validator
import copy
from typing import Any

from src.util.schema_validation import get_schema_format_checker


class SchemaTests(unittest.TestCase):
    def get_minimal_resume(self) -> Any:
        return {
            "meta": {"version": "1.0.0", "date": "1970-01-01"},
            "info": {"firstname": "John", "lastname": "Doe"},
            "contact": {"email": "test@test.com"},
        }

    def get_schema_validator(self) -> Draft202012Validator:
        schema_file = Path("schemas/resume.schema.json")
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file {schema_file} does not exist.")
        with schema_file.open("r") as sf:
            schema = json.load(sf)
            return Draft202012Validator(
                schema, format_checker=get_schema_format_checker()
            )

    def get_error_messages(self, validator, instance):
        return "\n".join(error.message for error in validator.iter_errors(instance))

    def test_schema_is_valid(self):
        schema_file = Path("schemas/resume.schema.json")
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file {schema_file} does not exist.")
        with schema_file.open("r") as sf:
            schema = json.load(sf)
        Draft202012Validator.check_schema(schema)

    def test_version_format(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        invalid_versions = ["invalid_version", True, 1, 1.0, "1", "1.0", "1.0.0.0"]
        for invalid_version in invalid_versions:
            resume["meta"]["version"] = invalid_version
            self.assertFalse(validator.is_valid(resume), invalid_version)

        valid_versions = ["1.0.0", "1.0.1", "1.1.0", "2.0.0", "10.0.0"]
        for valid_version in valid_versions:
            resume["meta"]["version"] = valid_version
            self.assertTrue(
                validator.is_valid(resume), self.get_error_messages(validator, resume)
            )

    def test_date_format(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        invalid_dates = [
            "2021/01/01",
            "01-01-2021",
            "2021-13-01",
            "2021-00-00",
            "2021-02-30",
        ]
        for invalid_date in invalid_dates:
            resume["meta"]["date"] = invalid_date
            self.assertFalse(validator.is_valid(resume), invalid_date)

        valid_dates = ["2021-01-01", "1999-12-31", "2022-02-28"]
        for valid_date in valid_dates:
            resume["meta"]["date"] = valid_date
            error_messages = self.get_error_messages(validator, resume)
            self.assertTrue(validator.is_valid(resume), error_messages)

    def test_email_format(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@domain",
        ]
        for invalid_email in invalid_emails:
            resume["contact"]["email"] = invalid_email
            self.assertFalse(validator.is_valid(resume), invalid_email)

        valid_emails = [
            "test@example.com",
            "user.name+tag@example.co.uk",
            "user_name@example.com",
        ]
        for valid_email in valid_emails:
            resume["contact"]["email"] = valid_email
            error_messages = self.get_error_messages(validator, resume)
            self.assertTrue(validator.is_valid(resume), error_messages)

    def test_phone_format(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["contact"]["phone"] = "123-456-7890"  # Add phone field

        invalid_phones = ["1234567890", "123-45-6789", "phone", "123-4567-890"]
        for invalid_phone in invalid_phones:
            resume["contact"]["phone"] = invalid_phone
            self.assertFalse(validator.is_valid(resume), invalid_phone)

        valid_phones = ["123-456-7890", "987-654-3210"]
        for valid_phone in valid_phones:
            resume["contact"]["phone"] = valid_phone
            error_messages = self.get_error_messages(validator, resume)
            self.assertTrue(validator.is_valid(resume), error_messages)

    def test_uri_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["info"]["website"] = "https://johndoe.com"
        resume["info"]["github"] = "https://github.com/johndoe"
        resume["contact"]["linkedin"] = "https://www.linkedin.com/in/johndoe"

        # Define a set of invalid URIs
        invalid_uris = [
            "htp:/invalid.com",
            "github.com/johndoe",
            "www.linkedin.com/in/johndoe",
            "https://",
            "://missing.scheme.com",
            "http//missing-colon.com",
            "http:missing-slashes.com",
            "http:/one-slash.com",
            "http://invalid_domain",
        ]

        # Test each invalid URI on all three fields
        for invalid_uri in invalid_uris:
            for field in ["website", "github", "linkedin"]:
                resume_copy = copy.deepcopy(resume)
                if field in ["website", "github"]:
                    resume_copy["info"][field] = invalid_uri
                else:
                    resume_copy["contact"][field] = invalid_uri
                print(resume_copy)
                self.assertFalse(
                    validator.is_valid(resume_copy),
                    f"Invalid URI '{invalid_uri}' in field '{field}' was determined to be valid",
                )

        # Reset to valid URIs before testing valid cases
        resume["info"]["website"] = "https://johndoe.com"
        resume["info"]["github"] = "https://github.com/johndoe"
        resume["contact"]["linkedin"] = "https://www.linkedin.com/in/johndoe"

        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(validator.is_valid(resume), error_messages)

    def test_meta_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        required_fields = ["version", "date"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["meta"][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Missing required field '{field}' in 'meta' passed validation.",
                )

    def test_meta_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["meta"]["unexpected_field"] = "unexpected"
        self.assertFalse(
            validator.is_valid(resume),
            "Unexpected additional property in 'meta' did not fail validation.",
        )

    def test_info_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        required_fields = ["firstname", "lastname"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["info"][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Missing required field '{field}' in 'info' passed validation.",
                )

    def test_info_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["info"]["unexpected_field"] = "unexpected"
        self.assertFalse(
            validator.is_valid(resume),
            "Unexpected additional property in 'info' did not fail validation.",
        )

    def test_contact_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["contact"]["unexpected_field"] = "unexpected"
        self.assertFalse(
            validator.is_valid(resume),
            "Unexpected additional property in 'contact' did not fail validation.",
        )

    def test_date_definition(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]

        # Test invalid date formats
        invalid_dates = [
            "2021-2-30",
            "21-02-2020",
            "2020/01",
            "abcd-ef-gh",
            "2020-13",
            "2020-1",
            True,
            202001,
        ]
        for invalid_date in invalid_dates:
            resume["education"][0]["graduated"] = invalid_date
            with self.subTest(date=invalid_date):
                self.assertFalse(validator.is_valid(resume), invalid_date)

        # Test valid date formats
        valid_dates = ["2020-12", "1999-01", "2023-07"]
        for valid_date in valid_dates:
            resume["education"][0]["graduated"] = valid_date
            with self.subTest(date=valid_date):
                self.assertTrue(
                    validator.is_valid(resume),
                    self.get_error_messages(validator, resume),
                )

    def test_location_definition(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Test missing required fields in location
        resume["education"] = [self.get_sample_education_entry()]
        incomplete_locations = [
            {"state": "EX"},  # Missing city
            {"city": "Example City"},  # Missing state
        ]
        for loc in incomplete_locations:
            resume["education"][0]["location"] = loc
            with self.subTest(location=loc):
                self.assertFalse(validator.is_valid(resume), loc)

        # Test additional properties in location
        extra_location = {"city": "Example City", "state": "EX", "continent": "Europe"}
        resume["education"][0]["location"] = extra_location
        self.assertFalse(validator.is_valid(resume), "Additional property in location")

        # Test valid location
        valid_location = {"city": "Example City", "state": "EX"}
        resume["education"][0]["location"] = valid_location
        self.assertTrue(validator.is_valid(resume), "Valid location")

        # Test valid location with country
        valid_location = {"city": "Example City", "state": "EX", "country": "USA"}
        resume["education"][0]["location"] = valid_location
        self.assertTrue(validator.is_valid(resume), "Valid location with country")

    def test_position_definition(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Test missing required fields in position
        resume["experience"] = [self.get_sample_experience_entry()]
        incomplete_positions = [
            {"start": "2020-01"},  # Missing title
            {"title": "Developer"},  # Missing start
        ]
        for pos in incomplete_positions:
            resume["experience"][0]["positions"] = [pos]
            with self.subTest(position=pos):
                self.assertFalse(validator.is_valid(resume), pos)

        # Test additional properties in position
        extra_position = {
            "title": "Developer",
            "start": "2020-01",
            "end": "2021-01",
            "department": "Engineering",
        }
        resume["experience"][0]["positions"] = [extra_position]
        self.assertFalse(validator.is_valid(resume), "Additional property in position")

        # Test valid position
        valid_position = {"title": "Developer", "start": "2020-01", "end": "2021-01"}
        resume["experience"][0]["positions"] = [valid_position]
        self.assertTrue(validator.is_valid(resume), "Valid position")

    def get_sample_education_entry(self):
        return {
            "name": "University of Example",
            "degree": "Bachelor of Science",
            "location": {"city": "Example City", "state": "EX"},
            "graduated": "2020-05",
            "highlights": ["Dean's List", "Honor Society"],
        }

    def test_education_valid_entry(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(validator.is_valid(resume), error_messages)

    def test_education_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]
        required_fields = ["name", "degree", "location", "graduated", "highlights"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["education"][0][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"'{field}' is not required",
                )

    def test_education_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]
        invalid_resume = copy.deepcopy(resume)
        invalid_resume["education"][0]["extra_field"] = "Not allowed"
        self.assertFalse(
            validator.is_valid(invalid_resume),
            "Additional property 'extra_field' was allowed",
        )

    def test_education_incorrect_types(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]
        type_tests = {
            "name": 123,
            "degree": True,
            "location": "Not an object",
            "graduated": "2020/05",
            "highlights": "Should be a list",
        }
        for field, invalid_value in type_tests.items():
            with self.subTest(field=field, invalid_value=invalid_value):
                invalid_resume = copy.deepcopy(resume)
                invalid_resume["education"][0][field] = invalid_value
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Invalid type for field '{field}' was determined to be valid",
                )

    def test_education_invalid_graduated_patterns(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [self.get_sample_education_entry()]
        invalid_graduated_dates = ["2020-5", "20-05", "202005", "2020-13"]
        for date in invalid_graduated_dates:
            with self.subTest(date=date):
                invalid_resume = copy.deepcopy(resume)
                invalid_resume["education"][0]["graduated"] = date
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Invalid graduated date '{date}' was determined to be valid",
                )

    def test_education_multiple_valid_entries(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["education"] = [
            self.get_sample_education_entry(),
            {
                "name": "Example Institute of Technology",
                "degree": "Master of Engineering",
                "location": {"city": "Tech City", "state": "TC"},
                "graduated": "2022-08",
                "highlights": ["Research Assistant", "Published Paper"],
            },
        ]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(validator.is_valid(resume), error_messages)

    def test_skills_valid_entry(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["skills"] = [
            {"category": "Programming", "examples": ["Python", "JavaScript"]}
        ]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(
            validator.is_valid(resume),
            f"Valid 'skills' entry failed validation: {error_messages}",
        )

    def test_skills_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["skills"] = [{"category": "Programming"}]  # Missing 'examples'
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry missing 'examples' should fail validation.",
        )

        resume["skills"] = [
            {"examples": ["Python", "JavaScript"]}  # Missing 'category'
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry missing 'category' should fail validation.",
        )

    def test_skills_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["skills"] = [
            {
                "category": "Programming",
                "examples": ["Python", "JavaScript"],
                "extra_field": "Not allowed",
            }
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with additional properties should fail validation.",
        )

    def test_skills_correct_types(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        # Incorrect type for 'category'
        resume["skills"] = [{"category": 123, "examples": ["Python", "JavaScript"]}]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with non-string 'category' should fail validation.",
        )

        # Incorrect type for 'examples'
        resume["skills"] = [{"category": "Programming", "examples": "Python"}]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with non-array 'examples' should fail validation.",
        )

        # Incorrect type within 'examples'
        resume["skills"] = [{"category": "Programming", "examples": ["Python", 123]}]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with non-string item in 'examples' should fail validation.",
        )

    def test_skills_example_uniqueness(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["skills"] = [
            {
                "category": "Programming",
                "examples": ["Python", "Python"],
            }  # Duplicate examples
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with duplicate 'examples' should fail validation.",
        )

    def test_skills_min_contains(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        # Empty 'examples' array
        resume["skills"] = [{"category": "Programming", "examples": []}]
        self.assertFalse(
            validator.is_valid(resume),
            "Skill entry with empty 'examples' should fail validation.",
        )

        # 'examples' with one item
        resume["skills"] = [{"category": "Programming", "examples": ["Python"]}]
        self.assertTrue(
            validator.is_valid(resume),
            "Skill entry with at least one 'example' should pass validation.",
        )

    def get_sample_experience_entry(self) -> dict:
        return {
            "company": "Example Corp",
            "location": {"city": "Business City", "state": "BC"},
            "positions": [
                {"title": "Software Engineer", "start": "2020-01", "end": "2022-01"}
            ],
            "highlights": ["Developed key features", "Improved performance"],
        }

    def test_experience_valid_entry(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["experience"] = [self.get_sample_experience_entry()]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(
            validator.is_valid(resume),
            f"Valid 'experience' entry failed validation: {error_messages}",
        )

    def test_experience_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["experience"] = [self.get_sample_experience_entry()]
        required_fields = ["company", "location", "positions", "highlights"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["experience"][0][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Experience entry missing '{field}' should fail validation.",
                )

    def test_experience_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["experience"] = [self.get_sample_experience_entry()]
        resume["experience"][0]["extra_field"] = "Not allowed"
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with additional properties should fail validation.",
        )

    def test_experience_correct_types(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Incorrect type for 'company'
        resume["experience"] = [{**self.get_sample_experience_entry(), "company": 123}]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-string 'company' should fail validation.",
        )

        # Incorrect type for 'location'
        resume["experience"] = [
            {**self.get_sample_experience_entry(), "location": "Not an object"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-object 'location' should fail validation.",
        )

        # Incorrect type for 'positions'
        resume["experience"] = [
            {**self.get_sample_experience_entry(), "positions": "Not an array"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-array 'positions' should fail validation.",
        )

        # Incorrect type within 'positions'
        resume["experience"] = [
            {**self.get_sample_experience_entry(), "positions": ["Not an object"]}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-object item in 'positions' should fail validation.",
        )

        # Incorrect type for 'highlights'
        resume["experience"] = [
            {**self.get_sample_experience_entry(), "highlights": "Should be a list"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-array 'highlights' should fail validation.",
        )

        # Incorrect type within 'highlights'
        resume["experience"] = [
            {
                **self.get_sample_experience_entry(),
                "highlights": ["Developed key features", 123],
            }
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with non-string item in 'highlights' should fail validation.",
        )

    def test_experience_min_items(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # 'positions' with no items
        resume["experience"] = [{**self.get_sample_experience_entry(), "positions": []}]
        self.assertFalse(
            validator.is_valid(resume),
            "Experience entry with empty 'positions' should fail validation.",
        )

        # 'positions' with one item
        resume["experience"] = [self.get_sample_experience_entry()]
        self.assertTrue(
            validator.is_valid(resume),
            "Experience entry with at least one 'position' should pass validation.",
        )

    def test_experience_unique_items(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Duplicate experience entries
        resume["experience"] = [
            self.get_sample_experience_entry(),
            self.get_sample_experience_entry(),
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Resume with duplicate 'experience' entries should fail validation.",
        )

        # Unique experience entries
        resume["experience"] = [
            self.get_sample_experience_entry(),
            {
                "company": "Another Corp",
                "location": {"city": "Tech City", "state": "TC"},
                "positions": [{"title": "Senior Developer", "start": "2022-02"}],
                "highlights": ["Led development teams", "Architected solutions"],
            },
        ]
        self.assertTrue(
            validator.is_valid(resume),
            self.get_error_messages(validator, resume),
        )

    def get_sample_project_entry(self) -> dict:
        return {
            "name": "Sample Project",
            "context": "Personal Project",
            "start": "2021-01",
            "end": "2021-12",
            "highlights": ["Implemented feature X", "Optimized performance Y"],
        }

    def test_projects_valid_entry(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["projects"] = [self.get_sample_project_entry()]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(
            validator.is_valid(resume),
            f"Valid 'projects' entry failed validation: {error_messages}",
        )

    def test_projects_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["projects"] = [self.get_sample_project_entry()]
        required_fields = ["name", "context", "start", "highlights"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["projects"][0][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Project entry missing '{field}' should fail validation.",
                )

    def test_projects_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["projects"] = [self.get_sample_project_entry()]
        resume["projects"][0]["extra_field"] = "Not allowed"
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with additional properties should fail validation.",
        )

    def test_projects_correct_types(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Incorrect type for 'name'
        resume["projects"] = [{**self.get_sample_project_entry(), "name": 123}]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-string 'name' should fail validation.",
        )

        # Incorrect type for 'context'
        resume["projects"] = [{**self.get_sample_project_entry(), "context": True}]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-string 'context' should fail validation.",
        )

        # Incorrect type for 'start'
        resume["projects"] = [{**self.get_sample_project_entry(), "start": 202101}]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-string 'start' should fail validation.",
        )

        # Incorrect type for 'end'
        resume["projects"] = [{**self.get_sample_project_entry(), "end": 202201}]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-string 'end' should fail validation.",
        )

        # Incorrect type for 'highlights'
        resume["projects"] = [
            {**self.get_sample_project_entry(), "highlights": "Should be a list"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-array 'highlights' should fail validation.",
        )

        # Incorrect type within 'highlights'
        resume["projects"] = [
            {
                **self.get_sample_project_entry(),
                "highlights": ["Implemented feature X", 456],
            }
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Project entry with non-string item in 'highlights' should fail validation.",
        )

    def test_projects_unique_items(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Duplicate project entries
        resume["projects"] = [
            self.get_sample_project_entry(),
            self.get_sample_project_entry(),
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Resume with duplicate 'projects' entries should fail validation.",
        )

        # Unique project entries
        resume["projects"] = [
            self.get_sample_project_entry(),
            {
                "name": "Another Project",
                "context": "Work Project",
                "start": "2022-03",
                "end": "2023-04",
                "highlights": ["Led development", "Integrated API"],
            },
        ]
        self.assertTrue(
            validator.is_valid(resume),
            self.get_error_messages(validator, resume),
        )

    def get_sample_leadership_entry(self) -> dict:
        return {
            "organization": "Example Organization",
            "location": {"city": "Leadership City", "state": "LC"},
            "positions": [{"title": "Team Lead", "start": "2019-01", "end": "2021-01"}],
            "highlights": ["Led a team of 10", "Implemented new processes"],
        }

    def test_leadership_valid_entry(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["leadership"] = [self.get_sample_leadership_entry()]
        error_messages = self.get_error_messages(validator, resume)
        self.assertTrue(
            validator.is_valid(resume),
            f"Valid 'leadership' entry failed validation: {error_messages}",
        )

    def test_leadership_missing_required_fields(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["leadership"] = [self.get_sample_leadership_entry()]
        required_fields = ["organization", "location", "positions", "highlights"]
        for field in required_fields:
            with self.subTest(field=field):
                invalid_resume = copy.deepcopy(resume)
                del invalid_resume["leadership"][0][field]
                self.assertFalse(
                    validator.is_valid(invalid_resume),
                    f"Leadership entry missing '{field}' should fail validation.",
                )

    def test_leadership_additional_properties(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()
        resume["leadership"] = [self.get_sample_leadership_entry()]
        invalid_resume = copy.deepcopy(resume)
        invalid_resume["leadership"][0]["extra_field"] = "Not allowed"
        self.assertFalse(
            validator.is_valid(invalid_resume),
            "Leadership entry with additional properties should fail validation.",
        )

    def test_leadership_correct_types(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Incorrect type for 'organization'
        resume["leadership"] = [
            {**self.get_sample_leadership_entry(), "organization": 123}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-string 'organization' should fail validation.",
        )

        # Incorrect type for 'location'
        resume["leadership"] = [
            {**self.get_sample_leadership_entry(), "location": "Not an object"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-object 'location' should fail validation.",
        )

        # Incorrect type for 'positions'
        resume["leadership"] = [
            {**self.get_sample_leadership_entry(), "positions": "Not an array"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-array 'positions' should fail validation.",
        )

        # Incorrect type within 'positions'
        resume["leadership"] = [
            {**self.get_sample_leadership_entry(), "positions": ["Not an object"]}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-object item in 'positions' should fail validation.",
        )

        # Incorrect type for 'highlights'
        resume["leadership"] = [
            {**self.get_sample_leadership_entry(), "highlights": "Should be a list"}
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-array 'highlights' should fail validation.",
        )

        # Incorrect type within 'highlights'
        resume["leadership"] = [
            {
                **self.get_sample_leadership_entry(),
                "highlights": ["Led a team of 10", 456],
            }
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with non-string item in 'highlights' should fail validation.",
        )

    def test_leadership_min_items(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # 'positions' with no items
        resume["leadership"] = [{**self.get_sample_leadership_entry(), "positions": []}]
        self.assertFalse(
            validator.is_valid(resume),
            "Leadership entry with empty 'positions' should fail validation.",
        )

    def test_leadership_unique_items(self):
        validator = self.get_schema_validator()
        resume = self.get_minimal_resume()

        # Duplicate leadership entries
        resume["leadership"] = [
            self.get_sample_leadership_entry(),
            self.get_sample_leadership_entry(),
        ]
        self.assertFalse(
            validator.is_valid(resume),
            "Resume with duplicate 'leadership' entries should fail validation.",
        )

        # Unique leadership entries
        resume["leadership"] = [
            self.get_sample_leadership_entry(),
            {
                "organization": "Another Organization",
                "location": {"city": "Innovation City", "state": "IC"},
                "positions": [{"title": "Senior Manager", "start": "2021-02"}],
                "highlights": [
                    "Managed multiple teams",
                    "Implemented strategic initiatives",
                ],
            },
        ]
        self.assertTrue(
            validator.is_valid(resume),
            self.get_error_messages(validator, resume),
        )


if __name__ == "__main__":
    unittest.main()
