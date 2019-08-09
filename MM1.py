# -*- coding: utf-8 -*-
import numpy as np
#############################################################################################3
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

#Número de clientes en cola
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Gráfica en tiempo real")

p = win.addPlot(title="Número de clientes en cola")
curva = p.plot(pen='y')
p.setRange(yRange=[0, 15])

p2 = win.addPlot(title="Utilización del servidor")
curva2 = p2.plot(pen='y')
p2.setRange(yRange=[0, 2])

def Update():
   global curva, reloj_sim, num_cli_sim, servidor_sim

   # Actualizamos reloj_sim y num_cli_sim

   curva.setData(reloj_sim, num_cli_sim)
   curva2.setData(reloj_sim, servidor_sim)

   QtGui.QApplication.processEvents()

#############################################################################################3

#Variables globales
CANT_TIPOS_EVENTOS = 2#Defimos número de tipos de eventos (usamos 2: arribos y llegadas)
#Criterio de estabilidad MM1: la tasa de servicio debe ser mayor que la tasa de llegada
TIEMPO_MEDIO_LLEGADA = 2.0#tiempo medio de llegada **LAMDA
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
reloj_sim = []
servidor_sim = []
num_cli_sim = []

#Subrutina init
def init():
    global TIEMPO_TOT_DEMORAS,ARREGLO_PROX_EV, TIEMPO, ESTADO, NCC, TIEMPO_ULT_EV, NUM_CLIENTES, TIEMPO_TOT_DEMORAS, ANCC
    #inicializamos.0 el reloj de simulación
    TIEMPO = 0

    #inicializamos variables de estado
    ESTADO = 0 # 0: si el servidor está ocioso - 1: si el servidor está ocupado
    NCC=0 #número de clientes en cola
    TIEMPO_ULT_EV=0.0 #tiempo del último evento que cambió el número en cola

    #inicializamos contadores estadísticos
    NUM_CLIENTES = 0 #número de clientes que completaron sus demoras
    TIEMPO_TOT_DEMORAS=0.0 #tiempo total de los clientes que completaron sus demoras
    ANCC=0.0 #área debajo de la función número de clientes en cola

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
    #print('ARREGLO_PROX_EV',ARREGLO_PROX_EV)

    #determinamos el tipo de evento del próximo evento que va a ocurrir
    for i in range(1,CANT_TIPOS_EVENTOS+1):
        if ARREGLO_PROX_EV[i] < TIEMPO_PROX_EV:
            TIEMPO_PROX_EV = ARREGLO_PROX_EV[i]
            TIPO_PROX_EV = i
        #print('TIEMPO_PROX_EV',TIEMPO_PROX_EV)
    #print("TIPO_PROX_EV timing", TIPO_PROX_EV)

    #veo que la lista de eventos no esté vacia
    if TIPO_PROX_EV > 0:
        #print('TIPO_PROX_EV > 0')
        TIEMPO = ARREGLO_PROX_EV[TIPO_PROX_EV]

        #print('TIEMPO', TIEMPO)

    #si la lista de eventos está vacía, fin de simulación
    else:
        print('Lista de eventos vacía. Fin de la simulación')

    return None

#Subrutina arribos
def arrive():
    #print("arribe")
    global ESTADO,TIEMPO_TOT_DEMORAS,NUM_CLIENTES,ARREGLO_TIEMPOS_ARRIBO,ARREGLO_PROX_EV,TIEMPO,TIEMPO_MEDIO_LLEGADA,ANCC,NCC,TIEMPO_ULT_EV,TOTAL_CLIENTES,DEMORA,TIEMPO_MEDIO_SERVICIO,TIEMPO_SERV_ACUM
    #programamos el próximo arribo
    ARREGLO_PROX_EV[1] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_LLEGADA)#stats.expon(TIEMPO_MEDIO_LLEGADA).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de llegada
    reloj_sim.append(ARREGLO_PROX_EV[1])

    #print("ESTADO",ESTADO)
    #Vemos el estado del servidor, si está vacío (=0) comienza el servicio el cliente que arribó
    if ESTADO == 1: #servidor ocupado, actualizamos área debajo de la función número de clientes en cola
        #print("servidor ocupado")
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
        servidor_sim.append(1)
    else:
        #print("servidor libre",NUM_CLIENTES)
        #servidor ocioso, cliente tiene demora nula
        DEMORA = 0.0

        #cambiamos estado del servidor a ocupado
        ESTADO = 1

        TIEMPO_TOT_DEMORAS += DEMORA

        #agregamos uno al número de clientes que completaron su demora
        NUM_CLIENTES += 1
        #print("NUM_CLIENTES + 1",NUM_CLIENTES)

        #generamos la salida
        ARREGLO_PROX_EV[2] = TIEMPO + np.random.exponential(1/TIEMPO_MEDIO_SERVICIO)#stats.expon(TIEMPO_MEDIO_SERVICIO).rvs() #tiempo actual + valor generado exponencialmente con lambda = tiempo medio de servicio

        TIEMPO_SERV_ACUM += (ARREGLO_PROX_EV[2] - TIEMPO)
        servidor_sim.append(0)

    num_cli_sim.append(NCC)
    Update()

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
    print("Sistema de cola simple")
    print("Tiempo medio entre arribos:", TIEMPO_MEDIO_LLEGADA,' minutos')#, '. Tasa de llegadas:', 1/TIEMPO_MEDIO_LLEGADA)
    print("Tiempo medio de servicio:", TIEMPO_MEDIO_SERVICIO,' minutos')#, '. Tasa de servicio:', 1/TIEMPO_MEDIO_SERVICIO)
    print("Número máximo de clientes:", TOTAL_CLIENTES)

    #VALORES TEÓRICOS
    promedio_clientes_en_cola = (TIEMPO_MEDIO_LLEGADA**2)/(TIEMPO_MEDIO_SERVICIO*(TIEMPO_MEDIO_SERVICIO-TIEMPO_MEDIO_LLEGADA))
    promedio_demora_en_cola = TIEMPO_MEDIO_LLEGADA/(TIEMPO_MEDIO_SERVICIO*(TIEMPO_MEDIO_SERVICIO-TIEMPO_MEDIO_LLEGADA))
    promedio_utilizacion_servidor = TIEMPO_MEDIO_LLEGADA/TIEMPO_MEDIO_SERVICIO

    AVGNCC = ANCC/TIEMPO
    print("Número promedio de clientes en cola", AVGNCC,'. Valor teórico: ',promedio_clientes_en_cola)

    AVGDEL = TIEMPO_TOT_DEMORAS/NUM_CLIENTES
    print("Demora promedio en cola:",AVGDEL,' minutos','. Valor teórico: ',promedio_demora_en_cola)

    AVGUTSERV = TIEMPO_SERV_ACUM/TIEMPO
    print("Utilización promedio del servidor:",AVGUTSERV,'. Valor teórico: ',promedio_utilizacion_servidor)
    #print(ANCC, NCC)
    #print(reloj_sim)
    #print(servidor_sim)
    #print(num_cli_sim)
    #print(len(reloj_sim),len(servidor_sim),len(num_cli_sim))
    return None

#Programa principal
def main_program():
    #print("entramos a main program")
    global NUM_CLIENTES, TOTAL_CLIENTES, TIPO_PROX_EV,TIEMPO_PROX_EV
    #iniciamos la simulación, llamamos subrutina init
    init()

    #si la simulación terminó, llamamos la rutina de reportes y fin de la simulación
    while NUM_CLIENTES <= TOTAL_CLIENTES:#no terminó simulación
        #print("NUM_CLIENTES",NUM_CLIENTES,"TOTAL_CLIENTES",TOTAL_CLIENTES)
        #determinamos próximo evento, llamamos subrutina timing
        timing()

        #vemos qué tipo de evento es el próximo
        if TIPO_PROX_EV == 1:
            #print('es arribo')
            #llamamos la rutina de arribos de eventos
            arrive()
        else:
            #print('es partida')
            #llamamos la rutina de partidas
            depart()

        reloj_sim.append(ARREGLO_PROX_EV[1])
        if ESTADO == 1: #servidor ocupado, actualizamos área debajo de la función número de clientes en cola
            servidor_sim.append(1)
        else:
            servidor_sim.append(0)
        num_cli_sim.append(NCC)
        Update()

    else:#terminó simulación
        #llamamos a la subrutina de reportes
        report()

    return True



if __name__ == '__main__':
    main_program()


#while True: Update() #Actualizamos todo lo rápido que podamos.

pg.QtGui.QApplication.exec_()
#############################################################################################3
