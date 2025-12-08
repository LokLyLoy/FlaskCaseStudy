from app import app
from flask import render_template, request


@app.get('/contact')
def contact():
    return render_template('page/contactpage.html')

@app.post('/contact-submit')
def contact_submit():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    message = request.form.get("message")

    return render_template('page/contact-result.html', firstname=firstname, lastname=lastname, email=email, message=message), 200