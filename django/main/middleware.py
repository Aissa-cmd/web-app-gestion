from django.db.models import Q
from main.models import Command, User
from django.utils import timezone
from django.db.models.functions import Extract
from functools import reduce
import calendar

class StatisticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)   
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        # get_params
        stat_agent_id = request.GET.get("stat_agent_id", None)
        stat_agent_year = request.GET.get("stat_agent_year", timezone.now().year)
        stat_order_year = request.GET.get('stat_order_year', timezone.now().year)

        # database queries
        all_orders = Command.objects.filter(date__year=stat_order_year)
        delivered_orders = all_orders.filter(Q(status=Command.Status.DELIVERED) & Q(date__year=stat_order_year))
        cancelled_orders = all_orders.filter(Q(status=Command.Status.CANCELLED) & Q(date__year=stat_order_year))
        returned_orders = all_orders.filter(Q(status=Command.Status.RETURNED) & Q(date__year=stat_order_year))

        search_query_args = (
            ('stat_agent_id', request.GET.get("stat_agent_id", None)),
            ('stat_agent_year', request.GET.get("stat_agent_year", None)),
            ('stat_order_year', request.GET.get('stat_order_year', None))
        )

        try:
            years_options = list(range(Command.objects.values_list('date', flat=True).order_by('date')[0].year, (timezone.localdate()+timezone.timedelta(days=366)).year))
        except:
            years_options = []

        orders_stat_avg = {
            "DELIVERED": f'{(delivered_orders.count() * (100/(all_orders.count() or 1))):.2f}',
            "CANCELLED": f'{(cancelled_orders.count() * (100/(all_orders.count() or 1))):.2f}',
            "RETURNED": f'{(returned_orders.count() * (100/(all_orders.count() or 1))):.2f}',
        }
        orders_stat_delivered = {
            calendar.month_abbr[1]: 0,
            calendar.month_abbr[2]: 0,
            calendar.month_abbr[3]: 0,
            calendar.month_abbr[4]: 0,
            calendar.month_abbr[5]: 0,
            calendar.month_abbr[6]: 0,
            calendar.month_abbr[7]: 0,
            calendar.month_abbr[8]: 0,
            calendar.month_abbr[9]: 0,
            calendar.month_abbr[10]: 0,
            calendar.month_abbr[11]: 0,
            calendar.month_abbr[12]: 0,
        }
        orders_stat_cancelled = {
            calendar.month_abbr[1]: 0,
            calendar.month_abbr[2]: 0,
            calendar.month_abbr[3]: 0,
            calendar.month_abbr[4]: 0,
            calendar.month_abbr[5]: 0,
            calendar.month_abbr[6]: 0,
            calendar.month_abbr[7]: 0,
            calendar.month_abbr[8]: 0,
            calendar.month_abbr[9]: 0,
            calendar.month_abbr[10]: 0,
            calendar.month_abbr[11]: 0,
            calendar.month_abbr[12]: 0,
        }
        orders_stat_retourned = {
            calendar.month_abbr[1]: 0,
            calendar.month_abbr[2]: 0,
            calendar.month_abbr[3]: 0,
            calendar.month_abbr[4]: 0,
            calendar.month_abbr[5]: 0,
            calendar.month_abbr[6]: 0,
            calendar.month_abbr[7]: 0,
            calendar.month_abbr[8]: 0,
            calendar.month_abbr[9]: 0,
            calendar.month_abbr[10]: 0,
            calendar.month_abbr[11]: 0,
            calendar.month_abbr[12]: 0,
        }

        
        agent_stat_delivered = {
            calendar.month_abbr[1]: 0,
            calendar.month_abbr[2]: 0,
            calendar.month_abbr[3]: 0,
            calendar.month_abbr[4]: 0,
            calendar.month_abbr[5]: 0,
            calendar.month_abbr[6]: 0,
            calendar.month_abbr[7]: 0,
            calendar.month_abbr[8]: 0,
            calendar.month_abbr[9]: 0,
            calendar.month_abbr[10]: 0,
            calendar.month_abbr[11]: 0,
            calendar.month_abbr[12]: 0,
        }
        agent_stat_returned = {
            calendar.month_abbr[1]: 0,
            calendar.month_abbr[2]: 0,
            calendar.month_abbr[3]: 0,
            calendar.month_abbr[4]: 0,
            calendar.month_abbr[5]: 0,
            calendar.month_abbr[6]: 0,
            calendar.month_abbr[7]: 0,
            calendar.month_abbr[8]: 0,
            calendar.month_abbr[9]: 0,
            calendar.month_abbr[10]: 0,
            calendar.month_abbr[11]: 0,
            calendar.month_abbr[12]: 0,
        }


        # =============
        all_agents = User.objects.filter(role=User.Types.AGENT)
        try:
            agent_to_show = None
            try:
                agent_to_show = all_agents.get(id=stat_agent_id)
            except:
                agent_to_show = all_agents.first()
            
            agent_to_show_all = agent_to_show.confirmations.all()
            agent_to_show_confirmations = agent_to_show_all.filter(date__year=stat_agent_year)
            agent_to_show_delivered = agent_to_show_confirmations.filter(status=Command.Status.DELIVERED)
            agent_to_show_returned = agent_to_show_confirmations.filter(status=Command.Status.RETURNED)

            agent_stat_avg = {
                "DELIVERED": (agent_to_show_delivered.count() * (100/(agent_to_show_confirmations.count() or 1))),
                "RETURNED": (agent_to_show_returned.count() * (100/(agent_to_show_confirmations.count() or 1))),
            }

            for order in agent_to_show_delivered:
                agent_stat_delivered[calendar.month_abbr[order.date.month]] += 1

            for order in agent_to_show_returned:
                agent_to_show_returned[calendar.month_abbr[order.date.month]] += 1
        except:
            agent_to_show = None
            agent_stat_avg = {
                "DELIVERED": 0.00,
                "RETURNED": 0.00,
            }
        
        # =============


        for order in delivered_orders:
            orders_stat_delivered[calendar.month_abbr[order.date.month]] += 1

        for order in cancelled_orders:
            orders_stat_cancelled[calendar.month_abbr[order.date.month]] += 1

        for order in returned_orders:
            orders_stat_retourned[calendar.month_abbr[order.date.month]] += 1

        # number of new, delivered, returned orders for today
        todays_date = timezone.make_aware(timezone.datetime.strptime(str(timezone.localdate()), "%Y-%m-%d")) # lower bound
        upper_bound = todays_date + timezone.timedelta(days=1)

        today_orders = Command.objects.filter(Q(date__gte=todays_date) & Q(date__lt=upper_bound))

        today_stats = {
            "NEW": today_orders.filter(status=Command.Status.NEW).count(),
            "DELIVERED": today_orders.filter(status=Command.Status.DELIVERED).count(),
            "CONFIRMED": today_orders.filter(status=Command.Status.CONFIRMED).count(),
            "NEW_ESTM": reduce(lambda a, b: a + float(b.price), today_orders.filter(status=Command.Status.NEW), 0.0),
            "DELIVERED_ESTM": reduce(lambda a, b: a + float(b.price), today_orders.filter(status=Command.Status.DELIVERED), 0.0),
            "CONFIRMED_ESTM": reduce(lambda a, b: a + float(b.price), today_orders.filter(status=Command.Status.CONFIRMED), 0.0)
        }

        response.context_data['orders_stat_delivered'] = orders_stat_delivered
        response.context_data['orders_stat_cancelled'] = orders_stat_cancelled
        response.context_data['orders_stat_retourned'] = orders_stat_retourned
        response.context_data['orders_stat_avg'] = orders_stat_avg
        response.context_data['order_stat_year'] = stat_order_year
        response.context_data['all_agents'] = all_agents
        response.context_data['agent_to_show'] = agent_to_show
        response.context_data['agent_stat_year'] = stat_agent_year
        response.context_data['agent_stat_delivered'] = agent_stat_delivered
        response.context_data['agent_stat_returned'] = agent_stat_returned
        response.context_data['agent_stat_avg'] = agent_stat_avg
        response.context_data['years_options'] = years_options
        response.context_data['search_query_args'] = search_query_args
        response.context_data['today_stats'] = today_stats
        return response
