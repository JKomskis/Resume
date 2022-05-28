
import logging
import subprocess
from pathlib import Path
from threading import Lock, Timer

from watchdog.events import PatternMatchingEventHandler

import template_renderer.template_renderer

class LatexFileEventHandler(PatternMatchingEventHandler):
    logger = logging.getLogger("LatexFileEventHandler")

    def __init__(self, renderer, output_folder, output_file):
        self.renderer = renderer
        self.output_folder = output_folder
        self.output_file = output_file
        self.mutex = Lock()
        self.buffering = False
        PatternMatchingEventHandler.__init__(self, patterns=["*.tex"])

    def on_modified(self, event):
        if event.is_directory:
            return

        with self.mutex:
            if(self.buffering):
                return
            LatexFileEventHandler.logger.info(f"{event.src_path} modified")
            timer = Timer(0.5, self.handle_on_modified)
            timer.start()
            self.buffering = True
    
    def handle_on_modified(self):
        with self.mutex:
            LatexFileEventHandler.logger.info(f"Building PDF from {self.output_file}")
            p = subprocess.Popen(["xelatex", self.output_file, "-interaction=nonstopmode"], cwd=self.output_folder,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
            LatexFileEventHandler.logger.info("PDF built")
            self.buffering = False
    
        