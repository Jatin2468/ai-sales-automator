from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key="YOUR_GEMINI_API_KEY")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), email: str = Form(...)):

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)

    total_revenue = df["Revenue"].sum()
    best_region = df.groupby("Region")["Revenue"].sum().idxmax()
    cancelled_orders = df[df["Status"]=="Cancelled"].shape[0]

    prompt = f"""
    Analyze this sales dataset and give short executive summary.

    Total Revenue: {total_revenue}
    Best Region: {best_region}
    Cancelled Orders: {cancelled_orders}
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    summary = response.text

    msg = MIMEText(summary)
    msg["Subject"] = "AI Sales Report"
    msg["From"] = "YOUR_GMAIL"
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login("YOUR_GMAIL","YOUR_APP_PASSWORD")
    server.send_message(msg)
    server.quit()

    return {"message":"Summary Sent Successfully"}