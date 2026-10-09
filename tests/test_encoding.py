"""Regression coverage for HTML decoding on Windows-style non-UTF-8 defaults."""
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request
from lab.server import make_server
from lab.store import Store


class EncodingTests(unittest.TestCase):
    def test_html_is_read_and_served_as_utf8_with_legacy_locale(self):
        original_read_text = Path.read_text

        def legacy_locale_read(path, *args, **kwargs):
            # Simulate Windows cp1252 when a caller forgets to specify encoding.
            kwargs.setdefault('encoding', 'cp1252')
            return original_read_text(path, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'visual').mkdir()
            expected = '<!doctype html><meta charset="utf-8"><p>caf\u00e9</p>'
            (root / 'visual/index.html').write_text(expected, encoding='utf-8')
            server = make_server(Store(root / 'lab.db'), 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch('lab.server.ROOT', root), patch.object(Path, 'read_text', legacy_locale_read):
                    with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/', timeout=3) as response:
                        self.assertEqual(response.headers.get_content_charset(), 'utf-8')
                        self.assertEqual(response.read().decode('utf-8'), expected)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == '__main__':
    unittest.main()
