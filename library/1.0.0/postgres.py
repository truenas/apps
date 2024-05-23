def pg_url(variant, host, user, password, dbname, port=5432):
    if not host:
        raise ValueError("host is required")
    if not user:
        raise ValueError("user is required")
    if not password:
        raise ValueError("password is required")
    if not dbname:
        raise ValueError("dbname is required")
    if variant == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    elif variant == "postgres":
        return f"postgres://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    else:
        raise ValueError(f"Unknown variant {variant}")


def pg_env(user, password, dbname, port=5432):
    if not user:
        raise ValueError("user is required")
    if not password:
        raise ValueError("password is required")
    if not dbname:
        raise ValueError("dbname is required")
    return {
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": password,
        "POSTGRES_DB": dbname,
        "POSTGRES_PORT": port,
    }
