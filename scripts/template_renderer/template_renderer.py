from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import logging
from jinja2.environment import Template

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch
from jinja2 import Environment, FileSystemLoader, select_autoescape

from util.merge_dicts import merge_dicts
from util.data_file_event_handler import DataFileEventHandler
from util.template_file_event_handler import TemplateFileEventHandler
from util.latex_file_event_handler import LatexFileEventHandler

class TemplateRenderer:
    logger = logging.getLogger("TemplateRenderer")

    def __init__(self, data_file: Path,
                        watch: bool,
                        templates_folder = Path("templates"),
                        output_folder = Path("dist"),
                        main_file = Path("resume.tex")):
        self.data_file_path = data_file
        self.watch = watch
        self.templates_folder = templates_folder
        self.output_folder = output_folder
        self.main_file = main_file

        self.template_env = Environment(
            loader = FileSystemLoader(self.templates_folder),
            autoescape = select_autoescape()
        )

        self.file_observer = Observer()
        self.watched_files: dict[Path, ObservedWatch] = {}

        shutil.rmtree(self.output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.data_file_handler = DataFileEventHandler(self, self.data_file_path)
        self.load_data()
        self.file_observer.start()

        self.template_file_handler = TemplateFileEventHandler(self)
        self.file_observer.schedule(self.template_file_handler, self.templates_folder, recursive=True)

        self.latex_file_handler = LatexFileEventHandler(self, self.output_folder, self.main_file)
        self.file_observer.schedule(self.latex_file_handler, self.output_folder, recursive=True)
    
    def load_data(self) -> None:
        self.data = self._load_data_helper(self.data_file_path)
        # TemplateRenderer.logger.info(json.dumps(self.data, indent=2))

    def _load_data_helper(self, data_file: Path) -> dict:
        TemplateRenderer.logger.info(f"Loading data from {data_file}")
        with open(data_file) as f:
            data = json.load(f)
            if "meta" in data and "extends" in data["meta"]:
                base_data = self._load_data_helper(data["meta"]["extends"])
                data = merge_dicts(base_data, data)

            if self.watch and not data_file in self.watched_files:
                TemplateRenderer.logger.info(f"Watching file {data_file}")
                self.watched_files[data_file] = self.file_observer.schedule(self.data_file_handler, data_file)

            return data

    def render_templates(self) -> None:
        template_files = self.templates_folder.rglob("*.jinja")
        template_files = [file.relative_to(self.templates_folder) for file in template_files]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.render_template, file) for file in template_files]
            results = [future.result() for future in futures]
            # print(results)
        
        class_files = self.templates_folder.rglob("*.cls")
        for file in class_files:
            output_file = self.output_folder / file.relative_to(self.templates_folder)
            shutil.copyfile(file, output_file)

    def render_template(self, file: Path) -> None:
        TemplateRenderer.logger.info(f"Rendering {file}")
        template = self.template_env.get_template(file.as_posix())
        rendered = template.render(self.data)

        output_file = Path(self.output_folder) / file.parent / file.stem
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as output_file:
            output_file.write(rendered)
    
    def close(self) -> None:
        self.file_observer.stop()
    
    def join(self) -> None:
        self.file_observer.join()