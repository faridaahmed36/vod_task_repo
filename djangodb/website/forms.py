from django import forms
from .models import Members
from .models import Tasks
from .models import Subscription

class MembersForm(forms.ModelForm):
    class Meta:
        model = Members
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['title', 'description', 'start_date', 'due_date', 'completion_date', 'status']
        
        
##########################################
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['start_date', 'frequency', 'report_time']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'report_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_report_time(self):
        report_time = self.cleaned_data['report_time']
        if report_time.minute != 0:
            raise forms.ValidationError("Report time must be an hour without minutes.")
        return report_time