import os
import sqlite3
import uuid
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "database.db")

# CONFIGURAÇÕES DE RESTRIÇÃO DE ENTREGA
RESTRICTION_MODE = "cooldown"  # Opções: "daily" ou "cooldown"
COOLDOWN_SECONDS = 30           # Usado quando RESTRICTION_MODE = "cooldown"


class DBService:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn

    def _init_db(self):
        """Cria o banco de dados e as tabelas caso não existam."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabela de Alunos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                grade TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        """)

        # Tabela de Entregas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id TEXT PRIMARY KEY,
                date_str TEXT NOT NULL,
                time_str TEXT NOT NULL,
                student_id TEXT NOT NULL,
                staff_user TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        """)

        # Insere alunos iniciais para teste se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO students (student_id, full_name, grade, status)
                VALUES (?, ?, ?, ?)
            """, [
                ("STU-001", "Maria Silva", "6º Ano A", "Active"),
                ("STU-002", "João Santos", "6º Ano A", "Active"),
                ("STU-003", "Ana Oliveira", "7º Ano B", "Active")
            ])

        conn.commit()
        conn.close()

    def get_all_students(self) -> list:
        """Retorna todos os alunos em formato idêntico ao do Google Sheets."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id AS Student_ID, full_name AS Full_Name, grade AS Grade, status AS Status FROM students"
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_student_by_id(self, student_id: str):
        """Busca os dados de um aluno pelo ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id AS Student_ID, full_name AS Full_Name, grade AS Grade FROM students WHERE UPPER(student_id) = ?",
            (student_id.strip().upper(),)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def is_delivery_restricted(self, student_id: str, now: datetime) -> tuple[bool, str]:
        """Verifica regras de duplicidade ou tempo de espera (cooldown)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        date_today_str = now.strftime("%Y-%m-%d")
        student_id_clean = student_id.strip().upper()

        cursor.execute(
            "SELECT date_str, time_str FROM deliveries WHERE UPPER(student_id) = ? ORDER BY date_str DESC, time_str DESC LIMIT 1",
            (student_id_clean,)
        )
        last_delivery = cursor.fetchone()
        conn.close()

        if not last_delivery:
            return False, ""

        last_date = last_delivery["date_str"]
        last_time = last_delivery["time_str"]

        if RESTRICTION_MODE == "daily":
            if last_date == date_today_str:
                return True, f"Aluno {student_id} já recebeu lanche hoje ({date_today_str})."

        elif RESTRICTION_MODE == "cooldown":
            prev_datetime = datetime.strptime(f"{last_date} {last_time}", "%Y-%m-%d %H:%M:%S")
            elapsed_seconds = (now - prev_datetime).total_seconds()
            if elapsed_seconds < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - elapsed_seconds)
                return True, f"Aguarde {remaining} segundos para registrar novamente para {student_id}."

        return False, ""

    def record_delivery(self, student_id: str, staff_user: str = "Admin") -> dict:
        """Registra a entrega do lanche no SQLite."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        is_restricted, message = self.is_delivery_restricted(student_id, now)
        if is_restricted:
            return {"success": False, "message": message, "status_code": 409}

        student = self.get_student_by_id(student_id)
        if not student:
            return {"success": False, "message": f"Aluno ID '{student_id}' não encontrado.", "status_code": 404}

        delivery_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO deliveries (delivery_id, date_str, time_str, student_id, staff_user) VALUES (?, ?, ?, ?, ?)",
            (delivery_id, date_str, time_str, student_id, staff_user)
        )
        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"Lanche entregue com sucesso para {student.get('Full_Name')}!",
            "delivery_id": delivery_id,
            "student_name": student.get("Full_Name"),
            "timestamp": f"{date_str} {time_str}",
            "status_code": 200
        }