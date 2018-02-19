# *- coding: utf-8 -*
# @author: Dante Fernando Bazaldua Huerta
# Manage all connections
import pyrebase
import requests  # Hacer query a CLVA-i
import time
import keys as security
import urllib

# Inicializar firebase
firebase = pyrebase.initialize_app(security.config)

# ------------------------ FIREBASE -------------------------
auth = firebase.auth()  # Objecto de autenticación
# Iniciar sesion en firebase
user = auth.sign_in_with_email_and_password(
  security.email,
  security.passwd
)
# print user
storage = firebase.storage()  # Referencia al storage
db = firebase.database()  # Referencia a la base de datos


# Clase para cada uno de los n objetos que pudieran
# suceder al leer el archivo de audio
class LvaProcess(object):

    link = ""
    response = ""
    response_text = ""
    status = ""
    uid = ""
    URL_inside = ""

    def __init__(self, link, uid):
        self.link = link
        self.uid = uid
        self.response = ""
        self.response_text = ""
        self.status = ""
        # self._processFile()

    # Codifica la URL
    def encodeURL(self, urlin):
        txt = ""
        tmp = ''
        for c in urlin:
            if c is '?':
                tmp = '%3F'
            elif c is '=':
                tmp = '%3D'
            elif c is '&':
                tmp = '%26'
            elif c is '/':
                tmp = '%2F'
            elif c is ':':
                tmp = '%3A'
            elif c is '%':
                tmp = '%25'
            else:
                tmp = c

            txt = txt + tmp
        # End for loop
        return txt

    # Proceso que ejecuta conexión con el storage
    def _processFile(self):
        URL = '/cloud/' + self.uid + '/' + self.link
        try:
            # Ejecutar solicitud
            audio = storage.child(URL).get_url(user['idToken'])
            # print user['idToken']
            # print "URL de descarga: -> %s" %(audio)

            # Codificar la URL
            e = audio
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'N-MS-AUTHCB': security.N_MS_AUTHCB
                }
            service = security.ra7
            url_encoded = urllib.quote(e, safe='')

            # print "URL_encoded de descarga: -> %s" %(url_encoded)
            # Truncate the string
            # info = (e[75:150] + '...') if len(e) > 200 else e
            # print info
            line_req = service + url_encoded
            # Ejecuta la consulta
            req = requests.get(line_req, headers=headers)
            self.response = req.json()
            self.status = req.status_code
            self.response_text = req.text
            rsp = (
                "\t\t"
                + self.uid +
                " -> "
                + self.link +
                " [ "
                + self.response_text +
                " ]"
            )
            return rsp
            # print "\t\t %s -> %s [OK]" %(str(self.uid), str(self.link))
            # TODO: Guardar la respuesta en el archivo de texto

        except Exception as e:
            print "Problema en LvaProcess %s" % (str(e))


class Transaction(object):
    uid = ""

    # Constructor:
    # Id de la transaccion
    def __init__(self, uid):
        self.uid = uid
        pass

    # Actualiza la rama con el resultado y la fecha
    def updateBranch(self, information):
        try:
            # Obtener el tiempo actual en el que se realiza la transaccion
            timex = time.localtime(time.time())
            transaction = db.child("Transfer/" + self.uid).get()
            th = transaction.val()
            # Cambiar los datos en la rama
            th["resultado"] = information
            th["date_final"] = time.strftime('%Y/%m/%d - %H:%M:%S %Z', timex)
            th["codec"] = "ra7"
            th["processed"] = True
            # print users
            db.child("Transfer").child(self.uid).set(th)

        except Exception as e:
            # TODO: mejorar el caching pues pudieron pasar muchas cosas como:
            # - No se encontró la rama ( fue eliminada por alguna razón )
            # - No se pudo obtener de manera correcta el resultado o fecha
            print e


class AudioFile(object):
    """
    Clase que obtiene todo el archivo de audio
    y garantiza un UID para la transacción
    """

    audioFile = None
    # Rutas relativas para cada audio:
    paths = []
    uid = ""

    # Constructor, asigna un uid para concretar la transaccion
    def __init__(self, uid):
        self.paths = []
        self.uid = uid
        # Obtener el archivo de procesamiento automaticamente
        self.getProcessingFile()

    # Obtener el archivo con los audios
    def getProcessingFile(self):
        try:
            poi = '/cloud/'+self.uid+'/processing.txt'
            self.audioFile = storage.child(poi).get_url(user['idToken'])
            # print "URL de descarga: -> %s" %(self.audioFile)
            if self.audioFile is not '':
                # Aquí se recibe el link del archivo que contiene
                # ubicación de los audios
                # Procesamiento del URL para obtener los audios
                self.process_file(self.audioFile)

        except Exception as e:
            log = "URL ERROR - " + str(e)
            print log

    # Modulo de proceso del archivo de texto
    def process_file(self, URL):
        try:
            # Ejecutar solicitud
            req = requests.get(URL)
            self.readlineByLine(req.text)
            # TODO: Mejorar el registro de actividades pues pudieron
            # haber sucedido las siguientes:
            # - El archivo no está bien escrito
            # - El achivo no contenía los correctos archivos

        except Exception as e:
            print str(e)

    # Lee linea por linea el texto completo
    def readlineByLine(self, raw):
        i = 0
        sep = raw.split('\n')
        tot = len(sep)
        try:
            for line in sep:
                if i > 4:
                    realAudio = self.parseLine(line)
                    new = realAudio.split('\r')
                    # print "L[%d] - %s" %( i, new )
                    self.paths.append(str(new[0]))
                    if i == (tot - 2):
                        break
                i = i + 1

        except Exception as e:
            print "No se ha leído", e
            # No Exception

    # Separa la linea y devuelve donde se encuentra cada archivo
    def parseLine(self, lineCode):
        # print lineCode
        separated = lineCode.split('||')
        last = separated[4].split('\\')
        return last[4]
