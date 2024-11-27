{% macro setup(values) -%}
#!/bin/sh
echo "Ensuring job config directory {{ values.consts.jobs_path }}/{{ values.fscrawler.job_name }} exists"
mkdir -p {{ values.consts.jobs_path }}/{{ values.fscrawler.job_name }}
{# Copy/Overwrite an example settings file to the config directory #}
echo "Copying example config file to {{ values.consts.jobs_path }}/{{ values.fscrawler.job_name }}/_settings.example.yaml"
cp -f {{ values.consts.example_config_path }} {{ values.consts.jobs_path }}/{{ values.fscrawler.job_name }}/_settings.example.yaml
{%- endmacro %}
