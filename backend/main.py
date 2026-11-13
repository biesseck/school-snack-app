from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from csv_service import CSVService
from pdf_generator import build_student_cards_pdf

app = FastAPI(title="School Snack Delivery API", version="1.0.0")

# Habilita CORS para testes na rede local (Celular + Laptop)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o serviço CSV (cria students.csv e deliveries.csv automaticamente)
csv_db = CSVService()


class DeliveryRequest(BaseModel):
    student_id: str
    staff_user: str = "Admin"


@app.get("/")
def read_root():
    return {"status": "online", "message": "School Snack API (CSV) is running."}


@app.get("/api/students")
def list_students():
    """Retorna a lista de alunos cadastrados no students.csv."""
    return {"students": csv_db.get_all_students()}


@app.post("/api/deliver")
def deliver_snack(req: DeliveryRequest):
    """Registra uma entrega de lanche no deliveries.csv."""
    result = csv_db.record_delivery(req.student_id, req.staff_user)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])
    return result


@app.get("/api/generate-pdf")
def generate_pdf():
    """Gera o PDF de cartões QR a partir do students.csv."""
    students = csv_db.get_all_students()
    if not students:
        raise HTTPException(status_code=404, detail="Nenhum aluno encontrado no arquivo students.csv.")

    pdf_stream = build_student_cards_pdf(students)
    return Response(
        content=pdf_stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=students_qr_codes.pdf"},
    )