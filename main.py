import os
import requests
from bs4 import BeautifulSoup
import datetime
import uuid
from ics import Calendar, Event
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Replace with the URL of the website you want to scrape
url = "https://www.urdupoint.com/islam/shia/london-prayer-timings.html"

# Make a request to the website and parse the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find the table containing the prayer times
table = soup.find("table", {"class": "main_timings_table"})

# Create a dictionary to store the prayer times
prayer_times = {}

# Loop through the rows of the table and extract the prayer times
headers = table.find_all("th")
for i, row in enumerate(table.find_all("tr")):
    columns = row.find_all("td")
    prayer_time = columns[0].text.strip()
    prayer_times[headers[i].text.strip()] = prayer_time

# Extract the Fajar, Zuhr, Asr, Maghrib, and Isha times from the dictionary
fajar_time = prayer_times["Fajar"]
zuhr_time = prayer_times["Zuhr"]
asr_time = prayer_times["Asr"]
maghrib_time = prayer_times["Maghrib"]
isha_time = prayer_times["Isha"]

# Create a new calendar event for each prayer time
calendar = Calendar()
for prayer_name, prayer_time in prayer_times.items():
    start_time = datetime.datetime.strptime(prayer_time, "%H:%M")
    end_time = start_time + datetime.timedelta(minutes=60)
    event = Event()
    event.uid = str(uuid.uuid4())
    event.name = f"Prayer Time - {prayer_name}"
    event.begin = start_time
    event.end = end_time
    calendar.events.add(event)

# Convert the calendar to a string
cal_str = str(calendar)

# Replace these variables with your own information
from_address = os.environ['FROM_ADDRESS']
password = os.environ['FROM_PASSWORD']
to_address = os.environ['TO_ADDRESS']
subject = "Prayer Times"
body = "Please find the prayer times below."

# Create a multipart message
msg = MIMEMultipart()
msg["From"] = from_address
msg["To"] = to_address
msg["Subject"] = subject

# Attach the calendar event to the message
part = MIMEApplication(cal_str, Name="event.ics")
part['Content-Disposition'] = f'attachment; filename="event.ics"'
msg.attach(part)

# Add the body text to the message
msg.attach(MIMEText(body))

# Connect to the SMTP server and send the email
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(from_address, password)
    smtp.sendmail(from_address, to_address, msg.as_string())
