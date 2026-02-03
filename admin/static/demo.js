// Демо-данные для тестирования админки
// Автоматически создаёт несколько тестовых платежей

const DEMO_PAYMENTS = [
    { amount: 1000, orderId: 'DEMO-001' },
    { amount: 2500, orderId: 'DEMO-002' },
    { amount: 500, orderId: 'DEMO-003' },
    { amount: 15000, orderId: 'DEMO-004' },
    { amount: 750, orderId: 'DEMO-005' },
];

// Функция для создания демо-платежей
async function createDemoPayments() {
    console.log('🎮 Создание демо-платежей...');
    
    for (const payment of DEMO_PAYMENTS) {
        try {
            const response = await fetch('/api/create-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payment)
            });
            
            const data = await response.json();
            console.log(`✅ ${payment.orderId}: ${data.success ? 'Успех' : 'Ошибка'}`);
            
            // Задержка между запросами
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.error(`❌ ${payment.orderId}: ${error.message}`);
        }
    }
    
    console.log('🎉 Демо-платежи созданы!');
}

// Экспорт для использования в консоли
window.createDemoPayments = createDemoPayments;

console.log('💡 Для создания демо-платежей введите: createDemoPayments()');
