#!/usr/bin/env python3
"""
NEXUS Persistence Viewer
View saved logs, workflow states, and run history from local storage.

Usage:
    python view_logs.py                    # Show recent runs
    python view_logs.py --run <run_id>     # View specific run
    python view_logs.py --history          # Show last 20 runs
    python view_logs.py --summary          # Show overall summary
    python view_logs.py --storage           # Show storage info
"""

import sys
import json
from pathlib import Path
from core.persistence import LocalPersistence, STORAGE_DIR, LOGS_DIR


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def show_recent_runs(limit: int = 10):
    """Show recent pipeline runs."""
    print_header(f"📋 Recent Runs (Last {limit})")
    
    runs = LocalPersistence.get_run_history(limit)
    
    if not runs:
        print("No runs found in storage.")
        return
    
    for i, run in enumerate(runs, 1):
        status_icon = "✅" if run["status"] == "success" else "❌"
        print(f"{i:2d}. {status_icon} {run['run_id'][:12]}")
        print(f"    Query: {run['query'][:60]}...")
        print(f"    Category: {run['category']} | Duration: {run['duration_ms']:.0f}ms")
        print(f"    Model: {run['model_used']} | Status: {run['status']}")
        if run.get('error'):
            print(f"    Error: {run['error'][:60]}...")
        print()


def show_run_detail(run_id: str):
    """Show detailed information for a specific run."""
    run = LocalPersistence.get_run_by_id(run_id)
    
    if not run:
        print(f"❌ Run not found: {run_id}")
        return
    
    print_header(f"Run Details: {run_id}")
    
    print("📊 Summary:")
    print(f"  Session ID: {run['session_id']}")
    print(f"  Query: {run['query']}")
    print(f"  Category: {run['category']}")
    print(f"  Status: {run['status']}")
    print(f"  Duration: {run['duration_ms']:.2f}ms")
    print(f"  Model: {run['model_used']}")
    print(f"  Logs: {run['log_count']} entries")
    if run.get('error'):
        print(f"  Error: {run['error']}")
    
    print("\n📝 Pipeline Logs:")
    print("-" * 80)
    for log in run['logs'][:30]:  # Show first 30 logs
        print(f"  {log}")
    
    if len(run['logs']) > 30:
        print(f"\n  ... and {len(run['logs']) - 30} more logs")
    
    print("\n💾 State Keys:")
    print("-" * 80)
    if run.get('state_snapshot'):
        for key in list(run['state_snapshot'].keys())[:15]:
            value = run['state_snapshot'][key]
            if isinstance(value, (list, dict)):
                print(f"  {key}: {type(value).__name__} with {len(value)} items")
            else:
                print(f"  {key}: {str(value)[:60]}")


def show_storage_info():
    """Show storage information."""
    print_header("💾 Storage Information")
    
    info = LocalPersistence.get_storage_info()
    
    print(f"Storage Directory: {info['storage_directory']}")
    print(f"Total Runs: {info['total_runs']}")
    print(f"Storage Size: {info['total_logs_mb']:.2f} MB")
    print(f"Logs Directory: {info['logs_dir']}")
    print(f"States Directory: {info['states_dir']}")
    print(f"Traces Directory: {info['traces_dir']}")
    if info.get('latest_run'):
        print(f"Latest Run: {info['latest_run']}")


def show_summary():
    """Show overall summary of all runs."""
    summary_file = LocalPersistence.export_summary()
    
    print_header("📊 Run Summary")
    
    with open(summary_file) as f:
        summary = json.load(f)
    
    print(f"Total Runs: {summary['total_runs']}")
    print(f"Successful: {summary['successful_runs']}")
    print(f"Failed: {summary['failed_runs']}")
    print(f"Success Rate: {summary['successful_runs'] / summary['total_runs'] * 100:.1f}%" if summary['total_runs'] > 0 else "N/A")
    print(f"\nPerformance:")
    print(f"  Total Duration: {summary['total_duration_ms'] / 1000:.2f}s")
    print(f"  Average Duration: {summary['average_duration_ms']:.2f}ms")
    print(f"  Total Tokens: {summary['total_tokens']}")
    print(f"  Total Cost: ${summary['total_cost_usd']:.4f}")
    
    if summary.get('recent_runs'):
        print(f"\nRecent Runs:")
        for run in summary['recent_runs'][:5]:
            status = "✅" if run['status'] == "success" else "❌"
            print(f"  {status} {run['run_id'][:12]} - {run['category'][:15]:15} - {run['duration_ms']:.0f}ms")


def main():
    """Main entry point."""
    if not LOGS_DIR.exists() or not list(LOGS_DIR.glob("*.json")):
        print("📁 No runs found. Run the pipeline first:")
        print("   python main.py --ui")
        print("   python main.py 'your query'")
        return
    
    if len(sys.argv) < 2:
        show_recent_runs(10)
        print("\n💡 Commands:")
        print("   python view_logs.py --run <run_id>     # View specific run")
        print("   python view_logs.py --history          # Show last 20 runs")
        print("   python view_logs.py --summary          # Show overall summary")
        print("   python view_logs.py --storage          # Show storage info")
        return
    
    command = sys.argv[1]
    
    if command == "--run" and len(sys.argv) > 2:
        show_run_detail(sys.argv[2])
    elif command == "--history":
        show_recent_runs(20)
    elif command == "--summary":
        show_summary()
    elif command == "--storage":
        show_storage_info()
    else:
        print(f"Unknown command: {command}")
        print("Use: --run <id>, --history, --summary, --storage")


if __name__ == "__main__":
    main()
