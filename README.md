# L01-Thomasmurrayh-iasantibanez
El presente archivo tiene como propósito explicar el código entregado, por
lo que seguirá la estructura del script, desde su inicio hasta el final. 

Lo primero que puede observarse en el script, son los import necesarios 
para el desarrollo del código. random es utilizada para aquellas eleciones aleatorias, y para obtener tiempos entre llegadas de peatones a las estaciones que siguieran una distribución exponencial. datetime es empleada para simular el paso del tiempo en la simulacion. Por último, collections es empeada para simular las filas en los andenes, para de esta forma poder realizar modificaciones a éstas tanto al comienzo (al subir) como al final (cambios de fila).

Luego, se crean las diversas clases empleadas en la simulación. En este punto, solo serán descritos aquellos parámetros no obvios y/o claves para alguna seccion del algoritmo.

La primera clase es la clase Estacion, que representa cada una de las estaciones que componen la L10. Dentro de sus parámetros, cuenta con identificador, su respectivo nombre, numero de andenes, una variable booleana que indica si se encuentra abierta o cerrada, una lista llamada Registro que contiene todos los peatones que llegan a la estación, una lista llamada pasada, empleada principalmente en la funcion capacidad_tren y datos_anden, un int llamado tot_bajan con el total de pasajeros que han bajado en la estaciony la variable t_last_stop, que se utiliza para actualizar el instante en el que llegó o salió el último tren.
Los dos métodos de la clase son respectivamente para abrir y cerrar cada estación. 

La segunda clase corresponde a Anden. Como su nombre lo dice, representa los andenes de las estaciones. dentro de sus parámetros relevantes, se encuentra el numero identificador de su estación asociada, su nombre, el sentido (1 si va hacia la estacion Tranca perro (regreso), 0 si viene desde dicha estación(ida)), la lista arribos que contiene todos los peatones que han accedido a la estación, una variable booleana llamada ocupado que indica si hay un tren ocupando el anden, y la variable t_last_stop, qe se utiliza para actualizar el instante en el que llegó o salió el último tren.















