import re
import os
import os.path
import itertools
from mypy import api as mypy_api
from pyls import hookimpl

line_pattern = r"([^:]+):(?:(\d+):)?(?:(\d+):)? (\w+): (.*)"


def parse_line(line, document=None):
    '''
    Return a language-server diagnostic from a line of the Mypy error report;
    optionally, use the whole document to provide more context on it.
    '''
    result = re.match(line_pattern, line)
    if result:
        _, lineno, offset, severity, msg = result.groups()
        lineno = int(lineno or 1)
        offset = int(offset or 0)
        errno = 2
        if severity == 'error':
            errno = 1
        diag = {
            'source': 'mypy',
            'range': {
                'start': {'line': lineno - 1, 'character': offset},
                # There may be a better solution, but mypy does not provide end
                'end': {'line': lineno - 1, 'character': offset + 1}
            },
            'message': msg,
            'severity': errno
        }
        if document:
            # although mypy does not provide the end of the affected range, we
            # can make a good guess by highlighting the word that Mypy flagged
            word = document.word_at_position(diag['range']['start'])
            if word:
                diag['range']['end']['character'] = (
                    diag['range']['start']['character'] + len(word))

        return diag


@hookimpl
def pyls_lint(config, document):
    args = ['--incremental',
            '--show-column-numbers',
            '--follow-imports', 'silent']

    config_files = config.plugin_settings('pyls_mypy').get('config_files', [])
    config_files = (os.path.expandvars(os.path.expanduser(p.strip()))
                    for p in config_files)
    config_files = [p for p in config_files if p]
    while config_files:
        # This seems a little complicated but the idea is that configuration
        # files in relative paths that are not separated by absolute path
        # configuration files, will all have an equal chance of being found
        # in each directory before the search moves up the project tree.
        config_file = None
        relative = list(itertools.takewhile(lambda p: not os.path.isabs(p),
                                            config_files))
        if relative:
            config_files = config_files[len(relative):]

            found = config.find_parents(os.getcwd(), relative)
            if not found:
                found = [p for p in relative if os.path.exists(p)]

            if found:
                config_file = found[0]
        else:
            value = config_files.pop(0)
            if os.path.exists(value):
                config_file = value

        if config_file is not None:
            args += ['--config-file', config_file]
            break

    live_mode = config.plugin_settings('pyls_mypy').get('live_mode', True)
    if live_mode:
        args += ['--command', document.source]
    else:
        args += [document.path]

    report, errors, _ = mypy_api.run(args)

    diagnostics = []
    for line in report.splitlines():
        diag = parse_line(line, document)
        if diag:
            diagnostics.append(diag)

    return diagnostics
