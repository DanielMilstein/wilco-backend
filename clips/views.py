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

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
model = ChatOpenAI(model="gpt-4o-mini")
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

# Crear la cadena de prompts
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
            #Cuando llega un clip mandar al LLM para ver si encuentra uno de los códigos 
            # de inicio y o término
            if long_message == True:
                message = message+" "+transcription
                print(f"Mensaje enviado al LLM {message}")
                response = classify_message(message)
                if response == "0":
                    print(f"LLamar {message}")
                    message = ""
                    long_message = False

            elif long_message == False:
                print(f"Mensaje enviado al LLM {transcription}")
                response = classify_message(transcription)
                if response == "0":
                    print(f"LLamar {transcription}")
                    message = ""
                    long_message = False
                elif response == "1":
                    message += transcription
                    long_message = True
                elif response == "3":
                    message += transcription
                    long_message = True
            
            print(f"long_message: {long_message}")
            print(f"message: {message}")
        
            
            


            
            #Si el código empieza y finaliza, procesar todo de una

            #Si el código solo empieza y aún no finaliza ir almacenando los siguientes clips en una 
            # variable global y procesarlo después


           
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def combinar_palabras(palabras):
    combinaciones = []
    for i in range(len(palabras) - 1):
        combinacion = palabras[i] + palabras[i + 1]  
        combinaciones.append(combinacion)
    return combinaciones

@traceable
def classify_message(message):
    try:
        print(f"El mensaje es: '{message}'")
        response = chain.invoke({"history": history, "user_message": message})
        #print(f"La respuesta es: {response}")

        return response
    except Exception as e:
        # Capturar cualquier error durante la invocación del modelo
        #print(f"Error al invocar el modelo: {e}")
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


