from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from backend.database import get_db
from backend.models import LeaveRequestDB, CertificateRequestDB
from backend.agents import get_agents
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import io
from fpdf import FPDF

app = FastAPI()

class LeaveRequest(BaseModel):
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    reason: str

class CertificateRequest(BaseModel):
    student_id: str
    certificate_type: str

@app.get("/")
def root():
    return {"message": "Multi-Agent AI Backend is running"}

@app.post("/request_leave/")
def request_leave(leave: LeaveRequest, db: Session = Depends(get_db)):
    agents = get_agents(db)
    return agents["leave_agent"].process_leave_request(leave.dict())

@app.get("/leave_requests/")
def get_leave_requests(db: Session = Depends(get_db)):
    """Fetch all leave requests from the database."""
    leaves = db.query(LeaveRequestDB).all()
    if not leaves:
        return {"message": "No leave requests found", "data": []}
    return {"message": "Leave requests retrieved successfully", "data": leaves}


@app.post("/generate_certificate/")
def generate_certificate(cert: CertificateRequest, db: Session = Depends(get_db)):
    agents = get_agents(db)
    return agents["cert_agent"].generate_certificate(cert.dict())

@app.get("/download_certificate/{certificate_id}")
def download_certificate(certificate_id: int, db: Session = Depends(get_db)):
    cert = db.query(CertificateRequestDB).filter(CertificateRequestDB.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Certificate of {cert.certificate_type}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Issued to: {cert.student_id}", ln=True, align='C')

    file_path = f"certificates/certificate_{certificate_id}.pdf"
    os.makedirs("certificates", exist_ok=True)
    pdf.output(file_path)

    return FileResponse(file_path, media_type="application/pdf",
                        filename=f"certificate_{certificate_id}.pdf")

@app.post("/generate-response/")
def generate_response(data: dict, db: Session = Depends(get_db)):
    query = data.get("messages", [])[0].get("content", "")
    if not query:
        raise HTTPException(status_code=400, detail="Invalid input: Missing 'content' field.")

    agents = get_agents(db)
    return {"response": agents["query_agent"].handle_query(query)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
