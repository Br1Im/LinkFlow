// Просмотр браузера в реальном времени
class BrowserViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.img = null;
        this.isActive = false;
        this.updateInterval = null;
    }
    
    start() {
        if (this.isActive) return;
        
        this.isActive = true;
        
        // Создаем элемент изображения
        if (!this.img) {
            this.img = document.createElement('img');
            this.img.style.width = '100%';
            this.img.style.height = 'auto';
            this.img.style.border = '2px solid rgba(255,255,255,0.2)';
            this.img.style.borderRadius = '8px';
            this.container.appendChild(this.img);
        }
        
        // Обновляем каждые 500ms
        this.updateInterval = setInterval(() => this.updateScreenshot(), 500);
        this.updateScreenshot();
    }
    
    stop() {
        this.isActive = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateScreenshot() {
        if (!this.isActive) return;
        
        try {
            const response = await fetch('/api/browser-screenshot?' + new Date().getTime());
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                // Освобождаем старый URL
                if (this.img.src && this.img.src.startsWith('blob:')) {
                    URL.revokeObjectURL(this.img.src);
                }
                
                this.img.src = url;
            }
        } catch (error) {
            console.error('Failed to update screenshot:', error);
        }
    }
}

// Глобальный экземпляр
window.browserViewer = null;
