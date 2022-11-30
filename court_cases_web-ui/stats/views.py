import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from stats.models import DmVCourtStats

# todo: https://stackoverflow.com/questions/35724208/how-to-paginate-search-results-in-django

log = logging.getLogger(__name__)

PAGE_SIZE: int = 25


def index(request):  # sample simple view
    return HttpResponse("Здесь будет статистическая информация!")


class StatsListView(LoginRequiredMixin, ListView):
    # by convention - name of the view:
    # template_name = 'stats/dmvcourtstats_list.html'
    template_name = "stats/stats_list.html"

    model = DmVCourtStats
    # paginate_by: int = 25

    def get(self, request):
        log.debug("StatsListView.get() is working.")

        strval = request.GET.get("search", False)
        log.debug(f"Search string: [{strval}].")

        # get list of objects from DB
        if strval:  # there is non-empty search string
            # Simple title-only search (one field)
            # ad_list = Ad.objects.filter(title__contains=strval) \
            #                     .select_related().order_by('-updated_at')[:10]

            # Multi-field search (several fields)
            # __icontains -> for case-insensitive search
            query = Q(court_alias__icontains=strval)
            query.add(Q(title__icontains=strval), Q.OR)
            object_list = (
                DmVCourtStats.objects.filter(query).select_related().distinct()
            )
        else:  # no search string - provide the full list
            object_list = DmVCourtStats.objects.all()

        log.debug(f"Objects list size: {len(object_list)}")
        objects_list_size = len(object_list)

        # when we've created object_list (found all data) - add pagination to it
        paginator = Paginator(
            object_list, PAGE_SIZE
        )  # use Paginator and show XX items per page
        page_number = request.GET.get("page", 1)  # current page number
        page_obj = paginator.get_page(
            page_number
        )  # get the current Page from Paginator
        # todo: Paginator: method get_page() is better (reliable) rather than page() - raises issues...
        # object_list = paginator.page(page_number)  # also assign a current page to the objects list
        object_list = page_obj

        # creating the context for the page: list of ADs (limited by search), favorites, search string
        ctx = {
            "object_list": object_list,
            "size": objects_list_size,
            "page_size": PAGE_SIZE,
            "search": strval,
            "page_obj": page_obj,
        }

        return render(request, self.template_name, ctx)
