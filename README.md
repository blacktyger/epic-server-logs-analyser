Script to extract data from epic-server log and files

###HOW TO USE:
Download and unpack in directory with `*.log` files

For windows run `start_analyser.bat`

For Linux type in cmd `/python3 main.py`

When running for the first time it will download missing Python libraries

After completed process there will be new directory `ips/` with 2 CSV files:
- `final_list.csv` with unique IPs and dates
- `files_done.csv` to keep track of already processed log files