#!/usr/bin/env python3
import importlib
import inspect
from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader("ix-dev/enterprise/minio/templates"),
)

validators = importlib.import_module("library.common.validations")
snippets = importlib.import_module("library.common.snippets")
utils = importlib.import_module("library.common.utils")

for name, func in inspect.getmembers(validators, inspect.isfunction):
    env.filters[name] = func
for name, func in inspect.getmembers(snippets, inspect.isfunction):
    env.globals.update({name: func})
for name, func in inspect.getmembers(utils, inspect.isfunction):
    env.globals.update({name: func})

template = env.get_template("docker-compose.yaml.j2")


mock = {
  "network": {
    "api_port": 9000,
    "console_port": 9001,
    "certificateID": None
  },
  "minio": {
    "access_key": "minio",
    "secret_key": "minio123",
    "server_url": "",
    "console_url": "",
    "user": 568,
    "group": 568,
    "logging": {
      "quiet": True,
      "anonymous": True
    },
    "logsearch": {
      "enabled": True,
      "disk_capacity_gb": 10,
      "postgres_password": "minio"
    }
  }
}
print(template.render(data=mock))
