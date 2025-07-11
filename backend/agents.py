import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from backend.models import LeaveRequestDB, CertificateRequestDB

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is not set. Check your .env file.")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

class LeaveRequestAgent:
    def __init__(self, db: Session):
        self.db = db

    def process_leave_request(self, leave_data):
        leave_entry = LeaveRequestDB(**leave_data)
        self.db.add(leave_entry)
        self.db.commit()
        return {"status": "approved", "message": "Leave request approved"}

class CertificateAgent:
    def __init__(self, db: Session):
        self.db = db

    def generate_certificate(self, cert_data):
        cert_entry = CertificateRequestDB(**cert_data)
        self.db.add(cert_entry)
        self.db.commit()
        return {"status": "generated", "message": "Certificate issued"}

class QueryAgent:
    def __init__(self):
        self.api_key = MISTRAL_API_KEY

    def handle_query(self, query):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "mistral-tiny", "messages": [{"role": "user", "content": query}], "max_tokens": 150}

        try:
            response = requests.post(MISTRAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
        except requests.RequestException as e:
            return f"Error processing request: {str(e)}"

def get_agents(db: Session):
    return {
        "leave_agent": LeaveRequestAgent(db),
        "cert_agent": CertificateAgent(db),
        "query_agent": QueryAgent()
    }
