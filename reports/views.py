from django.shortcuts import render, redirect
from .forms import ReportForm, ReportObjectiveForm
from .models import ReportObjective, Report
from .serializers import ReportSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .forms import ReportForm

def create_report(request):
    existing_objectives = ReportObjective.objects.all()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to a success page or the desired page
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
def create_report(request):
    if request.method == 'POST':
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_reports(request):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def view_report(request, id):
    report = Report.objects.get(pk=id)
    serializer = ReportSerializer(report)
    return Response(serializer.data)

@api_view(['PUT'])
def update_report(request, id):
    report = Report.objects.get(pk=id)
    serializer = ReportSerializer(report, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_report(request, id):
    report = Report.objects.get(pk=id)
    report.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def list_report_objectives(request):
    report_objectives = ReportObjective.objects.all()
    serializer = ReportObjectiveSerializer(report_objectives, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def view_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    serializer = ReportObjectiveSerializer(report_objective)
    return Response(serializer.data)

@api_view(['PUT'])
def update_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    serializer = ReportObjectiveSerializer(report_objective, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_report_objective(request, id):
    report_objective = ReportObjective.objects.get(pk=id)
    report_objective.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def create_report_objective(request):
    if request.method == 'POST':
        serializer = ReportObjectiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)