from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import json

from app.config import settings


class SchedulerService:
    def __init__(self):
        self.appointments: List[Dict] = []
        self.buffer_minutes = 30

    async def get_available_slots(
        self,
        date: Optional[str] = None,
        num_days: int = 5
    ) -> List[Dict]:
        available_slots = []

        start_date = datetime.now() if not date else datetime.strptime(date, "%Y-%m-%d")

        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)

            if current_date.weekday() >= 5:
                continue

            start_hour = int(settings.business_hours_start.split(":")[0])
            end_hour = int(settings.business_hours_end.split(":")[0])

            for hour in range(start_hour, end_hour):
                slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)

                if slot_time > datetime.now():
                    if not self._is_slot_booked(slot_time):
                        available_slots.append({
                            "date": current_date.strftime("%Y-%m-%d"),
                            "time": f"{hour:02d}:00",
                            "datetime": slot_time.isoformat()
                        })

        return available_slots[:10]

    async def book_appointment(
        self,
        customer_id: str,
        slot_datetime: str,
        customer_name: str,
        customer_email: str,
        purpose: str = "Sales Consultation"
    ) -> Dict:
        try:
            appointment_time = datetime.fromisoformat(slot_datetime)

            if self._is_slot_booked(appointment_time):
                return {
                    "success": False,
                    "message": "This slot is already booked. Please choose another time."
                }

            appointment = {
                "id": f"APT-{len(self.appointments) + 1}",
                "customer_id": customer_id,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "datetime": slot_datetime,
                "purpose": purpose,
                "status": "confirmed",
                "created_at": datetime.utcnow().isoformat()
            }

            self.appointments.append(appointment)

            logger.info(f"Appointment booked: {appointment['id']} for {customer_name}")

            return {
                "success": True,
                "appointment": appointment,
                "message": f"Your appointment is confirmed for {appointment_time.strftime('%B %d at %I:%M %p')}."
            }

        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "message": "Sorry, there was an error booking your appointment. Please try again."
            }

    async def cancel_appointment(self, appointment_id: str) -> bool:
        for apt in self.appointments:
            if apt["id"] == appointment_id:
                apt["status"] = "cancelled"
                return True
        return False

    async def get_customer_appointments(self, customer_id: str) -> List[Dict]:
        return [
            apt for apt in self.appointments
            if apt["customer_id"] == customer_id and apt["status"] == "confirmed"
        ]

    def _is_slot_booked(self, slot_time: datetime) -> bool:
        for apt in self.appointments:
            if apt["status"] == "confirmed":
                apt_time = datetime.fromisoformat(apt["datetime"])
                if abs((apt_time - slot_time).total_seconds()) < 1800:
                    return True
        return False

    def format_confirmation(self, appointment: Dict) -> str:
        apt_time = datetime.fromisoformat(appointment["datetime"])
        return f"""✅ Appointment Confirmed!

📅 Date: {apt_time.strftime('%B %d, %Y')}
🕐 Time: {apt_time.strftime('%I:%M %p')}
📋 Purpose: {appointment['purpose']}
🔖 Reference: {appointment['id']}

We'll send you a reminder before your appointment. Is there anything else you'd like to know?"""