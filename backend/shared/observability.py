import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import MetricServiceClient
from google.cloud.monitoring_v3.types import TimeSeries, Point, TimeInterval
import os

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class StructuredLogger:
    """Production-grade structured logger with GCP integration"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.gcp_enabled = os.getenv("GCP_LOGGING_ENABLED", "false").lower() == "true"
        
        if self.gcp_enabled:
            try:
                self.gcp_client = cloud_logging.Client()
                self.gcp_logger = self.gcp_client.logger(name)
            except Exception as e:
                self.logger.warning(f"Failed to initialize GCP logging: {e}")
                self.gcp_enabled = False
    
    def _log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        # Local logging
        getattr(self.logger, level.lower())(json.dumps(log_data))
        
        # GCP logging
        if self.gcp_enabled:
            try:
                self.gcp_logger.log_struct(log_data, severity=level.upper())
            except Exception as e:
                self.logger.error(f"GCP logging failed: {e}")
    
    def info(self, message: str, **kwargs):
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log('DEBUG', message, **kwargs)


class MetricsCollector:
    """Production-grade metrics collector with GCP Monitoring"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.gcp_enabled = self.project_id is not None
        
        if self.gcp_enabled:
            try:
                self.client = MetricServiceClient()
                self.project_name = f"projects/{self.project_id}"
            except Exception as e:
                logging.warning(f"Failed to initialize GCP monitoring: {e}")
                self.gcp_enabled = False
    
    def record_metric(
        self,
        metric_type: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a metric value"""
        
        # Local logging
        logging.info(f"Metric: {metric_type} = {value}, labels={labels}")
        
        # GCP Monitoring
        if self.gcp_enabled:
            try:
                series = TimeSeries()
                series.metric.type = f"custom.googleapis.com/chronicleops/{metric_type}"
                
                if labels:
                    for key, val in labels.items():
                        series.metric.labels[key] = str(val)
                
                series.resource.type = "global"
                
                now = datetime.utcnow()
                interval = TimeInterval({"end_time": {"seconds": int(now.timestamp())}})
                point = Point({"interval": interval, "value": {"double_value": value}})
                series.points = [point]
                
                self.client.create_time_series(
                    name=self.project_name,
                    time_series=[series]
                )
            except Exception as e:
                logging.error(f"Failed to record metric to GCP: {e}")
    
    def record_simulation_metrics(self, run_id: str, metrics: Dict[str, Any]):
        """Record simulation-specific metrics"""
        labels = {"run_id": run_id}
        
        self.record_metric("cash", metrics.get("cash", 0), labels)
        self.record_metric("runway_months", metrics.get("runway_months", 0), labels)
        self.record_metric("revenue_monthly", metrics.get("revenue_monthly", 0), labels)
        self.record_metric("costs_monthly", metrics.get("costs_monthly", 0), labels)
        self.record_metric("headcount", metrics.get("headcount", 0), labels)
        self.record_metric("service_level", metrics.get("service_level", 1.0), labels)
    
    def record_agent_decision(self, run_id: str, agent_role: str, action_type: str):
        """Record agent decision event"""
        labels = {
            "run_id": run_id,
            "agent_role": agent_role,
            "action_type": action_type
        }
        self.record_metric("agent_decisions", 1, labels)
    
    def record_policy_violation(self, run_id: str, rule: str):
        """Record policy violation"""
        labels = {"run_id": run_id, "rule": rule}
        self.record_metric("policy_violations", 1, labels)


# Global instances
logger = StructuredLogger("chronicleops")
metrics = MetricsCollector()
