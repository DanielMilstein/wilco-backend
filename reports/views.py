from django.shortcuts import render, redirect
from .forms import ReportForm, ReportObjectiveFormSet
from .models import ReportObjective

def create_report(request):
    existing_objectives = ReportObjective.objects.all()

    if request.method == 'POST':
        report_form = ReportForm(request.POST)
        report_objective_formset = ReportObjectiveFormSet(request.POST)

        if report_form.is_valid():
            report = report_form.save()

            # Handle existing objective selection
            selected_objective_id = request.POST.get('report_objective')
            if selected_objective_id:
                selected_objective = ReportObjective.objects.get(id=selected_objective_id)
                report.report_objective = selected_objective

            if report_objective_formset.is_valid():
                report_objective_formset.instance = report
                report_objective_formset.save()

            report.save()
            return redirect('success')  # Redirect to a success page or the desired page
    else:
        report_form = ReportForm()
        report_objective_formset = ReportObjectiveFormSet()
    
    return render(request, 'create_report.html', {
        'report_form': report_form,
        'report_objective_formset': report_objective_formset,
        'existing_objectives': existing_objectives,
    })
