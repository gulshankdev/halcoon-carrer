from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmployerEnquiryForm


def enquiry_view(request):
    """
    Employer hiring enquiry intake form.
    Captures staffing requirements, company parameters, and contact person details.
    """
    if request.method == 'POST':
        form = EmployerEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            request.session['latest_enquiry_company'] = enquiry.company_name
            messages.success(
                request,
                f"Thank you, {enquiry.contact_person}. Your hiring mandate for {enquiry.company_name} has been received."
            )
            return redirect('employers:enquiry_success')
        else:
            messages.error(
                request,
                "Please verify the information provided and address the errors highlighted below."
            )
    else:
        form = EmployerEnquiryForm()

    return render(request, 'employers/enquiry.html', {'form': form})


def enquiry_success_view(request):
    """
    Confirmation screen shown after successful employer enquiry submission.
    """
    company_name = request.session.pop('latest_enquiry_company', 'your company')
    return render(request, 'employers/enquiry_success.html', {'company_name': company_name})
