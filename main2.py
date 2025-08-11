# To run ngrok server, use the command: 'ngrok http 8007' keep it always running in a separate terminal. if it doesn't work, try: 'ngrok http <different port ex: 8001>'. Also change the port number value at the end of receive_whatsapp_message().
# Whenever you reopen vscode or restart ngrok server, follow the steps to use Chat Gulor in whatsapp:
# 1. Run ngrok server in a separate terminal.
# 2. Run this file.
# 3. Go to https://developers.facebook.com/apps/2128597717566467/whatsapp-business/wa-settings/?business_id=1052322746997515&phone_number_id= 
# 4. Add callback URL as: https://<ngrok_url>/webhook (the ngrok_url is seen from Forwarding row of ngrok terminal. It looks like: https://7472-2409-40f4-11e-c91c-256a-26ac-3339-7d50.ngrok-free.app/webhook)and verify token as: chat_gulor_token_verify
# 5. From this code, run the whatsapp_interface() and(or) discord_interface() only once(it works in the background using threads, listening for messages).
### TO DOs:


import os
from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.groq import Groq
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from telegram import Update
import datetime
from flask import Flask, request
import asyncio
import threading
import random
import requests
from telegram.constants import ChatAction
import discord
from discord.ext import commands


from dotenv import load_dotenv
import time

import imaplib
import email
import smtplib

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')   
META_VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')




global email_address
email_address = "abcd@gmail.com"
global password
password = "your app password from gmail"



memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
memory = Memory(db=memory_db)

def llm_agent(query):
    resp=Agent(
        model=Groq("meta-llama/llama-4-scout-17b-16e-instruct"),
        memory=memory,
        enable_agentic_memory=True,
        enable_user_memories=True,
        add_history_to_messages=True,
        storage=SqliteStorage(table_name="storage", db_file="tmp/storage.db"),
        search_previous_sessions_history=True,
        num_history_sessions=5,
        tools=[DuckDuckGoTools()],
        instructions="""You are not an Assistant. You are pretending as Gulor to reply to his messages. 
            You will receive a query containing the content of a message and the date it was sent. Each query will specify whether the message is an email or a telegram message or a whatsapp message or a discord message. The message content will be enclosed within a <message> tag, and the sent date and time will be within a <sent_date> tag. Occasionally, you may also encounter a <system> SYSTEM message. These SYSTEM messages originate from the system itself and are not sent by <Your Name>. When you receive a SYSTEM message, you should initiate the conversation, as you are expected to start the interaction in such cases. You may start with a 'Hi' or ask about a pending task that he has or ask for a doubt. Do not state that u r replying to system message.
            Your role is to reply to messages from <YourName> in a professional manner, representing Gulor. You may use the sent date to make your replies more contextually relevant. Additionally, you can draw upon your own memory and knowledge to enhance the relevance and quality of your responses. If the message is an email, reply only to the email body without creating or including a subject line. If the input is a regular message, respond accordingly, keeping the reply concise and appropriate for the medium. Always address your replies to <Your Name>, as he is the recipient.
            You are replying on behalf of Gulor. Here is some background information about Gulor: Gulor is a 24-year-old entrepreneur who runs an automation agency with three employees, all of whom are his friends. He is the Founder and CEO of Bonn AI Solutions. Gulor is known for being friendly and enjoys helping people. He is a seasoned professional in automation and web development, working primarily online from his home in Bangalore, India. Prior to founding his agency, Gulor had worked as a freelancer, taking on projects as a video editor and web developer for various clients.
            You are also provided with detailed information about <Your Name>, the person you are replying to. <Your Name> was born on <Birthday> and is based in <city> India. He is currently a <Profession>. <Your Name>’s interests include <Interests>. <Your strengths, weakness>. <Your Experiences>. <Your aspirations and future goals>.
            <Your Name> prefers mentorship that is candid and realistic, seeking feedback as if from a 45-year-old experienced mentor. He values hard-hitting, critical, and real-world guidance, with examples of potential pitfalls and advice on profitability. He is also dealing with feeling overwhelmed by excessive content consumption.
            When crafting your replies, ensure they sound natural and human, as if you are having a friendly conversation with <Your Name>. You may use internet resources to provide information if needed. Do not mention anything about updating memory or similar actions. If the message is a regular message, keep your reply brief and direct. If <Your Name> asks for advice or has a doubt, you may elaborate using your own experiences, but limit your response to a maximum of two paragraphs. Make your replies sound like you are talking to a friend in Indian English. Avoid using text formatting such as bold or italics, and do not use symbols like asterisks or underscores for formatting. Do not use phrases such as "How can I help you today?", "How can I assist you?", or "I am an AI Assistant." Minimize the use of emojis. Simulate a real human conversation and always reply in English. If replying to an email, maintain a professional yet friendly tone in your response to the email body. Be very concise if its a whatsapp or telegram message.
            """,
        add_state_in_messages=True,
        markdown=True,
        ).run(query)
    return resp.content






###INTERFACES:
#1. MAIL:

def mail_interface(israndom=0):
    global ranexit
    ranexit=None

    def send_mail(content):
        global ranexit
        if ranexit:
            print("Randomly Exiting...")
            return None
        print("Sending mail...")
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_address, password)
        s.sendmail(from_addr=email_address, to_addrs="abcd2@gmail.com", msg=content)
        s.quit()

        receive_mail()

    def receive_mail():
        global ranexit
        if ranexit:
            print("Randomly Exiting...")
            return None
        print("Receiving mail...")
        imap_server = "imap.gmail.com"
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(email_address, password)
        imap.select('inbox')
        _, msgnums = imap.search(None, '(UNSEEN FROM "abcd2@gmail.com")') 

        msgnum_list = msgnums[0].split()
        if len(msgnum_list) == 0:
            print("No new mail to process.")
            print()
            return
        _, data = imap.fetch(msgnum_list[0], "(RFC822)")
        message = email.message_from_bytes(data[0][1])
        ran=random.randint(0,8)
        if ran==0:
            ranexit=1
            return None
        print("Processing new mail...")
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                query=f"This is a mail. The mail content is: <message>{part.as_string().split('Content-Type: text/plain; charset="UTF-8"')[-1].split('Content-Type: text/html; charset="UTF-8"')[0].strip()} </message> The sent date is: <sent_date> {message['Date']} </sent_date>"
                response = llm_agent("Generate reply for this mail: "+str(query))

                send_mail(response)

        imap.close()
    if ranexit:
        print("Randomly Exiting...")
        return None
    if israndom:
        respp=llm_agent("<system>I am the SYSTEM, mailing you right now. Reply with some mail text maybe a 'Hi' or any update on pending tasks or ask any suggestion or doubt to <Your Name>. Do not include any other data about the system in the output you send. This mail is not sent by <Your Name>. It is sent by SYSTEM.</system>")
        send_mail(respp)
    else:
        receive_mail()





#TELEGRAM INTERFACE:

def telegram_interface(israndom=0):
    import requests
    import datetime
    print("Inside Telegram Interface")
    global last_telegram_update_id
    try:
        if israndom:
            resp = llm_agent("<system>I am the SYSTEM, messaging you right now. Reply with some message text maybe a 'Hi' or any update on pending tasks or ask any suggestion or doubt to <Your Name>. Do not include any other data about the system in the output you send. This message is not sent by <Your Name>. It is sent by SYSTEM.</system>")
            url = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage"
            payload = {
                "chat_id": 5687352159,
                "text": str(resp)
            }
            requests.post(url, data=payload)
            return

        # Use global to persist last update id between calls
        if 'last_telegram_update_id' not in globals():
            last_telegram_update_id = None
        get_updates_url = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/getUpdates"
        params = {"timeout": 10}
        if last_telegram_update_id:
            params["offset"] = last_telegram_update_id + 1
        response = requests.get(get_updates_url, params=params)
        data = response.json()
        messages = data.get("result", [])
        if not messages:
            print("No new message received")
            return
        # Find the most recent message
        for update in messages:
            if "message" in update:
                user_message = update["message"].get("text")
                chat_id = update["message"]["chat"].get("id")
                last_telegram_update_id = update["update_id"]
                if user_message and chat_id:
                    agent_response = llm_agent(f"This is a telegram message not a mail. The message is: <telegram_message> {user_message} </telegram_message> <sent_date> {datetime.datetime.now()} </sent_date>")
                    send_url = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage"
                    payload = {"chat_id": chat_id, "text": agent_response}
                    requests.post(send_url, data=payload)
                    print(f"Sent reply to Telegram user: {chat_id}")
        return
    except Exception as e:
        print(f"Telegram interface error: {e}")
        return






#WHATSAPP INTERFACE:
# To run ngrok server, use the command: 'ngrok http 8000' keep it always running in a separate terminal. if it doesn't work, try: 'ngrok http <different port ex: 8001>'

def whatsapp_interface():
    print("Inside Whatsapp Interface")
    ranexit=None
    def send_whatsapp_message(query, phone_number_id, user_phone_number, access_token):
        if ranexit:
            print("Randomly Exiting...")
            return None
        print("Sending Whatsapp Message...")
        print()
        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        ai_response = llm_agent(f"This is a whatsapp message not a mail. The message is: <whatsapp_message> {query} </whatsapp_message> <sent_date> {datetime.datetime.now()} </sent_date>")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": user_phone_number,
            "type": "text",
            "text": {"body": ai_response}
        }
        response = requests.post(url, json=payload, headers=headers)
        return response
    

    def receive_whatsapp_message():
        if ranexit:
            print("Randomly Exiting...")
            return None
        from flask import Flask, request

        app = Flask(__name__)
        def run_flask_app():
            app.run(host="0.0.0.0", port=8007)

        @app.route('/webhook', methods=['GET', 'POST'])
        def webhook():
            if request.method == 'GET':
                mode = request.args.get('hub.mode')
                token = request.args.get('hub.verify_token')
                challenge = request.args.get('hub.challenge')
                if mode == 'subscribe' and token == "chat_gulor_token_verify":
                    return challenge, 200
                else:
                    return "Verification token mismatch", 403
            if request.method == 'POST':
                data = request.get_json()
                try:
                    entry = data.get('entry', [])[0]
                    changes = entry.get('changes', [])[0]
                    value = changes.get('value', {})
                    messages = value.get('messages')

                    if messages:
                        ran=random.randint(0,9)
                        if ran==0:
                            ranexit=1
                            return None
                        message = messages[0]
                        sender = message.get('from')
                        print("SENDER: ", sender)
                        text = message.get('text', {}).get('body')
                        print("New Whatsapp Message Received...")

                        send_whatsapp_message(text, "yournumber", sender, WHATSAPP_ACCESS_TOKEN)

                except Exception as e:
                    pass
                return "OK", 200
            
        thread = threading.Thread(target=run_flask_app)
        thread.daemon = True 
        thread.start()

    if ranexit:
        print("Randomly Exiting...")
        return None
    else:
        receive_whatsapp_message()



    



# Discord interface:

def discord_interface():
    print("Inside Discord Interface")

    intents = discord.Intents.default()
    intents.message_content = True  # Required for reading message content
    client = discord.Client(intents=intents)

    def run_discord_bot():
        client.run(DISCORD_BOT_TOKEN)


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        print("New Discord messsage received...")
        user_message = message.content

        # Call llm_response on the received message
        ai_resp = llm_agent(f"This is a discord message not a mail. The message is: <discord_message> {user_message} </discord_message> <sent_date> {datetime.datetime.now()} </sent_date>")
        
        print("Sending New Discord message...\n")
        await message.channel.send(ai_resp)

            

    thread = threading.Thread(target=run_discord_bot)
    thread.daemon = True  # Allows the main program to exit even if the thread is running
    thread.start()
    print("Discord bot started in a separate thread.")

    ran = random.randint(0, 10)
    if ran == 0:
        return None






def randomly_message():
    ch=random.randint(1,2)
    print("\nCH: ",ch,'\n')
    if ch==1:
        mail_interface(ch)
        print("Randomly Sent Mail!")
    elif ch==2:
        telegram_interface(ch)
        print("Randomly Sent Message!")





whatsapp_interface()
discord_interface()
while True:
    mail_interface()
    print("Mail Interface Done!")
    telegram_interface()
    print("Telegram Interface Done!")
    time.sleep(900)
    randomly_message()
