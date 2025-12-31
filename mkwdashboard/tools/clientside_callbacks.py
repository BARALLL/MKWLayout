slider_time_formatting_callback = """
    function(value) {
        const tooltips = document.querySelectorAll('.rc-slider-tooltip-inner');

        if (!Array.isArray(value)) {
            value = [value];
        }

        tooltips.forEach((el, index) => {
            const val = value[index];
            if (val !== undefined) {
                const totalSeconds = val / 1000;
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                const formatted = String(minutes).padStart(2, '0') + ':' + 
                                  seconds.toFixed(2).padStart(5, '0');
                el.innerText = formatted;
            }
        });

        return window.dash_clientside.no_update;
    }
    """