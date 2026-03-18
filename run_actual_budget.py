import sys
import os
import subprocess

def run():
    app = "actual-budget"
    train = "community"
    test_file = "basic-values.yaml"
    
    cmd = f"docker run --platform linux/amd64 --quiet --rm -e FAKE_ENV=1 -v {os.getcwd()}:/workspace -v /var/run/docker.sock:/var/run/docker.sock:ro ghcr.io/truenas/apps_validation:latest apps_render_app render --path /workspace/ix-dev/{train}/{app} --values /workspace/ix-dev/{train}/{app}/templates/test_values/{test_file}"
    subprocess.run(cmd, shell=True)

run()
