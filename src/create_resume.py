import logging
import json
import datetime
import argparse
import os
from pathlib import Path

from template.JinjaRenderer import JinjaRenderer
from template.TemplateError import TemplateError
import re
import shutil


def nested_get(data, keys):
    for key in keys:
        if data is None:
            return None
        data = data.get(key)
    return data


def nested_set(data, keys, value):
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = value


def shorten_uris(resume_data):
    uri_keys = [["info", "github"], ["info", "website"], ["contact", "linkedin"]]

    for key in uri_keys:
        full_uri = nested_get(resume_data, key)
        if full_uri is not None:
            short_uri_key = key[:-1] + [key[-1] + "_short"]
            nested_set(resume_data, short_uri_key, full_uri.split("://")[-1])

    return resume_data


def convert_datetime_to_month_year(date):
    return datetime.datetime.strptime(date, "%Y-%m").strftime("%b %Y")


def convert_dates(resume_data):
    for educationEntry in resume_data.get("education", []):
        educationEntry["graduated_str"] = convert_datetime_to_month_year(
            educationEntry["graduated"]
        )

    for experienceEntry in resume_data.get("experience", []):
        for position in experienceEntry["positions"]:
            position["start_str"] = convert_datetime_to_month_year(position["start"])
            if position.get("end") is not None:
                position["end_str"] = convert_datetime_to_month_year(position["end"])

    for projectEntry in resume_data.get("projects", []):
        projectEntry["start_str"] = convert_datetime_to_month_year(
            projectEntry["start"]
        )
        if projectEntry.get("end") is not None:
            projectEntry["end_str"] = convert_datetime_to_month_year(
                projectEntry["end"]
            )

    for leadershipEntry in resume_data.get("leadership", []):
        for position in leadershipEntry["positions"]:
            position["start_str"] = convert_datetime_to_month_year(position["start"])
            if position.get("end") is not None:
                position["end_str"] = convert_datetime_to_month_year(position["end"])

    return resume_data


def concatenate_skills(resume_data):
    for skillEntry in resume_data.get("skills", []):
        skillEntry["examples_str"] = ", ".join(skillEntry["examples"])

    return resume_data


def make_location_string(location):
    location_string = location["city"]
    if location.get("state") is not None:
        location_string += f", {location['state']}"
    if location.get("country") is not None:
        location_string += f", {location['country']}"
    return location_string


def make_location_strings(resume_data):
    for educationEntry in resume_data.get("education", []):
        educationEntry["location_str"] = make_location_string(
            educationEntry["location"]
        )

    for experienceEntry in resume_data.get("experience", []):
        experienceEntry["location_str"] = make_location_string(
            experienceEntry["location"]
        )

    for leadershipEntry in resume_data.get("leadership", []):
        leadershipEntry["location_str"] = make_location_string(
            leadershipEntry["location"]
        )

    return resume_data


def escape_latex_in_str(text):
    return (
        text.replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace(" - ", " --- ")
        .replace("$", "\\$")
        .replace("^", "\\^")
        .replace("~", "\\textasciitilde ")
    )


def escape_latex(data):
    if isinstance(data, str):
        return escape_latex_in_str(data)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = escape_latex(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = escape_latex(value)

    return data


def add_present_strings(resume_data):
    for experienceEntry in resume_data.get("experience", []):
        for position in experienceEntry["positions"]:
            if position.get("end") is None:
                position["end_str"] = "Present"

    for projectEntry in resume_data.get("projects", []):
        if projectEntry.get("end") is None:
            projectEntry["end_str"] = "Present"

    for leadershipEntry in resume_data.get("leadership", []):
        for position in leadershipEntry["positions"]:
            if position.get("end") is None:
                position["end_str"] = "Present"

    return resume_data


def preprocess_resume_data_for_latex(resume_data):
    resume_data = escape_latex(resume_data)

    return resume_data


def preprocess_resume_data(resume_data):
    resume_data = shorten_uris(resume_data)
    resume_data = convert_dates(resume_data)
    resume_data = concatenate_skills(resume_data)
    resume_data = make_location_strings(resume_data)
    resume_data = add_present_strings(resume_data)

    return resume_data


def copy_cls_file_if_needed(template_file, output_file_parent):
    with open(template_file, "r") as f:
        for line in f:
            match = re.search(r"\\documentclass\[.*?\]{(.*?)}", line)
            if match:
                cls_name = match.group(1)
                cls_file = template_file.parent / f"{cls_name}.cls"

                if cls_file.exists():
                    logging.info(
                        f"Found document class '{cls_name}'. Copying '{cls_file}' to '{output_file_parent}'"
                    )
                    shutil.copy(cls_file, output_file_parent)
                break


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description="Create resume from template and data."
    )
    parser.add_argument("input_file", help="Input template file")
    parser.add_argument("data_file", help="Input data file")
    parser.add_argument(
        "-d",
        "--output_directory",
        help="Output directory (default: parent directory of the data file)",
    )
    args = parser.parse_args()

    template_file = Path(args.input_file)
    data_file = Path(args.data_file)
    if not args.output_directory:
        out_dir = Path.cwd()
    else:
        out_dir = Path(args.output_directory)

    filename_base = data_file.stem
    suffixes = template_file.suffixes
    if suffixes and suffixes[-1] == ".j2":
        suffixes.pop()
    output_file = out_dir / f"{filename_base}{''.join(suffixes)}"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    resume_data = None

    try:
        with data_file.open("r") as file:
            resume_data = json.load(file)
    except FileNotFoundError:
        logging.error(f"Data file {data_file} does not exist.")
        exit(1)

    if ".tex" in template_file.suffixes:
        resume_data = preprocess_resume_data_for_latex(resume_data)
        copy_cls_file_if_needed(template_file, output_file.parent)
    resume_data = preprocess_resume_data(resume_data)

    renderer = JinjaRenderer()
    try:
        output = renderer.render(template_file, resume_data)

        logging.info(f"Writing output to {output_file}")
        with output_file.open("w") as file:
            file.write(output)
    except TemplateError as e:
        logging.error(f"Error rendering template:\n{e}")
        exit(1)


if __name__ == "__main__":
    main()
