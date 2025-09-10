from django import forms
from .models import Cake
from .models import CakeReview
from .models import Register

class CakeForm(forms.ModelForm):
    class Meta:
        model = Cake
        fields = ['name', 'price', 'size', 'shape', 'description', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = CakeReview
        fields = ['cake', 'rating', 'comment']

class CakeReviewForm(forms.ModelForm):
    class Meta:
        model = CakeReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review...'}),
        }
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = ['full_name', 'address', 'phone']

        