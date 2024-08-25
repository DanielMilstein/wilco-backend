from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Clip
from .serializers import ClipSerializer
from django.shortcuts import render
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
import re

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
model = ChatOpenAI(model="gpt-4o-mini")

# Primer modelo
history = [
    AIMessage(content="Entendido, estoy listo para clasificar los mensajes."),
]

messages = [
    SystemMessage(content=(
        "Tu tarea es clasificar el mensaje basado en la presencia de ciertas claves. "
        "Clasifica el mensaje de la siguiente manera: "
        "Devuelve '0' si el mensaje contiene tanto una clave de inicio (R20, R22, A7) como la clave de fin (E1). "
        "Devuelve '1' si el mensaje contiene solo una clave de inicio (R20, R22, A7) pero no contiene la clave de fin (E1). "
        "Devuelve '2' si el mensaje contiene solo la clave de fin (E1) pero no contiene ninguna clave de inicio (R20, R22, A7). "
        "Devuelve '3' si el mensaje no contiene ninguna de las claves mencionadas."
    )),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{user_message}"),
]

chain = ChatPromptTemplate.from_messages(messages) | model | StrOutputParser()


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
            transcription = serializer.validated_data.get('transcription')
            if long_message == True:
                message = message + " " + transcription
                print(f"Mensaje enviado al LLM {message}")
                response = classify_message(message)
                if response == "0":
                    print(f"LLamar {message}")
                    claves,partes_separadas= procesar_mensaje(message)
                    print(f"Claves y texto: {claves}")
                    mensaje_ordenado = ordenar_mensaje(partes_separadas)
                    clave_coordenadas = encontrar_clave_coordenadas(mensaje_ordenado)
                    print(f"COORDENADAS: {clave_coordenadas}")

                    message = ""
                    long_message = False
                elif response == "2":
                    print(F"Clave de inicio, no fue captada. Por favor repetir mensaje")
            else:
                print(f"Mensaje enviado al LLM {transcription}")
                response = classify_message(transcription)
                if response == "0":
                    message = transcription
                    print(f"LLamar {message}")
                    claves,partes_separadas= procesar_mensaje(message)
                    print(f"Claves y texto: {claves}")
                    mensaje_ordenado = ordenar_mensaje(partes_separadas)
                    clave_coordenadas = encontrar_clave_coordenadas(mensaje_ordenado)
                    print(f"COORDENADAS: {clave_coordenadas}")
                    

                    message = ""
                    long_message = False
                elif response == "1":
                    message += transcription
                    long_message = True
                elif response == "2":
                    print(F"Clave de inicio, no fue captada. Por favor repetir mensaje")
                elif response == "3":
                    message += transcription
                    long_message = True
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def obtener_claves(mensaje):
    # Expresión regular ajustada para manejar casos como R20, R 20, y R,20
    print(f"mensaje {mensaje}")
    pattern = r"\b(R\s*,?\s*20|R\s*,?\s*22|A\s*,?\s*7|E\s*,?\s*1)\b"
    
    # Buscar todas las coincidencias en el string
    matches = re.findall(pattern, mensaje)
    
    # Limpiar las claves encontradas (eliminar espacios y comas)
    claves = [re.sub(r"[\s,]", "", match) for match in matches]
    
    print(f"Claves: {claves}")
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
    print(f"Mensaje ordenado: {mensaje_ordenado} ")

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
    pass

def asignar_operacion(mensaje_ordenado):
    if mensaje_ordenado[0] == "R20":
        print("LLAMAR BOMBEROS")
    


@traceable
def classify_message(message):
    try:
        print(f"El mensaje es: '{message}'")
        response = chain.invoke({"history": history, "user_message": message})
        return response
    except Exception as e:
        print(f"Error al invocar el modelo: {e}")
        return "Hubo un error al procesar tu solicitud. Por favor, intenta de nuevo."


@api_view(['GET'])
def api_list_clips(request):
    clips = Clip.objects.all()
    serializer = ClipSerializer(clips, many=True)
    #for clip in serializer:
        #print(f"Transcription for '{clip.title}': {clip.transcription}")
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


