import textwrap
def healthcheck_timeouts(interval=10, timeout=10, retries=5, start_period=30):
  return textwrap.indent(f"""
    interval: {interval}s
    timeout: {timeout}s
    retries: {retries}
    start_period: {start_period}s
  """, 2 * " ")
