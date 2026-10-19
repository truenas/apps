{% macro initialize_script() %}
"""Runs inside the official ERPNext container. Fresh installs only."""
import json
import os
from pathlib import Path
import re
import subprocess


def upgrade_guard(folder):
    expected = os.environ.get('EXPECTED_UPGRADE_OPERATION')
    path = folder / '.nas-upgrade-state.json'
    if not path.exists():
        if expected:
            raise SystemExit('Upgrade backup/migration state missing; startup blocked.')
        return
    state = json.loads(path.read_text())
    if not expected or state.get('operation') != expected:
        raise SystemExit('Upgrade operation mismatch; startup blocked.')
    if state.get('target') != os.environ.get('EXPECTED_UPGRADE_IMAGE'):
        raise SystemExit('Upgrade target mismatch; startup blocked.')
    if state.get('status') not in ('migrated', 'resumed'):
        raise SystemExit('Migration has not succeeded; startup blocked.')


def finish_upgrade(folder):
    path = folder / '.nas-upgrade-state.json'
    if not path.exists():
        return
    state = json.loads(path.read_text())
    if state['status'] == 'resumed':
        return
    config_path = folder / 'site_config.json'
    config = json.loads(config_path.read_text())
    config['maintenance_mode'] = state['previous_maintenance']
    config['pause_scheduler'] = state['previous_pause']
    temporary = config_path.with_name('site_config.resume-tmp')
    temporary.write_text(json.dumps(config, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(config_path)
    state['status'] = 'resumed'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(path)
    print('Upgrade verified; previous maintenance/scheduler settings restored.', flush=True)


def main():
    site = os.environ['SITE_NAME']
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,120}', site) or '..' in site:
        raise SystemExit('Invalid site name')
    root = Path('sites')
    marker = root / site / '.nas-initialized'
    pending = root / ('.nas-installing-' + site)
    upgrade_guard(root / site)

    def bench(*args):
        return subprocess.run(['bench', *args], check=True, capture_output=False)

    if pending.exists():
        raise SystemExit('A previous installation was interrupted. Inspect initializer logs; do not delete site data automatically.')
    if (root / site).exists():
        if not marker.exists():
            raise SystemExit('An unmanaged or incomplete site exists. Import is not supported by this prototype.')
        apps = subprocess.check_output(['bench', '--site', site, 'execute', 'frappe.get_installed_apps'], text=True)
        if 'erpnext' not in json.loads(apps):
            raise SystemExit('Existing site is missing ERPNext')
        finish_upgrade(root / site)
        print('Existing managed ERPNext site verified; skipping installation.', flush=True)
        return
    if not os.environ.get('ADMIN_PASSWORD') or not os.environ.get('DB_ROOT_PASSWORD'):
        raise SystemExit('Initial passwords are required')
    pending.write_text('Installation started; inspect logs if this marker remains.\n')
    bench('new-site', site, '--db-host', 'db', '--db-root-username', 'root',
          '--db-root-password', os.environ['DB_ROOT_PASSWORD'],
          '--admin-password', os.environ['ADMIN_PASSWORD'],
          '--mariadb-user-host-login-scope=%', '--install-app', 'erpnext')
    bench('--site', site, 'enable-scheduler')
    marker.write_text('Prototype initialized this site. Not an upgrade version marker.\n')
    pending.unlink()
    print('ERPNext installation complete.', flush=True)


if __name__ == '__main__':
    import fcntl
    with Path('sites/.catalog-initialize.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        requested = os.environ['SITE_NAME']
        marker = Path('sites/.catalog-site-name')
        if marker.exists() and marker.read_text().strip() != requested:
            raise SystemExit('Site name changed; refusing to create a second site.')
        if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,120}', requested) or '..' in requested:
            raise SystemExit('Invalid site name')
        marker.write_text(requested)
        Path('sites/apps.txt').write_text('\n'.join(sorted(p.name for p in Path('apps').iterdir() if p.is_dir())) + '\n')
        for args in [
            ['-g', 'db_host', 'db'], ['-gp', 'db_port', '3306'],
            ['-g', 'redis_cache', 'redis://redis-cache:6379'],
            ['-g', 'redis_queue', 'redis://redis-queue:6379'],
            ['-g', 'redis_socketio', 'redis://redis-queue:6379'],
            ['-gp', 'socketio_port', '9000'],
            ['-g', 'chromium_path', '/usr/lib/chromium/chromium-headless-shell'],
        ]:
            subprocess.run(['bench', 'set-config', *args], check=True)
        main()

{% endmacro %}
