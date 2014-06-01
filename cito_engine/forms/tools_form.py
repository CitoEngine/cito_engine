from django import forms


class BulkUploadForm(forms.Form):

    list_of_items = forms.CharField(widget=forms.Textarea, label='Paste items here')

    def __init__(self, *args, **kwargs):
        super(BulkUploadForm, self).__init__(*args, **kwargs)
        self.fields['list_of_items'].widget.attrs['rows'] = "15"