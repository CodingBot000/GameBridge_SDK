"""Keep partial subprocess evidence when an invocation cannot finish."""

def timeout_output(error):
    output=error.output or ''
    if isinstance(output,bytes):output=output.decode('utf-8',errors='replace')
    return output+'\nINCOMPLETE: subprocess timed out; no success verdict.\n'
