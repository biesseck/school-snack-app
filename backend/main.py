from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_service import DBService
from pdf_generator import build_student_cards_pdf

app = FastAPI(title="School Snack Delivery API", version="1.0.0")

# Habilita CORS para testes na rede local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o serviço SQLite
db = DBService()

class DeliveryRequest(BaseModel):
    student_id: str
    staff_user: str = "Admin"

@app.get("/")
def read_root():
    return {"status": "online", "message": "School Snack API (SQLite) is running."}

@app.get("/api/students")
def list_students():
    """Retorna a lista de alunos do SQLite."""
    return {"students": db.get_all_students()}

@app.post("/api/deliver")
def deliver_snack(req: DeliveryRequest):
    """Registra uma tentativa de entrega no SQLite."""
    result = db.record_delivery(req.student_id, req.staff_user)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])
    return result

@app.get("/api/generate-pdf")
def generate_pdf():
    """Gera o PDF de cartões QR buscando os alunos no SQLite."""
    students = db.get_all_students()
    if not students:
        raise HTTPException(status_code=404, detail="Nenhum aluno encontrado no banco de dados.")
    
    pdf_stream = build_student_cards_pdf(students)
    return Response(
        content=pdf_stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=student_qr_passes.pdf"}
    )