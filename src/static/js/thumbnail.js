// Отримуємо елементи
const modal = document.getElementById("modal");
const modalImage = document.getElementById("modal-image");
const captionText = document.getElementById("caption");
const closeBtn = document.querySelector(".close");

// Додаємо обробку кліку для всіх зображень з класом "thumbnail"
document.querySelectorAll(".thumbnail").forEach(img => {
    img.addEventListener("click", function () {
        modal.style.display = "block";           // Показуємо модальне вікно
        modalImage.src = this.src;              // Встановлюємо джерело зображення
        captionText.innerHTML = this.alt;       // Додаємо підпис з атрибута alt
    });
});

// Закриваємо модальне вікно при натисканні на хрестик
closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
});

// Закриваємо модальне вікно при кліку поза зображенням
modal.addEventListener("click", function (e) {
    if (e.target === modal) {
        modal.style.display = "none";
    }
});

