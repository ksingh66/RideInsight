from django.contrib import admin
from .models import UploadedCSV
from django.utils.html import format_html

@admin.register(UploadedCSV)
class UploadedCSVAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uploaded_at', 'is_processed', 'view_raw_csv', 'view_processed_csv')
    list_filter = ('is_processed', 'uploaded_at', 'user')
    
    def view_raw_csv(self, obj):
        if obj.raw_csv:
            return format_html('<a href="{}" target="_blank">View Raw CSV</a>', obj.raw_csv.url)
        return "No file"
    
    def view_processed_csv(self, obj):
        if obj.processed_csv and obj.is_processed:
            return format_html('<a href="{}" target="_blank">View Processed CSV</a>', obj.processed_csv.url)
        return "Not processed"
    
    view_raw_csv.short_description = 'Raw CSV'
    view_processed_csv.short_description = 'Processed CSV'