// charger toutes les données au démarrage
document.addEventListener('DOMContentLoaded', function() {
    loadKPI();
    loadPredictions();
    loadSchedule();
    loadAnomalies();
    loadRanking();
});

// charger les KPI
function loadKPI() {
    fetch('/api/kpi')
        .then(response => response.json())
        .then(data => {
            document.getElementById('kpi-energy').textContent = data.total_energy_kwh + ' kWh';
            document.getElementById('kpi-cost').textContent = data.total_cost_fcfa.toLocaleString() + ' FCFA';
            document.getElementById('kpi-anomalies').textContent = data.total_anomalies;
            document.getElementById('kpi-critical').textContent = data.critical_anomalies + ' critiques';
            document.getElementById('kpi-station').textContent = data.top_station_name;
            document.getElementById('kpi-station-energy').textContent = data.top_station_energy + ' kWh';
        })
        .catch(error => console.error('Erreur KPI:', error));
}

// charger et afficher les prévisions
function loadPredictions() {
    fetch('/api/predictions')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(d => d.hour + 'h');
            const energyValues = data.map(d => d.energy_predicted);
            
            const ctx = document.getElementById('predictionsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Énergie prévue (kWh)',
                        data: energyValues,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erreur prévisions:', error));
}

// charger et afficher le planning
function loadSchedule() {
    fetch('/api/schedule')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(d => d.hour + 'h');
            const pumpRates = data.map(d => d.pump_rate);
            const costs = data.map(d => d.cost_fcfa);
            
            const ctx = document.getElementById('scheduleChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Taux de pompage (%)',
                            data: pumpRates,
                            backgroundColor: 'rgba(52, 211, 153, 0.7)',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Coût (FCFA)',
                            data: costs,
                            backgroundColor: 'rgba(251, 146, 60, 0.7)',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Taux de pompage (%)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Coût (FCFA)'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erreur planning:', error));
}

// charger et afficher les anomalies (HYBRIDE: règles + ML)
function loadAnomalies() {
    fetch('/api/anomalies')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('anomalies-list');
            
            // Vérifier si données hybrides disponibles
            const ruleAnomalies = data.rule_based || [];
            const mlAnomalies = data.ml_based || [];
            const totalAnomalies = ruleAnomalies.length + mlAnomalies.length;
            
            if (totalAnomalies === 0) {
                container.innerHTML = '<p style="text-align:center; color:#999;">✓ Aucune anomalie détectée</p>';
                return;
            }
            
            let html = '';
            
            // Section 1: Anomalies détectées par règles
            if (ruleAnomalies.length > 0) {
                html += '<h3 style="color:#028090; margin-top:10px;">🔍 Détection par Règles (' + ruleAnomalies.length + ')</h3>';
                const topRules = ruleAnomalies.slice(0, 5);
                html += topRules.map(anomaly => `
                    <div class="anomaly-item ${anomaly.severity}" style="border-left:4px solid #028090;">
                        <div class="anomaly-header">
                            ${anomaly.date} - ${anomaly.hour}h - ${anomaly.severity}
                            <span style="float:right; font-size:11px; color:#666;">RÈGLE</span>
                        </div>
                        <div class="anomaly-details">
                            Débit: ${anomaly.flow} m³/h | Énergie: ${anomaly.energy} kWh | Niveau: ${anomaly.level}%
                        </div>
                        <div class="anomaly-alerts">
                            ${anomaly.alerts.map(alert => `<span class="alert-badge">${alert}</span>`).join('')}
                        </div>
                    </div>
                `).join('');
            }
            
            // Section 2: Anomalies détectées par ML
            if (mlAnomalies.length > 0) {
                html += '<h3 style="color:#02C39A; margin-top:20px;">🤖 Détection par IA (' + mlAnomalies.length + ')</h3>';
                const topML = mlAnomalies.slice(0, 5);
                html += topML.map(anomaly => `
                    <div class="anomaly-item" style="border-left:4px solid #02C39A; background:#f0fdf4;">
                        <div class="anomaly-header">
                            ${anomaly.date} - ${anomaly.hour}h
                            <span style="float:right; font-size:11px; color:#666;">ML (Isolation Forest)</span>
                        </div>
                        <div class="anomaly-details">
                            Débit: ${anomaly.flow} m³/h | Énergie: ${anomaly.energy} kWh | Niveau: ${anomaly.level}%
                        </div>
                        <div class="anomaly-alerts">
                            <span class="alert-badge" style="background:#02C39A;">${anomaly.subtype}</span>
                        </div>
                    </div>
                `).join('');
            }
            
            // Message informatif
            html += '<p style="text-align:center; color:#666; font-size:12px; margin-top:20px; padding:10px; background:#f9f9f9; border-radius:4px;">'+
                    '✓ Approche hybride : Règles (anomalies connues) + ML (patterns inhabituels)</p>';
            
            container.innerHTML = html;
        })
        .catch(error => console.error('Erreur anomalies:', error));
}

// charger et afficher le classement
function loadRanking() {
    fetch('/api/ranking')
        .then(response => response.json())
        .then(data => {
            const stations = data.by_energy_consumption;
            
            const labels = stations.map(s => s.station_name);
            const energyValues = stations.map(s => s.total_energy_kwh);
            
            // couleurs selon catégorie
            const colors = stations.map(s => {
                if (s.category === 'TRES_ENERGIVORE') return 'rgba(239, 68, 68, 0.7)';
                if (s.category === 'ENERGIVORE') return 'rgba(251, 146, 60, 0.7)';
                return 'rgba(34, 197, 94, 0.7)';
            });
            
            const ctx = document.getElementById('rankingChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Consommation (kWh)',
                        data: energyValues,
                        backgroundColor: colors
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erreur classement:', error));
}
