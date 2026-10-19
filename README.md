# TASK-30-LOG-FILE-ANALYZER# LOG-FILE-ANALYZER

A Python program that reads a server log file and reports request counts, error responses, the most frequent IP addresses and the most requested endpoints.

## Features

- Counts the total number of valid requests
- Counts client errors (4xx) and server errors (5xx) and shows the error rate
- Lists the top 5 IP addresses by number of requests
- Lists the top 5 most requested endpoints
- Shows request counts by HTTP method and by status code
- Skips and counts malformed log lines instead of crashing
- Saves the final summary to `summary_report.txt`
- Creates a sample `server.log` automatically if no log file is found, so no dataset is needed

## Concepts Used

- String processing and regular expressions
- Dictionaries and `collections.Counter`
- File handling (reading and writing text files)
- Basic data analysis
- Separation of parsing from analysis

## Requirements

- Python 3.8 or newer
- No external libraries (standard library only)

## Project Structure

```
LOG-FILE-ANALYZER/
├── log_analyzer.py      # main program
├── server.log           # sample log file
├── summary_report.txt   # generated report
└── README.md
```

## How to Run

Run with the default log file (`server.log`):

```
python log_analyzer.py
```

If `server.log` does not exist, a sample one is created first.

Run with your own log file:

```
python log_analyzer.py path/to/your_file.log
```

On Mac or Linux, use `python3` instead of `python`.

## Expected Log Format

The analyzer expects lines in the common access log style:

```
192.168.1.10 - - [19/Oct/2026:08:00:00 +0500] "GET /login HTTP/1.1" 200 1532
```

Each line contains the IP address, timestamp, HTTP method, endpoint, status code and response size. Lines that do not match this format are treated as malformed and skipped.

## Sample Output

```
==================================================
SERVER LOG SUMMARY REPORT
==================================================
Total valid requests : 500
Malformed lines      : 2
Total data transferred: 2231386 bytes

--- Error Summary ---
Client errors (4xx)  : 170
Server errors (5xx)  : 63
Total errors         : 233
Error rate           : 46.60%

--- Top 5 IP Addresses ---
1. 10.0.0.8           76 requests
2. 198.51.100.14      71 requests
...

--- Top 5 Most Requested Endpoints ---
1. /login             64 requests
2. /cart              60 requests
...
==================================================
```

The numbers differ on every new sample log because the sample data is generated randomly.

## How It Works

1. `read_log_file` reads the file line by line and passes each line to `parse_line`.
2. `parse_line` uses a regular expression to extract IP, method, endpoint, status and size. Lines that fail to match are counted as malformed.
3. `analyze` uses `Counter` to count IPs, endpoints, methods and status codes, and totals the errors.
4. `build_report` formats the results, which are printed and saved to `summary_report.txt`.

## Why Are Logs Useful?

Server logs record every request a system receives. They help with debugging problems, detecting errors and suspicious activity, monitoring traffic, and understanding which pages or APIs are used the most.

## Possible Improvements

- Filter results by date or time range
- Detect IPs with an unusually high number of failed requests
- Export the report as CSV or JSON
- Add a chart of requests per hour
