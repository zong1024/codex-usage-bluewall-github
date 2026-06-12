#!/usr/bin/env python3
"""
Scan token usage from multiple AI coding tools:
- Codex
- Claude Code
- MimoCode
- Hermes Agent
"""

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


def expand_path(path: str) -> Path:
    return Path(os.path.expanduser(os.path.expandvars(path)))


def scan_codex(days: int = 365) -> Dict[str, Dict]:
    """Scan Codex token usage from SQLite database."""
    db_path = expand_path("~/.codex/state_5.sqlite")
    if not db_path.exists():
        print("  Codex: database not found")
        return {}
    
    print("  Codex: scanning...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
    cursor.execute("""
        SELECT created_at, tokens_used 
        FROM threads 
        WHERE created_at >= ? AND tokens_used > 0
    """, (cutoff,))
    
    daily = {}
    for created_at, tokens_used in cursor.fetchall():
        date_str = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d")
        if date_str not in daily:
            daily[date_str] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        
        input_tokens = int(tokens_used * 0.7)
        output_tokens = tokens_used - input_tokens
        
        daily[date_str]["input_tokens"] += input_tokens
        daily[date_str]["output_tokens"] += output_tokens
        daily[date_str]["total_tokens"] += tokens_used
    
    conn.close()
    print(f"  Codex: found {len(daily)} days, {sum(d['total_tokens'] for d in daily.values()):,} tokens")
    return daily


def scan_claude_code(days: int = 365) -> Dict[str, Dict]:
    """Scan Claude Code token usage from session JSONL files."""
    sessions_dir = expand_path("~/.claude/projects")
    if not sessions_dir.exists():
        print("  Claude Code: sessions directory not found")
        return {}
    
    print("  Claude Code: scanning...")
    daily = {}
    cutoff = datetime.now() - timedelta(days=days)
    
    # Find all JSONL session files
    for project_dir in sessions_dir.iterdir():
        if not project_dir.is_dir():
            continue
        
        for jsonl_file in project_dir.glob("*.jsonl"):
            try:
                with open(jsonl_file, "r") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            
                            # Look for assistant messages with usage
                            if data.get("type") != "assistant":
                                continue
                            
                            message = data.get("message", {})
                            usage = message.get("usage", {})
                            
                            if not usage:
                                continue
                            
                            # Get timestamp
                            timestamp = data.get("timestamp")
                            if not timestamp:
                                continue
                            
                            msg_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            # Compare without timezone
                            if msg_date.replace(tzinfo=None) < cutoff:
                                continue
                            
                            date_str = msg_date.strftime("%Y-%m-%d")
                            
                            if date_str not in daily:
                                daily[date_str] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
                            
                            input_tokens = usage.get("input_tokens", 0)
                            output_tokens = usage.get("output_tokens", 0)
                            
                            daily[date_str]["input_tokens"] += input_tokens
                            daily[date_str]["output_tokens"] += output_tokens
                            daily[date_str]["total_tokens"] += input_tokens + output_tokens
                        
                        except (json.JSONDecodeError, KeyError):
                            continue
            except Exception:
                continue
    
    print(f"  Claude Code: found {len(daily)} days, {sum(d['total_tokens'] for d in daily.values()):,} tokens")
    return daily


def scan_mimocode(days: int = 365) -> Dict[str, Dict]:
    """Scan MimoCode token usage from database."""
    db_path = expand_path("~/.local/share/mimocode/mimocode.db")
    if not db_path.exists():
        print("  MimoCode: database not found")
        return {}
    
    print("  MimoCode: scanning...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Try to find token usage in message table
    # MimoCode stores messages with data field containing JSON
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)  # milliseconds
    
    cursor.execute("""
        SELECT time_created, data 
        FROM message 
        WHERE time_created >= ? AND agent_id = 'main'
    """, (cutoff,))
    
    daily = {}
    for time_created, data_str in cursor.fetchall():
        try:
            data = json.loads(data_str)
            
            # Extract usage from message data
            usage = data.get("usage", {})
            if not usage:
                continue
            
            date_str = datetime.fromtimestamp(time_created / 1000).strftime("%Y-%m-%d")
            
            if date_str not in daily:
                daily[date_str] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            daily[date_str]["input_tokens"] += input_tokens
            daily[date_str]["output_tokens"] += output_tokens
            daily[date_str]["total_tokens"] += input_tokens + output_tokens
        
        except (json.JSONDecodeError, KeyError):
            continue
    
    conn.close()
    print(f"  MimoCode: found {len(daily)} days, {sum(d['total_tokens'] for d in daily.values()):,} tokens")
    return daily


def scan_all_tools(days: int = 365) -> Dict[str, Dict[str, Dict]]:
    """Scan all tools and return per-tool daily usage."""
    print("Scanning AI coding tools...")
    
    return {
        "codex": scan_codex(days),
        "claude_code": scan_claude_code(days),
        "mimocode": scan_mimocode(days),
    }


def merge_tool_data(tool_data: Dict[str, Dict[str, Dict]]) -> Dict[str, Dict]:
    """Merge data from all tools into a single daily usage dict."""
    merged = {}
    
    for tool_name, daily_usage in tool_data.items():
        for date_str, usage in daily_usage.items():
            if date_str not in merged:
                merged[date_str] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "tools": {}
                }
            
            merged[date_str]["input_tokens"] += usage["input_tokens"]
            merged[date_str]["output_tokens"] += usage["output_tokens"]
            merged[date_str]["total_tokens"] += usage["total_tokens"]
            merged[date_str]["tools"][tool_name] = usage["total_tokens"]
    
    return merged


def calculate_statistics(daily_usage: Dict[str, Dict]) -> Dict:
    """Calculate summary statistics."""
    if not daily_usage:
        return {
            "total_tokens": 0,
            "peak_day": None,
            "peak_tokens": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "total_days_active": 0
        }
    
    total_tokens = sum(day["total_tokens"] for day in daily_usage.values())
    peak_day = max(daily_usage.items(), key=lambda x: x[1]["total_tokens"])
    
    # Calculate streaks
    dates = sorted(daily_usage.keys())
    longest_streak = 0
    temp_streak = 0
    prev_date = None
    
    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if prev_date is None:
            temp_streak = 1
        elif (date - prev_date).days == 1:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 1
        prev_date = date
    longest_streak = max(longest_streak, temp_streak)
    
    # Current streak
    today = datetime.now().date()
    current_streak = 0
    for i in range(365):
        check_date = today - timedelta(days=i)
        if check_date.strftime("%Y-%m-%d") in daily_usage:
            current_streak += 1
        else:
            break
    
    return {
        "total_tokens": total_tokens,
        "peak_day": peak_day[0],
        "peak_tokens": peak_day[1]["total_tokens"],
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_days_active": len(daily_usage)
    }


def save_usage_data(tool_data: Dict, merged_data: Dict, statistics: Dict, output_path: Path):
    """Save usage data to JSON file."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "tools_scanned": list(tool_data.keys()),
        "per_tool_summary": {
            tool: sum(d["total_tokens"] for d in daily.values())
            for tool, daily in tool_data.items()
        },
        "statistics": statistics,
        "daily_usage": merged_data
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan AI coding tool usage")
    parser.add_argument("--days", type=int, default=365, help="Number of days to scan")
    parser.add_argument("--output", type=str, default="data/ai-usage.json", help="Output file")
    parser.add_argument("--tools", nargs="+", help="Specific tools to scan")
    args = parser.parse_args()
    
    # Scan all tools
    tool_data = scan_all_tools(args.days)
    
    # Filter tools if specified
    if args.tools:
        tool_data = {k: v for k, v in tool_data.items() if k in args.tools}
    
    # Merge data
    merged_data = merge_tool_data(tool_data)
    statistics = calculate_statistics(merged_data)
    
    # Save
    output_path = expand_path(args.output)
    save_usage_data(tool_data, merged_data, statistics, output_path)
    
    # Print summary
    print("\n=== AI Coding Tool Usage Summary ===")
    for tool, total in statistics.items():
        if tool == "total_tokens":
            print(f"Total tokens: {total:,}")
        elif tool == "peak_day":
            print(f"Peak day: {statistics['peak_day']} ({statistics['peak_tokens']:,} tokens)")
        elif tool == "current_streak":
            print(f"Current streak: {statistics['current_streak']} days")
        elif tool == "longest_streak":
            print(f"Longest streak: {statistics['longest_streak']} days")
        elif tool == "total_days_active":
            print(f"Active days: {statistics['total_days_active']}")
    
    print("\nPer-tool breakdown:")
    for tool, total in statistics.get("per_tool_summary", {}).items():
        print(f"  {tool}: {total:,} tokens")


if __name__ == "__main__":
    main()
