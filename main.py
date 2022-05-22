from crypt import methods
import email
from datetime import datetime
from secrets import choice
from turtle import title
from flask import render_template, Flask, request, redirect, url_for, flash, make_response, session
from flask_mysqldb import MySQL
import re
from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField, DateField, RadioField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired, Email, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from flask_httpauth import HTTPBasicAuth
import pandas as pd


app = Flask(__name__)
auth = HTTPBasicAuth()

app.config.from_object('config')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'u47473'
app.config['MYSQL_PASSWORD'] = 'n8848569'
app.config['MYSQL_DB'] = 'u47473'
mysql = MySQL(app)



class ContactForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired(message="You forgot to fill data")])
    email = StringField("Email: ", validators=[Email(), DataRequired()])
    birth_date = DateField('Birth date', format='%Y-%m-%d',validators=[DataRequired()])
    gender = RadioField('Your gender',choices=[('1','man'),('2','woman')],validators=[DataRequired()], widget=widgets.TableWidget(with_table_tag=True))
    limbs = RadioField('Number of your limbs', choices = [('1','1'),('2','2'),('3','3'),('4','4')],validators=[DataRequired()], widget=widgets.TableWidget(with_table_tag=True))
    superpowers = SelectMultipleField('Your superpowers', choices=[('1', 'immortality'), ('2','passing through walls'), ('3','levitation')],validators=[DataRequired()])
    bio = TextAreaField("Your bio ",validators=[DataRequired()])
    check = BooleanField('familiarized with the contract', validators = [DataRequired(True)])
    submit = SubmitField()

    def validate_name(self, field):
        if not re.match(r"^[A-Za-z0-9]*$", field.data):
            style={'style' : 'border : 2px solid red'}
            field.render_kw = style 
            raise ValidationError('You can use only non space letter')

    def validate_email(self, field):
        email = field.data
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            style={'style' : 'border : 2px solid red'}
            field.render_kw = style 
            raise ValidationError('Seems like u use invalid email address or use non English letters') 

    def validate_bio(self, field):
        if not re.match(r'''[^'"<>]*$''', field.data):
            style={'style' : 'border : 2px solid red'}
            field.render_kw = style 
            raise ValidationError('''You cannot use quotes and scripts''')




@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('form'))

@app.route('/form', methods=['GET'])
def form():
    form = ContactForm()
    str = request.cookies.get('form_ok')
    if str is None:
        str = ["","","2000-12-31","","","",""]
    else:
        str = str.split("|")
    g = []
    for i in str[5]:
        g.append(i)
    form.name.data = str[0]
    form.email.data = str[1]
    form.birth_date.data = datetime.strptime(str[2], '%Y-%m-%d')
    form.gender.data = str[3]
    form.limbs.data = str[4]
    form.superpowers.data = g
    form.bio.data = str[6]
    return render_template('index.html', form = form)


@app.route('/form', methods=['POST'])
def post():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        birth_date = form.birth_date.data
        gender = form.gender.data
        limbs = form.gender.data
        superpowers= form.superpowers.data
        sup = ''.join(superpowers)
        bio = form.bio.data
        check = form.check.data
        if 'user' in session:
            cursor = mysql.connection.cursor()
            cursor.execute(''' SELECT id FROM users WHERE login = %s ;''', [session['user']])
            s = cursor.fetchall()
            print(s)
            cursor.execute(''' UPDATE form SET name = %s , email = %s , birth= %s , gender = %s , limbs = %s, bio = %s , box = %s
            WHERE id = %s ;''', (name,email,birth_date,gender,limbs,bio,check,s[0][0]))
            cursor.connection.commit()
            cursor.execute(''' UPDATE super SET super_name = %s WHERE id =  %s; ''', (sup,s[0][0]))
            cursor.close()
            flash("Success write")
            cook = name + "|" + email + "|" + birth_date.strftime('%Y-%m-%d') + "|" + gender + "|" + limbs + "|" + sup + "|" + bio + "|" + str(check)
            res = make_response(redirect(url_for('form')))
            res = make_response(redirect(url_for('form')))
            res.set_cookie('form_ok', cook , max_age=60*60*24*365)
            res.set_cookie('form_err', '0', max_age=0)
        else:
            cursor = mysql.connection.cursor()
            cursor.execute(''' INSERT INTO form VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ''', (0,name,email,birth_date,gender,limbs,bio,check))
            cursor.execute(''' INSERT INTO super VALUES(0,%s) ''', [sup])
            mysql.connection.commit()
            cursor.close()
            cook = name + "|" + email + "|" + birth_date.strftime('%Y-%m-%d') + "|" + gender + "|" + limbs + "|" + sup + "|" + bio + "|" + str(check)
            res = make_response(redirect(url_for('form')))
            res.set_cookie('form_ok', cook , max_age=60*60*24*365)
            res.set_cookie('form_err', '0', max_age=0)
            N = 7
            allowedChars = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(allowedChars) for _ in range(N))
            allowedChars = string.ascii_letters
            login = ''.join(random.choice(allowedChars) for _ in range(N))
            flash("Your login is: " + login + " and password is: " + password)
            hash = generate_password_hash(password)
            print(hash)
            cursor = mysql.connection.cursor()
            cursor.execute(''' SELECT MAX(id) FROM form; ''')
            s = cursor.fetchall()
            cursor.close()
            cursor = mysql.connection.cursor()
            cursor.execute(''' INSERT INTO users VALUES (%s,%s,%s,%s) ''', (0,login,hash,s[0][0]))
            cursor.connection.commit()
            cursor.close()
    else:
        name = form.name.data
        email = form.email.data
        birth_date = form.birth_date.data
        gender = form.gender.data
        limbs = form.gender.data
        superpowers= form.superpowers.data
        sup = ''.join(superpowers)
        bio = form.bio.data
        check = form.check.data
        flash("An error while sending datas")
        print(sup)
        res = make_response(render_template('index.html', form = form))
        cook = name + "|" + email + "|" + birth_date.strftime('%Y-%m-%d') + "|" + gender + "|" + limbs + "|" + sup + "|" + bio + "|" + str(check)
        res.set_cookie('form_err', cook)
    return res

@app.route('/login', methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def logIn():
    username = request.form.get("login")
    password = request.form.get("password")
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM users WHERE login = %s ''', [username]);
    datas = cursor.fetchall();
    cursor.close()
    print(datas)
    print(len(datas))
    if len(datas) == 0:
        res = render_template("login.html")
        flash("Wrong login/pass")
    elif check_password_hash(datas[0][2],password):
        print("ses")
        session['user'] = username
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM form WHERE id = %s ''', [datas[0][3]])
        datas = cursor.fetchall()
        cursor.close()
        name = datas[0][1]
        birth_date = datas[0][3]
        gender = datas[0][4]
        limbs = datas[0][5]
        bio = datas[0][6]
        check = datas[0][7]
        email = datas[0][2]
        sup = "13"
        cook = name + "|" + email + "|" + str(birth_date) + "|" + str(gender) + "|" + str(limbs) + "|" + str(sup) + "|" + str(bio) + "|" + str(check)
        res = redirect(url_for("form"))
        res.set_cookie('form_ok',cook)
        flash("Ok")
    else:
        res = render_template("login.html")
        flash("Wrong login/pass")
    return res



@auth.verify_password
def verify_password(username, password):
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT password FROM admins WHERE login = %s ; ''', [username])
    password_new = cursor.fetchall()
    cursor.close()
    # print(password_new)
    if check_password_hash(password_new[0][0],password):
        return username
    

@app.route('/rest-auth', methods=["GET"])
@auth.login_required
def get_response():
    print("GET")
    name = []
    email = []
    datas = []
    limbs = []
    gender = []
    bio = []
    id = []
    supe = []
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM form; ''')
    s = cursor.fetchall()
    cursor.execute(''' SELECT * FROM super; ''')
    s2 = cursor.fetchall()
    cursor.close()
    t1 = 0
    t2 = 0
    t3 = 0
    for i in range(0,len(s)):
        id.append(s[i][0])
        name.append(s[i][1])
        email.append(s[i][2])
        datas.append(s[i][3])
        gender.append(s[i][4])
        limbs.append(s[i][5])
        bio.append(s[i][6])
        supe.append(s2[i][1])
        buf = int(s2[i][1])
        while buf >= 1:
            h = buf % 10
            if h == 1:
                t1 +=1
            elif h == 2:
                t2 +=1
            elif h == 3:
                t3 +=1
            buf //= 10
    df = pd.DataFrame({
        'id' : id,
        'name': name,
        'email': email,
        'data':datas,
        'gender':gender,
        'limbs':limbs,
        'bio':bio,
        'super' : supe
    })
    return render_template("admin.html", tables=[df.to_html(classes='data')], titles=df.columns.values, immortal = t1, wall = t2, levitation = t3)

@app.route('/rest-auth', methods=["post"])
@auth.login_required
def del_user():
    id = int(request.form.get("id_del"))
    cursor = mysql.connection.cursor()
    cursor.execute(''' DELETE FROM form WHERE id = %s ; ''', [id])
    cursor.connection.commit()
    cursor.execute(''' DELETE FROM super WHERE id = %s ;''', [id])
    cursor.connection.commit()
    cursor.close()
    name = []
    email = []
    datas = []
    limbs = []
    gender = []
    bio = []
    id = []
    supe = []
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM form; ''')
    s = cursor.fetchall()
    cursor.execute(''' SELECT * FROM super; ''')
    s2 = cursor.fetchall()
    cursor.close()
    t1 = 0
    t2 = 0
    t3 = 0
    for i in range(0,len(s)):
        id.append(s[i][0])
        name.append(s[i][1])
        email.append(s[i][2])
        datas.append(s[i][3])
        gender.append(s[i][4])
        limbs.append(s[i][5])
        bio.append(s[i][6])
        supe.append(s2[i][1])
        buf = int(s2[i][1])
        while buf >= 1:
            h = buf % 10
            if h == 1:
                t1 +=1
            elif h == 2:
                t2 +=1
            elif h == 3:
                t3 +=1
            buf //= 10
    df = pd.DataFrame({
        'id' : id,
        'name': name,
        'email': email,
        'data':datas,
        'gender':gender,
        'limbs':limbs,
        'bio':bio,
        'super' : supe
    })
    return render_template("admin.html", tables=[df.to_html(classes='data')], titles=df.columns.values, immortal = t1, wall = t2, levitation = t3)

@app.route('/add-admin', methods=['GET'])
@auth.login_required
def get_admins():
    return render_template('admin_add.html')

@app.route('/add-admin', methods=["post"])
@auth.login_required
def add_admins():
    login = request.form.get("login")
    password = request.form.get("password")
    hash = generate_password_hash(password)
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO admins VALUES (%s,%s,%s) ''', (0,login, hash))
    cursor.connection.commit()
    cursor.close()
    print("Ok")
    return redirect(url_for("add_admins"))


if __name__ == "__main__":
    app.run()