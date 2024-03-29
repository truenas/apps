import yaml

YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

def healthcheck(test="", interval=10, timeout=10, retries=5, start_period=30):
  if not test:
    raise ValueError("Healtcheck: [test] must be set")

  timeouts = {
    "healthcheck": {
      "test": test,
      "interval": interval,
      "timeout": timeout,
      "retries": retries,
      "start_period": start_period
    }
  }

  return yaml.dump(timeouts, **YAML_OPTS)

def curl_test(url):
  return f"curl --silent --fail {url}"

def pg_test(host, user, db, port=5432):
  return f"pg_isready -h {host} -p {port} -d {db} -U {user}"
