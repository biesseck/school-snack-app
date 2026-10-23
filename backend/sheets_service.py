import os
import uuid
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# CONFIGURATION FOR DUPLICATE CONTROL
# RESTRICTION_MODE = "daily"     # Options: "daily" or "cooldown"
RESTRICTION_MODE = "cooldown"    # Options: "daily" or "cooldown"
COOLDOWN_SECONDS = 5             # Used only when RESTRICTION_MODE = "cooldown"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
SPREADSHEET_NAME = "School Snack MVP"


class SheetsService:
    def __init__(self):
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Credentials file not found at {CREDENTIALS_FILE}. "
                "Please place credentials.json in the backend directory."
            )
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(SPREADSHEET_NAME)
        self.students_tab = self.sheet.worksheet("Students")
        self.deliveries_tab = self.sheet.worksheet("Deliveries")

    def is_delivery_restricted(self, student_id: str, now: datetime) -> tuple[bool, str]:
        """
        Checks whether a student is restricted from receiving a snack.
        Returns: (is_restricted: bool, reasoning_message: str)
        """
        deliveries = self.deliveries_tab.get_all_records()
        student_id_clean = student_id.strip().upper()
        date_today_str = now.strftime("%Y-%m-%d")

        for entry in reversed(deliveries):  # Check most recent entries first
            entry_student = str(entry.get("Student_ID")).strip().upper()
            if entry_student != student_id_clean:
                continue

            entry_date_str = str(entry.get("Date")).strip()
            entry_time_str = str(entry.get("Timestamp")).strip()

            # --- MODE 1: DAILY RESTRICTION ---
            if RESTRICTION_MODE == "daily":
                if entry_date_str == date_today_str:
                    return True, f"Student {student_id} already received a snack today ({date_today_str})."

            # --- MODE 2: TIME COOLDOWN RESTRICTION ---
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
                            f"Cooldown active! Please wait {remaining} seconds before delivering to {student_id} again.",
                        )
                except ValueError:
                    # In case of malformed timestamp format in Google Sheets
                    continue

        return False, ""

    def get_all_students(self):
        """Fetch all student records from the Students tab."""
        return self.students_tab.get_all_records()

    def get_student_by_id(self, student_id: str):
        """Find student details by Student_ID."""
        records = self.get_all_students()
        for student in records:
            if str(student.get("Student_ID")).strip().upper() == student_id.strip().upper():
                return student
        return None

    def is_snack_delivered_today(self, student_id: str, date_str: str) -> bool:
        """Check if a student has already claimed a snack for the given date."""
        deliveries = self.deliveries_tab.get_all_records()
        for entry in deliveries:
            entry_student = str(entry.get("Student_ID")).strip().upper()
            entry_date = str(entry.get("Date")).strip()
            if entry_student == student_id.strip().upper() and entry_date == date_str:
                return True
        return False

    def record_delivery(self, student_id: str, staff_user: str = "Admin") -> dict:
        """Record snack delivery if not currently restricted."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # 1. Check duplicate / cooldown rule
        is_restricted, message = self.is_delivery_restricted(student_id, now)
        if is_restricted:
            return {
                "success": False,
                "message": message,
                "status_code": 409
            }

        # 2. Check student existence
        student = self.get_student_by_id(student_id)
        if not student:
            return {
                "success": False,
                "message": f"Student ID '{student_id}' not found in roster.",
                "status_code": 404
            }

        # 3. Append row to Deliveries tab
        delivery_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"
        new_row = [delivery_id, date_str, time_str, student_id, staff_user]
        self.deliveries_tab.append_row(new_row)

        return {
            "success": True,
            "message": f"Snack successfully delivered to {student.get('Full_Name')}!",
            "delivery_id": delivery_id,
            "student_name": student.get("Full_Name"),
            "timestamp": f"{date_str} {time_str}",
            "status_code": 200
        }