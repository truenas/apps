import library.common.utils as utils


def func_health_check(test: str = "", interval: int = 10, timeout: int = 10, retries: int = 5, start_period: int = 30) -> dict:
  if not test:
    utils.throw_error("Healtcheck: [test] must be set")

  return {
    "test": test,
    "interval": f'{interval}s',
    "timeout": f'{timeout}s',
    "retries": retries,
    "start_period": f'{start_period}s'
  }

def func_curl_test(url: str) -> str:
  return f"curl --silent --fail {url}"

def func_pg_test(user: str, db: str, host: str = "127.0.0.1", port: int = 5432) -> str:
  if not user:
    utils.throw_error("Postgres container: [user] must be set")

  if not db:
    utils.throw_error("Postgres container: [db] must be set")

  return f"pg_isready -h {host} -p {port} -d {db} -U {user}"

def func_postgres_uid() -> int:
  return 999
def func_postgres_gid() -> int:
  return 999
def func_postgres_run_as() -> str:
  return f"{func_postgres_uid()}:{func_postgres_gid()}"

def func_postgres_environment(user: str, password: str, db: str) -> dict:
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

def get_limits(data: dict) -> dict:
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

def func_resources(data: dict = {}) -> dict:
  return {
    "resources": {
      "limits": get_limits(data)
    },
  }
