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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from .forms import CommentsForm

@login_required(login_url='/login/')
def add_comment(request):
    if request.method == 'POST':
        if request.user.perms.access_level > 4:
            return render_to_response('unauthorized.html', context_instance=RequestContext(request))

        form = CommentsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
        else:
            print "Invalid form: %s " % form
            raise ValueError

        return redirect('/incidents/view/%s/' % form.cleaned_data.get('incident').id)
    else:
        return redirect('/incidents/')