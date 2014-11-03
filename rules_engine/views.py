from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic.edit import FormView, View
from .models import EventAndElementSuppressor, EventSuppressor, ElementSuppressor

from braces.views import LoginRequiredMixin
from .forms import SuppressionSearchForm, SuppressionAddForm


class SuppressionSearchView(LoginRequiredMixin, FormView):
    """
    Search suppressed events and elements
    """
    template_name = 'suppressor_view.html'
    form_class = SuppressionSearchForm
    # success_url = '/suppression/view/'

    def get_context_data(self, **kwargs):
        context = super(SuppressionSearchView, self).get_context_data(**kwargs)
        context['page_title'] = 'Search Suppression'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        element = form.cleaned_data.get('element').strip()
        eventid = form.cleaned_data.get('eventid')

        # Show all suppressed events if form is blank
        # TODO: add pagination
        if element == '' and eventid is None:
            context['element_sup'] = ElementSuppressor.objects.all()
            context['event_sup'] = EventSuppressor.objects.all()
            context['event_and_element_sup'] = EventAndElementSuppressor.objects.all()
        else:
            context['element_sup'] = ElementSuppressor.objects.filter(element__iexact=element)
            context['event_sup'] = EventSuppressor.objects.filter(event__pk=eventid)
            context['event_and_element_sup'] = EventAndElementSuppressor.objects.filter(Q(element__iexact=element) | Q(event__pk=eventid))

        context['form'] = form
        context['search_content'] = True
        return self.render_to_response(context=context)


class SuppressionAddView(LoginRequiredMixin, FormView):
    """
    View to add Supression
    """
    template_name = 'generic_form.html'
    form_class = SuppressionAddForm
    success_url = '/suppression/view/'

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super(SuppressionAddView, self).form_valid(form)


class RemoveSuppression(LoginRequiredMixin, View):
    """
    Removes suppression
    """
    def post(self, request):
        record_id = request.POST.get('record_id')
        record_type = request.POST.get('record_type')
        model = None

        if record_type == 'Element':
            model = ElementSuppressor
        elif record_type == 'Event':
            model = EventSuppressor
        elif record_type == 'EventAndElementSuppressor':
            model = EventAndElementSuppressor
        else:
            redirect('/suppression/view/')

        if model is not None:
            try:
                record = model.objects.get(pk=record_id)
                record.delete()
            except Exception:
                pass
        return redirect('/suppression/view/')