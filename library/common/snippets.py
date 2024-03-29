import yaml

def healthcheck_timeouts(interval=10, timeout=10, retries=5, start_period=30):
  timeouts = {
    "interval": interval,
    "timeout": timeout,
    "retries": retries,
    "start_period": start_period
  }

  return yaml.dump(timeouts)
