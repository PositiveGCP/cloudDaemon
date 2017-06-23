#!/usr/bin/python
# *- coding: utf-8 -*
# Tests for the 4.2.4 version of cloud Nemesysco service
# Dante Fernando Bazaldua Huerta
# 23-Jun-2017

import requests
import json
import sys
import keys as SEC

response = None
status = ""
response_text = ""

# Codifica la URL
def encodeURL( urlin ):
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

# Proceso que ejecuta conexión con el storage
# # TODO: RECIBE el archivo donde leer el url y guardar el resultado.
def _processFile( infile, outfile ):

    try:
        # Ejecutar solicitud
        with open( infile, 'r') as file:
            for e in file:
                audio = e
                break
            file.close()

        print "Audio a procesar: %s" % ( audio )

        # Codificar la URL
        headers = {'Accept': 'application/json',
               'Content-Type':'application/json',
               'Cache-Control':'no-cache',
               'N-MS-AUTHCB': SEC.N_MS_AUTHCB }

        url_encoded = encodeURL( audio )

        print "Encoded: %s" % ( url_encoded )

        # print "URL_encoded de descarga: -> %s" %(url_encoded)
        # Truncate the string
        # info = (e[75:150] + '...') if len(e) > 200 else e
        # print info
        line_req = SEC.RA7url + url_encoded
        # Ejecuta la consulta
        req = requests.get( line_req, headers=headers )
        response = req.json()
        status = req.status_code
        response_text = req.text

        print "STATUS: %s" %(status)
        print "Respuesta: %s" %(response_text)

        with open( outfile, 'w') as out:
            json.dump( response, out )


    except Exception as e:
        # Cachar excepciones
        print "Ocurrió excepcion en LvaProcess %s" %( str(e) )

def main():
    if len( sys.argv ) <= 1:
        print "Hacen falta argumentos."
    elif len( sys.argv ) is 3:
        print "Argumentos: %s, %s" % ( sys.argv[1], sys.argv[2] )
        _processFile( sys.argv[1], sys.argv[2] )

if __name__ == '__main__':
    main()
