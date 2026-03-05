// ============================================
// ONEA Pilotage Mix Énergétique - Dashboard JS (V2 - Corrigé)
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadAllData();
    setInterval(() => loadAllData(), 60000);
});

// ============================================
// NAVIGATION
// ============================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Désactiver tous les onglets
            navItems.forEach(nav => nav.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');

            // Activer l'onglet cliqué
            item.classList.add('active');
            const tabId = item.dataset.tab;
            document.getElementById(`tab-${tabId}`).style.display = 'block';

            // Mettre à jour le titre de la page
            const titles = {
                overview:     { title: "Vue d'ensemble",  subtitle: "Tableau de bord de performance et d'impact environnemental" },
                predictions:  { title: "Prévisions",       subtitle: "Consommation vs potentiel solaire sur 24h" },
                optimization: { title: "Optimisation",     subtitle: "Répartition du mix énergétique heure par heure" },
                anomalies:    { title: "Anomalies",        subtitle: "Détection et diagnostic des incidents" },
                stations:     { title: "Stations",         subtitle: "Classement RSE et performance par station" },
            };
            if (titles[tabId]) {
                document.getElementById('page-title').textContent    = titles[tabId].title;
                document.getElementById('page-subtitle').textContent = titles[tabId].subtitle;
            }

            loadTabData(tabId);
        });
    });
}

function loadAllData() {
    loadKPI();
    loadGauge();
    const activeTab = document.querySelector('.nav-item.active')?.dataset.tab || 'overview';
    loadTabData(activeTab);
}

function loadTabData(tabId) {
    if (tabId === 'predictions')  loadPredictions();
    if (tabId === 'optimization') loadSchedule();
    if (tabId === 'anomalies')    loadAnomalies();
    if (tabId === 'stations')     loadRanking();
}

// ============================================
// KPIs & STATUT SYSTÈME
// ============================================
function loadKPI() {
    fetch('/api/kpi')
        .then(r => r.json())
        .then(data => {
            document.getElementById('kpi-cost').textContent             = data.total_cost_fcfa.toLocaleString() + ' FCFA';
            document.getElementById('kpi-savings-percent').textContent  = `+${data.savings_percent}% d'économies`;
            document.getElementById('kpi-solar').textContent            = data.total_solar_kwh.toLocaleString() + ' kWh';
            document.getElementById('kpi-co2').textContent              = data.total_co2_kg.toLocaleString() + ' kg';
            document.getElementById('kpi-gasoil').textContent           = data.total_gasoil_liters + ' Litres de gasoil';
            document.getElementById('kpi-anomalies-total').textContent  = data.total_anomalies;
            document.getElementById('kpi-anomalies-critical').textContent = data.critical_anomalies + ' critiques';
            document.getElementById('anomalies-count').textContent      = data.total_anomalies;
        })
        .catch(err => console.error('Erreur KPI:', err));

    // Statut système (statique / enrichi depuis le backend si besoin)
    document.getElementById('system-summary').innerHTML = `
        <div class="status-grid">
            <div class="status-card status-ok">
                <div class="status-label">État du Réseau</div>
                <div class="status-val success">Connecté (SONABEL)</div>
            </div>
            <div class="status-card status-warning">
                <div class="status-label">Ensoleillement Actuel</div>
                <div class="status-val warning">Excellent (100%)</div>
            </div>
            <div class="status-card status-info">
                <div class="status-label">Pénalités SONABEL</div>
                <div class="status-val primary">Évitées (Peak Shaving)</div>
            </div>
            <div class="status-card status-ok">
                <div class="status-label">Groupe Électrogène</div>
                <div class="status-val success">À l'arrêt (0 L/h)</div>
            </div>
        </div>
    `;
}

function loadGauge() {
    const circle = document.getElementById('gauge-circle');
    if (!circle) return;
    setTimeout(() => {
        const pct = 75;
        circle.style.strokeDashoffset = 565.48 - (pct / 100) * 565.48;
        circle.style.stroke = 'var(--accent)';
        document.getElementById('gauge-value').textContent = pct + '%';
    }, 500);
}

// ============================================
// ONGLET : PRÉVISIONS
// ============================================
function loadPredictions() {
    fetch('/api/predictions')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('predictionsChart').getContext('2d');
            if (window.predChart) window.predChart.destroy();

            window.predChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(p => p.hour + 'h'),
                    datasets: [
                        {
                            label: 'Énergie Requise (kWh)',
                            data: data.map(p => p.energy_predicted),
                            borderColor: '#3b82f6',
                            tension: 0.4,
                            fill: false,
                            borderWidth: 2
                        },
                        {
                            label: 'Potentiel Solaire (kWh)',
                            data: data.map(p => p.solar_capacity_predicted),
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.4,
                            fill: true,
                            borderWidth: 2
                        }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        })
        .catch(err => console.error('Erreur prévisions:', err));
}

// ============================================
// ONGLET : OPTIMISATION (Mix Énergétique)
// ============================================
function loadSchedule() {
    fetch('/api/schedule')
        .then(r => r.json())
        .then(data => {
            // --- Graphique empilé ---
            const ctx = document.getElementById('scheduleChart').getContext('2d');
            if (window.schedChart) window.schedChart.destroy();

            window.schedChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(s => s.hour + 'h'),
                    datasets: [
                        { label: 'Solaire',  data: data.map(s => s.mix_solar_kwh),     backgroundColor: '#f59e0b' },
                        { label: 'SONABEL',  data: data.map(s => s.mix_sonabel_kwh),   backgroundColor: '#3b82f6' },
                        { label: 'Gasoil',   data: data.map(s => s.mix_generator_kwh), backgroundColor: '#ef4444' }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { x: { stacked: true }, y: { stacked: true } }
                }
            });

            // --- Tableau du mix (schedule-tbody UNIQUEMENT) ---
            document.getElementById('schedule-tbody').innerHTML = data.map(s => `
                <tr>
                    <td><strong>${s.hour}h</strong></td>
                    <td>
                        <span class="badge badge-${s.grid_status === 'OK' ? 'success' : 'danger'}${s.grid_status !== 'OK' ? ' pulse' : ''}">
                            ${s.grid_status}
                        </span>
                    </td>
                    <td class="text-solar">${s.mix_solar_kwh}</td>
                    <td class="text-sonabel">${s.mix_sonabel_kwh}</td>
                    <td class="text-gasoil">${s.gasoil_used_liters > 0 ? s.gasoil_used_liters + ' L' : '0'}</td>
                    <td>${s.pump_action}</td>
                    <td><strong>${s.cost_fcfa.toLocaleString()} FCFA</strong></td>
                </tr>
            `).join('');
        })
        .catch(err => console.error('Erreur optimisation:', err));
}

// ============================================
// ONGLET : ANOMALIES
// ============================================
let allAnomalies  = [];
let sortColumn    = 'severity_score';
let sortDirection = 'desc';

function loadAnomalies() {
    fetch('/api/anomalies')
        .then(r => r.json())
        .then(data => {
            allAnomalies = [...(data.rule_based || []), ...(data.ml_based || [])];
            renderAnomaliesTable();
        })
        .catch(err => console.error('Erreur anomalies:', err));
}

function renderAnomaliesTable() {
    // Cible STRICTEMENT le tbody de l'onglet anomalies
    const tbody = document.getElementById('anomalies-tbody');
    if (!tbody) return;

    const sorted = [...allAnomalies].sort((a, b) => {
        let valA = sortColumn === 'date' ? a.date + a.hour : a[sortColumn];
        let valB = sortColumn === 'date' ? b.date + b.hour : b[sortColumn];
        return sortDirection === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
    });

    if (sorted.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:2rem;">Aucune anomalie détectée</td></tr>`;
        return;
    }

    tbody.innerHTML = sorted.map((a, index) => `
        <tr class="clickable" onclick="showAnomalyDetails(${index})" style="cursor:pointer;">
            <td>${a.date} <strong>${a.hour}h</strong></td>
            <td>
                <span class="badge badge-${a.severity === 'CRITIQUE' ? 'danger pulse' : 'warning'}">
                    ${a.severity}
                </span>
            </td>
            <td>
                ${a.grid_status === 0
                    ? '<span class="badge badge-danger">Coupure</span>'
                    : '<span class="badge badge-success">OK</span>'}
            </td>
            <td>${Math.round(a.flow || 0)} m³/h</td>
            <td>${(a.alerts || ['Pattern inhabituel']).join(', ')}</td>
            <td>
                <button class="btn" style="padding:2px 8px; font-size:11px;">Détails</button>
            </td>
        </tr>
    `).join('');
}

// Tri par colonne (à appeler via onclick="setSort('colonne')" dans les <th>)
function setSort(col) {
    sortDirection = (sortColumn === col && sortDirection === 'asc') ? 'desc' : 'asc';
    sortColumn = col;
    renderAnomaliesTable();
}

// ============================================
// MODAL : DIAGNOSTIC ANOMALIE
// ============================================
function showAnomalyDetails(index) {
    const a = allAnomalies[index];
    if (!a) return;

    document.getElementById('modal-title').textContent = `Diagnostic : ${(a.alerts && a.alerts[0]) || 'Anomalie'}`;

    document.getElementById('modal-details-grid').innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Sévérité</div>
            <div class="detail-value text-${a.severity === 'CRITIQUE' ? 'gasoil' : 'solar'}">${a.severity}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Débit</div>
            <div class="detail-value">${Math.round(a.flow)} m³/h</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Niveau</div>
            <div class="detail-value">${a.level}%</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Réseau</div>
            <div class="detail-value">${a.grid_status === 1 ? 'SONABEL OK' : 'SUR GROUPE'}</div>
        </div>
    `;

    const diag = getDiagnostic(a.alerts || []);
    document.getElementById('modal-causes').innerHTML  = `<p>${diag.causes}</p>`;
    document.getElementById('modal-actions').innerHTML = `<p>${diag.actions}</p>`;

    document.getElementById('modal-overlay').classList.add('active');
}

function getDiagnostic(alerts) {
    if (alerts.includes('GASPILLAGE_GASOIL_GROUPE_ELECTROGENE')) {
        return {
            causes:  "Pompage à haut débit détecté pendant une coupure SONABEL. Le coût du kWh est multiplié par 4.",
            actions: "Réduire immédiatement le débit de pompe à 15% (maintien vital) via le variateur de vitesse."
        };
    }
    if (alerts.includes('RENDEMENT_SOLAIRE_ANORMAL (Plaques sales ?)')) {
        return {
            causes:  "L'ensoleillement est fort mais la production est inférieure de 40% aux prévisions IA. Encrassement probable (Harmattan/Poussière).",
            actions: "Planifier un nettoyage des panneaux photovoltaïques dans les 24h."
        };
    }
    if (alerts.includes('NIVEAU_BAS_CRITIQUE')) {
        return {
            causes:  "La consommation dépasse le volume pompé. Fuite majeure possible ou pic de demande exceptionnel.",
            actions: "Vérifier la pression en sortie de réservoir. Si pression normale, augmenter le pompage prioritaire."
        };
    }
    if (alerts.includes('PANNE_POMPE_PROBABLE')) {
        return {
            causes:  "Énergie consommée sans débit d'eau détecté. Risque de désamorçage ou rupture d'axe de pompe.",
            actions: "ARRÊT D'URGENCE requis pour éviter la surchauffe. Inspection mécanique nécessaire."
        };
    }
    return {
        causes:  "Comportement atypique détecté par l'algorithme d'Isolation Forest (Pattern ML).",
        actions: "Surveillance accrue recommandée. Vérifier l'étalonnage des capteurs de débit."
    };
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

// Fermer la modal en cliquant sur l'overlay
document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-overlay')) closeModal();
});

// ============================================
// ONGLET : STATIONS (Classement RSE)
// ============================================
function loadRanking() {
    fetch('/api/ranking')
        .then(r => r.json())
        .then(data => {
            let html = '<div class="ranking-grid">';

            // Top Pollueurs
            html += `
                <div>
                    <div class="ranking-title">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--danger)" stroke-width="2">
                            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
                        </svg>
                        Top Pollueurs (CO2 &amp; Gasoil)
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>Rang</th><th>Station</th><th>Impact Carbone</th></tr></thead>
                            <tbody>
                                ${data.by_carbon_footprint.map((s, i) => `
                                    <tr>
                                        <td><strong>#${i + 1}</strong></td>
                                        <td>${s.station_name}</td>
                                        <td class="text-gasoil">${s.co2_emissions_kg.toLocaleString()} kg CO2</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>`;

            // Champions Solaire
            html += `
                <div>
                    <div class="ranking-title">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--warning)" stroke-width="2">
                            <circle cx="12" cy="12" r="5"/>
                            <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                            <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                        </svg>
                        Champions Solaire
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>Rang</th><th>Station</th><th>Couverture Solaire</th></tr></thead>
                            <tbody>
                                ${data.by_solar_efficiency.map((s, i) => `
                                    <tr>
                                        <td><strong>#${i + 1}</strong></td>
                                        <td>${s.station_name}</td>
                                        <td class="text-solar">${s.solar_coverage_pct}% Solaire</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>`;

            html += '</div>';
            document.getElementById('ranking-content').innerHTML = html;
        })
        .catch(err => console.error('Erreur classement:', err));
}

// ============================================
// BOUTONS D'ACTION
// ============================================
function refreshData() {
    loadAllData();

    const btn = document.querySelector('.topbar-actions .btn:first-child');
    if (!btn) return;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = 'Actualisation…';
    btn.disabled = true;
    setTimeout(() => {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }, 800);
}

function exportPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Header
    doc.setFontSize(22);
    doc.setTextColor(30, 58, 138);
    doc.text('ONEA Energy Optimizer - Bilan Carbone', 20, 25);

    doc.setFontSize(11);
    doc.setTextColor(100);
    doc.text('Rapport stratégique généré le ' + new Date().toLocaleString('fr-FR'), 20, 35);
    doc.setDrawColor(200);
    doc.line(20, 40, 190, 40);

    // Section 1 : KPIs
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text('1. Synthèse du Mix Énergétique et Impact Environnemental (24h)', 20, 55);

    const kpiData = [
        ['Coût Global (Optimisé)',  document.getElementById('kpi-cost').textContent],
        ['Apport Solaire Gratuit',  document.getElementById('kpi-solar').textContent],
        ['Empreinte Carbone (CO2)', document.getElementById('kpi-co2').textContent],
        ['Gasoil Consommé',         document.getElementById('kpi-gasoil').textContent],
        ['Anomalies Système',       document.getElementById('kpi-anomalies-total').textContent],
    ];

    doc.autoTable({
        startY: 65,
        head: [['Indicateur Stratégique', 'Valeur Enregistrée']],
        body: kpiData,
        theme: 'grid',
        headStyles: { fillColor: [30, 58, 138], fontSize: 11 },
        bodyStyles: { fontSize: 10 },
        columnStyles: { 0: { cellWidth: 100 }, 1: { cellWidth: 70, fontStyle: 'bold' } }
    });

    // Section 2 : Constats
    const finalY = doc.lastAutoTable.finalY;
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text('2. Constats Opérationnels', 20, finalY + 20);

    doc.setFontSize(10);
    doc.setTextColor(80);
    const textContext =
        "L'algorithme a automatiquement basculé les pompages sur le parc solaire (0 FCFA/kWh) durant la journée. " +
        "Les heures de pointe tarifaires de la SONABEL (118 FCFA) ont été esquivées grâce au lissage de la charge (Peak Shaving), " +
        "évitant ainsi les pénalités de dépassement de puissance souscrite.\n\n" +
        "En cas de coupure du réseau, le système a minimisé le fonctionnement des groupes électrogènes pour réduire " +
        "drastiquement l'empreinte carbone et les coûts liés à l'achat de gasoil (675 FCFA/L).";

    doc.text(doc.splitTextToSize(textContext, 170), 20, finalY + 30);

    // Footer
    for (let i = 1; i <= doc.internal.getNumberOfPages(); i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text('ONEA Energy Optimizer V2 | Confidentiel', 105, 290, { align: 'center' });
    }

    doc.save(`ONEA_Bilan_MixEnergetique_${new Date().toISOString().split('T')[0]}.pdf`);
}