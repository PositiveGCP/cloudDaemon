# *- coding: utf-8 -*
# Testing script for firebase in branch transfer

import pyrebase
import time
import keys as security

firebase = pyrebase.initialize_app( security.config ) # Inicializar firebase

# ------------------------ FIREBASE -------------------------
auth = firebase.auth() # Objecto de autenticación
user = auth.sign_in_with_email_and_password( security.email, security.passwd ) # Iniciar sesion en firebase
storage = firebase.storage()    # Referencia al storage
db = firebase.database()        # Referencia a la base de datos

# Actualiza la rama con el resultado y la fecha
def updateBranch():
    try:
        timex = time.localtime(time.time()) # Obtener el tiempo actual en el que se realiza la transaccion
        information = "0|0|0|0|0"
        tk = {}
	th = {}
        # Cambiar los datos en la rama
        th["date"] = time.strftime( '%Y/%m/%d - %H:%M:%S', timex )
        th["date_final"] = ""
        th["key_empresa"] = "-Kae25-RyMrCjwVGmJ_N"
        th["key_encuesta"] = "-Kn2dWPakcknjBODagCl"
        th["key_persona"] = "-Kntv0z9zbKWD9nEyOvM"
        th["key_usuario"] = "5jOZv7YDXSbNVlqG3n6DFiV0lz43"
        th["processed"] = False
        th["resultado"] = ""
        th["status"] = "resultado"
        th["visto"] = False
        # print users
	tk["-KlapjrQR2UBegXAA8-"] = th
        # db.child("Transfer").push( th )
	db.child("Transfer").child("-Knu2HwW6B6yRrQfH_0r").set(th)
	print th
    except Exception as e:
    	print e

if __name__ == "__main__":
    updateBranch()
