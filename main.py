"""
NEXUS AI Marketplace - Main Entry Point
Run: python main.py [--test] [--ui]
"""

import sys
import os

# Ensure imports work from project root
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()


def main():
    args = sys.argv[1:]

    if "--test" in args:
        from workflow.graph import run_test_suite
        run_test_suite()

    elif "--ui" in args or not args:
        print("🌐 Starting NEXUS AI Marketplace UI...")
        print("   Open: http://localhost:7860")
        from app import build_enterprise_ui
        ui = build_enterprise_ui()
        ui.launch(server_name="0.0.0.0", server_port=7860, share=False)

    else:
        # Single query mode
        query = " ".join(args)
        from workflow.graph import process_query
        print(f"\n🔍 Processing: {query}\n")
        output, logs, _ = process_query(query)
        print(logs)
        print("\n" + "=" * 60)
        print(output)


if __name__ == "__main__":
    main()
