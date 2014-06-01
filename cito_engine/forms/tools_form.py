from django import forms
from cito_engine.models import Team, Category


class BulkUploadForm(forms.Form):

    list_of_items = forms.CharField(widget=forms.Textarea, label='Paste items here')
    team_list = []
    [team_list.append((t.id, t.name)) for t in Team.objects.all()]
    team = forms.ChoiceField(choices=team_list, label="Team")

    category_list = []
    [category_list.append((c.id, c.categoryType)) for c in Category.objects.all()]
    category = forms.ChoiceField(choices=category_list, label="Category")

    severity_list = (
        ('S0', 'S0'),
        ('S1', 'S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
    )

    severity = forms.ChoiceField(choices=severity_list, label="Severity")

    def __init__(self, *args, **kwargs):
        super(BulkUploadForm, self).__init__(*args, **kwargs)
        self.fields['list_of_items'].widget.attrs['rows'] = "15"