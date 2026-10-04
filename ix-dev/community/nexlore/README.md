# nexlore

[nexlore](https://github.com/DerKezorm/nexlore) is a notes app for your own server, in the browser: Markdown
files on your disk, written in a WYSIWYG editor, linked with wiki links and backlinks, and laid out as a map
you zoom into. Daily notes, tasks, templates, canvases, spaces shared with rights, accounts by invitation or
OpenID Connect, MCP for AI helpers, backups. Project site: https://www.nexlore.de

The first account becomes the operator and needs the setup code from the container logs, a new one at
every start until nexlore is set up. To choose it yourself, add `NEXLORE_SETUP_TOKEN` under
Additional Environment Variables.

The notes live in `vault` inside Data Storage. To keep them in a dataset of their own, add it under
Additional Storage (for example at `/vault`) and set `NEXLORE_VAULT_DIR` to that path under Additional
Environment Variables.
