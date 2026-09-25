# 🩸 Blood Donation System — Backend

REST API for the Blood Donation System, built with **FastAPI**. Handles donor registration, blood requests, search, and authentication for the [React frontend](https://github.com/taseen17/Blood-Donation-System-Frontend).

> **Live demo:** [blood-donation-system-phitron.netlify.app](https://blood-donation-system-phitron.netlify.app/)

## Features
- Donor registration and profile management
- Search donors by blood group and location/city
- Blood request creation and tracking
- User authentication (login/signup)
- Input validation with Pydantic

## Tech Stack
| Layer    | Technology            |
| -------- | ---------------------- |
| Framework | FastAPI (Python)      |
| Database | SQLite <!-- update to PostgreSQL here if that's what you're actually running in production --> |
| Validation | Pydantic |

## Project Structure
```
Blood-Donation-System-Backend/
├── router/            # API route definitions
├── database.py        # Database connection/session setup
├── models.py           # Data models
├── main.py             # App entry point
└── requirements.txt
```

## Getting Started

### Prerequisites
- Python 3.10+

### 1. Clone the repository
```
git clone https://github.com/taseen17/Blood-Donation-System-Backend
cd Blood-Donation-System-Backend
```

### 2. Set up the environment
```
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the server
```
uvicorn main:app --reload
```
The API runs at `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

## API Overview
| Method | Endpoint                    | Description            |
| ------ | --------------------------- | ---------------------- |
| POST   | `/register`                 | Register a new user    |
| POST   | `/login`                    | Log in                 |
| GET    | `/donor/available`          | List or search donors  |
| POST   | `/blood_requests`           | Create a blood request |
| GET    | `/blood_requests/available` | View blood requests    |

## What I Learned
- Designing and structuring a REST API with FastAPI
- Working with routers to organize endpoints
- Connecting a database layer with Pydantic models
- Handling authentication and request validation

## Future Improvements
- Email/SMS notifications for urgent requests
- Map-based donor search
- Automated tests and CI

## Author
**Mir Muktadir Ali Taseen**
- Portfolio: [taseen17.github.io/My-Portfolio](https://taseen17.github.io/My-Portfolio/)
- GitHub: [github.com/taseen17](https://github.com/taseen17)
- LinkedIn: [Mir Muktadir Ali Taseen](https://www.linkedin.com/in/mir-muktadir-ali-taseen-68098a2a4/)

## License
[MIT](LICENSE)
