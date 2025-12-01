from django.shortcuts import render

def home_view(request):
    return render(request, 'home/index.html')


from utils.email_utils import send_resend_email

def send_test(request):
    send_resend_email(
        to="vanessavaldezwhite@gmail.com",
        subject="Test Email from Resend API",
        html="<h2>Hello!</h2><p>Your Resend API is working.</p>"
    )
    return HttpResponse("Email sent!")
