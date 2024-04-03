#!/usr/bin/env python3
import importlib
import inspect
from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader("ix-dev/enterprise/minio/templates"),
)

items = [
  importlib.import_module("library.common.validations"),
  importlib.import_module("library.common.snippets"),
  importlib.import_module("library.common.utils")
]

for item in items:
  for name, func in inspect.getmembers(item, inspect.isfunction):
    if name.startswith("filter_"):
      env.filters[name.replace("filter_", "")] = func
    if name.startswith("func_"):
      env.globals.update({name.replace("func_", ""): func})

template = env.get_template("docker-compose.yaml.j2")

mock1 = {
  "network": {
    "api_port": 9000,
    "console_port": 9001,
    "certificateID": None
  },
  "storage": {
    "data": [
      {
        "type": "hostPath",
        "mountPath": "/data1",
        "hostPathConfig": {
          "path": "/mnt/test/data1",
        }
      },
      {
        "type": "hostPath",
        "mountPath": "/data2",
        "hostPathConfig": {
          "path": "/mnt/test/data2",
        }
      }
    ]
  },
  "resources": {
    "limits": {
      "cpus": "2.0",
      "memory": "4gb"
    },
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

mock2 = {
  "network": {
    "api_port": 9000,
    "console_port": 9001,
    "certificateID": None
  },
  "storage": {
    "data": [
      {
        "type": "hostPath",
        "mountPath": "/data1",
        "hostPathConfig": {
          "path": "/mnt/test/data1",
        }
      },
      {
        "type": "hostPath",
        "mountPath": "/data2",
        "hostPathConfig": {
          "path": "/mnt/test/data2",
        }
      }
    ]
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
      "enabled": False,
    }
  }
}

print(template.render(data=mock1))
