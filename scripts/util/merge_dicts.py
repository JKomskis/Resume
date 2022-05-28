def merge_dicts(a: dict, b: dict):
    """
    Merges b into a. All keys of b will be overridden in a.
    If a key of b is a nested dict in both a and b, the nested dict will
    be merged recursively.
    Based on: https://github.com/Maples7/dict-recursive-update/blob/master/dict_recursive_update/__init__.py
    """
    for key in b:
        if isinstance(b[key], dict) and isinstance(a.get(key), dict):
            a[key] = merge_dicts(a[key], b[key])
        else:
            a[key] = b[key]
    return a