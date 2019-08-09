# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import statistics

#Variables globales
CANT_TIPOS_EVENTOS = 2#Defimos número de tipos de eventos (usamos 2: arribos y llegadas)
#Criterio de estabilidad MM1: la tasa de servicio debe ser mayor que la tasa de llegada
TIEMPO_MEDIO_LLEGADA = 2.0#tiempo medio de llegada **lambda
TIEMPO_MEDIO_SERVICIO = 3.0#tiempo medio de servicio **MU
TOTAL_CLIENTES = 200#número total de clientes cuyas demoras serán observadas
TIEMPO = 0.0#Reloj de simulación
ESTADO = 0 # 0: si el servidor está ocioso - 1: si el servidor está ocupado
ANCC=0.0 #área debajo de la función número de clientes en cola
NCC=0 #número de clientes en cola
TIEMPO_ULT_EV=0.0 #tiempo del último evento que cambió el número en cola
NUM_CLIENTES = 0 #número de clientes que completaron sus demoras
ARREGLO_PROX_EV = np.zeros([CANT_TIPOS_EVENTOS+1]) #arreglo que contiene el tiempo del próximo evento I en la posición ARREGLO_PROX_EV[I]
TIEMPO_TOT_DEMORAS=0.0 #tiempo total de los clientes que completaron sus demoras
TIEMPO_PROX_EV = 0.0 #tiempo de ocurrencia del próximo evento a ocurrir
TIPO_PROX_EV = 0 #tipo de evento (1: ARRIBOS o 2: PARTIDAS) del próximo evento que va a ocurrir
ARREGLO_TIEMPOS_ARRIBO = np.zeros([TOTAL_CLIENTES+1]) #tiempo de arribo del cliente I que está esperando en cola
TIEMPO_SERV_ACUM = 0.0

#Subrutina init
def init():
    global TIEMPO, ESTADO, NCC, TIEMPO_ULT_EV, NUM_CLIENTES, TIEMPO_TOT_DEMORAS, ANCC, ARREGLO_PROX_EV, TIEMPO_PROX_EV, TIPO_PROX_EV, ARREGLO_TIEMPOS_ARRIBO,TIEMPO_SERV_ACUM
    #inicializamos.0 el reloj de simulación
    TIEMPO = 0.0

    #inicializamos variables de estado
    ESTADO = 0 # 0: si el servidor está ocioso - 1: si el servidor está ocupado
    NCC=0 #número de clientes en cola
    TIEMPO_ULT_EV=0.0 #tiempo del último evento que cambió el número en cola

    #inicializamos contadores estadísticos
    NUM_CLIENTES = 0 #número de clientes que completaron sus demoras
    TIEMPO_TOT_DEMORAS=0.0 #tiempo total de los clientes que completaron sus demoras
    ANCC=0.0 #área debajo de la función número de clientes en cola

    ARREGLO_PROX_EV = np.zeros([CANT_TIPOS_EVENTOS+1]) #arreglo que contiene el tiempo del próximo evento I en la posición ARREGLO_PROX_EV[I]
    TIEMPO_PROX_EV = 0.0 #tiempo de ocurrencia del próximo evento a ocurrir
    TIPO_PROX_EV = 0 #tipo de evento (1: ARRIBOS o 2: PARTIDAS) del próximo evento que va a ocurrir
    ARREGLO_TIEMPOS_ARRIBO = np.zeros([TOTAL_CLIENTES+1]) #tiempo de arribo del cliente I que está esperando en cola
    TIEMPO_SERV_ACUM = 0.0

    #inicializamos lista de eventos. Como no hay clientes en cola, se define el tiempo de la próxima salida en infinito.
    ARREGLO_PROX_EV[1] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_LLEGADA)#stats.expon(TIEMPO_MEDIO_LLEGADA).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de llegada
    ARREGLO_PROX_EV[2] = 10.0**30 #Lo seteamos en infinito

    TIEMPO_SERV_ACUM = 0.0

    return None

#Subrutina timing
def timing():
    global TIEMPO,ARREGLO_PROX_EV, TIPO_PROX_EV, TIEMPO_PROX_EV, CANT_TIPOS_EVENTOS
    TIEMPO_PROX_EV = 10.0**29 #tiempo de ocurrencia del próximo evento a ocurrir
    TIPO_PROX_EV = 0

    #determinamos el tipo de evento del próximo evento que va a ocurrir
    for i in range(1,CANT_TIPOS_EVENTOS+1):
        if ARREGLO_PROX_EV[i] < TIEMPO_PROX_EV:
            TIEMPO_PROX_EV = ARREGLO_PROX_EV[i]
            TIPO_PROX_EV = i

    #veo que la lista de eventos no esté vacia
    if TIPO_PROX_EV > 0:
        TIEMPO = ARREGLO_PROX_EV[TIPO_PROX_EV]

    #si la lista de eventos está vacía, fin de simulación
    else:
        print('Lista de eventos vacía. Fin de la simulación')

    return None

#Subrutina arribos
def arrive():
    global ESTADO,TIEMPO_TOT_DEMORAS,NUM_CLIENTES,ARREGLO_TIEMPOS_ARRIBO,ARREGLO_PROX_EV,TIEMPO,TIEMPO_MEDIO_LLEGADA,ANCC,NCC,TIEMPO_ULT_EV,TOTAL_CLIENTES,DEMORA,TIEMPO_MEDIO_SERVICIO,TIEMPO_SERV_ACUM
    #programamos el próximo arribo
    ARREGLO_PROX_EV[1] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_LLEGADA)#stats.expon(TIEMPO_MEDIO_LLEGADA).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de llegada

    #Vemos el estado del servidor, si está vacío (=0) comienza el servicio el cliente que arribó
    if ESTADO == 1: #servidor ocupado, actualizamos área debajo de la función número de clientes en cola
        ANCC += NCC*(TIEMPO-TIEMPO_ULT_EV)
        TIEMPO_ULT_EV = TIEMPO

        #agregamos uno al número de clientes en cola
        NCC += 1
        #verificamos condición de máximos clientes en cola TOTAL_CLIENTES
        if NCC <= TOTAL_CLIENTES:
            #ARREGLO_TIEMPOS_ARRIBO: tiempo de arribo del cliente I que está esperando en cola
            ARREGLO_TIEMPOS_ARRIBO[NCC] = TIEMPO
        else:
            print('Se alcanzó el límite de clientes a observar')
    else:
        #servidor ocioso, cliente tiene demora nula
        DEMORA = 0.0

        #cambiamos estado del servidor a ocupado
        ESTADO = 1

        TIEMPO_TOT_DEMORAS += DEMORA

        #agregamos uno al número de clientes que completaron su demora
        NUM_CLIENTES += 1

        #generamos la salida
        ARREGLO_PROX_EV[2] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_SERVICIO)#stats.expon(TIEMPO_MEDIO_SERVICIO).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de servicio

        TIEMPO_SERV_ACUM += (ARREGLO_PROX_EV[2] - TIEMPO)

    return None

#Subrutina partidas
def depart():
    global NCC, ESTADO, ANCC, TIEMPO, TIEMPO_ULT_EV, ARREGLO_TIEMPOS_ARRIBO, TIEMPO_TOT_DEMORAS, ARREGLO_PROX_EV, DEMORA, NUM_CLIENTES, TIEMPO_MEDIO_SERVICIO,TIEMPO_SERV_ACUM
    #si la cola está vacía, cambiamos el estado del servidor a ocioso
    #y seteamos el tiempo del próximo evento de partida en infinito
    if NCC > 0:
        #la cola no está vacía
        #actualizamos el área debajo de la función de números de clientes en cola
        ANCC += NCC*(TIEMPO-TIEMPO_ULT_EV)
        TIEMPO_ULT_EV = TIEMPO

        #restamos uno del número de clientes en cola
        NCC -= 1#NCC

        #calculamos la demora del cliente que está comenzando el servicio
        DEMORA = TIEMPO - ARREGLO_TIEMPOS_ARRIBO[1]#Para mi esto está mal, en lugar de 1 debería ser NCC

        TIEMPO_TOT_DEMORAS += DEMORA
        #agregamos uno al número de clientes que completaron su demora
        NUM_CLIENTES += 1
        #calculamos la partida
        ARREGLO_PROX_EV[2] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_SERVICIO)#stats.expon(TIEMPO_MEDIO_SERVICIO).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de servicio
        TIEMPO_SERV_ACUM += (ARREGLO_PROX_EV[2] - TIEMPO)

        #si la cola no está vacía, mover cada cliente de la cola en una posición
        if NCC != 0:
            for i in range(1, NCC + 1):
                j = i + 1
                ARREGLO_TIEMPOS_ARRIBO[i]=ARREGLO_TIEMPOS_ARRIBO[j]

    else:
        #marcamos el servidor como libre
        ESTADO = 0
        ARREGLO_PROX_EV[2] = 10.0**30 #Lo seteamos en infinito

    return None

#Subrutina reportes
def report():
    global TIEMPO_MEDIO_LLEGADA, TIEMPO_MEDIO_SERVICIO, TOTAL_CLIENTES, NUM_CLIENTES, ANCC, TIEMPO_TOT_DEMORAS, TIEMPO, TIEMPO_SERV_ACUM
    #mostramos encabezado y parámetros de entrada
    #print("Sistema de cola simple")
    #print("Tiempo medio entre arribos:", TIEMPO_MEDIO_LLEGADA,' minutos')#, '. Tasa de llegadas:', 1/TIEMPO_MEDIO_LLEGADA)
    #print("Tiempo medio de servicio:", TIEMPO_MEDIO_SERVICIO,' minutos')#, '. Tasa de servicio:', 1/TIEMPO_MEDIO_SERVICIO)
    #print("Número máximo de clientes:", TOTAL_CLIENTES)

    AVGNCC = ANCC/TIEMPO
    #print("Número promedio de clientes en cola", AVGNCC)

    AVGDEL = TIEMPO_TOT_DEMORAS/NUM_CLIENTES
    #print("Demora promedio en cola:",AVGDEL,' minutos')

    AVGUTSERV = TIEMPO_SERV_ACUM/TIEMPO
    #print("Utilización promedio del servidor:",AVGUTSERV)

    return AVGNCC, AVGDEL, AVGUTSERV

#Programa principal
#l:lambda; mu:mu
def main_program(l, mu):
    #print("entramos a main program")
    global NUM_CLIENTES, TOTAL_CLIENTES, TIPO_PROX_EV,TIEMPO_PROX_EV, TIEMPO_MEDIO_LLEGADA, TIEMPO_MEDIO_SERVICIO

    TIEMPO_MEDIO_LLEGADA = l

    TIEMPO_MEDIO_SERVICIO = mu

    reporte = ()
    #iniciamos la simulación, llamamos subrutina init
    init()

    #si la simulación terminó, llamamos la rutina de reportes y fin de la simulación
    while NUM_CLIENTES <= TOTAL_CLIENTES:#no terminó simulación
        #determinamos próximo evento, llamamos subrutina timing
        timing()

        #vemos qué tipo de evento es el próximo
        if TIPO_PROX_EV == 1:
            #llamamos la rutina de arribos de eventos
            arrive()
        else:
            #llamamos la rutina de partidas
            depart()

    else:#terminó simulación
        #llamamos a la subrutina de reportes
        reporte = report()

    return reporte

if __name__ == '__main__':
    clientes_en_cola = []
    demora_en_cola = []
    utilizacion_servidor = []

    #Valores teóricos
    promedio_clientes_en_cola = (TIEMPO_MEDIO_LLEGADA**2)/(TIEMPO_MEDIO_SERVICIO*(TIEMPO_MEDIO_SERVICIO-TIEMPO_MEDIO_LLEGADA))
    promedio_demora_en_cola = TIEMPO_MEDIO_LLEGADA/(TIEMPO_MEDIO_SERVICIO*(TIEMPO_MEDIO_SERVICIO-TIEMPO_MEDIO_LLEGADA))
    promedio_utilizacion_servidor = TIEMPO_MEDIO_LLEGADA/TIEMPO_MEDIO_SERVICIO

    n = 1000
    l = 2 #lamda
    mu = 3
    for i in range(n):
        rta = main_program(l,mu)
        clientes_en_cola.append(rta[0])
        demora_en_cola.append(rta[1])
        utilizacion_servidor.append(rta[2])

    lista_clientes_en_cola = []
    lista_demora_en_cola = []
    lista_utilizacion_servidor = []

    for i in range(n):
        clientes_en_cola_i = statistics.mean(clientes_en_cola[:i+1])
        lista_clientes_en_cola.append([i,clientes_en_cola_i])
        demora_promedio_i = statistics.mean(demora_en_cola[:i+1])
        lista_demora_en_cola.append([i,demora_promedio_i])
        utilizacion_servidor_i = statistics.mean(utilizacion_servidor[:i+1])
        lista_utilizacion_servidor.append([i,utilizacion_servidor_i])

    plt.title('Número promedio de clientes en cola')  # Colocamos el título
    x1, y1 = zip(*[m for m in lista_clientes_en_cola])
    p1 = plt.plot(x1, y1,'ro-', markersize=0.5, lw=0.5,color='g')
    #lambda=5 mu =8
    #x2, y2 = zip(*[m for m in lista_clientes_en_cola_2])
    #p2 = plt.plot(x2, y2,'ro-', markersize=0.5, lw=0.5,color='r')
    #plt.legend((p1[0], p2[0]), ('lambda=2; mu=3', 'lambda=5; mu=9'))
    plt.plot([promedio_clientes_en_cola for i in range(n)], linestyle='dashed', color='blue')
    plt.grid(True)
    plt.show()

    x, y = zip(*[m for m in lista_demora_en_cola])
    plt.title('Número promedio de demora en cola')  # Colocamos el título
    plt.plot(x, y,'ro-', markersize=0.5, lw=0.5,color='g')
    plt.plot([promedio_demora_en_cola for i in range(n)], linestyle='dashed', color='blue')
    plt.grid(True)
    plt.show()

    x, y = zip(*[m for m in lista_utilizacion_servidor])
    plt.title('Utilización promedio del servidor')  # Colocamos el título
    plt.plot(x, y,'ro-', markersize=0.5, lw=0.5,color='g')
    plt.plot([promedio_utilizacion_servidor for i in range(n)], linestyle='dashed', color='blue')
    plt.grid(True)
    plt.show()
