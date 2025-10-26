document.addEventListener('DOMContentLoaded', function() {
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    
    //минимальая дата заезда = сегодня
    const today = new Date().toISOString().split('T')[0];
    checkInInput.min = today;
    
    //при изменении даты заезда обновляем минимальную дату выезда
    checkInInput.addEventListener('change', function() {
        if (checkInInput.value) {
            const nextDay = new Date(checkInInput.value);
            nextDay.setDate(nextDay.getDate() + 1);
            checkOutInput.min = nextDay.toISOString().split('T')[0];
            
            //если дата выезда меньше новой минимальной, то очищаем её
            if (checkOutInput.value && checkOutInput.value < checkOutInput.min) {
                checkOutInput.value = '';
            }
        }
    });
});