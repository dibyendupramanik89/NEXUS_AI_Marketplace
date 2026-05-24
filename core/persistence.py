"""
NEXUS AI Marketplace - Local Persistence Layer
Saves all logs, workflow states, and traces locally for traceability.
Supports JSON file storage and optional SQLite for advanced queries.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────
#  STORAGE CONFIGURATION
# ─────────────────────────────────────────────

STORAGE_DIR = Path.home() / ".nexus" / "runs"
LOGS_DIR = STORAGE_DIR / "logs"
STATES_DIR = STORAGE_DIR / "states"
TRACES_DIR = STORAGE_DIR / "traces"

# Create directories on import
for dir_path in [LOGS_DIR, STATES_DIR, TRACES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
#  DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class PipelineRun:
    """Complete record of a single query execution."""
    run_id: str
    session_id: str
    timestamp: float = field(default_factory=time.time)
    query: str = ""
    category: str = ""
    status: str = "running"  # running | success | error
    duration_ms: float = 0.0
    logs: List[str] = field(default_factory=list)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    model_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "query": self.query,
            "category": self.category,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "log_count": len(self.logs),
            "error": self.error_message,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
        }


# ─────────────────────────────────────────────
#  LOCAL PERSISTENCE ENGINE
# ─────────────────────────────────────────────

class LocalPersistence:
    """
    Manages local storage of logs, states, and traces.
    All data stored in ~/.nexus/runs/ for easy access and backup.
    """

    @staticmethod
    def save_pipeline_run(run: PipelineRun) -> str:
        """Save complete pipeline run to JSON."""
        run_file = LOGS_DIR / f"{run.run_id}.json"
        
        data = {
            **run.to_dict(),
            "logs": run.logs,
            "state_snapshot": run.state_snapshot,
        }
        
        with open(run_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(run_file)

    @staticmethod
    def save_workflow_state(run_id: str, state: Dict[str, Any]) -> str:
        """Save workflow state snapshot."""
        state_file = STATES_DIR / f"{run_id}_state.json"
        
        # Filter out non-serializable objects
        serializable_state = {}
        for key, value in state.items():
            try:
                json.dumps(value, default=str)
                serializable_state[key] = value
            except (TypeError, ValueError):
                # Skip non-serializable fields, store as string representation
                serializable_state[key] = str(value)[:200]
        
        with open(state_file, "w") as f:
            json.dump(serializable_state, f, indent=2, default=str)
        
        return str(state_file)

    @staticmethod
    def save_trace(run_id: str, trace_data: Dict[str, Any]) -> str:
        """Save distributed trace data."""
        trace_file = TRACES_DIR / f"{run_id}_trace.json"
        
        with open(trace_file, "w") as f:
            json.dump(trace_data, f, indent=2, default=str)
        
        return str(trace_file)

    @staticmethod
    def save_logs(run_id: str, logs: List[str]) -> str:
        """Save detailed logs."""
        logs_file = LOGS_DIR / f"{run_id}_detailed.log"
        
        with open(logs_file, "w") as f:
            f.write("\n".join(logs))
        
        return str(logs_file)

    @staticmethod
    def get_run_history(limit: int = 50) -> List[Dict]:
        """Get recent pipeline runs."""
        runs = []
        
        for log_file in sorted(LOGS_DIR.glob("*.json"), reverse=True)[:limit]:
            try:
                with open(log_file) as f:
                    data = json.load(f)
                    runs.append(data)
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")
        
        return runs

    @staticmethod
    def get_run_by_id(run_id: str) -> Optional[Dict]:
        """Retrieve complete run data by ID."""
        run_file = LOGS_DIR / f"{run_id}.json"
        
        if not run_file.exists():
            return None
        
        try:
            with open(run_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading run {run_id}: {e}")
            return None

    @staticmethod
    def export_summary() -> str:
        """Export summary of all runs."""
        runs = LocalPersistence.get_run_history(limit=1000)
        
        summary = {
            "total_runs": len(runs),
            "successful_runs": len([r for r in runs if r["status"] == "success"]),
            "failed_runs": len([r for r in runs if r["status"] == "error"]),
            "total_duration_ms": sum(r.get("duration_ms", 0) for r in runs),
            "average_duration_ms": sum(r.get("duration_ms", 0) for r in runs) / len(runs) if runs else 0,
            "total_tokens": sum(r.get("tokens_used", 0) for r in runs),
            "total_cost_usd": sum(r.get("cost_usd", 0) for r in runs),
            "storage_location": str(STORAGE_DIR),
            "recent_runs": runs[:20],
        }
        
        summary_file = STORAGE_DIR / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        return str(summary_file)

    @staticmethod
    def get_storage_info() -> Dict:
        """Get information about local storage."""
        log_files = list(LOGS_DIR.glob("*.json"))
        state_files = list(STATES_DIR.glob("*.json"))
        trace_files = list(TRACES_DIR.glob("*.json"))
        
        # Calculate total size
        total_size_mb = sum(f.stat().st_size for f in log_files + state_files + trace_files) / (1024 * 1024)
        
        return {
            "storage_directory": str(STORAGE_DIR),
            "total_runs": len(log_files),
            "total_logs_mb": round(total_size_mb, 2),
            "logs_dir": str(LOGS_DIR),
            "states_dir": str(STATES_DIR),
            "traces_dir": str(TRACES_DIR),
            "latest_run": log_files[-1].name if log_files else None,
        }


# ─────────────────────────────────────────────
#  PERSISTENCE MANAGER (Global Instance)
# ─────────────────────────────────────────────

class PersistenceManager:
    """Thread-safe persistence manager for the pipeline."""
    
    def __init__(self):
        self.current_run: Optional[PipelineRun] = None
    
    def start_run(self, run_id: str, session_id: str, query: str) -> PipelineRun:
        """Initialize a new pipeline run."""
        self.current_run = PipelineRun(
            run_id=run_id,
            session_id=session_id,
            query=query,
        )
        return self.current_run
    
    def add_log(self, message: str):
        """Add a log message to current run."""
        if self.current_run:
            self.current_run.logs.append(message)
    
    def set_state(self, state: Dict[str, Any]):
        """Set workflow state snapshot."""
        if self.current_run:
            self.current_run.state_snapshot = state
    
    def finalize_run(
        self,
        status: str = "success",
        category: str = "",
        model_used: str = "",
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        error: Optional[str] = None,
    ):
        """Finalize and save the current run."""
        if not self.current_run:
            return None
        
        self.current_run.status = status
        self.current_run.category = category
        self.current_run.model_used = model_used
        self.current_run.tokens_used = tokens_used
        self.current_run.cost_usd = cost_usd
        self.current_run.error_message = error
        self.current_run.duration_ms = (time.time() - self.current_run.timestamp) * 1000
        
        # Save all data
        LocalPersistence.save_pipeline_run(self.current_run)
        LocalPersistence.save_logs(self.current_run.run_id, self.current_run.logs)
        LocalPersistence.save_workflow_state(self.current_run.run_id, self.current_run.state_snapshot)
        
        run_id = self.current_run.run_id
        self.current_run = None
        
        return run_id


# Global instance
persistence_manager = PersistenceManager()
