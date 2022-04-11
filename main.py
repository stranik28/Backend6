from flask import render_template, Flask, request
from flask_mysqldb import MySQL
import datetime


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'u47473'
app.config['MYSQL_PASSWORD'] = 'n8848569'
app.config['MYSQL_DB'] = 'u47473'
mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post():
    name = request.form.get('field-name')
    if name == "":
        return render_template('index.html', message = "You forgot to fill name space")
    email = request.form.get('field-email')
    if email == "":
        return render_template('index.html', message = "You forgot to fill email space")
    birth_date = request.form.get('field-date')
    if birth_date == "":
        return render_template('index.html', message = "You forgot to fill birth_date space")
    gender = request.form.get('radio1')
    if gender == None:
        return render_template('index.html', message = "You forgot to fill gender space")
    limbs = request.form.get('radio2')
    if limbs == None:
        return render_template('index.html', message = "You forgot to fill limbs space")
    superpowers = ""
    superpowers = superpowers.join(request.form.getlist('superpowers[]'))
    if superpowers == "":
        return render_template('index.html', message = "You forgot to fill superpowers space")
    bio = request.form.get("bio")
    if bio == "Пишите здесь":
        return render_template('index.html', message = "You forgot to fill bio space")
    check = request.form.get('check-1')
    if check == 0:
        return render_template('index.html', message = "You forgot to click on checkbox")
    birth_date = datetime.datetime.strptime(birth_date, "%Y-%d-%m")
    
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO form VALUES (%s,%s,%s,%s,%s,%s,%s) ''', (name,email,birth_date,gender,limbs,bio,check))
    cursor.execute(''' INSERT INTO super VALUES(0,%s) ''', (superpowers,))
    print("Ok")
    mysql.connection.commit()
    print("Ok")
    cursor.close()
    return render_template('index.html', message = "Ok")


if __name__ == "__main__":
    app.run()