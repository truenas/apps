{% macro health_script() %}
"""Read-only readiness checks. Never enqueue jobs or change site settings."""
import datetime
import contextlib
import json
import os
import socket
import sys
import urllib.request


def check_http(role, site):
    if role == 'websocket':
        url = 'http://127.0.0.1:9000/socket.io/?EIO=4&transport=polling'
    else:
        port = 8080 if role == 'frontend' else 8000
        url = f'http://127.0.0.1:{port}/api/method/ping'
    request = urllib.request.Request(url, headers={'Host': site})
    with urllib.request.urlopen(request, timeout=5) as response:
        body = response.read(16384).decode()
        if role == 'websocket':
            if not body.startswith('0') or 'sid' not in json.loads(body[1:]):
                raise RuntimeError('Socket.IO handshake failed')
        elif json.loads(body).get('message') != 'pong':
            raise RuntimeError('Frappe ping failed')


def check_worker(connection, queues):
    from rq import Worker
    from rq.defaults import DEFAULT_WORKER_TTL
    from frappe.utils.background_jobs import get_queue
    expected = {get_queue(queue).name for queue in queues}
    now = datetime.datetime.now(datetime.timezone.utc)
    for worker in Worker.all(connection=connection):
        if worker.hostname != socket.gethostname():
            continue
        if not expected.issubset(set(worker.queue_names())):
            continue
        heartbeat = worker.last_heartbeat
        if heartbeat is None:
            continue
        if heartbeat.tzinfo is None:
            heartbeat = heartbeat.replace(tzinfo=datetime.timezone.utc)
        # Idle RQ workers can block for TTL - 15 seconds between heartbeats.
        if 0 <= (now - heartbeat).total_seconds() <= DEFAULT_WORKER_TTL + 60:
            return
    raise RuntimeError('No recent local worker heartbeat for required queues')


def check_background(role, site):
    # Bench commands run from sites; Frappe derives bench/log paths from cwd.
    os.chdir('/home/frappe/frappe-bench/sites')
    import frappe
    from frappe.utils.background_jobs import get_redis_conn
    frappe.init(site=site, sites_path='/home/frappe/frappe-bench/sites')
    try:
        frappe.connect()
        frappe.db.sql('SELECT 1')
        if not frappe.cache.ping():
            raise RuntimeError('Cache ping failed')
        connection = get_redis_conn()
        if not connection.ping():
            raise RuntimeError('Queue ping failed')
        if role == 'scheduler':
            from frappe.utils.scheduler import is_schduler_process_running
            if not is_schduler_process_running():
                raise RuntimeError('Scheduler lock is not held')
        else:
            check_worker(connection, ['short', 'default'] if role == 'queue-short' else ['long'])
    finally:
        frappe.destroy()


def main():
    role = sys.argv[1]
    site = os.environ['SITE_NAME']
    if role in ('frontend', 'backend', 'websocket'):
        check_http(role, site)
    elif role in ('queue-short', 'queue-long', 'scheduler'):
        check_background(role, site)
    else:
        raise RuntimeError('Unknown healthcheck role')


if __name__ == '__main__':
    try:
        # Upstream connection retries may print URLs; keep health logs private.
        with open(os.devnull, 'w') as quiet:
            with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                main()
    except Exception as error:
        # Avoid credentials/connection URLs in Docker health logs.
        print('Readiness check failed: ' + type(error).__name__, flush=True)
        sys.exit(1)
{% endmacro %}
