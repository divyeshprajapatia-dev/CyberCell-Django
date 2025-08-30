// CyberCell - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation styles
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Custom file input label
    var fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = '';
            if (this.files && this.files.length > 1) {
                fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
            } else {
                fileName = e.target.value.split('\\').pop();
            }
            if (fileName) {
                var label = this.nextElementSibling;
                if (label) {
                    label.innerHTML = fileName;
                }
            }
        });
    });

    // Date range picker initialization
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.flatpickr-date', {
            dateFormat: 'Y-m-d',
            allowInput: true
        });

        flatpickr('.flatpickr-datetime', {
            enableTime: true,
            dateFormat: 'Y-m-d H:i',
            time_24hr: true,
            allowInput: true
        });

        flatpickr('.flatpickr-time', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            allowInput: true
        });

        flatpickr('.flatpickr-range', {
            mode: 'range',
            dateFormat: 'Y-m-d',
            allowInput: true
        });
    }

    // Crime statistics chart initialization
    function initCrimeStatsChart() {
        const crimeStatsChart = document.getElementById('crimeStatsChart');
        if (crimeStatsChart) {
            fetch('/api/crime-stats/')
                .then(response => response.json())
                .then(data => {
                    // Category chart
                    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
                    const categoryData = {
                        labels: data.categories.map(item => item.name),
                        datasets: [{
                            label: 'Reports by Category',
                            data: data.categories.map(item => item.count),
                            backgroundColor: [
                                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69',
                                '#6610f2', '#6f42c1', '#fd7e14', '#20c9a6', '#27a844', '#e83e8c'
                            ],
                            hoverBackgroundColor: [
                                '#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617', '#4e4f58',
                                '#5a0acf', '#5d37a8', '#dc6b02', '#169b7f', '#1f8c39', '#c71666'
                            ],
                            hoverBorderColor: "rgba(234, 236, 244, 1)",
                        }]
                    };
                    new Chart(categoryCtx, {
                        type: 'doughnut',
                        data: categoryData,
                        options: {
                            maintainAspectRatio: false,
                            tooltips: {
                                backgroundColor: "rgb(255,255,255)",
                                bodyFontColor: "#858796",
                                borderColor: '#dddfeb',
                                borderWidth: 1,
                                xPadding: 15,
                                yPadding: 15,
                                displayColors: false,
                                caretPadding: 10,
                            },
                            legend: {
                                display: true,
                                position: 'bottom'
                            },
                            cutoutPercentage: 70,
                        },
                    });

                    // Status chart
                    const statusCtx = document.getElementById('statusChart').getContext('2d');
                    const statusData = {
                        labels: data.statuses.map(item => item.status),
                        datasets: [{
                            label: 'Reports by Status',
                            data: data.statuses.map(item => item.count),
                            backgroundColor: [
                                '#f6c23e', '#4e73df', '#1cc88a', '#5a5c69', '#e74a3b'
                            ],
                            hoverBackgroundColor: [
                                '#dda20a', '#2e59d9', '#17a673', '#4e4f58', '#be2617'
                            ],
                            hoverBorderColor: "rgba(234, 236, 244, 1)",
                        }]
                    };
                    new Chart(statusCtx, {
                        type: 'pie',
                        data: statusData,
                        options: {
                            maintainAspectRatio: false,
                            tooltips: {
                                backgroundColor: "rgb(255,255,255)",
                                bodyFontColor: "#858796",
                                borderColor: '#dddfeb',
                                borderWidth: 1,
                                xPadding: 15,
                                yPadding: 15,
                                displayColors: false,
                                caretPadding: 10,
                            },
                            legend: {
                                display: true,
                                position: 'bottom'
                            },
                        },
                    });

                    // Monthly trend chart
                    const monthlyCtx = document.getElementById('monthlyTrendChart');
                    if (monthlyCtx) {
                        const monthlyData = {
                            labels: data.monthly.map(item => item.month),
                            datasets: [{
                                label: 'Reports per Month',
                                data: data.monthly.map(item => item.count),
                                lineTension: 0.3,
                                backgroundColor: "rgba(78, 115, 223, 0.05)",
                                borderColor: "rgba(78, 115, 223, 1)",
                                pointRadius: 3,
                                pointBackgroundColor: "rgba(78, 115, 223, 1)",
                                pointBorderColor: "rgba(78, 115, 223, 1)",
                                pointHoverRadius: 3,
                                pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                                pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                                pointHitRadius: 10,
                                pointBorderWidth: 2,
                                fill: true
                            }]
                        };
                        new Chart(monthlyCtx, {
                            type: 'line',
                            data: monthlyData,
                            options: {
                                maintainAspectRatio: false,
                                layout: {
                                    padding: {
                                        left: 10,
                                        right: 25,
                                        top: 25,
                                        bottom: 0
                                    }
                                },
                                scales: {
                                    xAxes: [{
                                        time: {
                                            unit: 'month'
                                        },
                                        gridLines: {
                                            display: false,
                                            drawBorder: false
                                        },
                                        ticks: {
                                            maxTicksLimit: 7
                                        }
                                    }],
                                    yAxes: [{
                                        ticks: {
                                            maxTicksLimit: 5,
                                            padding: 10,
                                            beginAtZero: true
                                        },
                                        gridLines: {
                                            color: "rgb(234, 236, 244)",
                                            zeroLineColor: "rgb(234, 236, 244)",
                                            drawBorder: false,
                                            borderDash: [2],
                                            zeroLineBorderDash: [2]
                                        }
                                    }],
                                },
                                legend: {
                                    display: false
                                },
                                tooltips: {
                                    backgroundColor: "rgb(255,255,255)",
                                    bodyFontColor: "#858796",
                                    titleMarginBottom: 10,
                                    titleFontColor: '#6e707e',
                                    titleFontSize: 14,
                                    borderColor: '#dddfeb',
                                    borderWidth: 1,
                                    xPadding: 15,
                                    yPadding: 15,
                                    displayColors: false,
                                    intersect: false,
                                    mode: 'index',
                                    caretPadding: 10,
                                }
                            }
                        });
                    }

                    // Location chart
                    const locationCtx = document.getElementById('locationChart');
                    if (locationCtx) {
                        const locationData = {
                            labels: data.locations.map(item => item.city + ', ' + item.state),
                            datasets: [{
                                label: 'Reports by Location',
                                data: data.locations.map(item => item.count),
                                backgroundColor: '#4e73df',
                                hoverBackgroundColor: '#2e59d9',
                                borderWidth: 1
                            }]
                        };
                        new Chart(locationCtx, {
                            type: 'horizontalBar',
                            data: locationData,
                            options: {
                                maintainAspectRatio: false,
                                layout: {
                                    padding: {
                                        left: 10,
                                        right: 25,
                                        top: 25,
                                        bottom: 0
                                    }
                                },
                                scales: {
                                    xAxes: [{
                                        gridLines: {
                                            display: false,
                                            drawBorder: false
                                        },
                                        ticks: {
                                            beginAtZero: true
                                        }
                                    }],
                                    yAxes: [{
                                        ticks: {
                                            padding: 10
                                        },
                                        gridLines: {
                                            color: "rgb(234, 236, 244)",
                                            zeroLineColor: "rgb(234, 236, 244)",
                                            drawBorder: false,
                                            borderDash: [2],
                                            zeroLineBorderDash: [2]
                                        }
                                    }],
                                },
                                legend: {
                                    display: false
                                },
                                tooltips: {
                                    backgroundColor: "rgb(255,255,255)",
                                    bodyFontColor: "#858796",
                                    titleMarginBottom: 10,
                                    titleFontColor: '#6e707e',
                                    titleFontSize: 14,
                                    borderColor: '#dddfeb',
                                    borderWidth: 1,
                                    xPadding: 15,
                                    yPadding: 15,
                                    displayColors: false,
                                    caretPadding: 10,
                                }
                            }
                        });
                    }
                })
                .catch(error => console.error('Error loading crime statistics:', error));
        }
    }

    // Initialize crime stats charts if they exist on the page
    initCrimeStatsChart();

    // Dashboard charts initialization
    function initDashboardCharts() {
        const dashboardCharts = document.getElementById('dashboardCharts');
        if (dashboardCharts) {
            fetch('/api/crime-stats/')
                .then(response => response.json())
                .then(data => {
                    // Monthly trend chart for dashboard
                    const monthlyTrendCtx = document.getElementById('monthlyReportsChart').getContext('2d');
                    const monthlyTrendData = {
                        labels: data.monthly.slice(-6).map(item => item.month),
                        datasets: [{
                            label: 'Reports',
                            data: data.monthly.slice(-6).map(item => item.count),
                            lineTension: 0.3,
                            backgroundColor: "rgba(78, 115, 223, 0.05)",
                            borderColor: "rgba(78, 115, 223, 1)",
                            pointRadius: 3,
                            pointBackgroundColor: "rgba(78, 115, 223, 1)",
                            pointBorderColor: "rgba(78, 115, 223, 1)",
                            pointHoverRadius: 3,
                            pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                            pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                            pointHitRadius: 10,
                            pointBorderWidth: 2,
                            fill: true
                        }]
                    };
                    new Chart(monthlyTrendCtx, {
                        type: 'line',
                        data: monthlyTrendData,
                        options: {
                            maintainAspectRatio: false,
                            layout: {
                                padding: {
                                    left: 10,
                                    right: 25,
                                    top: 25,
                                    bottom: 0
                                }
                            },
                            scales: {
                                xAxes: [{
                                    time: {
                                        unit: 'month'
                                    },
                                    gridLines: {
                                        display: false,
                                        drawBorder: false
                                    },
                                    ticks: {
                                        maxTicksLimit: 7
                                    }
                                }],
                                yAxes: [{
                                    ticks: {
                                        maxTicksLimit: 5,
                                        padding: 10,
                                        beginAtZero: true
                                    },
                                    gridLines: {
                                        color: "rgb(234, 236, 244)",
                                        zeroLineColor: "rgb(234, 236, 244)",
                                        drawBorder: false,
                                        borderDash: [2],
                                        zeroLineBorderDash: [2]
                                    }
                                }],
                            },
                            legend: {
                                display: false
                            },
                            tooltips: {
                                backgroundColor: "rgb(255,255,255)",
                                bodyFontColor: "#858796",
                                titleMarginBottom: 10,
                                titleFontColor: '#6e707e',
                                titleFontSize: 14,
                                borderColor: '#dddfeb',
                                borderWidth: 1,
                                xPadding: 15,
                                yPadding: 15,
                                displayColors: false,
                                intersect: false,
                                mode: 'index',
                                caretPadding: 10,
                            }
                        }
                    });

                    // Category doughnut chart for dashboard
                    const categoryDoughnutCtx = document.getElementById('categoryDoughnutChart').getContext('2d');
                    const categoryDoughnutData = {
                        labels: data.categories.map(item => item.name),
                        datasets: [{
                            data: data.categories.map(item => item.count),
                            backgroundColor: [
                                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69'
                            ],
                            hoverBackgroundColor: [
                                '#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617', '#4e4f58'
                            ],
                            hoverBorderColor: "rgba(234, 236, 244, 1)",
                        }]
                    };
                    new Chart(categoryDoughnutCtx, {
                        type: 'doughnut',
                        data: categoryDoughnutData,
                        options: {
                            maintainAspectRatio: false,
                            tooltips: {
                                backgroundColor: "rgb(255,255,255)",
                                bodyFontColor: "#858796",
                                borderColor: '#dddfeb',
                                borderWidth: 1,
                                xPadding: 15,
                                yPadding: 15,
                                displayColors: false,
                                caretPadding: 10,
                            },
                            legend: {
                                display: true,
                                position: 'bottom'
                            },
                            cutoutPercentage: 70,
                        },
                    });
                })
                .catch(error => console.error('Error loading dashboard data:', error));
        }
    }

    // Initialize dashboard charts if they exist on the page
    initDashboardCharts();

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const textToCopy = this.getAttribute('data-copy');
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success message
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    });

    // Back to top button
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });

        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
});