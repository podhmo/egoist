def get_path_from_function_name(fnname: str) -> str:
    """foo__bar__boo -> foo/bar/boo"""
    return fnname.replace("__", "/")
