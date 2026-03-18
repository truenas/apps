import subprocess
cmd = "docker compose -p fb36c7e464a0f8ec512e2294134a200c -f ix-dev/community/gotosocial/templates/rendered/docker-compose.yaml config"
subprocess.run(cmd, shell=True)
