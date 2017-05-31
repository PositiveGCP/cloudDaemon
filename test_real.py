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
        th = {}
        # Cambiar los datos en la rama
        th["date"] = "2017/05/25 - 04:39:15"
        th["date_final"] = time.strftime( '%Y/%m/%d - %H:%M:%S', timex )
        th["key_empresa"] = "-K_oamG1TExZkGP5Ed8g"
        th["key_encuesta"] = "-KkWAzrRALxnAXZ9IigB"
        th["key_persona"] = "-Kl0Y3VRJ5zmQSYiYCx_"
        th["key_usuario"] = "6yfAI6VIXlRyHDlPaT54IuTXGOC2"
        th["processed"] = False
        th["resultado"] = information
        th["status"] = "resultado"
        th["visto"] = False
        # print users
        db.child("Transfer").push( th )

    except Exception as e:
    	print e

if __name__ == "__main__":
    updateBranch()
