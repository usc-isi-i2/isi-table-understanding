def string2int(value):
    if isinstance(value, int):
        return value
    try:
        value = int(value)
        return value
    except:
        return None


# TODO: Check if this will work for all types of data
def data_to_string(data):
    return str(data)


def is_string_literal(value):
    if isinstance(value, str):
        return True
    return False
