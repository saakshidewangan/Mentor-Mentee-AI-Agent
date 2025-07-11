from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LeaveRequestDB(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)
    leave_type = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    reason = Column(String)

class CertificateRequestDB(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    certificate_type = Column(String)
