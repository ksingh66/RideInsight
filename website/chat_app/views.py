from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UploadedCSV
from .data_processor import DataSummarizer
from .Chatbot import HybridChatbot
import os


@login_required
def upload_view(request):
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            file = request.FILES['csv_file']
            csv_file = UploadedCSV(
                raw_csv=file,
                user=request.user,
            )
            csv_file.save()
            
            try:
                # Generate summary using DataSummarizer
                summarizer = DataSummarizer(csv_file.raw_csv.path)
                summary_path = f'summaries/summary_{csv_file.id}.txt'
                full_summary_path = os.path.join('media', summary_path)
                
                # Generate the summary
                summarizer.generate_summary(full_summary_path)
                
                # Update the model with processed file path
                csv_file.processed_csv = summary_path
                csv_file.is_processed = True
                csv_file.save()
                
                return redirect('chat', id=csv_file.id)
            except Exception as e:
                print(f"Error processing file: {e}")
                csv_file.delete()  # Clean up if processing fails
                return render(request, 'chat_app/upload.html', {'error': str(e)})
                
    return render(request, 'chat_app/upload.html')



@login_required
def chat_view(request, id):
    try:
        csv_file = UploadedCSV.objects.get(
            id=id,
            user=request.user,
            is_processed=True
        )
        
        if request.method == 'POST':
            user_message = request.POST.get('message')
            
            # Initialize chatbot with the summary
            chatbot = HybridChatbot(
                context_file=csv_file.processed_csv.path,
                rag_data_file=None
            )
            
            # Get response from chatbot
            response = chatbot.generate_response(user_message)
            return JsonResponse({'response': response})
            
        return render(request, 'chat_app/chat.html', {
            'csv_file': csv_file
        })
        
    except UploadedCSV.DoesNotExist:
        return redirect('upload')

@login_required
def end_chat(request, id):
    try:
        csv_file = UploadedCSV.objects.get(id=id, user=request.user)
        csv_file.delete()  # This will trigger your model's delete method
        return JsonResponse({'status': 'success'})
    except UploadedCSV.DoesNotExist:
        return JsonResponse({'status': 'error'})

