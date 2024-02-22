# TrueNAS Apps Catalog

Example Payload (this is passes to stdin)

```json
{
  "templates_dir": "/mnt/pool/ix-application/syncthing/1.0.0/templates/",
  "app_context": {
    "name": "syncthing",
    "version": "1.2.3",
    "app_dataset": "/mnt/pool/ix-application/releases/syncthing",
    "operation": "Create",
    "upgrade_metadata": {
      "from_version": "1.2.2",
      "to_version": "1.2.3"
    },
    "system": {
      "scale_version": "1.2.3"
    }
  },
  "values": {
    // values from UI eg
    "resources": {
      "limits": {
        "cpu": "2.0",
        "memory": "2gb"
      }
    }
  }
}
```

Example result

```json
{
  // Whether the operation was successful
  "success": true,
  // Custom error from produced
  // from the app dev under a condition in the template
  "error": "",
  // Trace of the go-tool
  "trace": "",
  // Array of strings
  "warnings": null,
  // Not implemented yet
  // Summary in md format, (Similar to NOTES.txt in helm charts)
  "summary": "",
  // Not implemented yet
  // Contains portal information for buttons
  "portals": [
    {
      "name": "Open",
      "scheme": "http",
      "host": "1.2.3.4",
      "port": 8384
    }
  ],
  // Not implemented yet
  // For example custom init scripts, or certificates
  // That need to be created before the app starts
  // Think similar to k8s configmaps
  // This might not be needed in the future, as docker-compose recently
  // added an option for inline files (it was only supported for swarm before)
  "files": [
    {
      "name": "",
      "content": ""
    }
  ],
  // Not implemented yet
  "security_context": {
    // each container has its own object
    "syncthing": {
      "user": "1000",
      "group": "1000",
      "caps_add": ["CAP_NET_BIND_SERVICE"],
      "caps_drop": ["ALL"],
      "privileged": false
    }
  },
  // Not implemented yet
  "devices": [
    {
      "path_on_host": "/dev/sda",
      "path_in_container": "/dev/sda"
    }
  ],
  "compose": {
    "services": {
      "syncthing": {
        "image": "syncthing:1.2.3",
        "container_name": "syncthing",
        "restart": "unless-stopped",
        "network_mode": "host",
        "volumes": ["/mnt/tank/syncthing:/var/syncthing"]
        // ...
      }
      // ...
    }
  }
}
```

## Example of how to run the tool

```shell
cd go-tools
# View result
go run cmd/go-template-compose/main.go < ../example/syncthing/payload.json | jq
# Run the app
go run cmd/go-template-compose/main.go < ../example/syncthing/payload.json |\
  jq '.compose' | docker-compose -f - up -d \
    --remove-orphans --force-recreate --project-name syncthing
```

## Development

```shell
cd go-tools # Or download the binary from the release page

## For yaml output (for easier reading) Default is json
go run cmd/go-template-compose/main.go < ../example/syncthing/payload.json --out yaml

## Output only compose
go run cmd/go-template-compose/main.go < ../example/syncthing/payload.json --compose-only --out yaml
```

## Other ideas/features/considerations

- The few things that are marked as not implemented yet in the above example.
- I'd like to have a questions.yaml template that will generate parts of the questions on the CI or as a pre-commit hook.

  The reason for this is that we can have common sections on a single place and we don't have to repeat ourselves.
  Or if we want to make a change in a label or description, or add/remove an option.

  For example, resources section, additional volumes, etc.
  In addition to that we can create custom function in the template func lib, that will parse this common sections and generate the compose file.
  With that if we want to change the format of it at a later time, we can create a single migration for all apps that use it (even for 3rd party catalogs).
  Tho it will also require for the middleware to expect updated user config from the template tool (probably under a subcommand)
  Migration will work similar to the currently used `migrate` python files.

  Reasoning behind all that is that we can remove common options from the app developer (including 3rd party catalogs) and only have to focus on the actual
  app specific options. Of course this will be opt-in feature and the app developer can still manually "craft" the questions.yaml file.
- Add a way to generate warnings from the template, and make them actionable from the UI before the app actually runs. (eg "This setting is deprecated, please use this instead", "This setting is not recommended, do you want to continue?")

## Example flow from the user perspective

### Option 1 (Custom App)

- User clicks on custom app
- User paste's in a docker-compose yaml file
- User clicks on "Install" button
- Compose file along with the app_context is passed to the template tool
- Template tool parses and executes the template
- Template tool validates things if we want to, eg host paths, ports, etc
- Template tool We extract any details we need from the compose file (eg security context etc)
- Template tool returns the result to the middleware
- Middleware sends the result the user/UI (eg display errors, summary or the compose file itself)
- Middleware sends the result to docker compose and starts the app

Since this will go through the template tool, user can also use the templating system if he wants to.

### Option 2 (Pre-made App)

- User selects an app from the catalog
- User fills in the questions
- User clicks button
  - "Install" button
    - Payload is passed to the template tool
    - Template tool parses and executes the template
    - Template tool validates things if we want to, eg host paths, ports, etc
    - Template tool We extract any details we need from the compose file (eg security context etc)
    - Template tool returns the result to the middleware
    - Middleware sends the result to docker compose and starts the app
  - User clicks on "Get compose file" button
    - Payload is passed to the template tool
    - Template tool parses and executes the template
    - Template tool validates things if we want to, eg host paths, ports, etc
    - Template tool We extract any details we need from the compose file (eg security context etc)
    - Template tool returns the result to the middleware
    - Middleware sends the result to the user/UI (eg display errors, summary or the compose file itself)
    - User can copy the compose file and use it as he wants (eg via Custom App flow) at this point user has detached from the catalog and can do whatever he wants with the compose file
