def message(train: str, mode: str, s: str) -> str:
    files = s.split(" ")

    if not len(files) > 0:
        exit(1)
        return ""

    message = f"## `{train}`\n\n"
    message += f"Files {mode}:\n\n"
    for file in files:
        message += f"- {file}\n"

    return message


if __name__ == "__main__":
    import sys

    print(message(sys.argv[1], sys.argv[2], sys.argv[3]))
