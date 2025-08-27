from django import forms
from .models import Cake
from .models import CakeReview

class CakeForm(forms.ModelForm):
    class Meta:
        model = Cake
        fields = ['name', 'price', 'size', 'shape', 'description', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = CakeReview
        fields = ['cake', 'rating', 'comment']


        