from flask import Flask,url_for,render_template,redirect,request,session
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField
import pickle
import numpy as np

app=Flask(__name__)

app.secret_key="my-secret-key"
model=pickle.load(open("randomforest.pkl","rb"))
scaler=pickle.load(open("scaler.pkl","rb"))

users={"nick": "1234"}

class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("password",validators=[DataRequired()])
    submit=SubmitField("Login")

@app.route('/')
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("home.html",username=session["user"])

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        if username in users and users[username]==password:
            session['user']=username
            return redirect("/")
        else:
            return render_template("login.html",form=form)
    return render_template("login.html",form=form)

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/login')

@app.route('/predict',methods=["POST"])
def predict():
    ocean=request.form['ocean_proximity']

    ocean_1H_OCEAN=0
    ocean_INLAND=0
    ocean_ISLAND=0
    ocean_NEAR_BAY=0
    ocean_NEAR_OCEAN=0

    if ocean=="ONE_HOUR":
        ocean_1H_OCEAN=1
    elif ocean=="INLAND":
        ocean_INLAND=1
    elif ocean=="ISLAND":
        ocean_ISLAND=1
    elif ocean=="NEAR_BAY":
        ocean_NEAR_BAY=1
    elif ocean=="NEAR_OCEAN":
        ocean_NEAR_OCEAN=1

    data=[
        float(request.form['longitude']),
        float(request.form['latitude']),
        float(request.form['housing_median_age']),
        float(request.form['total_rooms']),
        float(request.form['total_bedrooms']),
        float(request.form['population']),
        float(request.form['households']),
        float(request.form['median_income']),
        ocean_1H_OCEAN,ocean_INLAND,ocean_ISLAND,ocean_NEAR_BAY,ocean_NEAR_OCEAN
    ]
    final_data=np.array([data])

    final_data=scaler.transform(final_data)
    prediction=model.predict(final_data)

    return render_template("home.html",result=round(prediction[0],2))

if __name__=="__main__":
    app.run(debug=True)