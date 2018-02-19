# -*- coding: utf-8 -*-
# @author: Dante Fernando Bazaldua Huerta
# Segunda parte del cloud servicie que permite
# conexión con el servidor en Israel

import pyrebase
import requests  # Hacer query a CLVA-i
import json
import time
import keys as security

firebase = pyrebase.initialize_app(security.config)

auth = firebase.auth()  # Objecto de autenticación

# Iniciar sesion en firebase
user = auth.sign_in_with_email_and_password(
    security.email,
    security.passwd
)
# print user
storage = firebase.storage()  # Referencia al storage
db = firebase.database()  # Referencia a la base de datos


def sendmail(dictionary):
    transaction = db.child("Transfer/" + dictionary['id']).get()
    th = transaction.val()
    persona = db.child("Personas/" + th['key_persona']).get()
    p = persona.val()
    name = p['Nombre'] + " " + p["ApPat"] + " " + p["ApMat"]
    cuenta = db.child("Cuenta/" + th['key_empresa']).get()
    empresa = cuenta.val()
    nombre_empresa = empresa['NComercial']
    user = db.child("Usuarios/" + th['key_usuario']).get()
    usuario = user.val()
    master_email = usuario['email']

    # Get the new resume (100 - value)
    sde = dictionary['resume'].split("|")
    i = 0
    # Generate the new value of the sde
    for e in sde:
        temp = int(e)
        value = 100 - temp
        sde[i] = str(value)
        i = i + 1

    # Concat the new_sde
    new_sde = '|'.join(sde)

    # Temporalmente solo lo mandará a info@positivecompliance.com
    master_email = "info@positivecompliance.com"

    # dictionary
    d = {}
    d["nombre"] = name
    d["empresa"] = nombre_empresa
    d["resume"] = new_sde
    d["fecha"] = dictionary['fecha']
    d["id"] = dictionary["id"]
    d["master_acc"] = master_email
    # print d
    url = "http://pmail.positivecompliance.com/api.php"
    r = requests.post(url, data=json.dumps(d))
    print "Email sent - [ %s ]" % (str(r.status_code))


# d = {}
# d['id'] = '-L5AVR3pum-ifpgkq2g2'
# d['resume'] = "10|20|30|40|50|60|70|80|90"
# d['fecha'] = time.strftime('%Y/%m/%d - %H:%M:%S')
# sendmail(d)
