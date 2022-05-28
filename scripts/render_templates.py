import argparse
import time
from pathlib import Path
import logging

from template_renderer.template_renderer import TemplateRenderer

if __name__ == "__main__":
    format = "%(asctime)s: [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=format, datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument("data", nargs='?', default="resume.json",
        help="Input data file to use in template rendering. Default is 'resume.json'.")
    parser.add_argument("-w", "--watch", action="store_true",
        help="Watch templates and data files for changes and automatically re-render.")
    args = parser.parse_args()

    renderer = TemplateRenderer(Path(args.data), args.watch)
    renderer.render_templates()

    if args.watch:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            renderer.close()
        renderer.join()
    