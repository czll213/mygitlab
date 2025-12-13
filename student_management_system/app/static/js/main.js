// Main JavaScript file

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-hide flash messages
    setTimeout(function() {
        $('.alert').fadeOut(500);
    }, 5000);

    // Confirm before delete
    $('.delete-btn').on('click', function(e) {
        if (!confirm('确定要删除这个项目吗？')) {
            e.preventDefault();
        }
    });

    // Form validation
    $('form[data-validate="true"]').on('submit', function(e) {
        var isValid = true;
        $(this).find('input[required], select[required], textarea[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert('请填写所有必填字段。');
        }
    });

    // AJAX form submission
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var submitBtn = form.find('button[type="submit"]');
        var originalText = submitBtn.html();

        // Show loading state
        submitBtn.prop('disabled', true).html('<span class="spinner"></span> Loading...');

        $.ajax({
            url: form.attr('action'),
            method: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    if (response.redirect_url) {
                        setTimeout(function() {
                            window.location.href = response.redirect_url;
                        }, 1500);
                    }
                } else {
                    if (response.errors) {
                        // Show validation errors
                        form.find('.is-invalid').removeClass('is-invalid');
                        form.find('.invalid-feedback').remove();

                        $.each(response.errors, function(field, error) {
                            var input = form.find('[name="' + field + '"]');
                            input.addClass('is-invalid');
                            input.after('<div class="invalid-feedback">' + error + '</div>');
                        });
                    }
                    showAlert(response.message || '发生错误', 'danger');
                }
            },
            error: function(xhr) {
                var message = xhr.responseJSON ? xhr.responseJSON.message : '发生错误';
                showAlert(message, 'danger');
            },
            complete: function() {
                // Restore button state
                submitBtn.prop('disabled', false).html(originalText);
            }
        });
    });

    // Quick search functionality
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#searchTable tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    // Toggle password visibility
    $('.toggle-password').on('click', function() {
        var input = $(this).siblings('input');
        var icon = $(this).find('i');

        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            input.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // Export data functionality
    $('.export-btn').on('click', function() {
        var format = $(this).data('format');
        var table = $(this).data('table');

        if (format === 'csv') {
            exportTableToCSV(table);
        } else if (format === 'print') {
            window.print();
        }
    });

    // Real-time validation
    $('input[data-validate="realtime"]').on('input', function() {
        var input = $(this);
        var value = input.val();
        var type = input.data('type');

        if (type === 'email') {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                input.addClass('is-invalid');
            } else {
                input.removeClass('is-invalid');
            }
        } else if (type === 'phone') {
            var phoneRegex = /^[\d\s\-\+\(\)]+$/;
            if (!phoneRegex.test(value)) {
                input.addClass('is-invalid');
            } else {
                input.removeClass('is-invalid');
            }
        }
    });
});

// Utility functions
function showAlert(message, type) {
    var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
        '</div>';

    $('.container-fluid').prepend(alertHtml);

    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').first().fadeOut(500, function() {
            $(this).remove();
        });
    }, 5000);
}

function exportTableToCSV(tableId) {
    var csv = [];
    var rows = document.querySelectorAll(tableId + ' tr');

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');

        for (var j = 0; j < cols.length; j++) {
            // Remove HTML tags and get text content
            var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/"/g, '""');
            row.push('"' + data + '"');
        }

        csv.push(row.join(','));
    }

    var csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
    var downloadLink = document.createElement('a');

    downloadLink.download = 'export_' + new Date().toISOString().slice(0, 10) + '.csv';
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Loading indicator
function showLoading() {
    $('<div id="loadingOverlay" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;justify-content:center;align-items:center;"><div class="spinner-border text-light" style="width:3rem;height:3rem;" role="status"></div></div>').appendTo('body');
}

function hideLoading() {
    $('#loadingOverlay').remove();
}

// AJAX helpers
function makeAjaxRequest(url, method, data, callback) {
    showLoading();

    $.ajax({
        url: url,
        method: method,
        data: data,
        success: function(response) {
            hideLoading();
            // 检查响应的success字段
            if (response && typeof response === 'object') {
                if (response.success === false) {
                    // 处理业务逻辑失败的情况
                    showAlert(response.message || '操作失败', 'danger');
                } else if (callback) {
                    // 处理成功的情况
                    callback(response);
                }
            } else if (callback) {
                callback(response);
            }
        },
        error: function(xhr) {
            hideLoading();
            var message = xhr.responseJSON ? xhr.responseJSON.message : '发生错误';
            showAlert(message, 'danger');
        }
    });
}

// Enroll in course
function enrollInCourse(courseId) {
    makeAjaxRequest(
        '/student/courses/' + courseId + '/enroll',
        'POST',
        {},
        function(response) {
            // 这里的response已经是success=true的情况，因为makeAjaxRequest已经处理了success=false的情况
            showAlert(response.message || '选课成功', 'success');
            setTimeout(() => location.reload(), 1500);
        }
    );
}

// Drop course
function dropCourse(courseId) {
    if (confirm('确定要退选这门课程吗？')) {
        makeAjaxRequest(
            '/student/courses/' + courseId + '/drop',
            'POST',
            {},
            function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                }
            }
        );
    }
}

// Delete item
function deleteItem(url, itemId) {
    if (confirm('确定要删除这个项目吗？')) {
        makeAjaxRequest(
            url.replace(':id', itemId),
            'POST',
            { _method: 'DELETE' },
            function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    $('#item-' + itemId).fadeOut(500, function() {
                        $(this).remove();
                    });
                }
            }
        );
    }
}