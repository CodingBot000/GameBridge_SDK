"""Explicit error measurement contracts for regression reports."""
def valid_error_evidence(lane):
    if not isinstance(lane.get('errorModel'),str) or lane['errorModel'] not in ('separate','included-in-failures','checker-exit'):return False
    if lane.get('errorModel') == 'included-in-failures' and (type(lane.get('failures')) is not int or lane['failures'] < 0):
        return False
    if 'errors' in lane:
        value = lane['errors']
        if value is not None:
            return type(value) is int and value == 0
        return lane.get('errorModel') in ('included-in-failures', 'checker-exit')
    return lane.get('errorModel') in ('included-in-failures', 'checker-exit')


def copy_error_evidence(item):
    # Preserve missing vs null vs invalid: never coerce absent errors to zero.
    return {key:item[key] for key in ('errors','errorModel') if key in item}
