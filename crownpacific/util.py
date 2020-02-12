def strings_to_numbers(l, fmt='float'):
    """
    Turn number string into the specified format from a list of values or a single string

    >>> strings_to_numbers(['1', 'a', '2.34', 3])
    [1, 'a', 2.34, 3]
    >>> strings_to_numbers('2.34')
    2.34
    >>> strings_to_numbers('Hi There')
    'Hi There'
    >>> strings_to_numbers('   123456')
    123456
    >>> strings_to_numbers(False)
    """

    def _convert(s):
        if not s:
            return s
        try:
            if float(s).is_integer():
                return int(float(s))
            else:
                return float(s)
        except (ValueError, TypeError):
            return s

    if not l:
        return l
    if hasattr(l, "__iter__") and not isinstance(l, (str, int)):
        o = []
        for i in l:
            o.append(_convert(i))
        return o
    else:
        return _convert(l)