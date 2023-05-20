import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import csv
from flask import Flask,request,redirect,make_response
import sqlite3


app=Flask(__name__)


 

con=sqlite3.connect("db.db")
con.execute("CREATE TABLE IF NOT EXISTS accounts (ID INTEGER PRIMARY KEY AUTOINCREMENT , user_name VARCHAR(20),password VARCHAR(20),fname VARCHAR(20),lname VARCHAR(20), dob VARCHAR(12),email VARCHAR(30),ph INTEGER)")
con.commit()
con.close()

@app.route("/register", methods=['POST'])
def register():
    print(request.form)
    #Recieving the new member details from front-end    
    user_name=request.form.get('user_name')
    password=request.form.get('password')
    fname=request.form.get('fname')
    lname=request.form.get('lname')
    dob=request.form.get('dob')
    email=request.form.get('email')
    ph=request.form.get('ph')
    
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    cur.execute(f"INSERT INTO accounts (user_name,password,fname,lname,dob,email,ph) VALUES ('{user_name}','{password}','{fname}','{lname}','{dob}','{email}','{ph}')")
    con.commit()
    con.close()

    return redirect("http://localhost:4200/register",code=302)


@app.route("/user_name",methods=['POST'])
def user_name():

    username=request.json["username"]
    
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    cur.execute("SELECT user_name from accounts")
    op=cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM accounts;')
    count=cur.fetchall()[0][0]
    con.close()

    for i in range (count):
    
        if op[i][0]==username:
            return make_response("1",200)
    
    return make_response("0",202)


@app.route("/login",methods=['POST'])
def login():
    username=request.form.get("username")
    password=request.form.get("password")
    
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    cur.execute("SELECT user_name,password FROM accounts")
    op=cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM accounts")
    count=cur.fetchall()[0][0]
    con.close()
    
    for i in range(count):
    
        if op[i][0]==username and op[i][1]==password:
            return redirect("http://localhost:4200/pre")
    
    return redirect("http://localhost:4200/login")


@app.route("/predict",methods=['POST'])
def predict():
    
    json=request.json
    data=json['data']
    time=json['days']
    data=list(map(int,data.split(",")))

    
    actual = data.copy()
    X = np.array(data[:-1]).reshape(-1, 1)
    y = np.array(data[1:])
    predicted = []

    
    model = LinearRegression()
    model.fit(X, y)

    for i in range(time):
        temp = model.predict([[data[-1]]])[0]
        data.append(temp)
        predicted.append(temp)

    l1=len(actual)
    l2=len(predicted)
    ta=0
    tp=0
    if(l1>l2):
        ta=actual[:l2]
        tp=predicted
    else:
        ta=actual
        tp=predicted[:l1]
    mape = round(mean_absolute_percentage_error(ta, tp),3)
    mse = round(mean_squared_error(ta, tp),3)
    accuracy = 100 - mape

    with open("actual", 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(actual)

    with open("predicted", 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(predicted)

    return {'actual':data,'predicted':predicted,"mape":mape,"mse":mse,"accuracy":accuracy}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response



if(__name__=="__main__"):
    app.run(debug=True)