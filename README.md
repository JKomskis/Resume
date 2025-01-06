# Resume

I got tired of having to update my resume in three different places (Word document, website, and LinkedIn) for every change, so I created this repository to avoid that.
So, I rewrote the content of my resume as JSON, a schema to validate it, and templates that can render the content into different formats.

There are currently three versions of my resume:

- `resume.json`: The everyday resume I would use if asked for my resume
- `resume_extra.json`: The resume with my complete experience and project history, mostly for own reference
- `resume_one_pager.json`: A one-page version of my resume with what I consider the most important information

Yes, currently information is duplicated between the files. Eventually I'll find a good way to eliminate that. (If you have ideas, I'm all ears!)

## Features

- Well defined resume schema
- A script `validate_resume.py` to validate data against schema
- Template files `templates` to render resume in different formats

## Todo

- [ ] Implement a way to extend files to add or remove content without duplicating across files
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

To render a template with a data file: `render_resume.py data_file template_file [-d output_directory]`

- If no output directroy is specified, the current directory is used.

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
