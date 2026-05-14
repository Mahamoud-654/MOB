from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django.utils.timezone import localtime
import json
import calendar
from datetime import date, timedelta
from decimal import Decimal
from .models import DepositRequest, WithdrawalRequest
from .forms import DepositForm, WithdrawalForm


WALLET_INFO = {
    'waafi':   {'name': 'Waafi',   'number': '77 15 74 92',  'owner': 'Mohamed Hassan Mouhoumed',  'image': 'images/wallet/waafi.webp'},
    'cac':     {'name': 'CAC',     'number': '77 15 14 89',  'owner': 'Abdou-Hakim Elmi Moussa',   'image': 'images/wallet/cac.webp'},
    'd-money': {'name': 'D-Money', 'number': '77 15 74 92',  'owner': 'Mohamed Hassan Mouhoumed',  'image': 'images/wallet/d-money.webp'},
    'saba':    {'name': 'Saba',    'number': '118 762 58',   'owner': 'Mohamed Hassan Mouhoumed',  'image': 'images/wallet/saba.webp'},
}


def home(request):
    return render(request, 'home.html')


def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            deposit_req = form.save()
            return redirect('deposit_success', pk=deposit_req.pk)
    else:
        form = DepositForm()
    return render(request, 'deposit.html', {'form': form, 'wallet_info': WALLET_INFO})


def deposit_success(request, pk):
    return render(request, 'deposit_success.html', {'deposit': get_object_or_404(DepositRequest, pk=pk)})


def withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal_req = form.save()
            return redirect('withdrawal_success', pk=withdrawal_req.pk)
    else:
        form = WithdrawalForm()
    return render(request, 'withdrawal.html', {'form': form, 'wallet_info': WALLET_INFO})


def withdrawal_success(request, pk):
    return render(request, 'withdrawal_success.html', {'withdrawal': get_object_or_404(WithdrawalRequest, pk=pk)})


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, 'Identifiants incorrects ou accès non autorisé.')
    return render(request, 'admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def _build_calendar_data(year, month):
    """Build a calendar matrix with transaction counts per day."""
    cal = calendar.monthcalendar(year, month)
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    dep_by_day = {
        r['day']: r['count']
        for r in DepositRequest.objects.filter(created_at__date__gte=month_start, created_at__date__lte=month_end)
        .annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id'))
    }
    wit_by_day = {
        r['day']: r['count']
        for r in WithdrawalRequest.objects.filter(created_at__date__gte=month_start, created_at__date__lte=month_end)
        .annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id'))
    }

    weeks = []
    for week in cal:
        week_data = []
        for day_num in week:
            if day_num == 0:
                week_data.append({'day': None, 'deposits': 0, 'withdrawals': 0, 'total': 0})
            else:
                d = date(year, month, day_num)
                dep = dep_by_day.get(d, 0)
                wit = wit_by_day.get(d, 0)
                week_data.append({
                    'day': day_num,
                    'date': d,
                    'deposits': dep,
                    'withdrawals': wit,
                    'total': dep + wit,
                    'is_today': d == date.today(),
                })
        weeks.append(week_data)
    return weeks


@login_required(login_url='/admin-dashboard/login/')
def admin_dashboard(request):
    wallet_filter = request.GET.get('wallet', '')
    status_filter = request.GET.get('status', '')
    type_filter   = request.GET.get('type', 'all')
    today         = date.today()
    cal_year      = int(request.GET.get('cal_year',  today.year))
    cal_month     = int(request.GET.get('cal_month', today.month))

    # ── filtered lists ──────────────────────────────────────────────────────
    deposits    = DepositRequest.objects.all()
    withdrawals = WithdrawalRequest.objects.all()
    if wallet_filter:
        deposits    = deposits.filter(wallet=wallet_filter)
        withdrawals = withdrawals.filter(wallet=wallet_filter)
    if status_filter:
        deposits    = deposits.filter(status=status_filter)
        withdrawals = withdrawals.filter(status=status_filter)

    # ── KPI: global totals ───────────────────────────────────────────────────
    dep_approved = DepositRequest.objects.filter(status='approved').aggregate(total=Sum('amount'), count=Count('id'), avg=Avg('amount'))
    wit_approved = WithdrawalRequest.objects.filter(status='approved').aggregate(total=Sum('amount'), count=Count('id'), avg=Avg('amount'))

    total_dep_amount = dep_approved['total'] or Decimal('0')
    total_dep_count  = dep_approved['count'] or 0
    total_wit_amount = wit_approved['total'] or Decimal('0')
    total_wit_count  = wit_approved['count'] or 0
    avg_dep          = dep_approved['avg']   or Decimal('0')
    avg_wit          = wit_approved['avg']   or Decimal('0')

    total_pending  = DepositRequest.objects.filter(status='pending').count() + WithdrawalRequest.objects.filter(status='pending').count()
    total_rejected = DepositRequest.objects.filter(status='rejected').count() + WithdrawalRequest.objects.filter(status='rejected').count()
    total_all      = DepositRequest.objects.count() + WithdrawalRequest.objects.count()
    approval_rate  = round((total_dep_count + total_wit_count) / total_all * 100) if total_all else 0
    net_volume     = total_dep_amount - total_wit_amount

    # ── KPI: today ───────────────────────────────────────────────────────────
    today_dep = DepositRequest.objects.filter(created_at__date=today)
    today_wit = WithdrawalRequest.objects.filter(created_at__date=today)
    today_dep_amount = today_dep.filter(status='approved').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    today_wit_amount = today_wit.filter(status='approved').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    today_count      = today_dep.count() + today_wit.count()

    # ── KPI: this week ───────────────────────────────────────────────────────
    week_start = today - timedelta(days=today.weekday())
    week_dep   = DepositRequest.objects.filter(created_at__date__gte=week_start, status='approved').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    week_wit   = WithdrawalRequest.objects.filter(created_at__date__gte=week_start, status='approved').aggregate(t=Sum('amount'))['t'] or Decimal('0')

    # ── Chart: last 30 days daily volume ─────────────────────────────────────
    thirty_days_ago = today - timedelta(days=29)
    days_labels = [(thirty_days_ago + timedelta(days=i)).strftime('%d/%m') for i in range(30)]
    days_dates  = [thirty_days_ago + timedelta(days=i) for i in range(30)]

    dep_daily = {
        r['day']: float(r['total'])
        for r in DepositRequest.objects.filter(created_at__date__gte=thirty_days_ago, status='approved')
        .annotate(day=TruncDate('created_at')).values('day').annotate(total=Sum('amount'))
    }
    wit_daily = {
        r['day']: float(r['total'])
        for r in WithdrawalRequest.objects.filter(created_at__date__gte=thirty_days_ago, status='approved')
        .annotate(day=TruncDate('created_at')).values('day').annotate(total=Sum('amount'))
    }
    chart_dep_data = [dep_daily.get(d, 0) for d in days_dates]
    chart_wit_data = [wit_daily.get(d, 0) for d in days_dates]

    # ── Chart: by wallet ─────────────────────────────────────────────────────
    wallet_dep_amounts = {
        r['wallet']: float(r['total'])
        for r in DepositRequest.objects.filter(status='approved').values('wallet').annotate(total=Sum('amount'))
    }
    wallet_wit_amounts = {
        r['wallet']: float(r['total'])
        for r in WithdrawalRequest.objects.filter(status='approved').values('wallet').annotate(total=Sum('amount'))
    }
    wallet_labels  = [info['name'] for info in WALLET_INFO.values()]
    wallet_dep_ser = [wallet_dep_amounts.get(k, 0) for k in WALLET_INFO]
    wallet_wit_ser = [wallet_wit_amounts.get(k, 0) for k in WALLET_INFO]

    # ── Chart: status donut ───────────────────────────────────────────────────
    dep_status = {r['status']: r['count'] for r in DepositRequest.objects.values('status').annotate(count=Count('id'))}
    wit_status = {r['status']: r['count'] for r in WithdrawalRequest.objects.values('status').annotate(count=Count('id'))}
    status_approved = (dep_status.get('approved', 0) + wit_status.get('approved', 0))
    status_pending  = (dep_status.get('pending',  0) + wit_status.get('pending',  0))
    status_rejected = (dep_status.get('rejected', 0) + wit_status.get('rejected', 0))

    # ── Calendar ──────────────────────────────────────────────────────────────
    cal_weeks     = _build_calendar_data(cal_year, cal_month)
    cal_prev      = date(cal_year, cal_month, 1) - timedelta(days=1)
    cal_next_day  = date(cal_year, cal_month, 1)
    if cal_month == 12:
        cal_next = date(cal_year + 1, 1, 1)
    else:
        cal_next = date(cal_year, cal_month + 1, 1)

    month_names = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']

    context = {
        'deposits': deposits,
        'withdrawals': withdrawals,
        'wallet_info': WALLET_INFO,
        'wallet_filter': wallet_filter,
        'status_filter': status_filter,
        'type_filter': type_filter,

        # KPIs
        'total_dep_amount':  total_dep_amount,
        'total_dep_count':   total_dep_count,
        'total_wit_amount':  total_wit_amount,
        'total_wit_count':   total_wit_count,
        'avg_dep':           avg_dep,
        'avg_wit':           avg_wit,
        'total_pending':     total_pending,
        'total_rejected':    total_rejected,
        'approval_rate':     approval_rate,
        'net_volume':        net_volume,
        'today_dep_amount':  today_dep_amount,
        'today_wit_amount':  today_wit_amount,
        'today_count':       today_count,
        'week_dep':          week_dep,
        'week_wit':          week_wit,

        # Charts (JSON)
        'chart_labels':      json.dumps(days_labels),
        'chart_dep_data':    json.dumps(chart_dep_data),
        'chart_wit_data':    json.dumps(chart_wit_data),
        'wallet_labels':     json.dumps(wallet_labels),
        'wallet_dep_ser':    json.dumps(wallet_dep_ser),
        'wallet_wit_ser':    json.dumps(wallet_wit_ser),
        'status_approved':   status_approved,
        'status_pending':    status_pending,
        'status_rejected':   status_rejected,

        # Calendar
        'cal_weeks':         cal_weeks,
        'cal_year':          cal_year,
        'cal_month':         cal_month,
        'cal_month_name':    month_names[cal_month - 1],
        'cal_prev_year':     cal_prev.year,
        'cal_prev_month':    cal_prev.month,
        'cal_next_year':     cal_next.year,
        'cal_next_month':    cal_next.month,
        'today':             today,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='/admin-dashboard/login/')
def admin_stats(request):
    """API endpoint for refreshed stats (future use)."""
    return redirect('admin_dashboard')


@login_required(login_url='/admin-dashboard/login/')
def update_deposit_status(request, pk):
    if request.method == 'POST':
        dep = get_object_or_404(DepositRequest, pk=pk)
        action = request.POST.get('action')
        if action in ['approved', 'rejected']:
            dep.status = action
            dep.admin_note = request.POST.get('note', '')
            dep.save()
            label = 'approuvé' if action == 'approved' else 'rejeté'
            messages.success(request, f'Dépôt #{pk} {label} avec succès.')
    return redirect(request.POST.get('next', 'admin_dashboard'))


@login_required(login_url='/admin-dashboard/login/')
def update_withdrawal_status(request, pk):
    if request.method == 'POST':
        wit = get_object_or_404(WithdrawalRequest, pk=pk)
        action = request.POST.get('action')
        if action in ['approved', 'rejected']:
            wit.status = action
            wit.admin_note = request.POST.get('note', '')
            wit.save()
            label = 'approuvé' if action == 'approved' else 'rejeté'
            messages.success(request, f'Retrait #{pk} {label} avec succès.')
    return redirect(request.POST.get('next', 'admin_dashboard'))
