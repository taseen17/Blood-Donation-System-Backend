from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import true
from models import Donors, BloodRequests, RequestResponses, Donations, Notifications, Users
import models
from database import SessionLocal, engine
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from router import admin, auth
from router.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from fastapi import  HTTPException
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://blood-donation-system-phitron.netlify.app/"],  # your Vite dev server URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)

models.Base.metadata.create_all(bind=engine)

class CreateDonor(BaseModel):
    blood_group: str = 'A+','A-','B+','B-','AB+','AB-','O+','O-'
    last_donation_date: str
    is_available: bool = True
    total_donations: int = 0
    date_of_birth: str
    medical_notes: Optional[str] = None


class UpdateDonor(BaseModel):
    blood_group: Optional[str] = None
    last_donation_date: Optional[str] = None
    is_available: Optional[bool] = None
    total_donations: Optional[int] = None
    date_of_birth: Optional[str] = None
    medical_notes: Optional[str] = None


class createRequest(BaseModel):
    patient_name: str
    patient_age: int
    blood_group: str = 'A+','A-','B+','B-','AB+','AB-','O+','O-'
    quantity: int
    urgency_level: str = 'normal','urgent','critical'
    hospital_name: str
    city: str
    area: str
    contact_number: str
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class updateRequest(BaseModel):
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    blood_group: Optional[str] = None
    quantity: Optional[int] = None
    urgency_level: Optional[str] = None
    hospital_name: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    contact_number: Optional[str] = None

class CreateRequestResponse(BaseModel):
    response_status: str = 'accepted','declined'


class CreateDonation(BaseModel):
    request_id: Optional[int] = None  # Assuming the donation is not linked to a specific request
    quantity: int


class CreateNotification(BaseModel):
    message: str
    type: str
    is_read: bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/")
def welcome():
    return {"message": "Welcome to the Blood Donation API!"}


@app.post("/donor")
def create_donor(donor: CreateDonor, current_user: user_dependency, db: db_dependency):
    new_donor = Donors(
        user_id=current_user.id,
        blood_group=donor.blood_group,
        last_donation_date=donor.last_donation_date,
        is_available=donor.is_available,
        total_donations=donor.total_donations,
        date_of_birth=donor.date_of_birth,
        medical_notes=donor.medical_notes
    )
    db.add(new_donor)
    db.commit()
    db.refresh(new_donor)
    return {"message": "Donor profile created successfully", "donor_id": new_donor.id}

@app.get("/donor/available")
def get_available_donors(db: db_dependency, blood_group: Optional[str] = None, city: Optional[str] = None, area: Optional[str] = None):
    query = db.query(Donors).filter(Donors.is_available == True)

    if blood_group:
        query = query.filter(Donors.blood_group == blood_group)
    if city:
        query = query.filter(Donors.city == city)
    if area:
        query = query.filter(Donors.area == area)

    return query.all()

@app.get("/donor/{donor_id}")
def get_donor(donor_id: int, current_user: user_dependency, db: db_dependency):
    donor = db.query(Donors).filter(Donors.id == donor_id, Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    return donor

@app.put("/donor/{donor_id}")
def update_donor(donor_id: int, donor_update: UpdateDonor, current_user: user_dependency, db: db_dependency):
    donor = db.query(Donors).filter(Donors.id == donor_id, Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    for key, value in donor_update.model_dump(exclude_unset=True).items():
        setattr(donor, key, value)
    
    db.commit()
    db.refresh(donor)
    return {"message": "Donor profile updated successfully", "donor": donor}

@app.post("/blood_request")
def create_blood_request(request: createRequest, current_user: user_dependency, db: db_dependency):
    new_request = BloodRequests(
        requester_id=current_user.id,
        patient_name=request.patient_name,
        patient_age=request.patient_age,
        blood_group=request.blood_group,
        quantity=request.quantity,
        urgency_level=request.urgency_level,
        hospital_name=request.hospital_name,
        city=request.city,
        area=request.area,
        contact_number=request.contact_number,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"message": "Blood request created successfully", "request_id": new_request.id}

@app.get("/blood_request/available")
def get_available_blood_requests(db: db_dependency, blood_group: Optional[str] = None, city: Optional[str] = None, area: Optional[str] = None):
    query = db.query(BloodRequests).filter(BloodRequests.status == "pending")

    if blood_group:
        query = query.filter(BloodRequests.blood_group == blood_group)
    if city:
        query = query.filter(BloodRequests.city == city)
    if area:
        query = query.filter(BloodRequests.area == area)

    return query.all()

@app.get("/blood_request/responses")
def get_blood_request_responses(request_id: int, current_user: user_dependency, db: db_dependency):
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id, BloodRequests.requester_id == current_user.id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    
    response_rows = (
        db.query(RequestResponses, Users)
        .join(Donors, RequestResponses.donor_id == Donors.id)
        .join(Users, Donors.user_id == Users.id)
        .filter(RequestResponses.request_id == request_id)
        .all()
    )

    return {
        "responses": [
            {
                "response": response,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "city": user.city,
                    "area": user.area,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                },
            }
            for response, user in response_rows
        ]
    }

@app.get("/blood_request/{request_id}")
def get_blood_request(request_id: int, current_user: user_dependency, db: db_dependency):
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id, BloodRequests.requester_id == current_user.id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    return blood_request

@app.put("/blood_request/{request_id}")
def update_blood_request(request_id: int, request_update: updateRequest, current_user: user_dependency, db: db_dependency):
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id, BloodRequests.requester_id == current_user.id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")

    for key, value in request_update.model_dump(exclude_unset=True).items():
        setattr(blood_request, key, value)
    
    db.commit()
    db.refresh(blood_request)
    return {"message": "Blood request updated successfully", "blood_request": blood_request}

@app.delete("/blood_request/{request_id}")
def delete_blood_request(request_id: int, current_user: user_dependency, db: db_dependency):
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id, BloodRequests.requester_id == current_user.id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    
    db.delete(blood_request)
    db.commit()
    return {"message": "Blood request deleted successfully"}

@app.post("/request_response")
def create_request_response(request_id: int, response: CreateRequestResponse, current_user: user_dependency, db: db_dependency):
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    
    donor = db.query(Donors).filter(Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    new_response = RequestResponses(
        request_id=request_id,
        donor_id=donor.id,
        response_status=response.response_status,
        response_date= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    notifications = Notifications(
        user_id=blood_request.requester_id,
        message=f"New response received for blood request: {blood_request.id}",
        type=response.response_status,
        is_read=False,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(notifications)
    db.commit()
    return {"message": "Request response created successfully", "response_id": new_response.id}

@app.get("/request_response/{response_id}")
def get_request_response(response_id: int, current_user: user_dependency, db: db_dependency):
    response = db.query(RequestResponses).filter(RequestResponses.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Request response not found")
    
    donor = db.query(Donors).filter(Donors.id == response.donor_id, Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=403, detail="You do not have permission to view this response")
    
    return response

@app.get("/donor/responses")
def get_donor_responses(current_user: user_dependency, db: db_dependency):
    donor = db.query(Donors).filter(Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    responses = db.query(RequestResponses).filter(RequestResponses.donor_id == donor.id).all()
    return responses

@app.post("/donation")
def create_donation(donation: CreateDonation, current_user: user_dependency, db: db_dependency):
    donor = db.query(Donors).filter(Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    new_donation = Donations(
        donor_id=donor.id,
        request_id=None,  # Assuming the donation is not linked to a specific request
        donation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        quantity=donation.quantity
    )
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    return {"message": "Donation created successfully", "donation_id": new_donation.id}

@app.get("/donations/me")
def get_my_donations(current_user: user_dependency, db: db_dependency):
    donor = db.query(Donors).filter(Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    donations = db.query(Donations).filter(Donations.donor_id == donor.id).all()
    return donations

@app.get("/donation/{donation_id}")
def get_donation(donation_id: int, current_user: user_dependency, db: db_dependency):
    donation = db.query(Donations).filter(Donations.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    donor = db.query(Donors).filter(Donors.id == donation.donor_id, Donors.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=403, detail="You do not have permission to view this donation")
    
    return donation

@app.get("/notifications/me")
def get_my_notifications(current_user: user_dependency, db: db_dependency):
    notifications = db.query(Notifications).filter(Notifications.user_id == current_user.id).all()
    return notifications

@app.put("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int, current_user: user_dependency, db: db_dependency):
    notification = db.query(Notifications).filter(Notifications.id == notification_id, Notifications.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return {"message": "Notification marked as read", "notification": notification}

@app.get("/user/{user_id}")
def get_user_info(user_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this user's information")
    
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {user}

@app.get("/donors/search")
def search_donors(db: db_dependency, blood_group: str):
    query = db.query(Donors)
    if blood_group:
        query = query.filter(Donors.blood_group == blood_group.capitalize())
    donors = query.all()
    if not donors:
        raise HTTPException(status_code=404, detail="No donors found matching the search criteria")
    return donors

@app.get("/blood_requests/search")
def search_blood_requests(db: db_dependency, blood_group: str):
    query = db.query(BloodRequests)
    if blood_group:
        query = query.filter(BloodRequests.blood_group == blood_group.capitalize())
    blood_requests = query.all()
    if not blood_requests:
        raise HTTPException(status_code=404, detail="No blood requests found matching the search criteria")
    return blood_requests

@app.get("/donors/filter")
def filter_donors(db: db_dependency, availability: Optional[bool] = None):
    donors = db.query(Donors).filter(Donors.is_available == True).all()
    if not donors:
        raise HTTPException(status_code=404, detail="No donors found matching the filter criteria")
    return donors

@app.get("/blood_requests/sort")
def sort_blood_requests(db: db_dependency, sort_by: str = "newest or oldest"):
    query = db.query(BloodRequests)
    if sort_by == "newest":
        query = query.order_by(BloodRequests.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(BloodRequests.created_at.asc())
    blood_requests = query.all()
    return blood_requests

