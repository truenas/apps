

def func_health_check(test="", interval=10, timeout=10, retries=5, start_period=30):
  if not test:
    raise ValueError("Healtcheck: [test] must be set")

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
    raise ValueError("Postgres container: [user] must be set")

  if not db:
    raise ValueError("Postgres container: [db] must be set")

  return f"pg_isready -h {host} -p {port} -d {db} -U {user}"

def func_postgres_run_as():
  return "999:999"

def func_postgres_environment(user, password, db):
  if not user:
    raise ValueError("Postgres container: [user] must be set")

  if not password:
    raise ValueError("Postgres container: [password] must be set")

  if not db:
    raise ValueError("Postgres container: [db] must be set")

  return {
    "POSTGRES_USER": user,
    "POSTGRES_PASSWORD": password,
    "POSTGRES_DB": db
  }

DEFAULT_CPUS = "4.0"
DEFAULT_MEMORY = "8gb"

def get_limits(data):
  return {
    "cpus": str(data.get("limits", DEFAULT_CPUS).get("cpus", DEFAULT_CPUS)),
    "memory": data.get("limits", DEFAULT_MEMORY).get("memory", DEFAULT_MEMORY)
  }

def func_resources(data = {}):
  return {
    "resources": {
      "limits": get_limits(data)
    },
  }
