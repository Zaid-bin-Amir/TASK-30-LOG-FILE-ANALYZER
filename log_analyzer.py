import os
import random
import re
import sys
from collections import Counter
from datetime import datetime, timedelta

LOG_FILE = "server.log"
REPORT_FILE = "summary_report.txt"
TOP_N = 5

LINE_PATTERN = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<endpoint>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\d+)$'
)


def create_sample_log(path, total=500):
    ips = [
        "192.168.1.10", "192.168.1.25", "10.0.0.5", "10.0.0.8",
        "172.16.0.3", "203.0.113.9", "198.51.100.14", "8.8.8.8",
    ]
    endpoints = [
        "/", "/home", "/login", "/api/users", "/api/orders",
        "/products", "/cart", "/checkout", "/about", "/contact",
    ]
    methods = ["GET", "GET", "GET", "POST", "PUT", "DELETE"]
    statuses = [200, 200, 200, 200, 201, 301, 304, 400, 401, 403, 404, 404, 500, 503]
    start = datetime(2026, 10, 19, 8, 0, 0)

    lines = []
    for i in range(total):
        moment = start + timedelta(seconds=i * 7)
        stamp = moment.strftime("%d/%b/%Y:%H:%M:%S +0500")
        ip = random.choice(ips)
        method = random.choice(methods)
        endpoint = random.choice(endpoints)
        status = random.choice(statuses)
        size = random.randint(200, 9000)
        lines.append(
            f'{ip} - - [{stamp}] "{method} {endpoint} HTTP/1.1" {status} {size}'
        )

    lines.insert(50, "this line is corrupted")
    lines.insert(200, "")
    lines.insert(350, '999.1 - - [bad date] "GET" abc')

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def parse_line(line):
    match = LINE_PATTERN.match(line.strip())
    if not match:
        return None
    entry = match.groupdict()
    entry["status"] = int(entry["status"])
    entry["size"] = int(entry["size"])
    return entry


def read_log_file(path):
    entries = []
    malformed = 0
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            entry = parse_line(line)
            if entry is None:
                malformed += 1
            else:
                entries.append(entry)
    return entries, malformed


def analyze(entries):
    ip_counts = Counter(e["ip"] for e in entries)
    endpoint_counts = Counter(e["endpoint"] for e in entries)
    method_counts = Counter(e["method"] for e in entries)
    status_counts = Counter(e["status"] for e in entries)

    client_errors = sum(c for s, c in status_counts.items() if 400 <= s < 500)
    server_errors = sum(c for s, c in status_counts.items() if 500 <= s < 600)
    total_bytes = sum(e["size"] for e in entries)

    return {
        "total_requests": len(entries),
        "ip_counts": ip_counts,
        "endpoint_counts": endpoint_counts,
        "method_counts": method_counts,
        "status_counts": status_counts,
        "client_errors": client_errors,
        "server_errors": server_errors,
        "total_errors": client_errors + server_errors,
        "total_bytes": total_bytes,
    }


def build_report(results, malformed):
    total = results["total_requests"]
    error_rate = (results["total_errors"] / total * 100) if total else 0.0

    lines = []
    lines.append("=" * 50)
    lines.append("SERVER LOG SUMMARY REPORT")
    lines.append("=" * 50)
    lines.append(f"Total valid requests : {total}")
    lines.append(f"Malformed lines      : {malformed}")
    lines.append(f"Total data transferred: {results['total_bytes']} bytes")
    lines.append("")
    lines.append("--- Error Summary ---")
    lines.append(f"Client errors (4xx)  : {results['client_errors']}")
    lines.append(f"Server errors (5xx)  : {results['server_errors']}")
    lines.append(f"Total errors         : {results['total_errors']}")
    lines.append(f"Error rate           : {error_rate:.2f}%")
    lines.append("")
    lines.append("--- Requests by Method ---")
    for method, count in results["method_counts"].most_common():
        lines.append(f"{method:<8} {count}")
    lines.append("")
    lines.append("--- Requests by Status Code ---")
    for status, count in sorted(results["status_counts"].items()):
        lines.append(f"{status:<8} {count}")
    lines.append("")
    lines.append(f"--- Top {TOP_N} IP Addresses ---")
    for rank, (ip, count) in enumerate(results["ip_counts"].most_common(TOP_N), 1):
        lines.append(f"{rank}. {ip:<18} {count} requests")
    lines.append("")
    lines.append(f"--- Top {TOP_N} Most Requested Endpoints ---")
    for rank, (endpoint, count) in enumerate(
        results["endpoint_counts"].most_common(TOP_N), 1
    ):
        lines.append(f"{rank}. {endpoint:<18} {count} requests")
    lines.append("=" * 50)
    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else LOG_FILE

    if not os.path.exists(path):
        print(f"'{path}' not found. Creating a sample log file...")
        create_sample_log(path)

    try:
        entries, malformed = read_log_file(path)
    except OSError as error:
        print(f"Could not read the log file: {error}")
        return

    if not entries:
        print("No valid log entries found.")
        return

    results = analyze(entries)
    report = build_report(results, malformed)

    print(report)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        file.write(report + "\n")
    print(f"\nReport saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
