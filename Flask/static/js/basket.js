document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll('.item'); // Отримуємо всі елементи товарів
    const grandTotalElement = document.getElementById('grandTotal'); // Елемент для відображення загальної суми

    function updateGrandTotal() {
        let grandTotal = 0; // Ініціалізуємо загальну суму
        items.forEach(item => {
            const itemTotalPrice = parseFloat(item.querySelector('.totalPrice').textContent); // Отримуємо ціну кожного товару
            grandTotal += itemTotalPrice; // Додаємо ціну до загальної суми
        });
        grandTotalElement.textContent = grandTotal.toFixed(2); // Оновлюємо текст елемента загальної суми
    }

    items.forEach(item => {
        const unitPrice = parseFloat(item.querySelector('.totalPrice').textContent); // Отримуємо базову ціну з відповідного товару
        const counterValueInput = item.querySelector('.counter-value'); // Поле вводу для кількості
        const totalPriceElement = item.querySelector('.totalPrice'); // Елемент для відображення загальної ціни
        const decrementButton = item.querySelector('.decrement'); // Кнопка зменшення
        const incrementButton = item.querySelector('.increment'); // Кнопка збільшення
        const itemId = item.dataset.itemId; // Отримуємо ID товару з атрибута data-item-id

        // Функція для оновлення загальної ціни та відправки POST запиту на сервер
        function updateTotalPrice() {
            const count = parseInt(counterValueInput.value, 10); // Отримуємо значення кількості
            const totalPrice = unitPrice * count; // Обчислюємо загальну ціну
            totalPriceElement.textContent = totalPrice.toFixed(2); // Оновлюємо текст елемента
            updateGrandTotal(); // Оновлюємо загальну суму

            // Відправка нової кількості на сервер
            fetch(`/update_quantity/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quantity: count })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    console.log(data.message);
                } else {
                    console.error(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }

        // Обробник події для кнопки зменшення
        decrementButton.addEventListener('click', () => {
            let count = parseInt(counterValueInput.value, 10);
            if (count > 1) {
                count--; // Зменшуємо значення на 1
                counterValueInput.value = count; // Оновлюємо поле вводу
                updateTotalPrice(); // Оновлюємо загальну ціну
            }
        });

        // Обробник події для кнопки збільшення
        incrementButton.addEventListener('click', () => {
            let count = parseInt(counterValueInput.value, 10);
            count++; // Збільшуємо значення на 1
            counterValueInput.value = count; // Оновлюємо поле вводу
            updateTotalPrice(); // Оновлюємо загальну ціну
        });

        // Викликаємо функцію, щоб відобразити початкову ціну
        updateTotalPrice();
    });
});




function toggleSelect(selected) {
    // Сховати всі поля вибору
    const selectFields = document.querySelectorAll('.selectField');
    selectFields.forEach(field => {
        field.style.display = 'none';
    });

    // Показати тільки вибране поле
    const selectedField = document.getElementById(selected);
    if (selectedField) {
        selectedField.style.display = 'block';
    }
}

const phoneInput = document.getElementById("phone");

        // Функція для встановлення префікса +38, якщо його ще немає
function addPrefix() {
    if (!phoneInput.value.startsWith("+38")) {
        phoneInput.value = "+38";
    }
}

        // Викликаємо addPrefix при фокусі на поле вводу
phoneInput.addEventListener("focus", addPrefix);

        // Додаємо обробник для обмеження на 10 цифр після +38 та блокування нецифрових символів
phoneInput.addEventListener("input", () => {
            // Залишаємо тільки цифри після префікса
    const onlyNumbers = phoneInput.value.slice(3).replace(/\D/g, "");

            // Залишаємо лише перші 10 цифр після префікса
    const limitedNumbers = onlyNumbers.slice(0, 10);
            // Оновлюємо значення поля з префіксом +38 та лімітованими цифрами
        phoneInput.value = "+38" + limitedNumbers;
});