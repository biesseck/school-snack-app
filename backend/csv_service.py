import csv
import os
import threading
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
STUDENTS_CSV = os.path.join(BASE_DIR, "students.csv")
DELIVERIES_CSV = os.path.join(BASE_DIR, "deliveries.csv")

# CONFIGURAÇÕES DE RESTRIÇÃO DE ENTREGA
RESTRICTION_MODE = "cooldown"  # Opções: "daily" ou "cooldown"
COOLDOWN_SECONDS = 30           # Usado quando RESTRICTION_MODE = "cooldown"


class CSVService:
    def __init__(self):
        # Lock evita corrupção caso duas requisições tentem escrever no CSV ao mesmo tempo
        self._lock = threading.Lock()
        self._init_csv_files()

    def _init_csv_files(self):
        """Cria os arquivos CSV com cabeçalhos e dados iniciais caso não existam."""
        with self._lock:
            if not os.path.exists(STUDENTS_CSV):
                with open(STUDENTS_CSV, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Student_ID", "Full_Name", "Grade", "Status"])
                    writer.writerows([
                        ["STU-001", "Maria Silva", "6º Ano A", "Active"],
                        ["STU-002", "João Santos", "6º Ano A", "Active"],
                        ["STU-003", "Ana Oliveira", "7º Ano B", "Active"],
                    ])

            if not os.path.exists(DELIVERIES_CSV):
                with open(DELIVERIES_CSV, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Delivery_ID", "Date", "Timestamp", "Student_ID", "Staff_User"])

    def get_all_students(self) -> list:
        """Lê todos os registros do students.csv."""
        with self._lock:
            if not os.path.exists(STUDENTS_CSV):
                return []
            with open(STUDENTS_CSV, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)

    def get_student_by_id(self, student_id: str):
        """Busca um aluno pelo Student_ID."""
        students = self.get_all_students()
        target_id = student_id.strip().upper()
        for student in students:
            if str(student.get("Student_ID", "")).strip().upper() == target_id:
                return student
        return None

    def _get_all_deliveries(self) -> list:
        """Lê todos os registros do deliveries.csv (uso interno sem lock extra)."""
        if not os.path.exists(DELIVERIES_CSV):
            return []
        with open(DELIVERIES_CSV, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def is_delivery_restricted(self, student_id: str, now: datetime) -> tuple[bool, str]:
        """Verifica se o aluno já retirou lanche no dia ou dentro do tempo de cooldown."""
        deliveries = self._get_all_deliveries()
        student_id_clean = student_id.strip().upper()
        date_today_str = now.strftime("%Y-%m-%d")

        # Percorre de trás para frente para achar o registro mais recente primeiro
        for entry in reversed(deliveries):
            entry_student = str(entry.get("Student_ID", "")).strip().upper()
            if entry_student != student_id_clean:
                continue

            entry_date_str = str(entry.get("Date", "")).strip()
            entry_time_str = str(entry.get("Timestamp", "")).strip()

            if RESTRICTION_MODE == "daily":
                if entry_date_str == date_today_str:
                    return True, f"Aluno {student_id} já recebeu lanche hoje ({date_today_str})."

            elif RESTRICTION_MODE == "cooldown":
                try:
                    prev_datetime = datetime.strptime(
                        f"{entry_date_str} {entry_time_str}", "%Y-%m-%d %H:%M:%S"
                    )
                    elapsed_seconds = (now - prev_datetime).total_seconds()
                    if elapsed_seconds < COOLDOWN_SECONDS:
                        remaining = int(COOLDOWN_SECONDS - elapsed_seconds)
                        return (
                            True,
                            f"Aguarde {remaining} segundos para registrar novamente para {student_id}.",
                        )
                except ValueError:
                    continue

        return False, ""

    def record_delivery(self, student_id: str, staff_user: str = "Admin") -> dict:
        """Valida e anexa uma nova linha no deliveries.csv."""
        student = self.get_student_by_id(student_id)
        if not student:
            return {
                "success": False,
                "message": f"Aluno ID '{student_id}' não encontrado.",
                "status_code": 404,
            }

        with self._lock:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            is_restricted, message = self.is_delivery_restricted(student_id, now)
            if is_restricted:
                return {"success": False, "message": message, "status_code": 409}

            delivery_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

            with open(DELIVERIES_CSV, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([delivery_id, date_str, time_str, student_id.strip().upper(), staff_user])

        return {
            "success": True,
            "message": f"Lanche entregue com sucesso para {student.get('Full_Name')}!",
            "delivery_id": delivery_id,
            "student_name": student.get("Full_Name"),
            "timestamp": f"{date_str} {time_str}",
            "status_code": 200,
        }