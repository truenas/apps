import yaml

YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

def health_check(test="", interval=10, timeout=10, retries=5, start_period=30):
  if not test:
    raise ValueError("Healtcheck: [test] must be set")

  hc = {
    "test": test,
    "interval": f'{interval}s',
    "timeout": f'{timeout}s',
    "retries": retries,
    "start_period": f'{start_period}s'
  }

  return yaml.dump(hc, **YAML_OPTS)

def curl_test(url):
  return f"curl --silent --fail {url}"

def pg_test(user, db, host="127.0.0.1", port=5432):
  if not user:
    raise ValueError("Postgres container: [user] must be set")

  if not db:
    raise ValueError("Postgres container: [db] must be set")

  return f"pg_isready -h {host} -p {port} -d {db} -U {user}"

def postgres_run_as():
  return "999:999"

def postgres_environment(user, password, db):
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
