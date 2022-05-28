# Resume

I got tired of having to update my resume in three different places (Word document, website, and LinkedIn) for every change, so I created this repository to end that nonsense.
The repository is now the single source of truth for my resume.

## Features

- [ ] Well defined resume schema
- [ ] Validate data against schema
- [ ] Inherit data files through the `meta.extends` field
- [ ] Template LaTeX files through Jinja2
- [ ] Create one-off resumes
- [ ] Scrape LinkedIn profile and check for out of date information

## Setup

Before installing, you will need:

- A LaTeX distribution, such as MikTeX or TeX Live.
- A recent version of Python3

Setup instructions:

1. Run `python3 -m venv venv` to create a virtual environment.
2. Run `source venv/bin/activate` to activate the virtual environment.
3. Run `pip install requirements.txt` to install necessary packages for the tools.

## Schema

A JSON schema is detailed in `schema/resume.schema.json`.
Why define a new schema? Some work has already been done in this space, but those seem to no longer be active.
I also feel resumes are so unique that I wanted to have my own schema and not be limited by a schema defined by others.

## Acknowledgements

- Resume template based on <https://github.com/posquit0/Awesome-CV> but heavily modified.
- MY JSON schema is inspired by [JsonResume](https://jsonresume.org/schema/) and the [FRESH Resume Schema](https://github.com/fresh-standard/fresh-resume-schema/blob/master/schema/fresh-resume-schema_1.0.0-beta.json)

## Licenses

All original code in this repository are covered by the GNU GPLv3 license (see LICENSE for details). All LaTeX related files (those in the `templates` folder) are covered by the LPPL v1.3c license.

This project also uses third party files, which are distributed under their own terms (see LICENSE-3RD-PARTY). Note that this is my best effort to meet the license requirements of the third party projects I use. If you believe I've failed to meet a requirement of a dependency, please let me know and I will do my best to address it.

## Attributions

Awesome CV

- Copyright 2015-2016 Claud D. Park <posquit0.bj@gmail.com>
- <https://github.com/posquit0/Awesome-CV>
- LPPL v1.3c

## Resources

- <https://jinja2docs.readthedocs.io/en/stable/api.html>
- <https://resumelab.com/resume/latex-templates>
- <https://github.com/posquit0/Awesome-CV>
- <https://github.com/fresh-standard/fresh-resume-schema/blob/master/schema/fresh-resume-schema_1.0.0-beta.json>
- <https://jsonresume.org/schema/>
- <https://jinja.palletsprojects.com/en/3.0.x/api/#policies>
