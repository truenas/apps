{% macro native_script() %}
"""Integrated catalog candidate: bootstrap, source backup and target initialization."""
import fcntl
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
from native_policy import operation_id
from patch_policy import SOURCE, TARGET, SOURCE_DIGEST, SOURCE_ID, validate_patch
import rehearsal as job

BENCH = Path('/home/frappe/frappe-bench')


def configure(root):
    site = os.environ['SITE_NAME']
    image = os.environ['CATALOG_IMAGE']
    if image not in (SOURCE, TARGET):
        raise RuntimeError('Native candidate supports only the reviewed image pair')
    operation = operation_id(site, image)
    job.ROOT = root
    os.environ.update(OPERATION_ID=operation, SOURCE_IMAGE=SOURCE, TARGET_IMAGE=image,
        SOURCE_DIGEST=SOURCE_DIGEST, OBSERVED_SOURCE_IMAGE_ID=SOURCE_ID,
        PREVIOUS_UPGRADE_OPERATION=operation_id(site,SOURCE),
        CATALOG_OPERATION_LAYOUT='catalog-patch-v1', SIMULATE_FAILURE='0',
        EXPECTED_UPGRADE_OPERATION=operation, EXPECTED_UPGRADE_IMAGE=image)
    return site, image, operation


def read_state(root, site):
    path = root/site/'.nas-upgrade-state.json'
    return json.loads(path.read_text()) if path.exists() else None


def fresh_state(state, image, operation):
    return state and all(state.get(key)==value for key,value in (
        ('layout','catalog-native-v1'),('installation','fresh'),('operation',operation),
        ('source',image),('target',image),('status','resumed')))


def write_text(path, value):
    temporary=path.with_name(path.name+'.native-tmp')
    with temporary.open('w') as output:
        output.write(value+'\n'); output.flush(); os.fsync(output.fileno())
    temporary.replace(path)
    descriptor=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)


def bootstrap(root):
    site,image,operation=configure(root)
    marker=root/'.catalog-image'
    if marker.exists():
        installed=marker.read_text().strip()
        if (root/'.catalog-site-name').read_text().strip()!=site:
            raise RuntimeError('Native site name changed')
        if installed!=image:
            validate_patch(installed,image,SOURCE_DIGEST,SOURCE_ID)
            if not (root/site/'.nas-initialized').is_file():
                raise RuntimeError('Initialized source required before patch')
        print('Native managed storage verified.',flush=True)
        return
    if any(path.name not in ('.catalog-runtime.lock','.catalog-bootstrap.lock','.zfs') for path in root.iterdir()):
        raise RuntimeError('Non-empty unmanaged native storage')
    shutil.copytree(BENCH/'sites',root,dirs_exist_ok=True,symlinks=True)
    write_text(root/'.catalog-site-name',site)
    write_text(marker,image)
    print('Native fresh storage prepared.',flush=True)


def backup(root):
    site,image,operation=configure(root)
    installed=(root/'.catalog-image').read_text().strip()
    state=read_state(root,site)
    initialized=(root/site/'.nas-initialized').is_file()
    if installed==image:
        if not initialized and state is None:
            print('Native fresh install: source backup not needed.',flush=True)
            return
        if fresh_state(state,image,operation):
            print('Native unchanged fresh installation: no migration.',flush=True)
            return
        if job.matching_state(state,operation,SOURCE) and state.get('status') in ('migrated','resumed'):
            job.verify_backup(state)
            print('Native completed source backup verified.',flush=True)
            return
        raise RuntimeError('Native target state is incomplete or unsupported')
    validate_patch(installed,image,SOURCE_DIGEST,SOURCE_ID)
    if not state or state.get('operation')!=operation:
        if not fresh_state(state,SOURCE,operation_id(site,SOURCE)):
            raise RuntimeError('Expected managed native source installation required')
    os.environ['UPGRADE_PHASE']='backup'
    job.run_job(locked=True)


def initialize(root, install):
    site,image,operation=configure(root)
    marker=root/'.catalog-image'
    state=read_state(root,site)
    initialized=(root/site/'.nas-initialized').is_file()
    if not initialized:
        if state is not None or marker.read_text().strip()!=image:
            raise RuntimeError('Incomplete native installation state')
        saved={key:os.environ.pop(key) for key in ('EXPECTED_UPGRADE_OPERATION','EXPECTED_UPGRADE_IMAGE')}
        try: install()
        finally: os.environ.update(saved)
        if not (root/site/'.nas-initialized').is_file():
            raise RuntimeError('Native initializer did not complete')
        job.write_json(root/site/'.nas-upgrade-state.json',dict(layout='catalog-native-v1',
            installation='fresh',operation=operation,source=image,target=image,status='resumed'))
        print('NATIVE FRESH INSTALL COMPLETE.',flush=True)
        return
    if fresh_state(state,image,operation) and marker.read_text().strip()==image:
        install()
        print('NATIVE UNCHANGED INSTALL VERIFIED.',flush=True)
        return
    if image!=TARGET:
        raise RuntimeError('Native downgrade or unsupported state refused')
    import patch_target
    patch_target.finish(job,install,locked=True)
    print('NATIVE PATCH COMPLETE.',flush=True)


def main():
    action=sys.argv[1]
    root=Path('/persistent/sites') if action=='bootstrap' else BENCH/'sites'
    with (root/'.catalog-runtime.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if action=='bootstrap': bootstrap(root)
        elif action=='backup': backup(root)
        elif action=='initialize': initialize(root,lambda:runpy.run_path('/catalog/initialize.py',run_name='__main__'))
        else: raise RuntimeError('Unknown native lifecycle action')


if __name__=='__main__':
    try: main()
    except Exception as error:
        print('Native lifecycle blocked: '+type(error).__name__,flush=True)
        raise SystemExit(1)

{% endmacro %}

{% macro native_policy_script() %}
"""Stable lifecycle identity for catalog-created sites; independent of user secrets."""
import hashlib
import re


def operation_id(site, image):
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,120}', site) or '..' in site:
        raise RuntimeError('Invalid native site identity')
    return hashlib.sha256(('catalog-native-v1\0'+site+'\0'+image).encode()).hexdigest()[:32]

{% endmacro %}

{% macro native_job_script() %}
"""Offline same-image rehearsal or explicit same-content digest pinning."""
import fcntl
from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path('/home/frappe/frappe-bench/sites')


def write_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as output:
        os.chmod(temporary, 0o600)
        json.dump(value, output, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def assert_queue_quiescent():
    from queue_guard import require_empty
    require_empty()


def layout():
    value = os.environ.get('CATALOG_OPERATION_LAYOUT', 'catalog-rehearsal-v1')
    if value not in ('catalog-rehearsal-v1', 'catalog-upgrade-v1', 'catalog-patch-v1'):
        raise RuntimeError('Unsupported operation layout')
    return value


def image_parts(image):
    match = re.fullmatch(r'frappe/erpnext:v(16)\.(\d+)\.(\d+)(?:@(sha256:[a-f0-9]{64}))?', image)
    if not match:
        raise RuntimeError('Expected pinned ERPNext v16 image reference')
    return tuple(map(int, match.groups()[:3])), match.group(4)


def validate_transition(source, target, source_digest, observed_id):
    old, old_digest = image_parts(source)
    new, new_digest = image_parts(target)
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', source_digest or '') or not re.fullmatch(r'sha256:[a-f0-9]{64}', observed_id or ''):
        raise RuntimeError('Observed source image ID and repository digest required')
    if old_digest and old_digest != source_digest:
        raise RuntimeError('Observed source digest differs from installed reference')
    if not new_digest or new != old or new_digest != source_digest:
        raise RuntimeError('Only same-version same-content digest pinning is implemented')


def identities(allow_target=False):
    site = os.environ['SITE_NAME']
    operation = os.environ['OPERATION_ID']
    image = os.environ['SOURCE_IMAGE']
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,120}', site) or '..' in site:
        raise RuntimeError('Invalid site name')
    if not re.fullmatch(r'[a-f0-9]{32}', operation):
        raise RuntimeError('Invalid operation ID')
    target = os.environ['TARGET_IMAGE']
    if layout() in ('catalog-upgrade-v1', 'catalog-patch-v1'):
        if layout() == 'catalog-patch-v1':
            from patch_policy import validate_patch
            validate_patch(image, target, os.environ.get('SOURCE_DIGEST'), os.environ.get('OBSERVED_SOURCE_IMAGE_ID'))
        else:
            validate_transition(image, target, os.environ.get('SOURCE_DIGEST'), os.environ.get('OBSERVED_SOURCE_IMAGE_ID'))
        from erpnext import __version__
        expected = image_parts(image if os.environ.get('UPGRADE_PHASE') == 'backup' else target)[0]
        if tuple(map(int, __version__.split('.'))) != expected:
            raise RuntimeError('Container ERPNext version differs from requested phase')
    elif not re.fullmatch(r'frappe/erpnext:v16\.\d+\.\d+(?:@sha256:[a-f0-9]{64})?', image) or target != image:
        raise RuntimeError('Only same-image rehearsal is implemented')
    if (ROOT / '.catalog-site-name').read_text().strip() != site:
        raise RuntimeError('Site identity mismatch')
    allowed = (image, target) if allow_target else (image,)
    if (ROOT / '.catalog-image').read_text().strip() not in allowed:
        raise RuntimeError('Image identity mismatch')
    if not (ROOT / site / '.nas-initialized').is_file():
        raise RuntimeError('Managed initialized site required')
    return site, operation, image


def matching_state(state, operation, image):
    return state and all(state.get(key) == value for key, value in (
        ('layout', layout()), ('operation', operation),
        ('source', image), ('target', os.environ['TARGET_IMAGE'])))


def verify_backup(state):
    recovery = ROOT / '.catalog-recovery' / state['operation']
    files = state.get('backup_files', {})
    if len(files) < 8:
        raise RuntimeError('Backup inventory incomplete')
    for name, metadata in files.items():
        if Path(name).name != name:
            raise RuntimeError('Invalid backup filename')
        path = recovery / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size != metadata['size'] or digest(path) != metadata['sha256']:
            raise RuntimeError('Backup integrity check failed')


def run_job(locked=False):
    with (nullcontext() if locked else (ROOT / '.catalog-runtime.lock').open('a')) as lock:
        if not locked:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        site, operation, image = identities(allow_target=layout() == 'catalog-patch-v1')
        folder = ROOT / site
        state_path = folder / '.nas-upgrade-state.json'
        state = json.loads(state_path.read_text()) if state_path.exists() else None

        def bench(*arguments):
            subprocess.run(['bench', '--site', site, *arguments], check=True,
                           cwd=ROOT.parent)

        if os.environ['UPGRADE_PHASE'] == 'backup':
            if ((ROOT / '.catalog-image').read_text().strip() != image
                    and not (matching_state(state, operation, image) and state.get('status') in ('migrated', 'resumed'))):
                raise RuntimeError('Source image marker required for a new backup')
            if state and state.get('operation') == operation:
                if matching_state(state, operation, image) and state.get('status') in ('backed_up', 'migrated', 'resumed'):
                    verify_backup(state)
                    print('BACKUP ALREADY COMPLETE.', flush=True)
                    return
                raise RuntimeError('Interrupted or mismatched operation; automatic retry refused')
            if layout() in ('catalog-upgrade-v1', 'catalog-patch-v1'):
                previous = os.environ.get('PREVIOUS_UPGRADE_OPERATION')
                supported = ('catalog-rehearsal-v1', 'catalog-restore-v1', 'catalog-upgrade-v1')
                if layout() == 'catalog-patch-v1':
                    supported += ('catalog-native-v1',)
                if state and (state.get('layout') not in supported
                        or state.get('status') != 'resumed' or state.get('target') != image
                        or state.get('operation') != previous):
                    raise RuntimeError('Source is not the expected successful installed operation')
                if not state and previous:
                    raise RuntimeError('Previous installed operation state is missing')
            else:
                previous = os.environ.get('PREVIOUS_UPGRADE_OPERATION')
                if state and (state.get('layout') not in ('catalog-rehearsal-v1', 'catalog-restore-v1')
                        or state.get('status') != 'resumed' or state.get('target') != image
                        or (previous and state.get('operation') != previous)):
                    raise RuntimeError('A different unfinished or unsupported operation exists')
                if previous and not state:
                    raise RuntimeError('Previous installed operation state is missing')
            assert_queue_quiescent()
            config = json.loads((folder / 'site_config.json').read_text())
            recovery = ROOT / '.catalog-recovery' / operation
            recovery.mkdir(mode=0o700, parents=True, exist_ok=False)
            os.chmod(recovery.parent, 0o700)
            state = dict(layout=layout(), operation=operation,
                source=image, target=os.environ['TARGET_IMAGE'], status='backing_up',
                previous_maintenance=config.get('maintenance_mode', 0),
                previous_pause=config.get('pause_scheduler', 0))
            if layout() in ('catalog-upgrade-v1', 'catalog-patch-v1'):
                state.update(source_digest=os.environ['SOURCE_DIGEST'],
                    observed_source_image_id=os.environ['OBSERVED_SOURCE_IMAGE_ID'])
            write_json(state_path, state)
            for source, name in ((folder / 'site_config.json', 'site_config.before.json'),
                    (ROOT / 'common_site_config.json', 'common_site_config.before.json'),
                    (ROOT / '.catalog-site-name', 'catalog-site-name.before'),
                    (ROOT / '.catalog-image', 'catalog-image.before')):
                shutil.copyfile(source, recovery / name)
                os.chmod(recovery / name, 0o600)
            config.update(maintenance_mode=1, pause_scheduler=1)
            write_json(folder / 'site_config.json', config)
            bench('backup', '--with-files', '--ignore-backup-conf', '--backup-path', str(recovery))
            names = [path.name for path in recovery.iterdir() if path.is_file()]
            for suffix in ('-database.sql.gz', '-files.tar', '-private-files.tar', '-site_config_backup.json'):
                matches = [name for name in names if name.endswith(suffix)]
                if suffix == '-files.tar':
                    matches = [name for name in matches if not name.endswith('-private-files.tar')]
                if len(matches) != 1:
                    raise RuntimeError('Missing or ambiguous backup component: ' + suffix)
            files = {}
            for path in recovery.iterdir():
                if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
                    raise RuntimeError('Invalid backup component')
                os.chmod(path, 0o600)
                with path.open('rb') as completed:
                    os.fsync(completed.fileno())
                files[path.name] = {'size': path.stat().st_size, 'sha256': digest(path)}
            state['backup_files'] = files
            verify_backup(state)
            state['status'] = 'backed_up'
            write_json(recovery / 'manifest.json', state)
            write_json(state_path, state)
            print('BACKUP COMPLETE: .catalog-recovery/' + operation, flush=True)
            return

        if os.environ['UPGRADE_PHASE'] != 'migrate' or not matching_state(state, operation, image):
            raise RuntimeError('Matching backup state required')
        verify_backup(state)
        if state['status'] in ('migrated', 'resumed'):
            print('MIGRATION ALREADY COMPLETE.', flush=True)
            return
        if state['status'] != 'backed_up':
            raise RuntimeError('Interrupted migration; restore recovery required before retry')
        if os.environ.get('SIMULATE_FAILURE') == '1':
            raise RuntimeError('EXPECTED TEST FAILURE before migration; resume must remain blocked')
        assert_queue_quiescent()
        state['status'] = 'migrating'
        write_json(state_path, state)
        bench('migrate')
        config = json.loads((folder / 'site_config.json').read_text())
        config.update(maintenance_mode=1, pause_scheduler=1)
        write_json(folder / 'site_config.json', config)
        state['status'] = 'migrated'
        write_json(state_path, state)
        print('MIGRATION COMPLETE. Use matching guarded resume.', flush=True)


if __name__ == '__main__':
    run_job()

{% endmacro %}

{% macro native_patch_policy_script() %}
"""Explicitly reviewed image pair for the isolated catalog patch experiment."""
SOURCE_DIGEST = 'sha256:f2d409c58ed1b688b6f2914d4a7f8b2468ee60bd1a3f1bd82d6fe32071806cb1'
SOURCE_ID = 'sha256:e43ea1a1aa4bf9a7d01001aaa0120ce564d9af5d10b588064bb8de0aad7ec213'
SOURCE = 'frappe/erpnext:v16.51.0@' + SOURCE_DIGEST
TARGET = 'frappe/erpnext:v16.51.1@sha256:a856e7f65c7bfc9cfa2e74f95b62e11d37190c380d958cbf3bea5d05e2ec9268'


def validate_patch(source, target, source_digest, observed_id):
    if (source, target, source_digest, observed_id) != (SOURCE, TARGET, SOURCE_DIGEST, SOURCE_ID):
        raise RuntimeError('Only the explicitly reviewed v16.51.0 to v16.51.1 image pair is supported')

{% endmacro %}

{% macro native_patch_target_script() %}
"""Target-image migration and durable identity commit under exclusive exclusion."""
import fcntl
from contextlib import nullcontext
import importlib.util
import json
import os
from pathlib import Path
import runpy

BAKED = Path('/home/frappe/frappe-bench/assets')

def finish(job, initialize, locked=False):
    with (nullcontext() if locked else (job.ROOT / '.catalog-runtime.lock').open('a')) as lock:
        if not locked:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.environ['UPGRADE_PHASE'] = 'migrate'
        site, operation, source = job.identities(allow_target=True)
        state_path = job.ROOT / site / '.nas-upgrade-state.json'
        job.run_job(locked=True)
        state = json.loads(state_path.read_text())
        if not job.matching_state(state, operation, source) or state.get('status') not in ('migrated', 'resumed'):
            raise RuntimeError('Successful matching patch migration required')
        job.verify_backup(state)
        assets = job.ROOT / 'assets'
        baked = BAKED
        if not baked.is_dir() or not assets.is_symlink() or assets.readlink() != baked:
            raise RuntimeError('Expected official baked asset symlink required')
        marker = job.ROOT / '.catalog-image'
        temporary = marker.with_name(marker.name + '.patch-tmp')
        with temporary.open('w') as output:
            output.write(os.environ['TARGET_IMAGE'] + '\n')
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(marker)
        descriptor = os.open(marker.parent, os.O_RDONLY)
        try: os.fsync(descriptor)
        finally: os.close(descriptor)
        initialize()
        config_path = job.ROOT / site / 'site_config.json'
        config = json.loads(config_path.read_text())
        config.update(maintenance_mode=state['previous_maintenance'], pause_scheduler=state['previous_pause'])
        job.write_json(config_path, config)
        state['status'] = 'resumed'
        job.write_json(state_path, state)
        print('PATCH LIFECYCLE COMPLETE.', flush=True)


def main():
    spec = importlib.util.spec_from_file_location('patch_job', '/catalog/rehearsal.py')
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    finish(job, lambda: runpy.run_path('/catalog/initialize.py', run_name='__main__'))


if __name__ == '__main__':
    try: main()
    except Exception as error:
        print('Patch lifecycle blocked: ' + type(error).__name__, flush=True)
        raise SystemExit(1)

{% endmacro %}

{% macro native_queue_guard_script() %}
"""Read-only queue gate: do not migrate across pending or unresolved RQ work."""


def check_queues(queues, registry_types):
    for queue in queues:
        if queue.count:
            raise RuntimeError('Queued work must be drained before migration')
        for registry_type in registry_types:
            registry = registry_type(name=queue.name, connection=queue.connection)
            # Never let an inspection clean up stale started jobs automatically.
            if registry.get_job_ids(cleanup=False):
                raise RuntimeError('Unresolved RQ work must be reviewed before migration')


def require_empty():
    from redis import Redis
    from rq import Queue
    from rq.registry import StartedJobRegistry, DeferredJobRegistry, ScheduledJobRegistry, FailedJobRegistry
    connection = Redis.from_url('redis://redis-queue:6379', socket_connect_timeout=5, socket_timeout=5)
    connection.ping()
    check_queues(Queue.all(connection=connection),
        (StartedJobRegistry, DeferredJobRegistry, ScheduledJobRegistry, FailedJobRegistry))

{% endmacro %}
