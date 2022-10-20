import logging
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from courts.models import DmCourtCases

log = logging.getLogger(__name__)

PAGE_SIZE: int = 100


def index(request):
    return HttpResponse("Здесь будет информация о судах!")


class CourtsListView(LoginRequiredMixin, ListView):
    # by convention - name of the view:
    # template_name = 'courts/dmcourtcases_list.html'
    template_name = 'courts/courts_list.html'

    model = DmCourtCases
    # paginate_by: int = 25
    # context_object_name = 'object_list'

    def get(self, request):
        log.debug('CourtsListView.get() is working.')

        strval = self.request.GET.get("search", False)
        log.debug(f"Search string: [{strval}].")

        # get list of objects from DB
        if strval:  # there is non-empty search string
            # Multi-field search (several fields), __icontains -> for case-insensitive search
            query = Q(court__icontains=strval)
            query.add(Q(court_alias__icontains=strval), Q.OR)
            query.add(Q(section_name__icontains=strval), Q.OR)
            query.add(Q(case_num__icontains=strval), Q.OR)
            query.add(Q(case_info__icontains=strval), Q.OR)
            query.add(Q(judge__icontains=strval), Q.OR)
            object_list = DmCourtCases.objects.filter(query).select_related().distinct()
        else:  # no search string - provide the full list
            object_list = DmCourtCases.objects.all().order_by('court_alias')

        paginator = Paginator(object_list, PAGE_SIZE)  # todo: !!!

        # found objects list size
        log.debug(f'Objects list size: {len(object_list)}')
        objects_list_size = len(object_list)

        # when we've created object_list (found all data) - add pagination to it
        #paginator = Paginator(object_list, PAGE_SIZE)  # use Paginator and show XX items per page
        page_number = request.GET.get('page', 1)  # current page number
        # get the current Page (frame of data) from Paginator and replace the found
        # objects list with the current frame of data (we have to show only the current page)
        page_obj = paginator.get_page(page_number)
        object_list = page_obj
        log.debug('Generated the current page.')

        # creating the context for the page: list of ADs (limited by search), favorites, search string
        ctx = {'object_list': object_list, 'size': objects_list_size, 'page_size': PAGE_SIZE,
               'search': strval, 'page_obj': page_obj}

        return render(request, self.template_name, ctx)

    # def get_context_data(self, **kwargs):  # adding some data to the context
    #     log.debug('CourtsListView.get_context_data() is working.')
    #     context = super().get_context_data(**kwargs)
    #     context['page_size'] = PAGE_SIZE
    #     return context
