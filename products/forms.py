from django import forms

from products.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'recommend', 'rate', )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args,**kwargs)

        if not self.user or not self.user.is_authenticated:
            self.fields['name'] = forms.CharField(max_length=100, required=False,)
            self.fields['email'] = forms.EmailField(max_length=100,required=False,)
