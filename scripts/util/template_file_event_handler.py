
import logging
from pathlib import Path
from threading import Lock, Timer

from watchdog.events import PatternMatchingEventHandler

import template_renderer.template_renderer

class TemplateFileEventHandler(PatternMatchingEventHandler):
    logger = logging.getLogger("TemplateFileEventHandler")

    def __init__(self, renderer):
        self.renderer = renderer
        self.mutex = Lock()
        self.buffering = False
        PatternMatchingEventHandler.__init__(self, patterns=["*.jinja"])

    def on_modified(self, event):
        if event.is_directory:
            return

        with self.mutex:
            if(self.buffering):
                return
            TemplateFileEventHandler.logger.info(f"{event.src_path} modified")
            timer = Timer(0.5, self.handle_on_modified)
            timer.start()
            self.buffering = True
    
    def handle_on_modified(self):
        with self.mutex:
            self.renderer.render_templates()
            self.buffering = False
    
        