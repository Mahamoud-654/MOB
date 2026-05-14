var currentType = null;
var currentPk = null;
var currentAction = null;

function openModal(type, pk, action) {
    currentType = type;
    currentPk = pk;
    currentAction = action;

    var modal = document.getElementById('action-modal');
    var title = document.getElementById('modal-title');
    var desc = document.getElementById('modal-desc');
    var confirmBtn = document.getElementById('modal-confirm-btn');

    var typeLabel = type === 'deposit' ? 'dépôt' : 'retrait';
    var actionLabel = action === 'approved' ? 'approuver' : 'rejeter';

    title.textContent = action === 'approved' ? 'Confirmer l\'approbation' : 'Confirmer le rejet';
    desc.textContent = 'Voulez-vous ' + actionLabel + ' la demande de ' + typeLabel + ' #' + pk + ' ?';

    confirmBtn.textContent = action === 'approved' ? 'Approuver' : 'Rejeter';
    confirmBtn.className = 'btn-confirm' + (action === 'rejected' ? ' danger' : '');

    document.getElementById('modal-note').value = '';
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal(e) {
    if (e && e.target !== document.getElementById('action-modal')) return;
    closeModalBtn();
}

function closeModalBtn() {
    var modal = document.getElementById('action-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

function confirmAction() {
    if (!currentType || !currentPk || !currentAction) return;

    var form = document.getElementById('action-form');
    var urls = {
        'deposit': '/admin-dashboard/depot/' + currentPk + '/statut/',
        'withdrawal': '/admin-dashboard/retrait/' + currentPk + '/statut/',
    };

    form.action = urls[currentType];
    document.getElementById('form-action').value = currentAction;
    document.getElementById('form-note').value = document.getElementById('modal-note').value;

    form.style.display = 'block';
    form.submit();
}

function toggleSidebar() {
    var sidebar = document.querySelector('.admin-sidebar');
    sidebar.classList.toggle('open');
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModalBtn();
});
