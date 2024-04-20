from flask import Flask, render_template, request
import re
from datetime import datetime, timedelta
from flask_babel import Babel
import requests
import smtplib
import os


app = Flask(__name__)
babel = Babel(app)


@app.route("/")
def home():
    return render_template("home.html")

# New functions
@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/sucess/")
def sucess():
    return render_template("sucess.html")

##### FLASK-BABEL use instead for strftime
## python -m flask run

@app.route('/send_shift_reminder', methods=['GET', 'POST'])
def send_shift_reminder():
    if request.method == 'POST':
        # sets up today and tomorrow's date
        today_date = datetime.today().date()
        tomorrow = today_date + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%-m/%-d/%Y")

        # list of all the shifts tomorrow
        shifts_for_tomorrow = []

        # sheety API
        sheety_endpoint = "https://api.sheety.co/643f139aa2473d2a0881c4056fafdfd8/shiftManager/sheet1"
        response = requests.get(sheety_endpoint)
        data = response.json()

        # checks for any shifts for tomorrow and adds it to a list
        for row in data["sheet1"]:
            if row["date"] == tomorrow_date:
                shifts_for_tomorrow.append(row)
        
        if shifts_for_tomorrow:
            # setting up email
            my_email = os.environ.get("email")
            password = os.environ.get("email_password")

            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                for entry in shifts_for_tomorrow:
                    connection.sendmail(
                        from_addr=my_email,
                        to_addrs=entry["email"],
                        msg=f"Subject: Shift Reminder\n\nHey {entry['employee']}! You have a shift tomorrow ({entry['date']}) at {entry['startTime']} to {entry['endTime']}"
                    )
        
        return sucess()
    else:
        return "Use a POST request to trigger the shift reminder."
    

if __name__ == '__main__':
    app.run(debug=True)
