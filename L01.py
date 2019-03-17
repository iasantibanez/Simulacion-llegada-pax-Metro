import random
from random import expovariate
import datetime
import collections

LISTA_TOTAL_EVENTOS = []
LISTA_FLUJOS = [[], [], [], [], [], [], [], [], [], []]
#-------------------Clases-----------------------------------

class LineaMetro:
    def __init__(self,_ID):
        self._ID =_ID
        self.estaciones_dict = {}

    def _get_estacion(self):
        return self.estaciones_dict

    def add_Estacion(self, _id, name):
        p = Estacion(id=_id, nombre=name)
        self.estaciones_dict.update({p.id:p.nombre})
        return p


class Estacion:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.andenes = 2  #0->ida, 1->vuelta
        self.abierta = False
        self.Registro = []
        self.t_last_update = datetime.time(5, 0, 0)
        self.pasada = []   #lista para registrar trenes que pasan y capacidad antes y despues abrir puertas
                           #[instante, id_tren, cap_antes, cap_despues, direccion]
        self.tot_bajan = 0

    def abrir(self):
        self.abierta = True
        print("la estacion esta abriendo")

    def cerrar(self):
        self.abierta = False
        print("la estacion esta cerrando")


class Anden:
    def __init__(self, id_estacion, nombre, sentido, arribos):
        self.id_estacion = id_estacion
        self.fila_pos = [collections.deque(), collections.deque(), collections.deque(), collections.deque(),
                         collections.deque(), collections.deque(), collections.deque(), collections.deque(),
                         collections.deque(),collections.deque()]
        self.arribos = []
        self.ocupado = False
        self.t_last_stop = datetime.time(5, 0, 0)
        if sentido == 1:
            self.sentido = 1  #regreso hacia tranca perro
        else:
            self.sentido = 0  #ida desdetranca perro
        # CONTADORES
        self.cont_suben = 0
        self.cont_cambian_fila = 0
        self.cont_bajan = 0

    def min_fila(self):  ##obtiene posicion fila mas vacia
        best_row = 1000
        pos = 0
        for i in range(len(self.fila_pos)):
            now = len(self.fila_pos[i])
            if now < best_row:
                best_row = now
                pos = i
        return pos

    def update_time(self, tiempo):   ##actualiza tiempo
        self.t_last_stop = tiempo

    def llegada(self, id_tren, sentido):  ##llegada de tren a estacion
        global LISTA_TOTAL_EVENTOS
        global LISTA_FLUJOS
        self.ocupado = True
        lista_aux = []
        lista_aux.append(Simulacion.t_aux)
        lista_aux.append(id_tren)
        suma = 0
        for i in range(Trenes[id_tren].vagones):
            suma += len(Vagones[id_tren][i].personas)
        lista_aux.append(suma)
        #print("Comienza descenso de pasajeros")
        for i in range(Trenes[id_tren].vagones):
            Vagones[id_tren][i].descenso(self.t_last_stop)  ##descenso pasajeros
            self.cont_bajan+=Vagones[id_tren][i].cont_descenso
        Andenes[self.id_estacion][sentido].ascenso(id_tren, sentido)  ##abordan pasajeros
        suma2 = 0
        for i in range(Trenes[id_tren].vagones):
            suma2 += len(Vagones[id_tren][i].personas)
        lista_aux.append(suma2)
        lista_aux.append(sentido)
        Estaciones[self.id_estacion].pasada.append(lista_aux)
        if self.id_estacion == 0 and sentido == 1:   # no se suben pax en terminal (sentido contrario)
            pass
        elif self.id_estacion == 9 and sentido == 0: # no se suben pax en terminal (sentido contrario)
            pass
        else:
            LISTA_FLUJOS[self.id_estacion].append(self.cont_suben)

        LISTA_TOTAL_EVENTOS.append((self.t_last_stop.strftime("%H:%M:%S"), "[BAJA PAX]", self.cont_bajan,
                                    "personas bajaron del Tren:", id_tren))
        LISTA_TOTAL_EVENTOS.append((self.t_last_stop.strftime("%H:%M:%S"), "[SUBE PAX]", self.cont_suben,
                                    "personas suben al Tren:", id_tren))
        LISTA_TOTAL_EVENTOS.append((self.t_last_stop.strftime("%H:%M:%S"), "[CAMBIO FILA PAX]", self.cont_cambian_fila,
                                    "personas cambian de fila"))

    def ascenso(self, id_tren, sentido):
        self.cont_suben = 0
        self.cont_cambian_fila = 0
        for j in range(Trenes[id_tren].vagones):
            tiempo_disponible = 30 - Vagones[id_tren][j].t_descenso
            for k in range(len(self.fila_pos[j])):
                #1) [suben personas] si hay tiempo disponible y si capacidad es menor a 200
                if (tiempo_disponible > 0) and len(Vagones[id_tren][j].personas) < 200:
                    pax = self.fila_pos[j].popleft()  # se saca de la fila
                    Vagones[id_tren][j].personas.append(pax)  # se mete al vagon
                    tiempo_disponible -= 1/Vagones[id_tren][j].flujo
                    self.cont_suben+=1
                #2) [cambio de fila] si en esa fila[j] hay un vagon[id_tren][j] lleno
                elif len(Vagones[id_tren][j].personas) >= 200:
                    if random.random() < 0.6:
                        #cambiar de fila
                        mejor_fila = Andenes[self.id_estacion][sentido].min_fila()
                        if mejor_fila != j:
                            pax=self.fila_pos[j].pop()
                            Andenes[self.id_estacion][sentido].fila_pos[mejor_fila].append(pax)
                            tiempo_disponible -= 1
                            #      "cambia a fila", mejor_fila)
                            self.cont_cambian_fila += 1
        #3 [cambio de fila] para filas no visitadas por vagones
        filas_no_visitadas = 10 - Trenes[id_tren].vagones
        for j in range(filas_no_visitadas):  # cada fila no visitada
            tiempo_disponible2 = 30
            for k in range(len(self.fila_pos[9-j])): # cada persona de la fila no "visitada"
                if tiempo_disponible2 > 0 and len(self.fila_pos[9-j]) > 0 and random.random() < 0.7:
                    #cambiar fila
                    mejor_fila = Andenes[self.id_estacion][sentido].min_fila()
                    if mejor_fila != (9-j):
                        pax = self.fila_pos[9-j].pop()
                        Andenes[self.id_estacion][sentido].fila_pos[mejor_fila].append(pax)
                        tiempo_disponible -= 1
                        self.cont_cambian_fila += 1
        #sale tren
        #se va gente


class Tren:
    def __init__(self, id):
        global LISTA_TOTAL_EVENTOS
        self.id = id
        self.vagones = int(random.uniform(7, 11))
        self.estacion = None
        self.listavagones = []  #0: puerta vagon i cerrada, 1: abierta, para cada vagon
        self.t_next_arrive = 0
        self.sentido = None

    def next_station(self):
        if self.sentido == 0 and self.estacion != 9:
            self.estacion += 1
        elif self.sentido == 1 and self.estacion != 0:
            self.estacion -= 1
        elif self.sentido == 0 and self.estacion == 9:
            self.estacion -= 1
            self.sentido = 1
            LISTA_TOTAL_EVENTOS.append((self.hora.strftime("%H:%M:%S"), "[CAMBIO DE SENTIDO], tren_id:", self.id,
                                        "Nuevo Anden :", self.sentido))
        elif self.sentido == 1 and self.estacion == 0:
            self.estacion += 1
            self.sentido = 0
            LISTA_TOTAL_EVENTOS.append((self.hora.strftime("%H:%M:%S"), "[CAMBIO DE SENTIDO], tren_id:", self.id,
                                        "Nuevo Anden :", self.sentido))

    def max_tiempo_bajada(self): #se verifican el t_bajada de todos los vagones max[mayor_t_descenso,30]
        for n_vagon in range(self.vagones):
            maximo = 0
            act = Vagones[self.id][n_vagon].t_descenso
            if maximo < act:
                maximo = act
        return max(maximo, 30)

    @property
    def _get_perfilcarga(self):
        for i in range(self.vagones):
            self.listavagones[i] = Vagones[self.id][i].personas

    def _get_hora(self, hora):
        self.hora = hora


class Vagon:
    def __init__(self, id_tren, number):
        self.number = number
        self.capacidad = 200 #200 [pax]
        self.flujo = 25 #[pax/seg]
        self.personas = collections.deque() #pasajeros a bordo
        self.id_tren = id_tren
        self.t_descenso = 30
        self.cont_descenso = 0

    def descenso(self, t_bajada):  #proceso de descenso de cada vagon
        #baja gente
        self.cont_descenso = 0
        self.t_bajada = t_bajada
        bajan = []   ##lista con personas que bajan
        if len(self.personas) == 0:
            pass
        else:
            for i in self.personas:
                if i.destino == Trenes[self.id_tren].estacion:
                    bajan.append(i)
                    Estaciones[Trenes[self.id_tren].estacion].tot_bajan += 1
            for persona in bajan:
                self.personas.remove(persona)
                self.cont_descenso += 1

        self.t_descenso = len(bajan)/self.flujo


class Persona:
    def __init__(self,id_persona, origen, T_llegada):
        self.origen = origen
        self.destino = origen
        self.T_llegada = T_llegada
        self.id = id_persona
        while self.origen == self.destino:  #se asigna destino distinto al origen
            if datetime.time(7, 0, 0) <= T_llegada <= datetime.time(8, 59, 0):  #hora Punta-Mañana
                if random.random() < 0.7:
                    self.destino = random.choice([3, 4, 5, 6])
                else:
                    self.destino = random.choice([0, 1, 2, 7, 8, 9])
            elif datetime.time(18, 0, 0) <= T_llegada <= datetime.time(19, 59, 0):  #hora Punta-TARDE
                if random.random() < 0.8:
                    self.destino = random.choice([0, 1, 2, 7, 8, 9])
                else:
                    self.destino = random.choice([3, 4, 5, 6])

            else:                                                             # HORA VALLE+BAJO
                self.destino = int(random.uniform(0, 9))


class schedule:  ##Clase con tasas de llegada por hora como atributos
    def __init__(self, bajo, valle, punta):
        self.valle = valle
        self.punta = punta
        self.bajo = bajo
        self.rate = 0

    def tramo_horario(self, hora):   ##metodo que identifica la tasa de llegada a las estaciones segun la hora
        if datetime.time(5, 0, 0) <= hora <= datetime.time(5, 59, 59):  #preapertura
            rate = 200/3600
        elif datetime.time(6, 0, 0) <= hora <= datetime.time(6, 59, 59):
            rate = self.valle/3600
        elif datetime.time(7, 0, 0) <= hora <= datetime.time(8, 59, 59):
            rate = self.punta/3600
        elif datetime.time(9, 0, 0) <= hora <= datetime.time(17, 59, 59):
            rate = self.valle/3600
        elif datetime.time(18, 0, 0) <= hora <= datetime.time(19, 59, 59):
            rate = self.punta/3600
        elif datetime.time(20, 0, 0) <= hora <= datetime.time(20, 44, 59):
            rate = self.valle/3600
        elif datetime.time(20, 45, 0) <= hora <= datetime.time(23, 0, 0):
            rate = self.bajo/3600
        else:
            rate = 0

        return rate


##Lista con los nombres de las estaciones
ListaE = ["Tranca Perro", "Nuestra Señora Danielita", "Avenida Hans Lobel", "Plaza Mavrakis", "Hugo Hurtado",
          "San Halcón de Chicureo", "Quinta Osornal", "Cote d'Ivoire", "Manquehuito", "Hernando de Valdivia"]


#--------------------------------------Funciones( linea de tiempo, proceso de llegadas poisson )-----------------------
def conversion(t_0, delta):  # sirve para moverse en un tiempo delta desde t_0
    delta_seg = delta.total_seconds() + t_0.hour*3600 + t_0.minute*60 + t_0.second
    hr = 0
    mm = 0
    seg = 0
    if delta_seg >= 3600:
        hr = int(delta_seg//3600)
        delta_seg = int(delta_seg - hr*3600)

    if delta_seg >= 60:
        mm = int(delta_seg//60)
        delta_seg = int(delta_seg - mm*60)

    if delta_seg >= 0:
        seg = int(delta_seg)

    return datetime.time(hr, mm, seg)


def llegada_personas(t_inicial, t_final):  #metodo que obtiene instantes de llegada segun tasas definidas por horario
    lista_llegada = []   ##Lista que contiene instantes de llegada de pasajeros a la estacion
    t_aux = t_inicial

    while t_aux <= t_final:
        tasa = Tasas.tramo_horario(t_aux)
        delta_llegada_pax = datetime.timedelta(seconds=round(expovariate(tasa)))  #tiempo entre llegadas sucesivas
        tiempo_llegada_pax = conversion(t_aux, delta_llegada_pax)
        t_aux = tiempo_llegada_pax
        lista_llegada.append(tiempo_llegada_pax)

    return lista_llegada

#----------------------Funciones pedidas (capacidad_tren, horarios, simular_verboso, patrones etc )-------------------


def capacidad_tren(estaciones):
    for j in estaciones:
        for i in range(len(Estaciones)):
            if j == Estaciones[i].nombre:
                for h in range(len(Estaciones[i].pasada)):
                    tren = Estaciones[i].pasada[h][1]
                    cap_antes = 200*len(Trenes[tren].listavagones) - Estaciones[i].pasada[h][2]
                    cap_despues = 200*len(Trenes[tren].listavagones) - Estaciones[i].pasada[h][3]
                    print(Estaciones[i].pasada[h][0], ": Tren ", Estaciones[i].pasada[h][1], "llega a la estacion", j)
                    print("    Antes de abrir las puertas: ", cap_antes)
                    print("    Despues de cerrar las puertas: ", cap_despues)


def datos_anden(estacion, anden):    #parametro anden = 1: direccion a tranca perro, enunciado
    nombre = estacion
    sentido = anden
    for i in range(len(Estaciones)):
        if Estaciones[i].nombre == nombre:
            people = len(Andenes[i][sentido].arribos)
            dif_total = 0
            lista_sentido = []
            for j in range(len(Estaciones[i].pasada)):
                if Estaciones[i].pasada[j][4] == sentido:
                    lista_sentido.append(Estaciones[i].pasada[j])
            contador = len(lista_sentido) - 1
            while contador > 0:
                ultimo = datetime.datetime.combine(datetime.date.today(), lista_sentido[contador][0])
                anterior = datetime.datetime.combine(datetime.date.today(), lista_sentido[contador - 1][0])
                dif_t_trenes = ultimo - anterior
                dif_en_minutos = dif_t_trenes.total_seconds() / 60
                dif_total += dif_en_minutos
                contador -= 1
            dif_promedio = dif_total/(len(lista_sentido) - 1)
    print("A la estacion ", estacion, "an arribado un total de ", people,
          "viajeros. En promedio, pasan trenes cada ", dif_promedio, "  minutos.")


def patrones():
    max_arribos = 0
    max_bajadas = 0
    for i in range(len(Estaciones)):
        if len(Estaciones[i].Registro) > max_arribos:
            max_arribos = len(Estaciones[i].Registro)
            pos_arribos = i
    for i in range(len(Estaciones)):
        if Estaciones[i].tot_bajan > max_bajadas:
            max_bajadas = Estaciones[i].tot_bajan
            pos_bajadas = i
    print("La estacion a la que llegaron mas pasajeros fue ", Estaciones[pos_arribos].nombre,
          "con un total de ", max_arribos)
    print("La estacion en la que bajaron mas pasajeros fue ", Estaciones[pos_bajadas].nombre,
          "con un total de ", max_bajadas)


def simular_verboso():
    Simulacion.run()
    print("se inicia la simulacion")
    for evento in LISTA_TOTAL_EVENTOS:
        print(evento)


def horarios(bajo, valle, punta):
    Tasas.bajo = bajo
    Tasas.valle = valle
    Tasas.punta = punta
    print("se han fijado las tasas de llegada;", "bajo:", bajo, "valle:", valle, "punta:", punta)
    pax_bajo = 0
    pax_valle = 0
    pax_punta = 0
    #se ejecuta la simulacion (con dichos datos)
    Simulacion.run()
    #total personas en (valle,bajo,punta)
    for i in Estaciones:
        for k in Estaciones[i].Registro:
            if datetime.time(5, 0, 0) <= k.T_llegada <= datetime.time(5, 59, 59): #preapertura
                pax_bajo += 1
            elif datetime.time(6, 0, 0) <= k.T_llegada <= datetime.time(6, 59, 59):
                pax_valle += 1
            elif datetime.time(7, 0, 0) <= k.T_llegada <= datetime.time(8, 59, 59):
                pax_punta += 1
            elif datetime.time(9, 0, 0) <= k.T_llegada <= datetime.time(17, 59, 59):
                pax_valle += 1
            elif datetime.time(18, 0, 0) <= k.T_llegada <= datetime.time(19, 59, 59):
                pax_punta += 1
            elif datetime.time(20, 0, 0) <= k.T_llegada <= datetime.time(20, 44, 59):
                pax_valle += 1
            elif datetime.time(20, 45, 0) <= k.T_llegada <= datetime.time(23, 0, 0):
                pax_bajo += 1
            else:
                pass
    print("han llegado:", "horario bajo:", pax_bajo, "horario valle:", pax_valle, "horario punta:", pax_punta)
    # Estacion con menor flujo subida
    max_flow = 0
    min_flow = 10000
    est_max_flow = 0
    est_min_flow = 0
    flow=0
    flow_list=[]
    for i in Estaciones:
        flow=0
        for subidas in LISTA_FLUJOS[i]:
            flow +=subidas
        flow_list.append(flow)
    print(flow_list)
    for i in Estaciones:
        if min_flow > flow_list[i]:
            min_flow = flow_list[i]
            est_min_flow = i
        if max_flow < flow_list[i]:
            max_flow = flow_list[i]
            est_max_flow = i
    print("considera los dos andenes por estacion")
    print("minimo flujo de subida [pax/dia]:", min_flow, Estaciones[est_min_flow].nombre)
    print("maximo flujo de subida:[pax/dia]", max_flow, Estaciones[est_max_flow].nombre)


########################################################################################################
#------------------Creacion de objetos (linea, estacion, andenes, vagones)------------------------------


Linea10_M = LineaMetro(10) #creo la linea 10.
Estaciones = {}  # estaciones[id_numero]=  objeto de estación
Andenes = {}     # Andenes[Estacion][sentido{0,1}]= objeto de anden.
for i in range(len(ListaE)):
    Estaciones[i] = Linea10_M.add_Estacion(_id=i, name=ListaE[i])   # creo 10 estaciones y las agrego a la L10
    Andenes[i] = [Anden(id_estacion=i, nombre=ListaE[i], sentido=0, arribos=0),  # anden ida
                  Anden(id_estacion=i, nombre=ListaE[i], sentido=1, arribos=0)]  # anden vuelta


#_____________________________________Trenes Y Vagones______________________________
Trenes = {}  # estaciones[id_tren N°]=  objeto de estación
Vagones = []     # Andenes[TREN N°][vagon N°]= objeto de anden.
for i in range(16):
    Trenes[i] = Tren(id=i)  ##creacion de los trenes
    Vagones.append([])   ##creacion lista de vagones de cada tren

for i in Trenes:
    for j in range(Trenes[i].vagones):
        Vagones[i].append(Vagon(id_tren=i, number=j))  ##creacion vagones
        Trenes[i].listavagones.append([])
        Vagones[i][j].puertas = []

# setear origen de trenes
a = 0
for i in range(8):
    a += 1
    delta_llegada_tren = datetime.timedelta(seconds=60*5*a)
    Trenes[i].estacion = 0
    Trenes[i].t_next_arrive = conversion(datetime.time(6, 0, 0), delta_llegada_tren)
    Trenes[i].sentido = 0
    Trenes[i+8].estacion = 9
    Trenes[i+8].t_next_arrive = conversion(datetime.time(6, 0, 0), delta_llegada_tren)
    Trenes[i+8].sentido = 1


#_____________________________________Personas_________________________________________________________________________
personas_id = 0

def procesopoisson(t_inicial, t_final, estacion):
    global personas_id
    arrivals = llegada_personas(t_inicial, t_final)  #arrivals[estacion][persona]
    for j in range(len(arrivals)):   # total estaciones.
        pax = Persona(id_persona = personas_id, origen=estacion, T_llegada=arrivals[j])      #crea objetos_personas
        Estaciones[estacion].Registro.append(pax)
        asignacion(estacion, pax)
        personas_id += 1

#_____________________________________Personas a Anden a mejor fila____________________________________________________
def asignacion(estacion, persona):  ##metodo que ubica pasajeros que llegan a estacion en la mejor fila disponible
        if persona.origen < persona.destino:
            mejor_fila=Andenes[estacion][0].min_fila()
            Andenes[estacion][0].fila_pos[mejor_fila].append(persona)
            Andenes[estacion][0].arribos.append(persona)            #historial_Registro por anden
        else:
            mejor_fila = Andenes[estacion][1].min_fila()
            Andenes[estacion][1].fila_pos[mejor_fila].append(persona)
            Andenes[estacion][1].arribos.append(persona)            #historial_Registro por anden


#_______________________________________Inicializacion_________________________________________________________________

Tasas = schedule(2000, 2000, 2000)
arrivals = 0
[hh_0, mm_0, ss_0] = [5, 0, 0]   #hora inicio simulacion
[hh_f, mm_f, ss_f] = [23, 0, 0]   #hora fin simulacion

t_inicial = datetime.time(hh_0, mm_0, ss_0)
t_final = datetime.time(hh_f, mm_f, ss_f)
delta = datetime.timedelta(seconds=10)     # precision con la que avanza el tiempo


# _______________________________________Simulación____________________________________________________________________
class simulacion:
    global LISTA_TOTAL_EVENTOS
    def __init__(self, t_incial, t_final):
        self.t_aux = t_inicial
        self.t_final = t_final

    def run(self):
        print("inicio de la simulacion:", self.t_aux)
        while self.t_aux < self.t_final:
            #print(self.t_aux)
            for i in Trenes:
                Trenes[i]._get_perfilcarga
                if self.t_aux >= Trenes[i].t_next_arrive:
                    LISTA_TOTAL_EVENTOS.append((Trenes[i].t_next_arrive.strftime("%H:%M:%S"),
                                                "[LLEGA TREN] id_tren:", Trenes[i].id, "a la estacion;",
                                                Estaciones[Trenes[i].estacion].nombre, Trenes[i].estacion, "// Anden :",
                                                Andenes[Trenes[i].estacion][Trenes[i].sentido].sentido))
                    # setea estacion de llegada
                    N_estacion = Trenes[i].estacion
                    # se actualiza el tiempo del ultimo tren que paso por anden:
                    Andenes[N_estacion][Trenes[i].sentido].update_time(self.t_aux)
                    # se genera las personas que llegaron antes de la ultima actualizacion de estacion.
                    procesopoisson(Estaciones[N_estacion].t_last_update,self.t_aux,N_estacion)
                    # actualiza el tiempo para la estacion apenas llege algun tren (para continuar posteriormente con el procesopoisson)
                    Estaciones[N_estacion].t_last_update = self.t_aux

                    #-------------------------------------------------------------------
                    #llega tren, se activa proceso de bajada,subida,cambios de fila
                    Andenes[N_estacion][Trenes[i].sentido].llegada(i, Trenes[i].sentido)

                    #-------------------------------------------------------------------
                    #se define t_next_arrive (proximo tiempo de llegada a la siguiente estacion)
                    tviaje = 4*60
                    tparada = Trenes[i].max_tiempo_bajada()
                    t_salida = conversion(Trenes[i].t_next_arrive, datetime.timedelta(seconds=tparada))
                    Trenes[i]._get_hora(t_salida)

                    #se define proxima estacion
                    Trenes[i].next_station()
                    LISTA_TOTAL_EVENTOS.append((t_salida.strftime("%H:%M:%S"), "[SALIDA TREN] id_tren:", Trenes[i].id,
                                                "proxima estacion;", Estaciones[Trenes[i].estacion].nombre,
                                                Trenes[i].estacion, "// Anden :",
                                                Andenes[Trenes[i].estacion][Trenes[i].sentido].sentido))
                    delta_next = datetime.timedelta(seconds=tviaje + tparada)
                    Trenes[i].t_next_arrive = conversion(Trenes[i].t_next_arrive, delta_next)

            self.t_aux = conversion(self.t_aux, delta)
        print("tiempo final simulacion:", self.t_aux)
    #    print("#####################################################")
#        print("------------------FIN DE LA SIMULACION---------------")#
        print("#####################################################")

#Se ejecuta simulacion
Simulacion = simulacion(t_inicial, t_final)

horarios(2000,2000,2000)
#simular_verboso()
#capacidad_tren(["Tranca Perro", "Nuestra Señora Danielita"])
#datos_anden("Tranca Perro", 0)
patrones()
