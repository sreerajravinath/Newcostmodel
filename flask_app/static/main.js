document.addEventListener('DOMContentLoaded', function() {
    const manufacturerSelect = document.querySelector('select[name="manufacturer"]');
    const makeSelect = document.querySelector('select[name="make"]');
    const modelSelect = document.querySelector('select[name="model"]');

    if (manufacturerSelect) {
        manufacturerSelect.addEventListener('change', function() {
            fetchDropdownValues('make', manufacturerSelect.value);
        });
    }

    if (makeSelect) {
        makeSelect.addEventListener('change', function() {
            fetchDropdownValues('model', manufacturerSelect.value, makeSelect.value);
        });
    }

    function fetchDropdownValues(dropdown, manufacturer, make = '') {
        let url = `/lookup/2/${dropdown}?manufacturer=${manufacturer}`;
        if (make) {
            url += `&make=${make}`;
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                let selectElement;
                if (dropdown === 'make') {
                    selectElement = makeSelect;
                } else if (dropdown === 'model') {
                    selectElement = modelSelect;
                }

                selectElement.innerHTML = '';
                data.forEach(value => {
                    let option = document.createElement('option');
                    option.value = value;
                    option.text = value;
                    selectElement.appendChild(option);
                });
            });
    }
});
