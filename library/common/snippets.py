import library.common.utils as utils


def func_health_check(test="", interval=10, timeout=10, retries=5, start_period=30):
  if not test:
    utils.throw_error("Healtcheck: [test] must be set")

  return {
    "test": test,
    "interval": f'{interval}s',
    "timeout": f'{timeout}s',
    "retries": retries,
    "start_period": f'{start_period}s'
  }

def func_curl_test(url):
  return f"curl --silent --fail {url}"

def func_pg_test(user, db, host="127.0.0.1", port=5432):
  if not user:
    utils.throw_error("Postgres container: [user] must be set")

  if not db:
    utils.throw_error("Postgres container: [db] must be set")

  return f"pg_isready -h {host} -p {port} -d {db} -U {user}"

def func_postgres_uid():
  return "999"
def func_postgres_gid():
  return "999"
def func_postgres_run_as():
  return f"{func_postgres_uid()}:{func_postgres_gid()}"

def func_postgres_environment(user, password, db):
  if not user:
    utils.throw_error("Postgres container: [user] must be set")

  if not password:
    utils.throw_error("Postgres container: [password] must be set")

  if not db:
    utils.throw_error("Postgres container: [db] must be set")

  return {
    "POSTGRES_USER": user,
    "POSTGRES_PASSWORD": password,
    "POSTGRES_DB": db
  }

DEFAULT_CPUS = "2.0"
DEFAULT_MEMORY = "4gb"

def get_limits(data):
  limits = {
    "cpus": DEFAULT_CPUS,
    "memory": DEFAULT_MEMORY
  }

  if not data:
    return limits

  limits.update({
    "cpus": str(data.get("limits", DEFAULT_CPUS).get("cpus", DEFAULT_CPUS)),
    "memory": data.get("limits", DEFAULT_MEMORY).get("memory", DEFAULT_MEMORY)
  })

  return limits

def func_resources(data = {}):
  return {
    "resources": {
      "limits": get_limits(data)
    },
  }
