import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler

import template_renderer.template_renderer

class DataFileEventHandler(FileSystemEventHandler):
    logger = logging.getLogger("DataFileEventHandler")

    def __init__(self, renderer, data_file_path: Path):
        self.renderer = renderer
        self.data_file_path = data_file_path

    def on_modified(self, event):
        if event.is_directory:
            return
    
        DataFileEventHandler.logger.info(f"{event.src_path} modified")
        self.renderer.load_data()
        self.renderer.render_templates()