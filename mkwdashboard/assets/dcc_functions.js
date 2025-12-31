window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.msToTimedelta = function(value) {
    const seconds = Math.floor(value / 1000);
    const milliseconds = Math.floor(value % 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secondsRemaining = seconds % 60;

    if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secondsRemaining.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
    } else {
        return `${minutes.toString().padStart(2, '0')}:${secondsRemaining.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
    }
}