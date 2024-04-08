#!/usr/bin/env python3
import importlib
import inspect
import yaml
import sys
import os
from jinja2 import Environment, FileSystemLoader

if len(sys.argv) < 3:
  raise ValueError("path must be set")

values_path = sys.argv[1]
app_path = sys.argv[2]

print(f"Values path: {values_path}")
print(f"App path: {app_path}")

if not values_path:
  raise ValueError("values path must be set")

if not app_path:
  raise ValueError("app path must be set")

if not os.path.exists(values_path):
  raise ValueError("values path does not exist")

if not os.path.exists(app_path):
  raise ValueError("app path does not exist")

env = Environment(
    loader=FileSystemLoader(f"{app_path}/templates"),
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

with open(values_path) as f:
  mock = yaml.safe_load(f)

print(template.render(data=mock))
