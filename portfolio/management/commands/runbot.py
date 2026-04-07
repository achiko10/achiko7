import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Booking, Project, Appointment
from django.utils import timezone
from datetime import timedelta
from openai import OpenAI

class Command(BaseCommand):
    help = 'Runs the Telegram Bot via Long Polling with OpenAI Integration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Zenith Telegram Bot (AI Powered)..."))
        
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not token:
            self.stderr.write("Error: TELEGRAM_BOT_TOKEN is missing in settings.py")
            return
            
        self.client = None
        if openai_key:
            try:
                self.client = OpenAI(api_key=openai_key)
                self.stdout.write(self.style.SUCCESS("OpenAI connected!"))
            except Exception as e:
                self.stderr.write(f"OpenAI Initialization Error: {e}")

        base_url = f"https://api.telegram.org/bot{token}"
        offset = None

        while True:
            try:
                # Long polling request
                url = f"{base_url}/getUpdates?timeout=30"
                if offset:
                    url += f"&offset={offset}"
                    
                response = requests.get(url, timeout=40).json()

                if response.get('ok') and response.get('result'):
                    for update in response['result']:
                        offset = update['update_id'] + 1
                        
                        message = update.get('message')
                        if not message or 'text' not in message:
                            continue
                            
                        chat_id = message['chat']['id']
                        text = message['text'].strip()
                        
                        # Only allow our designated owner to interact with the bot
                        if str(chat_id) != str(settings.TELEGRAM_CHAT_ID):
                            self.send_message(base_url, chat_id, "❌ თქვენ არ გაქვთ ამ ბოტზე წვდომის უფლება.")
                            continue
                        
                        self.process_command(base_url, chat_id, text, base_url)
                        
            except requests.exceptions.RequestException as e:
                self.stderr.write(f"Network error: {e}")
                time.sleep(5)
            except Exception as e:
                self.stderr.write(f"Error: {e}")
                time.sleep(2)

    def process_command(self, base_url, chat_id, text, bot_url):
        command_parts = text.split()
        if not command_parts:
            return
            
        command = command_parts[0].lower()
        
        if command == "/start":
            msg = (
                "👋 *მოგესალმები Zenith Admin\\!*\n\n"
                "მე ვარ შენი პერსონალური ასისტენტი\\. შეგიძლიათ დამელაპარაკოთ ჩვეულებრივ ენაზე ან გამოიყენოთ ბრძანებები:\n\n"
                "📅 /agenda \\- ჩემი უახლოესი შეხვედრები\n"
                "📊 /stats \\- საიტის სტატისტიკა\n"
                "📩 /latest \\- ბოლო შემოსული მესიჯები\n"
                "💼 /projects \\- Ჩემი Პროექტები"
            )
            self.send_message(base_url, chat_id, msg)
        
        elif command.startswith("/accept_"):
            try:
                appt_id = int(command.split("_")[1])
                appt = Appointment.objects.get(id=appt_id)
                appt.status = 'CONFIRMED'
                appt.save()
                self.send_message(base_url, chat_id, f"✅ *შეხვედრა დადასტურებულია*:\n{self.escape_md(appt.name)} \\- {self.escape_md(str(appt.date))} @ {self.escape_md(appt.time_slot)}")
            except:
                self.send_message(base_url, chat_id, "❌ შეხვედრა ვერ მოიძებნა ან ID არასწორია.")

        elif command.startswith("/reject_"):
            try:
                appt_id = int(command.split("_")[1])
                appt = Appointment.objects.get(id=appt_id)
                appt.status = 'REJECTED'
                appt.save()
                self.send_message(base_url, chat_id, f"❌ *შეხვედრა გაუქმებულია*:\n{self.escape_md(appt.name)} \\- დრო კვლავ განთავისუფლდა კალენდარში.")
            except:
                self.send_message(base_url, chat_id, "❌ შეხვედრა ვერ მოიძებნა ან ID არასწორია.")

        elif command == "/agenda":
            today = timezone.now().date()
            appts = Appointment.objects.filter(status='CONFIRMED', date__gte=today).order_by('date', 'time_slot')[:5]
            if not appts:
                self.send_message(base_url, chat_id, "😎 უახლოეს დღეებში დადასტურებული შეხვედრები არ გაქვს.")
                return
            msg = "📅 *შენი უახლოესი შეხვედრები:*\n\n"
            for a in appts:
                msg += f"🔸 *{self.escape_md(str(a.date))} @ {self.escape_md(a.time_slot)}*\n"
                msg += f"   👤 {self.escape_md(a.name)} \\({self.escape_md(a.email)}\\)\n\n"
            self.send_message(base_url, chat_id, msg)
            
        elif command == "/stats":
            total_bookings = Booking.objects.count()
            today_bookings = Booking.objects.filter(created_at__date=timezone.now().date()).count()
            total_projects = Project.objects.count()
            
            msg = (
                "📊 *სტატისტიკა:*\n\n"
                f"ჯამური შეტყობინებები: *{total_bookings}*\n"
                f"დღევანდელი შეტყობინებები: *{today_bookings}*\n"
                f"აქტიური პროექტები საიტზე: *{total_projects}*"
            )
            self.send_message(base_url, chat_id, msg)
            
        elif command == "/latest":
            bookings = Booking.objects.order_by('-created_at')[:3]
            if not bookings:
                self.send_message(base_url, chat_id, "📭 შეტყობინებები ჯერ არ არის.")
                return
                
            msg = "📩 *ბოლო შეტყობინებები:*\n\n"
            for b in bookings:
                msg += f"👤 *{self.escape_md(b.name)}*\n"
                msg += f"📧 {self.escape_md(b.email)}\n"
                msg += f"💬 _{self.escape_md(b.message[:50])}.._\n"
                msg += "\\-\\-\\-\\-\\-\\-\\-\\-\n"
                
            self.send_message(base_url, chat_id, msg)
            
        elif command == "/projects":
            projects = Project.objects.all()
            if not projects:
                self.send_message(base_url, chat_id, "პროექტები არ მოიძებნა.")
                return
                
            msg = "💼 *შენი პროექტები:*\n\n"
            for p in projects:
                msg += f"🔹 *{self.escape_md(p.title)}*\n"
            self.send_message(base_url, chat_id, msg)
            
        else:
            if self.client:
                # Use OpenAI for natural language response
                ai_response = self.get_ai_response(text)
                self.send_message(base_url, chat_id, ai_response)
            else:
                self.send_message(base_url, chat_id, "❓ ბრძანება არასწორია. სცადეთ /start")

    def get_ai_response(self, user_text):
        # Gather context
        projects = Project.objects.all()
        project_list = ", ".join([p.title for p in projects])
        
        bookings_count = Booking.objects.count()
        today_bookings = Booking.objects.filter(created_at__date=timezone.now().date()).count()
        
        upcoming_appts = Appointment.objects.filter(status='CONFIRMED', date__gte=timezone.now().date())[:5]
        appt_text = ""
        for a in upcoming_appts:
            appt_text += f"- {a.name} ({a.date} @ {a.time_slot})\n"

        system_prompt = (
            "შენ ხარ Zenith-ს ადმინისტრაციული ასისტენტი. შენი სახელია 'Zenith AI'. "
            "შენ პასუხობ საიტის მფლობელს (ადმინს) მაქსიმალურად ადამიანურ, მეგობრულ და ბუნებრივ ქართულ ენაზე. "
            "არ დაწერო რობოტივით. გამოიყენე ემოჯიები საჭიროებისამებრ. "
            "\n\nკონტექსტი საიტის შესახებ:\n"
            f"- საიტზე არის {projects.count()} პროექტი: {project_list}.\n"
            f"- სულ შემოსულია {bookings_count} შეტყობინება (დღეს: {today_bookings}).\n"
            f"- უახლოესი დადასტურებული შეხვედრები:\n{appt_text if appt_text else 'შეხვედრები არ არის'}\n"
            "\nთუ ადმინი გეკითხება სტატისტიკაზე, პროექტებზე ან გესაუბრება, უპასუხე ამ მონაცემებზე დაყრდნობით. "
            "თუ კითხვა აბსოლუტურად არ ეხება საქმეს, მაინც იყავი თავაზიანი ასისტენტი."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ AI პასუხის მიღებისას მოხდა შეცდომა: {str(e)}"

    def send_message(self, base_url, chat_id, text):
        # Automatically format response for MarkdownV2 if it looks like AI output (no explicit backslashes)
        # but if it has Markdown characters, we should be careful.
        # For simplicity, if it's AI, we send it as plain text unless we handle escaping.
        # Regular command responses use self.escape_md.
        
        # Check if text is probably already escaped or if it's from AI
        is_ai = "Zenith AI" in text or not "\\" in text
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2" if not is_ai else "" # MarkdownV2 is sensitive to unescaped chars
        }
        
        # If AI, sometimes it uses bold/italics. Let's try Markdown (not V2) for AI as it's more forgiving.
        if is_ai:
            payload["parse_mode"] = "Markdown"

        requests.post(f"{base_url}/sendMessage", json=payload)
        
    def escape_md(self, text):
        if not text:
             return ""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = str(text).replace(char, f"\\{char}")
        return text
