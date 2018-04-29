# -*- coding: utf-8 -*-
# @author: Dante Fernando Bazaldua Huerta
# Manage all connections
#
import keys as security
# External libraries
import pyrebase  # Conexión con firebase

firebase = pyrebase.initialize_app(security.config)  # Inicializar firebase

# ------------------------ FIREBASE -------------------------
auth = firebase.auth()  # Objecto de autenticación
# Iniciar sesion en firebase
user = auth.sign_in_with_email_and_password(security.email, security.passwd)
storage = firebase.storage()  # Referencia al storage
db = firebase.database()  # Referencia a la base de datos

DB_PATH_POSITION = 'Encuestas'


def getPositionKey(key):
    try:
        element = db.child('Transfer').child(key).get()
        tran = element.val()
        if 'key_encuesta' not in tran:
            return None
    except Exception as e:
        print str(e)
        return None

    return tran['key_encuesta']


def getPositionInfo(key_encuesta):
    try:
        element = db.child(DB_PATH_POSITION).child(key_encuesta).get()
        tran = element.val()
        if 'cuestionario' not in tran:
            return None
    except Exception as e:
        print str(e)
        return None

    return tran['cuestionario']


def convertPosIntoPathList(questionary):
    count = 0
    paths = []
    try:
        for element in questionary:
            for key in element:
                if (key == "tipo") and (element[key] == "pregunta"):
                    paths.append(str(count) + ".wav")
                    count = count + 1
        if count == 0:
            return 0

    except Exception as e:
        print str(e)

    return paths


uid = "-L7x2Gaf_9aDjg2z7ZVN"
key_encuesta = getPositionKey(uid)
if key_encuesta is not None:
    quest = getPositionInfo(key_encuesta)
    if quest is not None:
        paths = convertPosIntoPathList(quest)
        print paths
