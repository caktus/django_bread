def unlistify_dict_values(dictionary):
    """
    Return a dictionary same as the input, except any values that are single-element
    lists have been replaced by the element from that list.
    """
    result = dict(dictionary)  # Copy it
    for key, value in result.items():
        if isinstance(value, list) and len(value) == 1:
            result[key] = value[0]
    return result
