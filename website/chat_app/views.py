from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UploadedCSV
import datetime
@login_required #Checks to see if user is logged in - if not it redirects them to login page
def upload_view(request):
    if request.method == 'POST': #Listens for a submitted form/ for a POST request from the html
        if 'csv_file' in request.FILES: 
            file = request.FILES['csv_file'] #If csv_file (this is the name of the csv file form field) is present it stores it as a variable
            csv_file = UploadedCSV(
                raw_csv=file,
                user=request.user,  # Current logged-in user
            )
            csv_file.save()
            # Print info about the uploaded file
            print(f"Received file: {file.name}")
            print(f"File size: {file.size} bytes")
            print(f"File type: {file.content_type}")

            return redirect('chat')
    return render(request, 'chat_app/upload.html')