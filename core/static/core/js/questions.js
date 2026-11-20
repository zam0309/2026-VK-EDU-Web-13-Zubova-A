async function send(url, data) {
    const token = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': token},
        body: new URLSearchParams(data),
    });

    if (response.status === 401) {
        throw new Error('Войдите в аккаунт и попробуйте снова.');
    }

    const type = response.headers.get('content-type') || '';
    const result = type.includes('application/json') ? await response.json() : {};
    if (!response.ok) {
        throw new Error(result.error || 'Не удалось сохранить. Обновите страницу и попробуйте снова.');
    }
    return result;
}

for (const vote of document.querySelectorAll('[data-vote]')) {
    const buttons = vote.querySelectorAll('button');
    for (const button of buttons) {
        button.addEventListener('click', async () => {
            for (const item of buttons) item.disabled = true;
            try {
                const result = await send(vote.dataset.vote, {value: button.value});
                vote.querySelector('.fw-bold').textContent = result.rating;
            } catch (error) {
                alert(error.message);
            } finally {
                for (const item of buttons) item.disabled = false;
            }
        });
    }
}

const boxes = document.querySelectorAll('[data-correct]');
for (const box of boxes) {
    box.addEventListener('change', async () => {
        const checked = box.checked;
        for (const item of boxes) item.disabled = true;
        try {
            const result = await send(box.dataset.correct, {
                answer: box.value,
                checked: checked ? '1' : '0',
            });
            for (const item of boxes) {
                if (item === box || result.checked) {
                    item.checked = item === box && result.checked;
                    item.closest('.card').classList.toggle('answer-correct', item.checked);
                }
            }
        } catch (error) {
            box.checked = !checked;
            alert(error.message);
        } finally {
            for (const item of boxes) item.disabled = false;
        }
    });
}
