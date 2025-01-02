from jsonschema import Draft202012Validator
import re


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.\+-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_uri(uri: str) -> bool:
    pattern = (
        r"^(?:http|ftp)s?://(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}(?::\d{2,5})?(?:/\S*)?$"
    )
    return re.match(pattern, uri) is not None


def get_schema_format_checker():
    format_checker = Draft202012Validator.FORMAT_CHECKER

    format_checker.checks(
        "email",
    )(is_valid_email)

    format_checker.checks(
        "uri",
    )(is_valid_uri)

    return format_checker
