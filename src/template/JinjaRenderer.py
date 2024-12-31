import logging
from pathlib import Path
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
    TemplateSyntaxError,
    TemplateError as JinjaTemplateError,
)

from template.IRenderer import IRenderer
from template.TemplateError import TemplateError


class JinjaRenderer(IRenderer):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.env = Environment(
            loader=FileSystemLoader("."),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        pass

    def render(self, template_file: Path, data) -> str:
        self.logger.info(f"Rendering Template {template_file}")
        try:
            template = self.env.get_template(template_file.as_posix())
            output = template.render(data)
            return output
        except TemplateSyntaxError as e:
            message = f"Syntax Error: {e.filename}:{e.lineno}\n  "
            if e.source:
                lines = e.source.split("\n")
                if e.lineno <= len(lines):
                    message += lines[e.lineno - 1]
            message += f"\n{e.message}"
            raise TemplateError(message)
        except TemplateNotFound as e:
            message = f"Template Not Found: {e.name}"
            raise TemplateError(message)
        except JinjaTemplateError as e:
            message = f"Unknown Template Error: {str(e)}"
            raise TemplateError(message)
