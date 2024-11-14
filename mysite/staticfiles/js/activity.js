let activityTimeout;

function updateActivity() {
    fetch('/update-activity/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    });
}

// Обновляем статус каждые 4 минуты
setInterval(updateActivity, 240000);

// Отправляем статус оффлайн при закрытии вкладки
window.addEventListener('beforeunload', () => {
    fetch('/set-offline/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        keepalive: true
    });
}); 