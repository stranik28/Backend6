from crypt import methods
from email import message
import email
from datetime import datetime
from secrets import choice
from turtle import title
from flask import render_template, Flask, request, redirect, url_for, flash, make_response
from flask_mysqldb import MySQL
import re
from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField, DateField, RadioField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired, Email, ValidationError


app = Flask(__name__)

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
        if not re.match(r"^\S*$", field.data):
            style={'style' : 'border : 2px solid red'}
            field.render_kw = style 
            raise ValidationError('You can use only non space letter')

    def validate_email(self, field):
        email = field.data
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            style={'style' : 'border : 2px solid red'}
            field.render_kw = style 
            raise ValidationError('Seems like u use invalid email address or use non English letters')


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('form'))

@app.route('/form', methods=['GET'])
def form():
    form = ContactForm()
    str = request.cookies.get('form_ok').split("|")
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
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO form VALUES (%s,%s,%s,%s,%s,%s,%s) ''', (name,email,birth_date,gender,limbs,bio,check))
        cursor.execute(''' INSERT INTO super VALUES(0,%s) ''', [sup])
        mysql.connection.commit()
        cursor.close()
        flash("Success send datas")
        cook = name + "|" + email + "|" + birth_date.strftime('%Y-%m-%d') + "|" + gender + "|" + limbs + "|" + sup + "|" + bio + "|" + str(check)
        res = make_response(redirect(url_for('form')))
        res.set_cookie('form_ok', cook , max_age=60*60*24*365)
        res.set_cookie('form_err', '0', max_age=0)
        return res
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


if __name__ == "__main__":
    app.run()