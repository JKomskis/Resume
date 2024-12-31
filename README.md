# Resume

I got tired of having to update my resume in three different places (Word document, website, and LinkedIn) for every change, so I created this repository to end that nonsense.
So, I rewrote the content of my resume as JSON, a schema to validate it, and templates that can render the content into different formats.

## Features

- Well defined resume schema
- A script `validate_resume.py` to validate data against schema
- Template files `templates` to render resume in different formats

## Todo

- [ ] Implement a way to extend files to add or remove content
- [ ] Scrape LinkedIn profile and generate json from content

## Setup

Before running, you will need:

- A LaTeX distribution, such as MikTeX or TeX Live, include XeLaTeX
  - For ubuntu, install packages `texlive`, `texlive-xetex`, and `texlive-fonts-extra`
- For my latex resume template, you will need to install the garamondx font:
  - The `getnonfreefonts` script: `sudo texlua install-getnonfreefonts`
  - The `garamondx` font: `sudo getnonfreefonts --sys garamondx`
  - Alternatively, you can switch to `ebagaramond` in the `resume.cls` file
- A recent version of Python3

Setup instructions:

1. Run `python3 -m venv .venv` to create a virtual environment.
2. Run `source venv/bin/activate` to activate the virtual environment.
3. Run `pip install requirements.txt` to install necessary packages for the tools.

## Usage

To validate the data file against the schema: `validate_resume.py data_file schema_file`

To render a template with a data file: `render_resume.py data_file template_file [-o output_file]`

- If no output file is specified, the output file will have the same name as the data file, but with the extension of the template file.

If using VSCode, LaTeX Workshop and latexmk can be used to automatically build the PDF after modifying the .tex/.cls files or rerunning the python script.

## Schema

The JSON schema is detailed in `schemas/resume.schema.json`.

## Acknowledgements

- Resume template based on [Awesome-CV](https://github.com/posquit0/Awesome-CV) and [RenderCV](https://rendercv.com/)
- JSON schema is inspired by
  - [JsonResume](https://jsonresume.org/schema/)
  - [FRESH Resume Schema](https://github.com/fresh-standard/fresh-resume-schema/blob/master/schema/fresh-resume-schema_1.0.0-beta.json)
  - [RendereCV](https://rendercv.com/)

## Licenses

All original code in this repository are covered by the GNU GPLv3 license (see LICENSE for details). All LaTeX related files (those in the `templates` folder) are covered by the LPPL v1.3c license.
