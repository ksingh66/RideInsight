from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import UploadedCSV
from django.contrib import messages
from .data_processor import DataSummarizer
from .Chatbot import HybridChatbot
from django.contrib.auth import authenticate, login
from django.views import View
from .models import CustomUser
from .forms import CustomUserRegistrationForm
import os

def is_approved(user):
    """
    Checks if a user is both authenticated and approved to use the system.
    This combines Django's built-in authentication check with our custom approval status.
    """

    return user.is_authenticated and user.is_approved

def approved_user_required(view_func):
    """
    Custom decorator that ensures users are both logged in and approved.
    If either check fails, the user is redirected to the login page.
    """
    decorated_view = user_passes_test(
        is_approved,
        login_url='login',
        redirect_field_name='next'
    )(view_func)
    return decorated_view


class CustomLoginView(View): # We build on the View class thats built in Django
    template_name = 'chat_app/login.html' # Location of login page

    def get(self, request):
        # If user is already authenticated, redirect them
        if request.user.is_authenticated:
            return redirect('upload')  # Redirect to your main page
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username') 
        password = request.POST.get('password')
        
        # First authenticate the user (checks username and password) - built in function
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If user exists and credentials are correct, check approval status
            if user.is_approved:
                # If approved, log them in and redirect
                login(request, user)
                return redirect('upload')  # Redirect to your main page
            else:
                # If not approved, show error message
                messages.error(request, 'Your account is pending approval. Please wait for administrator approval.')
                return redirect('pending')
        else:
            # If authentication failed (wrong credentials)
            messages.error(request, 'Invalid username or password.') # Send the message into the html
        
        # If anything fails, render the login page again
        return render(request, self.template_name)

@approved_user_required
def upload_view(request): #This is the view for the upload page
    if request.method == 'POST': #Upon the customer pressing the submit button
        if 'csv_file' in request.FILES:
            file = request.FILES['csv_file']

            #Generate a UploadedCSV object for that user
            csv_file = UploadedCSV( 
                raw_csv=file,
                user=request.user,
            )
            csv_file.save()
            
            try:
                # Generate summary using DataSummarizer
                summarizer = DataSummarizer(csv_file.raw_csv.path)

                # summary_path is where we want the summary to be stored
                summary_path = f'summaries/summary_{csv_file.id}.txt'
                full_summary_path = os.path.join('media', summary_path)
                
                # Generate the summary
                summarizer.generate_summary(full_summary_path)
                
                # Update the model with processed file path
                csv_file.processed_csv = summary_path
                csv_file.is_processed = True
                csv_file.save()
                
                return redirect('chat', id=csv_file.id) # Upon a successful processing redirect the user to the chat url
            except Exception as e:
                print(f"Error processing file: {e}")
                csv_file.delete()  # Clean up if processing fails
                return render(request, 'chat_app/upload.html', {'error': str(e)})
                
    return render(request, 'chat_app/upload.html')



@approved_user_required
def chat_view(request, id):
    try:
        # Get an already made CSV object with .objects.get ; then set the id argument 
        # Load the CSV object regardless of if its a POST or GET request
        csv_file = UploadedCSV.objects.get(
            id=id,
            user=request.user,
            is_processed=True
        )
        
        if request.method == 'POST': 
            user_message = request.POST.get('message') #Upon the user pressing send
            
            # Initialize chatbot with the summary
            chatbot = HybridChatbot(
                context_file=csv_file.processed_csv.path,
                rag_data_file=None
            )
            
            # Get response from chatbot
            response = chatbot.generate_response(user_message)
            return JsonResponse({'response': response})
            
        if request.method == "GET":
            return render(request, 'chat_app/chat.html', {
                'csv_file': csv_file
            })
        
    except UploadedCSV.DoesNotExist:
        return redirect('upload')

@approved_user_required
def end_chat(request, id):
    try:
        csv_file = UploadedCSV.objects.get(id=id, user=request.user)
        csv_file.delete()  # This will trigger your model's delete method
        return JsonResponse({'status': 'success'})
    except UploadedCSV.DoesNotExist:
        return JsonResponse({'status': 'error'})

def register(request):
    """
    Handle user registration with email-based authentication.
    GET requests display the registration form.
    POST requests process the form and create a new user if valid.
    """
    if request.user.is_authenticated:
        return redirect('upload')
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False
            user.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'chat_app/register.html', {
        'form': form,
        'title': 'Register New Account'
    })

def pending_view(request):
    return render(request, 'chat_app/pending.html')
