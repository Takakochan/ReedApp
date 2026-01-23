from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import ContactForm

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Create email content
            email_subject = f"Reed App Contact: {subject}"
            email_message = f"""
New contact form submission from Reed App:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent from the Reed App contact form.
            """
            
            try:
                # Send email
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['takakokunugi@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you! Your message has been sent successfully. We will get back to you soon.')
                return redirect('contact:contact')
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})
