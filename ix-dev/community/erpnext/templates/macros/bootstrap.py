{% macro bootstrap_script() %}
import fcntl
import os
from pathlib import Path
import shutil

root = Path('/persistent/sites')
version = os.environ['CATALOG_IMAGE']
with (root / '.catalog-bootstrap.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    marker = root / '.catalog-image'
    if marker.exists():
        if marker.read_text().strip() != version:
            raise SystemExit('Image changed. Catalog upgrade integration is not implemented; refusing startup.')
        print('Existing catalog storage verified.', flush=True)
    else:
        remaining = [p for p in root.iterdir() if p.name not in ('.catalog-bootstrap.lock', '.zfs')]
        if remaining:
            raise SystemExit('Non-empty unmanaged sites storage; refusing bootstrap.')
        shutil.copytree('/home/frappe/frappe-bench/sites', root, dirs_exist_ok=True, symlinks=True)
        marker.write_text(version)
        print('Initial site assets copied to dataset.', flush=True)

{% endmacro %}
