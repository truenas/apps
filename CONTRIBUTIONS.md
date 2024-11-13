# Contributions

Thank you for your interest in contributing to the Apps Catalog.

## Library

The library is written in Python and is located in the `/library/2.x.x` directory.
You will rarely need to interact with the library directly.

## New Apps

If you want to add a new app to the catalog, the easier way is
to copy an existing app that is similar to the one you want to add,
then modify it to your needs. You can find usage examples in either,
other apps that use the library, or in the `/library/2.x.x/tests` directory.

⚠️ Make sure you are copying an app that uses library version 2.x.x.

For icons and screenshots that we store in our CDN, you can leave the links
in the PR descriptions, and the PR reviewer will upload them and give you the links.

⚠️ Make sure that you are only adding/modifying files under the `/ix-dev` or `/library` directories!
All other files should be ignored, as they are mostly auto-generated.

## Local Testing

You will need to have `docker`, `docker compose` and `python` installed.
Additionally, you need the following Python packages installed:
`pyyaml, psutil, pytest, pytest-cov, bcrypt, pydantic`

If you have `nix-shell` installed, you can run the following command to
start a shell with all the required python packages installed:

```bash
nix-shell -p 'python3.withPackages (ps: with ps; [ pyyaml psutil pytest pytest-cov bcrypt pydantic ])'
```

The directory `test_values` contains test files for each app.
To run a test against a test file, run the following command:

```bash
./.github/scripts/ci.py --app qbittorrent --train community --test-file basic-values.yaml --wait=true
```

`--wait=true` will start the container, and wait until you stop it. It will also show the URL of the web UI (if available).
`--render-only=true` will just print the rendered compose file, without starting the container. (You can pipe the output to a file if you want to save it.)

Both flags are optional. If you don't specify them, it will run the app against the test file.
And stop it as soon as it becomes healthy. It will timeout after 10 minutes if it doesn't become healthy.
If you manually `ctrl+c`, you will have to cleanup the leftover containers.

The above command will also do the following:

- Generate the `item.yaml` file
- Update the contents of the `templates/library/` directory based on the `lib_version` on the `app.yaml` file
- Update the `lib_version_hash` on the `app.yaml` file

⚠️ Some notes for the test files:

Most apps that use v2 library will use the `/opt/tests/**` directory for storage. This is mostly
because MacOS whitelists this directory by default. And linux does not have this restriction.

Make sure before running the test, that is not going to mount any directories that you don't want to.
