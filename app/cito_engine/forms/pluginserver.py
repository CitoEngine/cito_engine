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

from django.forms import ModelForm, Form, CharField
from cito_engine.models import PluginServer


class PluginServerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PluginServerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PluginServer
        fields = '__all__'


class PluginSearchForm(Form):
    search_term = CharField(max_length=64, required=True)

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['search_term'].widget.attrs["placeholder"] = 'Search plugin'