################################

# basic banking system
# dummy data of 10 customers (name,email,current balance)
# Home page,View customers page,select and view once customers page
# transer money page for one customer to another

################################

from flask import Flask, render_template, request, redirect, flash, session, url_for
from flaskext.mysql import MySQL
import uuid
import datetime

app = Flask(__name__)  # creating the Flask class object
app.config['SECRET_KEY'] = 'IMS'

# sql configuration
mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'saket2315'
app.config["MYSQL_DATABASE_DB"] = 'sample_bank'
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
mysql.init_app(app)

# # db connection active
conn = mysql.connect()
cur = conn.cursor()

###################################

# app functions


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/allcustomers', methods=['GET'])
def allCustomers():
    if request.method == 'GET':
        cur.execute(
            "SELECT * FROM `users` ")
        users = cur.fetchall()
        link = '/allcustomers/1421'
    return render_template('ViewCustomers.html', userList=users, link=link)


@app.route('/allcustomers/<id>', methods=['GET'])
def detailedCustomer(id):
    # getting info of selected customer
    cur.execute(
        "SELECT * FROM `users` WHERE `user_id` = '" + id + "'")
    userData = cur.fetchone()
    # getting transaction info
    cur.execute(
        "SELECT * FROM `transcations` WHERE `sender_id` = '" + id + "'")
    debitedBy = cur.fetchall()

    cur.execute(
        "SELECT * FROM `transcations` WHERE `receiver_id` = '" + id + "'")
    creditedBy = cur.fetchall()

    return render_template('detailedCustomer.html', userData=userData, arr1=debitedBy, arr2=creditedBy)


@app.route('/transferList', methods=['GET', 'POST'])
def transferMoney():
    if request.method == "POST":
        try:
            # getting user data
            # genrates a unique bill id
            myuuid = uuid.uuid4()
            str1 = str(myuuid)
            t_id = str1[:10]
            s_id = request.form['sender_id']
            r_id = request.form['receiver_id']
            amount = float(request.form['amount'])
            x = datetime.datetime.now()
            date = x.strftime("%x")

            # print(user_name, s_id, r_id, amount)

            # getting old balance of sender and receiver
            # for sender
            cur.execute(
                "SELECT balance FROM `users` WHERE `user_id` = '" + s_id + "'")
            senderOldBalance = cur.fetchone()
            # for receiver
            cur.execute(
                "SELECT balance FROM `users` WHERE `user_id` = '" + r_id + "'")
            receiverOldBalance = cur.fetchone()

            # adding money
            newamount = float(receiverOldBalance[0])+amount
            cur.execute("UPDATE `users` SET `balance`= '" + str(newamount) + "' WHERE `user_id`= '" +
                        r_id + "'")
            conn.commit()
            # deducing money
            senderNewBalance = float(senderOldBalance[0])-amount
            cur.execute("UPDATE `users` SET `balance`= '" + str(senderNewBalance) + "' WHERE `user_id`= '" +
                        s_id + "'")
            conn.commit()

            # storing the transaction record
            cur.execute("INSERT INTO `transcations`(`id`,`sender_id`,`receiver_id`,`amount`,`date`) VALUES (%s,"
                        "%s,%s,%s,%s)", (t_id, s_id, r_id, amount, date))
            conn.commit()
            # sending message to ui
            flash("Transcation Successfull !")

        except:
            flash("Transcation Unsuccessfull !")

    return render_template('transferMoney.html')


app.run(debug=True)
