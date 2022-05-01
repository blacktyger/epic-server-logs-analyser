from functools import wraps
from time import time
import subprocess
import sys
import os


class LogFileTracker:
    def __init__(self, storage_path):
        import pandas as pd
        self.storage = storage_path

        # Load existing FILES_DONE CSV to df or create new empty df
        if os.path.isfile(self.storage):
            self.df = pd.read_csv(self.storage)
        else:
            self.df = pd.DataFrame(columns=['file', 'new_ip', 'time'])
            self.df.to_csv(self.storage, index=False)

    def is_file_already_processed(self, file: str):
        return file in self.df['file'].values

    def add_file_to_processed_list(self, file):
        import pandas as pd
        if not file['file'][0] in self.df['file'].values:
            self.df = pd.concat([self.df, file], ignore_index=True)
            self.df.to_csv(self.storage, index=False)


def import_handler():
    """Install 3rd parties packages via pip"""
    print('\n', icon('info'), 'Installing new Python packages', '\n')
    packages = ['log-symbols', 'pandas', 'halo']

    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def icon(type_: str):
    """Print coloured icons in system CMD"""
    try:
        from log_symbols import LogSymbols
    except Exception:
        import_handler()
        from log_symbols import LogSymbols

    return eval(f"LogSymbols.{type_.upper()}.value")


def timing(func):
    """Measure execution time of decorated function"""
    @wraps(func)
    def wrap(*args, **kw):
        ts = time()
        result = func(*args, **kw)
        te = time()
        # print(f'{func.__name__} took: %2.4f sec' % (te-ts))
        return result, '%2.4f sec' % (te-ts)
    return wrap


