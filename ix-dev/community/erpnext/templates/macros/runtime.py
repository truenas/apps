{% macro runtime_script() %}
"""Hold shared storage access for the lifetime of a catalog runtime process."""
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

BENCH = Path('/home/frappe/frappe-bench')
IMAGE_ENTRYPOINT = ['/usr/local/bin/entrypoint.sh']


def validate_state(root, site, image, operation=None):
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,120}', site) or '..' in site:
        raise RuntimeError('Invalid site name')
    if (root / '.catalog-site-name').read_text().strip() != site:
        raise RuntimeError('Catalog site identity mismatch')
    if (root / '.catalog-image').read_text().strip() != image:
        raise RuntimeError('Catalog image identity mismatch')
    folder = root / site
    if not (folder / '.nas-initialized').is_file() or (root / ('.nas-installing-' + site)).exists():
        raise RuntimeError('Site initialization is incomplete')
    state_path = folder / '.nas-upgrade-state.json'
    if not state_path.exists():
        if operation:
            raise RuntimeError('Expected upgrade state is missing')
        return
    state = json.loads(state_path.read_text())
    if not operation or state.get('operation') != operation:
        raise RuntimeError('Upgrade operation mismatch')
    if state.get('target') != image or state.get('status') != 'resumed':
        raise RuntimeError('Upgrade is not ready for runtime')


def expected_operation():
    explicit = os.environ.get('EXPECTED_UPGRADE_OPERATION')
    if explicit:
        return explicit
    if os.environ.get('CATALOG_NATIVE_LIFECYCLE') == '1':
        from native_policy import operation_id
        return operation_id(os.environ['SITE_NAME'], os.environ['CATALOG_IMAGE'])
    return None


def run():
    root = BENCH / 'sites'
    with (root / '.catalog-runtime.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        validate_state(root, os.environ['SITE_NAME'], os.environ['CATALOG_IMAGE'],
                       expected_operation())
        if len(sys.argv) < 2:
            raise RuntimeError('Runtime command missing')
        child = None
        pending_signal = None
        worker_command = sys.argv[1:3] == ['bench', 'worker']

        def forward(number, frame):
            nonlocal pending_signal
            pending_signal = number
            if child is not None:
                try:
                    if worker_command:
                        # bench execs the RQ worker. Signal its PID so the horse
                        # can finish; group SIGTERM would kill that job directly.
                        child.send_signal(number)
                    else:
                        os.killpg(child.pid, number)
                except ProcessLookupError:
                    pass

        signal.signal(signal.SIGTERM, forward)
        signal.signal(signal.SIGINT, forward)
        child = subprocess.Popen(IMAGE_ENTRYPOINT + sys.argv[1:], cwd=BENCH, start_new_session=True)
        if pending_signal is not None:
            forward(pending_signal, None)
        result = child.wait()
        return result if result >= 0 else 128 - result


if __name__ == '__main__':
    try:
        sys.exit(run())
    except Exception as error:
        print('Catalog runtime blocked: ' + type(error).__name__, flush=True)
        sys.exit(1)
{% endmacro %}
