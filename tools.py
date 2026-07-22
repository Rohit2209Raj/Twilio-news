from crewai.tools import BaseTool
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

load_dotenv()

class WhatsAppSenderTool(BaseTool):
    name: str = "WhatsApp Sender"
    description: str = "Sends message to WhatsApp via Twilio"


    def _run(self,message:str)->str:
        try:
            if not message or message.strip():
                raise ValueError("Message cannot be empty")

            required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'MY_WHATSAPP_NUMBER']
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Missing environment variables: {missing}")

            client=Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            formatted_msg=f'''
            📊 *News Update*
                {'='*30}
                {message}
                {'='*30}
                🕒 {datetime.now().strftime('%I:%M %p, %d %b')}
                🤖 AI News Assistant
                            """.strip()
                '''

            msg=client.message.create(
                from_="whatsapp:+14155238886",
                body=formatted_msg,
                to=f"whatsapp:{os.getenv('MY_WHATSAPP_NUMBER')}"
            )
            return f"✅ Message sent! SID: {msg.sid}"

        except TwilioRestException as e:
            error_msg = f"Twilio Error: {str(e)}"
            print(error_msg)
            return f"❌ {error_msg}"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return f"❌ {error_msg}"