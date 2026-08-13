#!/usr/bin/env python3
"""Minify CSS and HTML assets for Radio Calico."""

import os
import sys
from pathlib import Path
import logging
from time import time

try:
    import rcssmin
    import htmlmin
except ImportError:
    print("Error: Required packages not installed. Run: pip install rcssmin htmlmin2")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
STATIC_DIR = PROJECT_ROOT / "app" / "static"
TEMPLATES_DIR = PROJECT_ROOT / "app" / "templates"


def minify_css(input_file: Path, output_file: Path = None) -> tuple[bool, int]:
    """Minify a CSS file. Returns (success, size_saved_bytes)."""
    if output_file is None:
        output_file = input_file

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original = f.read()

        original_size = len(original.encode('utf-8'))
        minified = rcssmin.cssmin(original)
        minified_size = len(minified.encode('utf-8'))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified)

        saved = original_size - minified_size
        percent = (saved / original_size * 100) if original_size > 0 else 0
        logger.info(f"  ✓ {input_file.name}: {original_size}B → {minified_size}B ({percent:.1f}% saved)")
        return True, saved
    except Exception as e:
        logger.error(f"  ✗ {input_file.name}: {e}")
        return False, 0


def minify_html(input_file: Path, output_file: Path = None) -> tuple[bool, int]:
    """Minify an HTML file. Returns (success, size_saved_bytes)."""
    if output_file is None:
        output_file = input_file

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original = f.read()

        original_size = len(original.encode('utf-8'))
        # htmlmin2 minifies HTML while preserving template tags
        minified = htmlmin.minify(original, remove_empty_space=True, remove_comments=True)
        minified_size = len(minified.encode('utf-8'))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified)

        saved = original_size - minified_size
        percent = (saved / original_size * 100) if original_size > 0 else 0
        logger.info(f"  ✓ {input_file.name}: {original_size}B → {minified_size}B ({percent:.1f}% saved)")
        return True, saved
    except Exception as e:
        logger.error(f"  ✗ {input_file.name}: {e}")
        return False, 0


def minify_all(verbose=False) -> dict:
    """Minify all CSS and HTML files. Returns stats."""
    stats = {
        'css_files': 0,
        'html_files': 0,
        'total_saved': 0,
        'success': True
    }

    # Minify CSS
    if STATIC_DIR.exists():
        css_files = list(STATIC_DIR.glob('*.css'))
        if css_files:
            logger.info(f"\n📦 Minifying CSS ({len(css_files)} files):")
            for css_file in css_files:
                success, saved = minify_css(css_file)
                stats['css_files'] += 1
                stats['total_saved'] += saved
                if not success:
                    stats['success'] = False

    # Minify HTML templates
    if TEMPLATES_DIR.exists():
        html_files = list(TEMPLATES_DIR.glob('*.html'))
        if html_files:
            logger.info(f"\n📄 Minifying HTML templates ({len(html_files)} files):")
            for html_file in html_files:
                success, saved = minify_html(html_file)
                stats['html_files'] += 1
                stats['total_saved'] += saved
                if not success:
                    stats['success'] = False

    return stats


def watch_mode():
    """Watch for CSS/HTML changes and minify automatically."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    except ImportError:
        logger.error("watchdog not installed. Run: pip install watchdog")
        sys.exit(1)

    class MinifyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            path = Path(event.src_path)
            if path.suffix == '.css' and STATIC_DIR in path.parents:
                minify_css(path)
            elif path.suffix == '.html' and TEMPLATES_DIR in path.parents:
                minify_html(path)

    observer = Observer()
    observer.schedule(MinifyHandler(), str(STATIC_DIR), recursive=False)
    observer.schedule(MinifyHandler(), str(TEMPLATES_DIR), recursive=False)
    observer.start()

    logger.info("👀 Watching for CSS/HTML changes...")
    logger.info(f"   CSS: {STATIC_DIR}")
    logger.info(f"   HTML: {TEMPLATES_DIR}")
    logger.info("\nPress Ctrl+C to stop\n")

    try:
        while True:
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("\n✅ Watch mode stopped")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'watch':
        watch_mode()
    else:
        start_time = time()
        stats = minify_all()
        elapsed = time() - start_time

        logger.info(f"\n{'='*50}")
        logger.info(f"✅ Minification complete in {elapsed:.2f}s")
        logger.info(f"   CSS files: {stats['css_files']}")
        logger.info(f"   HTML files: {stats['html_files']}")
        logger.info(f"   Total saved: {stats['total_saved']:,} bytes ({stats['total_saved']/1024:.1f} KB)")
        logger.info(f"{'='*50}\n")

        sys.exit(0 if stats['success'] else 1)
