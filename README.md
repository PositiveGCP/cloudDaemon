# Processing

**Positive Compliance LLC**

Copyright (c) 2017--, The Positive Compliance Development Team.

-----
**Autor:** Dante Bazaldua - [danteese](https://github.com/danteese)

*Release:* 2.1.1 (July 2018)

Contenido:

- [Processing](#processing)
    - [Arquitectura](#arquitectura)
    - [Principios](#principios)
        - [Production](#production)
            - [Transacciones en tiempo real](#transacciones-en-tiempo-real)
        - [Development](#development)
            - [`processing`](#processing)
            - [`pscloud`](#pscloud)
                - [Pruebas unitarias](#pruebas-unitarias)

Este servicio fue creado con el objetivo de canalizar los problemas que se tenían con un procesamiento en servidores locales a uno que mejorara la portabilidad y pudiera establecer conexiones simultáneas con los servicios de Nemesysco en Israel a través de su API.

## Arquitectura

Archivos y carpetas importantes, esto quiere decir que se requiere que existan es por eso que la primera vez que se ejecuta en un ambiente que no es el del servidor por defecto debe ejecutarse:

```bash
$ make
```

```
cloud
│   processing (executable)
│   pscloud (core program)
│
└───log
└───node 
└───tran
```

En realidad nunca se trabaja directamente con estos archivos y/o carpetas puesto que existe todo un framework pensado para  trabajar correctamente al cloud sin necesidad de hacer modificaciones manuales.


## Principios

Este servicio está construido "on top" de la biblioteca de Firebase de Streaming lo que permite tener un HTTP Stream escuchando a todo momento si existen cambios en la base de datos que parezcan importantes. Por ahora la que escucha es: `Transfer`.

### Production

Significa que se requiere que el sistema trabaje por si sólo y mantenga estricta comuncación con sus servicios internos y no con el usuario.

* El servicio por defecto para mantener el stream en línea es `pm2`:

```bash
$ cd node
$ pm2 start listen.js --name=processing
```

Para **matar el sistema** (en caso de un posible reprocesamiento de toda la rama o problema directamente en la aplicación).

```bash
$ pm2 delete processing
```

#### Transacciones en tiempo real

Puede ser útil en el caso de querer revisar si el sistema está funcionando correcatmente. Para poder efectuar una revisión es necesario estar en la carpeta `/node` y ejecutar:

```bash
$ tail -f status.log
``` 

Las transacciones pasadas no tiene caso revisarlas por este medio, es mejor estar atentos a la base de datos.

### Development

El escenario anterior es el más adecuado para mantener el sistema trabajando con la mínima intervención humana, pero para realizar pruebas es necesario entender *como funcionan los programas más importantes de esta distribución*:

#### `processing`

Ejecutable de Python "on top" de la biblioteca click que permite una interface amigable para el usuario y la hace una CLI, es decir un wrapper de `pscloud`.

Principales comandos: 

+ Cuando se requiere información de la transacción de la persona:

```bash
$ ./processing find --key={ID_TRANSFER}
```

El comando anterior va a imprimir en pantalla el archivo de la transacción (que están guardados en `/tran` dentro del mismo directorio) pero por medio de un Hasheo (md5) a la hora en que se procesó. 

Este archivo se puede consultar de dos formas:

1. En formato *.txt en la que se expone la hora de consulta el resultado obtenido limpio.
2. El formato *.json el cual contiene toda la información que procesó el servidor de Nemesysco y que regresó. 

> Este método se va a eliminar en la siguiente distribución para solo dejar cabida a un JSON.

#### `pscloud`

Este es el programa principal sobre el que todo proceso corre, en un escenario simple tiene el objetivo de poder procesar solo una transacción a la vez.

> En versiones anteriores este sistema es el que se ponía como daemon, sin embargo a partir del cambio de RA7 (principios de 2018) se tuvo que pasar completamente a nodejs.

De aquí no hay mucho que decir más que la ventaja de realizar prebas unitarias.

##### Pruebas unitarias

En caso de que existan problemas internos en cuanto al procesamiento, comunicación o mal envío de correos a través del API de correos se pueden realizar pruebas unitarias para ver que está sucediendo en todo el sistema. 

**Importante:** Estas pruebas reflejan su resultado en la base de datos que se está conectando.

```bash
$ ./pscloud --mode=dev -s -k -LIWM1yccPgshtXxRtNDl
```

Las opciones de este comando se pueden acceder fácilmente desde la ayuda del propio comando pero se explican brevemente acontinuación: 

|Opción|Descripción|
|---|---|
|mode \| m | Exhibe a la terminal del usuario lo que está haciendo durante cada paso que ejecuta **(modo logger)**.|
|single \| s | Procesa solo una transaccion y no se fija en lo que exista en el árbol por cola de procesamiento. | 
|key \| k | Llave de la transacción a procesar. |

**Importante**: Estas son opciones por lo cual es necesario que empiecen con '-'.