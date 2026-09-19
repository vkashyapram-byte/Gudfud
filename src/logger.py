import logging
import json
from datetime import datetime

class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj.update(record.extra)
            
        return json.dumps(log_obj)

def setup_logger(name="gudfud"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONLogFormatter())
        logger.addHandler(handler)
        
    return logger
