from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Clip

@receiver(post_save, sender=Clip)
def process_transcription(sender, instance, **kwargs):
    transcription = instance.transcription
    transcription_list = transcription.split(" ")

    if transcription_list[0] == "R20":
        print("Incendio Forestal")
        # Add your specific logic for "R20-Incendio Forestal" here
    elif transcription_list[0] == "Q7":
        print("Explosión en Fábrica Químicos")
        # Add your specific logic for "Q7-Explosión en Fábrica Químicos" here
    else:
        print(f"No specific action for transcription: {transcription}")

print("hola")