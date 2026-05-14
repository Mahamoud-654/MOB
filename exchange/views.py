from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from .models import DepositRequest, WithdrawalRequest
from .forms import DepositForm, WithdrawalForm


WALLET_INFO = {
    'waafi': {
        'name': 'Waafi',
        'number': '77 15 74 92',
        'owner': 'Mohamed Hassan Mouhoumed',
        'image': 'images/wallet/waafi.webp',
        'color': '#E63946',
    },
    'cac': {
        'name': 'CAC',
        'number': '77 15 14 89',
        'owner': 'Abdou-Hakim Elmi Moussa',
        'image': 'images/wallet/cac.webp',
        'color': '#2D6A4F',
    },
    'd-money': {
        'name': 'D-Money',
        'number': '77 15 74 92',
        'owner': 'Mohamed Hassan Mouhoumed',
        'image': 'images/wallet/d-money.webp',
        'color': '#1D3557',
    },
    'saba': {
        'name': 'Saba',
        'number': '118 762 58',
        'owner': 'Mohamed Hassan Mouhoumed',
        'image': 'images/wallet/saba.webp',
        'color': '#F4A261',
    },
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

    return render(request, 'deposit.html', {
        'form': form,
        'wallet_info': WALLET_INFO,
    })


def deposit_success(request, pk):
    deposit_req = get_object_or_404(DepositRequest, pk=pk)
    return render(request, 'deposit_success.html', {'deposit': deposit_req})


def withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal_req = form.save()
            return redirect('withdrawal_success', pk=withdrawal_req.pk)
    else:
        form = WithdrawalForm()

    return render(request, 'withdrawal.html', {
        'form': form,
        'wallet_info': WALLET_INFO,
    })


def withdrawal_success(request, pk):
    withdrawal_req = get_object_or_404(WithdrawalRequest, pk=pk)
    return render(request, 'withdrawal_success.html', {'withdrawal': withdrawal_req})


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Identifiants incorrects ou accès non autorisé.')

    return render(request, 'admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required(login_url='/admin-dashboard/login/')
def admin_dashboard(request):
    wallet_filter = request.GET.get('wallet', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', 'all')

    deposits = DepositRequest.objects.all()
    withdrawals = WithdrawalRequest.objects.all()

    if wallet_filter:
        deposits = deposits.filter(wallet=wallet_filter)
        withdrawals = withdrawals.filter(wallet=wallet_filter)
    if status_filter:
        deposits = deposits.filter(status=status_filter)
        withdrawals = withdrawals.filter(status=status_filter)

    total_deposits_approved = DepositRequest.objects.filter(status='approved').aggregate(
        total=Sum('amount'), count=Count('id'))
    total_withdrawals_approved = WithdrawalRequest.objects.filter(status='approved').aggregate(
        total=Sum('amount'), count=Count('id'))
    total_pending = (
        DepositRequest.objects.filter(status='pending').count() +
        WithdrawalRequest.objects.filter(status='pending').count()
    )

    context = {
        'deposits': deposits,
        'withdrawals': withdrawals,
        'wallet_info': WALLET_INFO,
        'wallet_filter': wallet_filter,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'total_deposits_amount': total_deposits_approved['total'] or 0,
        'total_deposits_count': total_deposits_approved['count'] or 0,
        'total_withdrawals_amount': total_withdrawals_approved['total'] or 0,
        'total_withdrawals_count': total_withdrawals_approved['count'] or 0,
        'total_pending': total_pending,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='/admin-dashboard/login/')
def update_deposit_status(request, pk):
    if request.method == 'POST':
        deposit_req = get_object_or_404(DepositRequest, pk=pk)
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        if action in ['approved', 'rejected']:
            deposit_req.status = action
            deposit_req.admin_note = note
            deposit_req.save()
            status_label = 'approuvé' if action == 'approved' else 'rejeté'
            messages.success(request, f'Dépôt #{pk} {status_label} avec succès.')
    return redirect(request.POST.get('next', 'admin_dashboard'))


@login_required(login_url='/admin-dashboard/login/')
def update_withdrawal_status(request, pk):
    if request.method == 'POST':
        withdrawal_req = get_object_or_404(WithdrawalRequest, pk=pk)
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        if action in ['approved', 'rejected']:
            withdrawal_req.status = action
            withdrawal_req.admin_note = note
            withdrawal_req.save()
            status_label = 'approuvé' if action == 'approved' else 'rejeté'
            messages.success(request, f'Retrait #{pk} {status_label} avec succès.')
    return redirect(request.POST.get('next', 'admin_dashboard'))
