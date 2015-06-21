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

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models.query_utils import Q
from cito_engine.models import Category
from cito_engine.forms import categories


@login_required(login_url='/login/')
def view_all_categories(request):
    if request.user.perms.access_level > 4:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Categories'
    box_title = page_title
    try:
        categories = Category.objects.all().order_by('categoryType')
    except Category.DoesNotExist:
        categories = None

    return render_to_response('view_categories.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def edit_category(request, category_id):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Editing category'
    box_title = page_title
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = categories.CategoryForm(request.POST)
        if form.is_valid():
            category_type = form.cleaned_data['categoryType']
            if Category.objects.filter(~Q(pk=category_id), categoryType__iexact=category_type).count() > 0:
                errors = ['Category with name \"%s\" already exists.' % category_type]
            else:
                query = dict(categoryType=category_type)
                Category.objects.filter(pk=category_id).update(**query)
                success_msg = 'Category Updated.'
                return redirect('/categories/')
    else:
        form = categories.CategoryForm(instance=category)
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def add_category(request):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Add a new category'
    box_title = page_title
    if request.method == 'POST':
        form = categories.CategoryForm(request.POST)
        if form.is_valid():
            category_type = form.cleaned_data['categoryType']
            if Category.objects.filter(categoryType__iexact=category_type).count() > 0:
                errors = ['Category named \"%s\" already exists' % category_type]
            else:
                form.save()
                return redirect('/categories/')
    else:
        form = categories.CategoryForm()
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))
