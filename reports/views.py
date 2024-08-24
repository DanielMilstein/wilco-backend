from django.shortcuts import render, redirect
from .forms import ReportForm, ReportObjectiveForm
from .models import ReportObjective, Report
from .serializers import ReportSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .forms import ReportForm
from openai import OpenAI


client = OpenAI()

def create_report(request):
    existing_objectives = ReportObjective.objects.all()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()

            report = Report.objects.last()  # Get the last report that was created


            # OpenAI API
            clip_transcripts = "\n".join([clip.transcription for clip in report.audio_clips.all()])
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization.\
                            I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain\
                            the most important points, providing a coherent and readable summary that could help a person understand the main\
                            points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."},
                            {"role": "system", "content": f'Objective: {report.report_objective}'},
                        {"role": "user", "content": clip_transcripts},
                    ],
                )

                summary = response.choices[0].message.content
            except Exception as e:
                print(e)
                summary = "Error: Unable to generate summary"
            report.summary = summary
            report.save()  # Save the report with the summary

            return render(request, 'view_report.html', {'report': report})
    else:
        form = ReportForm()
    return render(request, 'create_report.html', {'form': form, 'existing_objectives': existing_objectives})

def create_report_objective(request):
    if request.method == 'POST':
        report_objective_form = ReportObjectiveForm(request.POST)

        if report_objective_form.is_valid():
            report_objective_form.save()
            return redirect('create_report')  # Redirect to the create_report view
    else:
        report_objective_form = ReportObjectiveForm()
    
    return render(request, 'create_report_objective.html', {
        'report_objective_form': report_objective_form,
    })



def list_reports(request):
    reports = Report.objects.all()
    return render(request, 'list_reports.html', {'reports': reports})


def view_report(request, id):
    report = Report.objects.get(pk=id)
    return render(request, 'view_report.html', {'report': report})


@api_view(['POST'])
def api_create_report(request):
    if request.method == 'POST':
        serializer = ReportSerializer(data=request.data)

        clip_transcripts = "\n".join([clip.transcription for clip in report.audio_clips.all()])
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization.\
                        I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain\
                        the most important points, providing a coherent and readable summary that could help a person understand the main\
                        points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."},
                        {"role": "system", "content": f'Objective: {report.report_objective}'},
                    {"role": "user", "content": clip_transcripts},
                ],
            )

            summary = response.choices[0].message.content
        except Exception as e:
            print(e)
            summary = "Error: Unable to generate summary"
        report.summary = summary
        report.save()  # Save the report with the summary
        
        # Serialize the report and return it in the response
        serializer = ReportSerializer(report)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_list_reports(request):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_view_report(request, id):
    report = Report.objects.get(pk=id)
    serializer = ReportSerializer(report)
    return Response(serializer.data)

@api_view(['PUT'])
def api_update_report(request, id):
    report = Report.objects.get(pk=id)
    serializer = ReportSerializer(report, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_report(request, id):
    report = Report.objects.get(pk=id)
    report.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_list_report_objectives(request):
    report_objectives = ReportObjective.objects.all()
    serializer = ReportObjectiveSerializer(report_objectives, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_view_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    serializer = ReportObjectiveSerializer(report_objective)
    return Response(serializer.data)

@api_view(['PUT'])
def api_update_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    serializer = ReportObjectiveSerializer(report_objective, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    report_objective.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def api_create_report_objective(request):
    if request.method == 'POST':
        serializer = ReportObjectiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_send_report(request):
    if request.method == 'POST':
        response = client.audio.speech.create(
            model = 'tts-1-hd',
            voice = 'onyx',
            input = request.data['summary']
        )

        response.stream_to_file(f'{request.data["title"]}.mp3')