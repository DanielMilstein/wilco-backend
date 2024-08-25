from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Clip
from .serializers import ClipSerializer
from django.shortcuts import render
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
import re
import what3words
import requests
import json
from django.http import JsonResponse
from reports.views import send_report


model = ChatOpenAI(model="gpt-4o-mini")
history = [
    AIMessage(content="Entendido, estoy listo para clasificar los mensajes."),
]

messages = [
    SystemMessage(content=(
        "Eres una central de asistencia de emergencia. Recibes una lista de dos elementos. "
        "El primer elemento es un código de activación que indica el tipo de emergencia, "
        "y el segundo elemento es el lugar donde ocurrió. Tu tarea es traducir el código de activación "
        "y generar un mensaje de alerta que indique a las unidades que se dirijan al lugar indicado."
        "\n\n"
        "Si el código de activación es:\n"
        "- 'A7': Genera el mensaje 'Alerta: Filtración de gases peligrosos en {lugar}. Diríjanse de inmediato.'\n"
        "- 'R20': Genera el mensaje 'Alerta: Choque en {lugar}. Diríjanse de inmediato.'\n"
        "- 'R22': Genera el mensaje 'Alerta: Incendio Forestal con información en {lugar}. Diríjanse de inmediato.'"
    )),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{user_message}"),
]
chain = ChatPromptTemplate.from_messages(messages) | model | StrOutputParser()

API_KEY = '31PTULZ0'
W3W_API_URL = 'https://api.what3words.com/v3/'
geocoder = what3words.Geocoder(API_KEY)


# Variables globales
message = ""
long_message = False


# Create your views here.
def list_clips(request):
    clips = Clip.objects.all()
    return render(request, 'list_clips.html', {'clips': clips})


def view_clip(request, id):
    clip = Clip.objects.get(pk=id)
    return render(request, 'view_clip.html', {'clip': clip})


@api_view(['POST'])
def api_create_clip(request):
    global message, long_message
    if request.method == 'POST':
        serializer = ClipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            transcription = serializer.validated_data.get('transcription').upper()
            if long_message == True:
                message = message + " " + transcription
                #print(f"Mensaje enviado al LLM {message}")
                response = classify_message(message)
                if response == "0":
                    manejar_mensaje_completo(message)
                    message = ""
                    long_message = False
                elif response == "2":
                    print(F"Clave de inicio, no fue captada. Por favor repetir mensaje")
            else:
                print(f"Mensaje enviado al LLM {transcription}")
                response = classify_message(transcription)
                if response == "0":
                    message = transcription
                    claves,direccion,mensaje_alerta = manejar_mensaje_completo(message)
                    manejar_alerta(claves,direccion,mensaje_alerta)
                    message = ""
                    long_message = False
                elif response == "1" or response == "3":
                    message += transcription
                    long_message = True
                elif response == "2":
                    print(F"Clave de inicio, no fue captada. Por favor repetir mensaje")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def obtener_claves(mensaje):
    # Expresión regular ajustada para manejar casos como R20, R 20, y R,20
    #print(f"mensaje {mensaje}")
    pattern = r"\b(R\s*,?\s*20|R\s*,?\s*22|A\s*,?\s*7|E\s*,?\s*1)\b"
    
    # Buscar todas las coincidencias en el string
    matches = re.findall(pattern, mensaje)
    
    # Limpiar las claves encontradas (eliminar espacios y comas)
    claves = [re.sub(r"[\s,]", "", match) for match in matches]
    
    #print(f"Claves: {claves}")
    return claves

def separar_claves_y_texto(mensaje, claves):
    # Expresión regular flexible para las claves ya obtenidas
    pattern = r"|".join([re.escape(clave) for clave in claves])
    pattern = fr"\b({pattern})\b"

    # Lista para almacenar las partes separadas
    partes_separadas = []
    ultimo_indice = 0

    # Recorrer las coincidencias de la expresión regular
    for match in re.finditer(pattern, mensaje):
        inicio, fin = match.span()
        # Agregar el texto intermedio a la lista, si existe
        if inicio > ultimo_indice:
            texto_intermedio = mensaje[ultimo_indice:inicio].strip(", ")
            if texto_intermedio:
                partes_separadas.append(texto_intermedio)
        # Agregar la clave encontrada a la lista
        partes_separadas.append(match.group())
        ultimo_indice = fin

    # Agregar cualquier texto restante después de la última clave
    if ultimo_indice < len(mensaje):
        texto_restante = mensaje[ultimo_indice:].strip(", ")
        if texto_restante:
            partes_separadas.append(texto_restante)

    return partes_separadas

def procesar_mensaje(mensaje):
    claves = obtener_claves(mensaje)
    #print(f"Claves encontradas: {claves}")
    partes_separadas = separar_claves_y_texto(mensaje, claves)
    
    return claves,partes_separadas

def ordenar_mensaje(partes_separadas):
    #print(f"Entrando partes separadas {partes_separadas}")
    mensaje_ordenado = []
    for parte in partes_separadas:
        if parte in ["R20","R22","A7"]:
            mensaje_ordenado.insert(0,parte)
        elif len(mensaje_ordenado)>0 and parte not in ["E,1","E1"]:
            mensaje_ordenado.append(parte)
        elif parte in ["E,1","E1"]:
            break
    mensaje_ordenado.append("E1")
    #print(f"Mensaje ordenado: {mensaje_ordenado} ")

    return mensaje_ordenado

def separar_string(texto):
    partes = re.split(r'[,\s]+', texto)
    partes = [parte for parte in partes if parte]
    return partes

def encontrar_clave_coordenadas(mensaje_ordenado):
    claves_coordenadas = []
    if len(mensaje_ordenado)>1:
        clave_coordenadas = mensaje_ordenado[1]
        claves = separar_string(clave_coordenadas)
        for i in range(3):
            try:
                claves_coordenadas.append(claves[i])
            except:
                pass

    return claves_coordenadas

def traducir_coordenadas(clave_coordenadas):
    direccion = ""
    for lugar in clave_coordenadas:
        direccion = direccion +"." + lugar
    
    direccion = direccion.strip('.')
    direccion= re.sub(r'\.+', '.', direccion)
    direccion_traducida = get_address(direccion)
    print(f"direccion {direccion}")
    print(f"direccion {direccion_traducida}")
    return direccion_traducida

def generar_alerta(clave_coordenadas,direccion):
    try:
        codigo_activacion = clave_coordenadas[0]
        user_message = f"El código de activación es {codigo_activacion} y el lugar es {direccion}."
        response = chain.invoke({"history": history, "user_message": user_message})
        print(f"Mensaje de alerta: {response}")
        return response
    except Exception as e:
        print(f"Error al invocar el modelo: {e}")
        return "Hubo un error al procesar tu solicitud. Por favor, intenta de nuevo."


def manejar_alerta(claves, direccion, mensaje_alerta):
    all_phone_numbers = {
        'bomberos'    :  "+56990972126",
        'ambulancia'  :  "+56942545982",
        'carabineros' : "+56968404532"
                    }
    try:
        clave_inicio = claves[0]
        if clave_inicio in ["R20","R,20","r20"]:
            print("CHOQUE, llamar a bomberos y ambulancia")
            print(mensaje_alerta)
            # Llamar a send report con el mensaje generado con json y los números de teléfono
            title = "Emergencia_R20"
            summary = mensaje_alerta
            phone_numbers = [all_phone_numbers['bomberos'], all_phone_numbers['ambulancia']]
            send_report(title = title, summary = summary, phone_numbers = phone_numbers)

        elif clave_inicio in ["R22","R,22","r22"]:
            print("INCENDIO FORESTAL BIDUBIDU LLAMAR A BOMBEROS y carabineros")
            print(mensaje_alerta)
            # Llamar a send report con el mensaje generado con json y los números de teléfono
            title = "Emergencia_R22"
            summary = mensaje_alerta
            phone_numbers = [all_phone_numbers['bomberos'], all_phone_numbers['carabineros']]
            send_report(title = title, summary = summary, phone_numbers = phone_numbers)

        elif clave_inicio in ["A7","A,7","a7"]:
            print("QUIMICOS llamar a bomberos y ambulancia")
            print(mensaje_alerta)
            # Llamar a send report con el mensaje generado con json y los números de teléfono
            title = "Emergencia_A7"
            summary = mensaje_alerta
            phone_numbers = [all_phone_numbers['bomberos'], all_phone_numbers['ambulancia']]
            send_report(title = title, summary = summary, phone_numbers = phone_numbers)

    except Exception as e:
        print(f"Error al manejar la alerta: {e}")




def classify_message(message):
    # Define the regular expression patterns for start and end keys
    start_keys_pattern = r"\b(R\s*,?\s*20|R\s*,?\s*22|A\s*,?\s*7)\b"
    end_key_pattern = r"\b(E\s*,?\s*1)\b"
    
    # Find start and end keys in the message
    start_keys = re.findall(start_keys_pattern, message)
    end_keys = re.findall(end_key_pattern, message)
    
    # Classify the message based on the presence of start and end keys
    if start_keys and end_keys:
        return "0"  # Both start and end keys are present
    elif start_keys and not end_keys:
        return "1"  # Only start keys are present
    elif not start_keys and end_keys:
        return "2"  # Only end key is present
    else:
        return "3"  # Neither start nor end keys are present

def manejar_mensaje_completo(message):
    #print(f"LLamar {message}")
    claves, partes_separadas = procesar_mensaje(message)
    #print(f"Claves y texto: {claves}")
    
    mensaje_ordenado = ordenar_mensaje(partes_separadas)
    clave_coordenadas = encontrar_clave_coordenadas(mensaje_ordenado)
    
    #print(f"COORDENADAS: {clave_coordenadas}")
    
    direccion = traducir_coordenadas(clave_coordenadas)
    #ENVIAR A PEPE
    
    generar_alerta(claves, clave_coordenadas)

    # Llamar a send report con el mensaje generado






def get_address(direccion_traducida):
    api_key = API_KEY
    words = direccion_traducida
    try:
        url = 'https://api.what3words.com/v3/convert-to-coordinates?'
        params = {
            'words': words,
            'key': api_key,
            'lang': 'es'
            }
        response = requests.get(url, params=params)
        response_data = response.json()
        print(response_data, "URL")
        print(api_key)

        if 'coordinates' in response_data:
            lat = response_data['coordinates']['lat']
            lon = response_data['coordinates']['lng']
            return (f"latitude {lat} longitude {lon}")
    except:
        return (f"No se encontraron las coordenadas")
      

    

@api_view(['GET'])
def api_list_clips(request):
    clips = Clip.objects.all()
    serializer = ClipSerializer(clips, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_view_clip(request, id):
    clip = Clip.objects.get(pk=id)
    serializer = ClipSerializer(clip)
    return Response(serializer.data)

@api_view(['PUT'])
def api_update_clip(request, id):
    clip = Clip.objects.get(pk=id)
    serializer = ClipSerializer(clip, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_clip(request, id):
    clip = Clip.objects.get(pk=id)
    clip.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
