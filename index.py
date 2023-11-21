from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345@localhost/crud_flask"
db = SQLAlchemy(app)

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    group = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=200)])
    submit = SubmitField("Save")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=12)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    group = SelectField("Group", coerce=int)
    submit = SubmitField("Save")

@app.route("/groups")
def groups():
    groups = Groups.query.all()
    return render_template("groups.html", groups=groups)

@app.route("/groups/new", methods=["GET", "POST"])
def new_group():
    form = GroupForm()
    message = ""
    if form.validate_on_submit():
        group = Groups(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        message = "Group saved successfully"
        return redirect(url_for("groups"))
    return render_template("new_group.html", form=form, message=message)

@app.route("/groups/edit/<int:id>", methods=["GET", "POST"])
def edit_group(id):
    group = Groups.query.get_or_404(id)
    form = GroupForm()
    message = ""
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.commit()
        message = "Group updated successfully"
        return redirect(url_for("groups"))
    elif request.method == "GET":
        form.name.data = group.name
    return render_template("edit_group.html", form=form, id=id, message=message)

@app.route("/groups/delete/<int:id>")
def delete_group(id):
    group = Groups.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    return redirect(url_for("groups"))

@app.route("/contacts")
def contacts():
    contacts = Contacts.query.all()
    return render_template("contacts.html", contacts=contacts)

@app.route("/contacts/new", methods=["GET", "POST"])
def new_contact():
    form = ContactForm()
    message = ""
    form.group.choices = [(g.id, g.name) for g in Groups.query.order_by('name')]
    if form.validate_on_submit():
        contact = Contacts(name=form.name.data, phone=form.phone.data, email=form.email.data, group =form.group.data)
        db.session.add(contact)
        db.session.commit()
        message = "Contact saved successfully"
        return redirect(url_for("contacts"))
    return render_template("new_contact.html", form=form, message=message)

@app.route("/contacts/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    contact = Contacts.query.get_or_404(id)
    form = ContactForm()
    message = ""
    form.group.choices = [(g.id, g.name) for g in Groups.query.order_by('name')]

    if form.validate_on_submit():
        contact.name = form.name.data
        contact.phone = form.phone.data
        contact.email = form.email.data
        contact.group = form.group.data
        db.session.commit()
        message = "Contact updated successfully"
        return redirect(url_for("contacts"))
    elif request.method == "GET":
        form.name.data = contact.name
        form.phone.data = contact.phone
        form.email.data = contact.email
        form.group.data = contact.group
    return render_template("edit_contact.html", form=form, message=message)

@app.route("/contacts/delete/<int:id>")
def delete_contact(id):
    contact = Contacts.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for("contacts"))



    