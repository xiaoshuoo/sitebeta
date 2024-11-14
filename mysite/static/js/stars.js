function createStars() {
    const starsContainer = document.getElementById('stars');
    const count = 100;
    
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        
        // Случайное положение
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        
        // Случайный размер
        const size = Math.random() * 2 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Случайная задержка анимации
        star.style.animationDelay = `${Math.random() * 2}s`;
        star.style.animationDuration = `${2 + Math.random() * 3}s`;
        
        starsContainer.appendChild(star);
    }
}

document.addEventListener('DOMContentLoaded', createStars); 