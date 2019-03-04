const WEATHER_IMAGE_PATH = '/static/image/weather/';

const REGION_CODE = {
    서울: 1,
    대전: 2,
    대구: 3,
    부산: 4
};
Object.freeze(REGION_CODE);

function createTooltipBtn(id, klass) {
    let tooltipBtn = getElement('button', {
        id: id,
        klass: klass
    });
    tooltipBtn.appendChild(getElement('i', {
        klass: 'far fa-sun'
    }));
    return tooltipBtn;
}

function appendSmallOnElement(text, element, klass) {
    let small = getElement('small', {
        klass: klass,
    });
    small.innerHTML = text;
    element.appendChild(small);
}

function appendIconOnElement(icons, element, klass) {
    for (let word of icons) {
        let img = getElement('img', {
            klass: klass
        });
        img.src = [WEATHER_IMAGE_PATH, word, '.png'].join('');
        element.appendChild(img);
    }
}

function compareByRegion(first, second) {
    if (REGION_CODE[first.region_name] < REGION_CODE[second.region_name]) {
        return -1;
    }
    if (REGION_CODE[first.region_name] > REGION_CODE[second.region_name]) {
        return 1;
    }
    return 0;
}

function getFullyAttachedBtn(dateSquare, element) {
    const btnId = 'forecast-tooltip-btn-' + element.date;
    const btnClass = 'forecast-tooltip-btn';
    const btn = createTooltipBtn(btnId, btnClass);

    /* btn에 커서를 올릴 때 tooltip이 나타나기 위한 설정. */
    btn.setAttribute('data-toggle', 'tooltip');
    btn.setAttribute('data-html', 'true');
    btn.setAttribute('data-title', ' ');
    btn.setAttribute('data-placement', 'bottom');

    /* 서울 대구 대전 부산 순서로 나타나도록 정렬. */
    element.forecasts.sort(compareByRegion);

    for (let forecast of element.forecasts) {
        let anchor = getElement('a');
        appendSmallOnElement(forecast.region_name, anchor, 'weather-content');
        appendSmallOnElement(forecast.temperature, anchor, 'weather-content');

        /* 날씨 아이콘이 일관된 순서로 나타나도록 정렬. */
        forecast.weather.sort();
        appendIconOnElement(forecast.weather, anchor, 'weather-icon');
        btn.setAttribute('data-title', [btn.getAttribute('data-title'), anchor.outerHTML, '<br>'].join());
    }
    return btn;
}

function setTooltipCSS(tooltipDoms) {
    tooltipDoms.hover(function () {
        const tooltipInners = $('.tooltip-inner');
        tooltipInners.css('text-align', 'left');
        tooltipInners.css('background-color', '#f4f4f4');
    });
}
