from datetime import datetime

class ScanLogger:
    def __init__(self):
        self.events = []
        self.start_time = None
        self.end_time = None
        self.config = {}

    def start_scan(self, config: dict):
        self.start_time = datetime.now()
        self.config = config
        self.events = []

    def log(self, symbol: str, stage: str, status: str, detail: str = ""):
        """
        stage: "UNIVERSE_FILTER" / "STRATEGY" / "CLASSIFIER" / "PHASE" / "EARNINGS"
        status: "PASS" / "SKIP" / "FAIL" / "INFO"
        """
        self.events.append({
            "time": datetime.now().isoformat(),
            "symbol": symbol,
            "stage": stage,
            "status": status,
            "detail": detail
        })

    def end_scan(self):
        self.end_time = datetime.now()

    def summary(self) -> dict:
        total = len(set(e["symbol"] for e in self.events))
        passed = len(set(
            e["symbol"] for e in self.events
            if e["status"] == "PASS"
            and e["stage"] == "STRATEGY"
        ))
        skipped_by_stage = {}
        for e in self.events:
            if e["status"] == "SKIP":
                stage = e["stage"]
                skipped_by_stage[stage] = skipped_by_stage.get(stage, 0) + 1
        
        duration = 0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).seconds
            
        return {
            "total_analyzed": total,
            "opportunities_found": passed,
            "skipped_by_stage": skipped_by_stage,
            "duration_seconds": duration,
            "config": self.config
        }
