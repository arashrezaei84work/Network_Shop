document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-to-cart-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const url = form.dataset.url;
        const quantity = document.getElementById('qty-input').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        Swal.fire({
            title: 'در حال افزودن...',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ quantity })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error('INVALID_RESPONSE');
            }
            return res.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'به سبد اضافه شد!',
                    text: 'می‌خواهید سبد خرید را مشاهده کنید؟',
                    icon: 'success',
                    showCancelButton: true,
                    confirmButtonText: 'مشاهده سبد',
                    cancelButtonText: 'ادامه خرید'
                }).then(r => {
                    if (r.isConfirmed) {
                        window.location.href = CART_URL;
                    }
                });
            } else if (data.error === 'AUTH_REQUIRED') {
                Swal.fire('خطا', 'لطفاً ابتدا وارد حساب شوید', 'warning');
            } else {
                Swal.fire('خطا', data.error || 'خطای ناشناخته', 'error');
            }
        })
        .catch(() => {
            Swal.fire('خطا', 'پاسخ نامعتبر از سرور', 'error');
        });
    });
});
