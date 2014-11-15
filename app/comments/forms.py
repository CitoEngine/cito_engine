"""Copyright 2014 Cyrus Dasadia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.forms import ModelForm, HiddenInput
from comments.models import Comments


class CommentsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['rows'] = "5"
        self.fields['text'].label = "Comment"

    class Meta:
        model = Comments
        widgets = {'incident': HiddenInput, 'user': HiddenInput}
        exclude = ['date_added']
