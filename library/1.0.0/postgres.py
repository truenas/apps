from . import utils


def pg_url(variant, host, user, password, dbname, port=5432):
    if not host:
        utils.throw_error("Expected [host] to be set")
    if not user:
        utils.throw_error("Expected [user] to be set")
    if not password:
        utils.throw_error("Expected [password] to be set")
    if not dbname:
        utils.throw_error("Expected [dbname] to be set")

    if variant == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    elif variant == "postgres":
        return f"postgres://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    else:
        utils.throw_error(f"Expected [variant] to be one of [postgresql, postgres], got [{variant}]")


def pg_env(user, password, dbname, port=5432):
    if not user:
        utils.throw_error("Expected [user] to be set for postgres")
    if not password:
        utils.throw_error("Expected [password] to be set for postgres")
    if not dbname:
        utils.throw_error("Expected [dbname] to be set for postgres")
    return {
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": password,
        "POSTGRES_DB": dbname,
        "POSTGRES_PORT": port,
    }
