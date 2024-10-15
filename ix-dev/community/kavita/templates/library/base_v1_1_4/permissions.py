import jsonschema

from . import utils

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "dir": {"type": "string"},
        "mode": {"type": "string", "enum": ["always", "check"]},
        "uid": {"type": "integer"},
        "gid": {"type": "integer"},
        "chmod": {"type": "string"},
        "is_temporary": {"type": "boolean"},
    },
    "required": ["dir", "mode", "uid", "gid", "chmod", "is_temporary"],
}


def perms_container(items=[], volumes=[]):
    if not items:
        raise ValueError("Expected [items] to be set for perms_container")
    if not volumes:
        raise ValueError("Expected [volumes] to be set for perms_container")

    command = [process_dir_shell_func()]
    for item in items:
        try:
            jsonschema.validate(item, ITEM_SCHEMA)
        except jsonschema.ValidationError as e:
            utils.throw_error(f"Item [{item}] is not valid: {e}")
        cmd = [
            "process_dir",
            item["dir"],
            item["mode"],
            str(item["uid"]),
            str(item["gid"]),
            item["chmod"],
            str(item["is_temporary"]).lower(),
        ]
        command.append(" ".join(cmd))

    return {
        "image": "bash",
        "user": "root",
        "deploy": {
            "resources": {
                "limits": {"cpus": "1.0", "memory": "512m"},
            }
        },
        "entrypoint": ["bash", "-c"],
        "command": ["\n".join(command)],
        "volumes": volumes,
    }


# Don't forget to use double $ for shell variables,
# otherwise docker-compose will try to expand them
def process_dir_shell_func():
    return """
function process_dir() {
    local dir=$$1
    local mode=$$2
    local uid=$$3
    local gid=$$4
    local chmod=$$5
    local is_temporary=$$6

    local fix_owner="false"
    local fix_perms="false"

    if [ -z "$$dir" ]; then
        echo "Path is empty, skipping..."
        return 0
    fi

    if [ ! -d "$$dir" ]; then
        echo "Path [$$dir] does is not a directory, skipping..."
        return 0
    fi

    if [ "$$is_temporary" = "true" ]; then
        echo "Path [$$dir] is a temporary directory, ensuring it is empty..."
        # Exclude the safe directory, where we can use to mount files temporarily
        find "$$dir" -mindepth 1 -maxdepth 1 ! -name "ix-safe" -exec rm -rf {} +
    fi

    if [ "$$is_temporary" = "false" ] && [ -n "$$(ls -A $$dir)" ]; then
        echo "Path [$$dir] is not empty, skipping..."
        return 0
    fi

    echo "Current Ownership and Permissions on [$$dir]:"
    echo "chown: $$(stat -c "%u %g" "$$dir")"
    echo "chmod: $$(stat -c "%a" "$$dir")"

    if [ "$$mode" = "always" ]; then
        fix_owner="true"
        fix_perms="true"
    fi

    if [ "$$mode" = "check" ]; then
        if [ $$(stat -c %u "$$dir") -eq $$uid ] && [ $$(stat -c %g "$$dir") -eq $$gid ]; then
            echo "Ownership is correct. Skipping..."
            fix_owner="false"
        else
            echo "Ownership is incorrect. Fixing..."
            fix_owner="true"
        fi

        if [ "$$chmod" = "false" ]; then
            echo "Skipping permissions check, chmod is false"
        elif [ -n "$$chmod" ]; then
            if [ $$(stat -c %a "$$dir") -eq $$chmod ]; then
                echo "Permissions are correct. Skipping..."
                fix_perms="false"
            else
                echo "Permissions are incorrect. Fixing..."
                fix_perms="true"
            fi
        fi
    fi

    if [ "$$fix_owner" = "true" ]; then
        echo "Changing ownership to $$uid:$$gid on: [$$dir]"
        chown -R "$$uid:$$gid" "$$dir"
        echo "Finished changing ownership"
        echo "Ownership after changes:"
        stat -c "%u %g" "$$dir"
    fi

    if [ -n "$$chmod" ] && [ "$$fix_perms" = "true" ]; then
        echo "Changing permissions to $$chmod on: [$$dir]"
        chmod -R "$$chmod" "$$dir"
        echo "Finished changing permissions"
        echo "Permissions after changes:"
        stat -c "%a" "$$dir"
    fi
}
"""
