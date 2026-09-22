from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    phone_number = Column(String)
    role = Column(String)
    city = Column(String)
    area = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(String)


class Donors(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blood_group = Column(String)
    last_donation_date = Column(String)
    is_available = Column(Boolean, default=True)
    total_donations = Column(Integer, default=0)
    date_of_birth = Column(String)
    medical_notes = Column(String)


class BloodRequests(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    patient_name = Column(String)
    patient_age = Column(Integer)
    blood_group = Column(String)
    quantity = Column(Integer)
    urgency_level = Column(String)
    status = Column(String, default="pending")
    hospital_name = Column(String)
    city = Column(String)
    area = Column(String)
    contact_number = Column(String)
    created_at = Column(String) 


class RequestResponses(Base):
    __tablename__ = "request_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id"))
    donor_id = Column(Integer, ForeignKey("donors.id"))
    response_status = Column(String, default="declined")
    response_date = Column(String)


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    type = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(String)


class Donations(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id"))
    request_id = Column(Integer, ForeignKey("blood_requests.id"))
    donation_date = Column(String)
    quantity = Column(Integer)




