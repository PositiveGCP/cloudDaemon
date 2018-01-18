# *- coding: utf-8 -*

# @author: Dante bazaldua
# @brief: Daemon to query Firebase and process information using LVA-CLOUD
# @date: 27th may, 2017

import pyrebase  # Conexión con firebase
# Librería que contiene la configuración de cuenta y de usuarios
import keys as security
import mainCLVA as bslogic
import time  # Tiempo de ejecución para logs
import os  # Ocupar directorios
import Queue  # Creación de la lista de espera
import threading
import json  # Guardar la informacion de manera correcta
from daemonize import Daemonize  # Daemon the service

import mail as smail

firebase = pyrebase.initialize_app(security.config)  # Inicializar firebase

# ------------------------ FIREBASE -------------------------
auth = firebase.auth()  # Objecto de autenticación
# Iniciar sesion en firebase
user = auth.sign_in_with_email_and_password(security.email, security.passwd)
storage = firebase.storage()  # Referencia al storage
db = firebase.database()  # Referencia a la base de datos

main_path = os.path.dirname(os.path.realpath('__file__'))

# Archivos para logging
log_file = ""
transactions_file = ""

kiwi = Queue.Queue()  # Kiwi
unp = []  # UIDS del kiwi

# ------------------------ log system functions -------------------------
# create_logfile, create_transfile, system_log, transaction_log permiten
# interactuar con el sistema en cuanto a escritura de archivos
# Regresa el nombre de archivo de logsystem


def create_logfile():
    timestamp = str(int(time.time()))
    log = os.path.join(main_path, 'logsystem/' + timestamp + ".txt")
    return log


def create_transfile(uid, type_f):
    """
    Regresa el nombre del archivo para la transaccion
    """
    new_uid = uid.split('-')
    extension = ""
    if type_f is "json":
        extension = ".json"
    elif type_f is "text":
        extension = ".txt"

    log = os.path.join(main_path, 'transactions/' + new_uid[1] + extension)
    return log


def system_log(task, message):
    msg = "$ [ " + task + " ] - " + message
    print "%s" % (msg)
    with open(log_file, 'a') as out:
        out.write(msg + "\n")
        out.close()


def transaction_log(filename, response, status, date):
    msg = "[ " + status + " ] - " + response + "[ " + date + " ]"
    # print "%s" %(msg)
    # print filename
    with open(filename, 'a') as out:
        out.write(msg + "\n")
        out.close()


class SetQueue(Queue.Queue):
    """
    Modificacion de clase para poder iterar en esta
    """
    def _init(self, maxsize):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


class Firebase(object):
    """
    Clase firebase que por ahora solo permite revisar las transacciones y
    comenzar con el kiwi.
    """

    # Variables para saber que tantos tasks hay sin resolver
    # El uid de transacción de cada uno
    uid_trans = []
    info_trans = None

    def __init__(self):
        pass

    def check_transactions(self):
        task = "check_transactions"
        transactions = db.child("Transfer").get()
        count = 0
        try:
            print "\n$ Transacciones actuales: "
            print "%20s | %10s | %30s | %30s" % ("UID_transaccion",
                                                 "Status", "Fecha_inicio",
                                                 "Fecha_proceso")
            print "-" * 105
            # Recorrer las transacciones
            for trans in transactions.each():

                pro = None
                dfinal = ""

                # Validar la existencia de campo processed
                if "processed" in trans.val():
                    if trans.val()['processed'] is False:
                        count = count + 1
                        self.uid_trans.append(trans.key())
                        pro = trans.val()['processed']
                    else:
                        pro = True

                # Validar la existencia de fecha final
                if "date_final" in trans.val():
                    dfinal = trans.val()['date_final']

                if "date" in trans.val():
                    d = trans.val()['date']
                else:
                    trans.val()['date'] = "2017/12/06 - 12:00:00"

                print "%20s | %10s | %30s | %30s" % (trans.key(), pro,
                                                     trans.val()['date'],
                                                     dfinal)
            # Mostrar el kiwi
            # print self.uid_trans
            if len(self.uid_trans) > 10:
                tr = "[< 10]"
            else:
                tr = str(self.uid_trans)

            print "\n"
            msg = "Cantidad de transacciones sin procesar: " + str(count) + " -> " + tr
            # Realizar log del sistema
            system_log(task, msg)

        except Exception as firebase_err:
            err = str(firebase_err)
            system_log(task, err)


def pathFinder(req):
    """
    Función OPTIMIZADA para busquedas en el arreglo.
    """
    # print req
    xresponse = ""
    if len(req) > 1:
        index = req.index("<<QUESTIONS>>")
        voi = req[index + 1]
        # Let's split a little
        vois = voi.split('||')
        xresponse = vois[3]
    else:
        xresponse = "0"

    return xresponse


def consume_uids():
    """
    Consume lo que exista en el queue
    """
    task = "consume_uids"
    while(True):
        print "\t --> Thread waiting..."
        item = kiwi.get()

        # Clear objects
        tnt = None
        audio_file = None

        # Crear archivo para guardar resultados de transaccion
        transactions_file = create_transfile(str(item), "text")
        # print "\t $ Nombre del archivo [%s]" %( transactions_file )

        # ------------------------ Business logic -------------------------
        try:
            tnt = bslogic.Transaction(str(item))  # Crear objeto transaccion
            audio_file = bslogic.AudioFile(tnt.uid)  # Crear objeto de audio

            msg = "Iniciando procesamiento: " + str(item) + ". - [" + time.strftime('%Y/%m/%d - %H:%M:%S') + "]"
            system_log(task, msg)

            responseobj = []
            results = []  # The raw data

            print "\n$ Procesamiento actual: "
            print "%20s | %30s | %10s" % ("Audio File", "Time", "Score")
            print "-" * 75

            # Procesamiento de los archivos de voz
            for element in audio_file.paths:
                # A este punto se debió haber procesado cada uno de los audios
                # print "\t $ Procesando: %s %s" %( element, time.strftime('%Y/%m/%d - %H:%M:%S') ),
                voice = bslogic.LvaProcess(element, tnt.uid)
                # Añadido debido a la complejidad para ver que sucede durante el proceso
                LVA_RESPONSE = voice._processFile()
                # Agrear al objeto el json de respuesta y guardar en archivo de texto
                partial = pathFinder(voice.response)
                system_log(task, "RES: [ " + partial + " ]")
                # Formato de impresión en tabla
                print "%20s | %30s | %10s" % (element, time.strftime('%Y/%m/%d - %H:%M:%S'), partial)
                # Guardar en el archivo de texto
                transaction_log(transactions_file, voice.response_text, str(voice.status), time.strftime('%Y/%m/%d - %H:%M:%S') )  # Escribir la transaccion
                results.append(voice.response)
                responseobj.append(partial)  # Se guarda en el objeto las respuestas

            # Crear el string que se guarda en firebase res|res|res...
            strres = ""
            temp = ""
            j = 0
            for i in responseobj:
                if j is 0:
                    temp = temp + i
                else:
                    temp = temp + "|" + i
                j += 1

            strres = temp

            # Crear el json y guardar la informacion completa
            transactions_file_json = create_transfile(str(item), "json")
            result_data = {}

            result_data['uid_trans'] = str(item)
            result_data['fecha'] = time.strftime('%Y/%m/%d - %H:%M:%S')
            result_data['resume'] = strres
            result_data['raw_data'] = results

            with open(transactions_file_json, 'w') as fp:
                json.dump(result_data, fp, sort_keys=True, indent=4)
                fp.close()
            print "\t $ JSON guardado."

            # ----- Actualizar la rama donde se encontraba la transaccion
            tnt.updateBranch(strres)
            # Modificacion urgente para el mail TODO: optimizar
            if strres is not "":
                d = {}
                d['id'] = str(item)
                d['resume'] = strres
                d['fecha'] = time.strftime('%Y/%m/%d - %H:%M:%S')
                smail.sendmail(d)


            print "\t $ Rama actualizada: %s" %(item)

            msg = "Actualizacion de " + str(item)  + ". Procesamiento de " + str(len( audio_file.paths )) + " audios. - [" + time.strftime('%Y/%m/%d - %H:%M:%S') + "]. Resultado : " + strres
            system_log(task, msg)


        except Exception as err_processing:
            print "Ocurrio durante el proceso[%s]: %s" % (task, str(err_processing))

        print "\t\t$ Finished --> %s [%s]" % (str(item), kiwi.qsize())

        # print "\t ConsThread: terminó queue[current size = {0}] at time = {1} ".format( kiwi.qsize(), time.strftime('%H:%M:%S'))
        kiwi.task_done()


def producer_uids(strkiwi):
    """
    Siguiendo la filosofía de productor-consumidor para threads
    @params: ki es el queue en texto a transadar en en un tipo de dato
    """
    task = "productor_thread"
    try:
        for e in strkiwi:
            # print "\t Thread Productor [ %s ]" %( e )
            kiwi.put(e)  # Poner en el queue el elemento n de transacciones

        msg = "Se concretó la creación del kiwi. Nodos: " + str(len(strkiwi))
        # Realizar log del sistema
        system_log(task, msg)
        kiwi.join()

    except Exception as err:
        print err


def producer_stream(message):

    tail = []

    # Dividimos el path
    uid = message["path"].split("/")
    if len(uid) > 2:
        pass
    else:  # Nos interesa solo cuando se agrega una transaccion completa
        print uid[1]  # El id de interés
        if message["data"] is not None:
            if "processed" in message["data"]:
                # El campo processed si se encuentra por tanto
                # es una transaccion válida
                if message["data"]["processed"] is False:  # Not processed
                    tail.append(uid[1])
                    producer_uids(tail)
                else:
                    pass
            else:  # Si solo se quiere procesar por algun error
                if message["data"] is "processed":
                    tail.append(uid[1])
                    producer_uids(tail)
        else:
            pass


# Main function
def main():

    # ------------------------ Streaming -------------------------
    my_stream = db.child("Transfer").stream(producer_stream, stream_id="new_transaction")

    task = "main_thread"
    msg = "Iniciando el servicio..."
    system_log(task, msg)  # Realizar log del sistema

    msg = "Obteniendo UIDs sin procesar..."
    system_log(task, msg)  # Realizar log del sistema

    # Revisar en Firebase si hay transacciones sin procesar
    FB_connect = Firebase()
    FB_connect.check_transactions()
    # Obtener transacciones
    unp = FB_connect.uid_trans

    # Comenzar con el consumo de los nodos del queue
    threads_num = 1  # Solo dos threads de consumo
    for i in range(threads_num):
        t1 = threading.Thread(name = "Consumidor_de_uids -" + str(i), target=consume_uids, args=())
        t1.start()

    # Crear el kiwi de procesamiento
    if len(unp) is not 0:
        # Es decir que si hay encuestas sin procesar
        t2 = threading.Thread(name = "ProducerThread", target=producer_uids, args=(unp,))
        t2.start()

    else:
        msg = "Nada en cola, esperando al stream..."
        system_log(task, msg)

    kiwi.join()
    t1.join()
    t2.join()
    print "Bye, by Dante Baz\n"


if __name__ == "__main__":
    log_file = create_logfile()  # System: Archivo donde guardar el log del sistema.
    os.system('clear')  # Clean screen
    print "%s\nAuthor: %s" %("Daemon Start - CLVA v0.4 Positive Compliance","Dante Fernando Bazaldua Huerta")
    # In case of no daemon
    # main()
    myname=os.path.basename(sys.argv[0])
    pidfile='/tmp/%s' % myname       # any name
    daemon = Daemonize(app=myname,pid=pidfile, action=main)
    daemon.start()
