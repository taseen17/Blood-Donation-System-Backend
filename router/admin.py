from fastapi import APIRouter, Depends, HTTPException, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from router.auth import get_current_user
from models import Users, Donors, BloodRequests, RequestResponses, Notifications, Donations
from typing import Annotated


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/admin")
def read_admin_data(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    # Fetch admin data from the database
    admin_data = db.query(Users).filter(Users.role == "admin").all()
    return {"admin_data": admin_data}

@router.get("/admin/users")
def read_users(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    users = db.query(Users).all()
    return {"users": users}

@router.get("/admin/donors")
def read_donors(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    donors = db.query(Donors).all()
    return {"donors": donors}

@router.get("/admin/blood_requests")
def read_blood_requests(current_user: user_dependency, db: db_dependency):  
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    blood_requests = db.query(BloodRequests).all()
    return {"blood_requests": blood_requests}

@router.get("/admin/request_responses")
def read_request_responses(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    request_responses = db.query(RequestResponses).all()
    return {"request_responses": request_responses}

@router.get("/admin/notifications")
def read_notifications(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    notifications = db.query(Notifications).all()
    return {"notifications": notifications}

@router.get("/admin/summary")
def read_summary(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    total_users = db.query(Users).count()
    total_donors = db.query(Donors).count()
    total_blood_requests = db.query(BloodRequests).count()
    total_request_responses = db.query(RequestResponses).count()
    total_notifications = db.query(Notifications).count()

    summary = {
        "total_users": total_users,
        "total_donors": total_donors,
        "total_blood_requests": total_blood_requests,
        "total_request_responses": total_request_responses,
        "total_notifications": total_notifications
    }

    return {"summary": summary}

@router.get("/admin/user/{user_id}")
def read_user(user_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@router.get("/admin/donor/{donor_id}")
def read_donor(donor_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    donor = db.query(Donors).filter(Donors.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return {"donor": donor}

@router.get("/admin/blood_request/{request_id}")
def read_blood_request(request_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    return {"blood_request": blood_request}

@router.get("/admin/request_response/{response_id}")
def read_request_response(response_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    request_response = db.query(RequestResponses).filter(RequestResponses.id == response_id).first()
    if not request_response:
        raise HTTPException(status_code=404, detail="Request response not found")
    return {"request_response": request_response}

@router.get("/admin/notification/{notification_id}")
def read_notification(notification_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    notification = db.query(Notifications).filter(Notifications.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"notification": notification}

@router.get("/admin/active_donors")
def read_active_donors(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    active_donors = db.query(Donors).filter(Donors.is_available == True).all()
    return {"active_donors": active_donors}

@router.get("/admin/pending_requests")
def read_pending_requests(current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    pending_requests = db.query(BloodRequests).filter(BloodRequests.status == "pending").all()
    return {"pending_requests": pending_requests}

@router.get("/admin/unread_notifications")
def read_unread_notifications(current_user: user_dependency, db: db_dependency):    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    unread_notifications = db.query(Notifications).filter(Notifications.is_read == False).all()
    return {"unread_notifications": unread_notifications}

@router.put("/admin/verify_user/{user_id}")
def verify_user(user_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return {"message": "User verified successfully"}

@router.delete("/admin/delete_user/{user_id}")
def delete_user(user_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    donor_ids = [donor_id for donor_id, in db.query(Donors.id).filter(Donors.user_id == user_id).all()]
    request_ids = [request_id for request_id, in db.query(BloodRequests.id).filter(BloodRequests.requester_id == user_id).all()]

    if donor_ids or request_ids:
        response_query = db.query(RequestResponses)
        if donor_ids and request_ids:
            response_query = response_query.filter(
                (RequestResponses.donor_id.in_(donor_ids)) |
                (RequestResponses.request_id.in_(request_ids))
            )
        elif donor_ids:
            response_query = response_query.filter(RequestResponses.donor_id.in_(donor_ids))
        else:
            response_query = response_query.filter(RequestResponses.request_id.in_(request_ids))
        response_query.delete(synchronize_session=False)

        donation_query = db.query(Donations)
        if donor_ids and request_ids:
            donation_query = donation_query.filter(
                (Donations.donor_id.in_(donor_ids)) |
                (Donations.request_id.in_(request_ids))
            )
        elif donor_ids:
            donation_query = donation_query.filter(Donations.donor_id.in_(donor_ids))
        else:
            donation_query = donation_query.filter(Donations.request_id.in_(request_ids))
        donation_query.delete(synchronize_session=False)

    db.query(Notifications).filter(Notifications.user_id == user_id).delete(synchronize_session=False)
    db.query(Donors).filter(Donors.user_id == user_id).delete(synchronize_session=False)
    db.query(BloodRequests).filter(BloodRequests.requester_id == user_id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.delete("/admin/delete_donor/{donor_id}")
def delete_donor(donor_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    donor = db.query(Donors).filter(Donors.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    db.delete(donor)
    db.commit()
    return {"message": "Donor deleted successfully"}

@router.delete("/admin/delete_blood_request/{request_id}")
def delete_blood_request(request_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    blood_request = db.query(BloodRequests).filter(BloodRequests.id == request_id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    db.delete(blood_request)
    db.commit()
    return {"message": "Blood request deleted successfully"}

@router.delete("/admin/delete_request_response/{response_id}")
def delete_request_response(response_id: int, current_user: user_dependency, db: db_dependency):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    request_response = db.query(RequestResponses).filter(RequestResponses.id == response_id).first()
    if not request_response:
        raise HTTPException(status_code=404, detail="Request response not found")
    db.delete(request_response)
    db.commit()
    return {"message": "Request response deleted successfully"}

@router.delete("/admin/delete_notification/{notification_id}")
def delete_notification(notification_id: int, current_user: user_dependency, db: db_dependency):    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    notification = db.query(Notifications).filter(Notifications.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}
