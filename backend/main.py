from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sheets_service import SheetsService
from pdf_generator import build_student_cards_pdf

app = FastAPI(title="School Snack Delivery API", version="1.0.0")

# Enable CORS for local network testing (Mobile + Laptop)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Sheets service instance
try:
    sheets = SheetsService()
except Exception as e:
    print(f"[Warning] Failed to initialize Google Sheets service: {e}")
    sheets = None

class DeliveryRequest(BaseModel):
    student_id: str
    staff_user: str = "Admin"

@app.get("/")
def read_root():
    return {"status": "online", "message": "School Snack API is running."}

@app.get("/api/students")
def list_students():
    """Returns the roster of all active students."""
    if not sheets:
        raise HTTPException(status_code=500, detail="Google Sheets service not configured.")
    return {"students": sheets.get_all_students()}

@app.post("/api/deliver")
def deliver_snack(req: DeliveryRequest):
    """Processes a QR scan attempt and records snack delivery."""
    if not sheets:
        raise HTTPException(status_code=500, detail="Google Sheets service not configured.")
    
    result = sheets.record_delivery(req.student_id, req.staff_user)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])
    
    return result

@app.get("/api/generate-pdf")
def generate_pdf():
    """Generates and streams a printable PDF containing student QR codes."""
    if not sheets:
        raise HTTPException(status_code=500, detail="Google Sheets service not configured.")
    
    students = sheets.get_all_students()
    if not students:
        raise HTTPException(status_code=444, detail="No student records found to generate PDF.")
    
    pdf_stream = build_student_cards_pdf(students)
    return Response(
        content=pdf_stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=students_qr_codes.pdf"}
    )