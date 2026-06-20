import re
from typing import Dict, Any

class ADRParser:
    def parse(self, content: str) -> Dict[str, Any]:
        result = {
            "title": "",
            "status": "",
            "context": "",
            "decision": "",
            "consequences": ""
        }
        
        # Simple markdown section parser
        lines = content.split('\n')
        current_section = "title"
        
        for line in lines:
            if line.startswith("# "):
                result["title"] = line[2:].strip()
                continue
            
            lower_line = line.lower()
            if "status" in lower_line and line.startswith("##"):
                current_section = "status"
                continue
            elif "context" in lower_line and line.startswith("##"):
                current_section = "context"
                continue
            elif "decision" in lower_line and line.startswith("##"):
                current_section = "decision"
                continue
            elif "consequence" in lower_line and line.startswith("##"):
                current_section = "consequences"
                continue
                
            if current_section and line.strip():
                if current_section == "status" and not result["status"]:
                    # Try to extract just the status keyword
                    status_match = re.search(r'(proposed|accepted|rejected|deprecated|superseded)', lower_line)
                    if status_match:
                        result["status"] = status_match.group(1).upper()
                    else:
                        result["status"] += line + "\n"
                else:
                    result[current_section] += line + "\n"
                    
        for key in result:
            result[key] = result[key].strip()
            
        return result
