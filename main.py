"""
Read epic-server.log files and extract data for analysis and visualisations
"""

import glob
import re
import os

import tools

try:
    from log_symbols import LogSymbols
    from halo import Halo
    import pandas as pd

except Exception:
    tools.import_handler()  # Install missing packages
    from log_symbols import LogSymbols
    from halo import Halo
    import pandas as pd


RESULT_DIR = "ips"
IP_PATTERN = r'[0-9]+(?:\.[0-9]+){3}:[0-9]+'
FINAL_LIST = os.path.join(RESULT_DIR, "final_list.csv")
FILES_DONE = os.path.join(RESULT_DIR, "files_done.csv")
IGNORE_IPS = ('0.0.0.0', '127.0.0.1')
FILES_EXT = '*.log'


def load_directory(path: str = None):
    if not path:
        path = os.getcwd()

    os.chdir(path)
    files = glob.glob(FILES_EXT)

    return files


def parse_line(line: str):
    ip_match = re.search(IP_PATTERN, line)

    if ip_match:
        ip = ip_match[0]
        date = line[:9]
        return date, ip

    return None


def parse_log_file(file: str):
    rows = []

    with open(file) as file:
        while line := file.readline():
            if valid_line := parse_line(line=line):
                date, ip = valid_line
                if not ip.startswith(IGNORE_IPS):
                    rows.append({'date': date, 'ip': ip})

    df = pd.DataFrame(rows)
    return df


def remove_duplicates(df: pd.DataFrame):
    try:
        df.drop_duplicates(keep='first', subset=['ip'], inplace=True)
    except Exception:
        pass
    return df


def update_final_list(data: pd.DataFrame):
    # Load existing final_list CSV to df or create new empty df
    if os.path.isfile(FINAL_LIST):
        df = pd.read_csv(FINAL_LIST)
    else:
        df = pd.DataFrame(columns=['date', 'ip'])

    rows_before = int(df.shape[0])

    # Add new rows to existing df
    df = pd.concat([df, data], ignore_index=True)

    # Make sure dates are int type
    df['date'] = df['date'].astype(int)

    # Sort values by dates
    df.sort_values(by='date', inplace=True)

    # Remove same IPs saving only those with the earliest date
    df = remove_duplicates(df)

    # Save df to CSV file
    df.to_csv(FINAL_LIST, index=False)

    rows_after = int(df.shape[0])

    return rows_before, rows_after

def process_file(file: str):
    if tracker.is_file_already_processed(file):
        return False

    @tools.timing
    def _process(file):
        spinner.start(f'Working on {file}..')
        file_data = parse_log_file(file=file)
        cleaned_data = remove_duplicates(file_data)
        return update_final_list(cleaned_data),

    try:
        rows, time = _process(file)
        new_rows = rows[0][1] - rows[0][0]
        spinner.stop_and_persist(
            tools.icon('success'),
            f'Finished: {log_file}, '
            f'New: {new_rows}, '
            f'Total: {rows[0][1]}, '
            f'Time: {time}')
        return log_file, new_rows, time

    except Exception as e:
        spinner.stop_and_persist(tools.icon('error'), f'{log_file} error!')
        print(e)
        return False


if __name__ == '__main__':
    # Make sure there is directory for script files ("ips/")
    if not os.path.isdir(RESULT_DIR):
        os.mkdir(RESULT_DIR)

    spinner = Halo(text='', spinner='growVertical')
    tracker = tools.LogFileTracker(storage_path=os.path.join(os.getcwd(), FILES_DONE))

    # Welcome message
    msg = f'# Running Epic-Cash server logs analysing script #'
    print(f"{len(msg) * '#'}"
          f"{msg}"
          f"{len(msg) * '#'}")

    # Load all valid files from directory (default CWD)
    valid_files = load_directory()

    if not valid_files:
        # Handle no valid files in directory case
        print(tools.icon('info'), f'No {FILES_EXT} files in this directory')
    else:
        # Iterate through all valid files in directory and its children
        print(f"{tools.icon('info')} {FILES_EXT} files to process: {valid_files}")

        for log_file in valid_files:
            if file_data := process_file(file=log_file):
                # Create new file entry to processed_files list
                file, new_ip, time = file_data
                df = pd.DataFrame([{'file': file, 'new_ip': new_ip, 'time': time}], index=None)
                tracker.add_file_to_processed_list(df)
            else:
                print(f'{tools.icon("info")} {log_file} was already processed')


