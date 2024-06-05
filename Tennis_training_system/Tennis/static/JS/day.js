const day = document.querySelector(".day"),
    prevDayBtn = document.querySelector(".prev-day-btn"),
    nextDayBtn = document.querySelector(".next-day-btn"),
    daysContainer = document.querySelector(".day-grid-tile-container"),
    timelineContainer = document.querySelector(".timeline"),
    eventsContainer = document.querySelector(".event-container");

let eventsCode = "";

const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
];

const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

const monthsWith30Days = ["April", "June", "September", "November"];
const monthsWith31Days = ["January", "March", "May", "July", "August", "October", "December"];

const date = new Date();

let currentDay = date.getDay();
let currentDate = date.getDate();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();

function renderDay() {
    day.innerHTML = `${days[currentDay]} <br> ${currentDate} ${months[currentMonth]} ${currentYear}`;
}

function isLeapYear(year) {
    return (year % 100 === 0) ? (year % 400 === 0) : (year % 4 === 0);
}

function nextMonth() {
    currentDate = 1;
    currentMonth++;
}

function checkIfNewYearAndIncrement(month){
    if((month+1) > 11){
        currentDate = 1;
        currentMonth = 0;
        currentYear++;
    }
    else {
        nextMonth()
    }
}

function generateTimeline() {
    let hours = "";

    for (let i = 1; i <= 23; i++) {
        hours += `<div class="hour">${i}:00</div>`;
    }
    timelineContainer.innerHTML = hours;
}

function generateDay() {
    const day = `<div class="day-grid-tile"></div>`;
    daysContainer.innerHTML = day;
}

function generateBreakLines() {
    let breakLines = '';

    breakLines += `<div class="day-break-line" id="blank-day-break-line"></div>`;

    for (let i = 0; i <= 22; i++) {
        breakLines += `<div class="day-break-line"></div>`;
    }
    const dayBreakLines = document.querySelector(".day-grid-tile");
    dayBreakLines.innerHTML = breakLines;
}

function convertStringTimeToMinutes(time) {
    let [hours, minutes] = time.split(':');
    let hoursInt = parseInt(hours);
    let hoursToMinutes = hoursInt*60;
    let minutesFloat = parseFloat(minutes);
    let convertedTime = hoursToMinutes + minutesFloat;

    return convertedTime;
}

function eventDuration(startTimeStr, endTimeStr) {
    let startTimeInMinutes = convertStringTimeToMinutes(startTimeStr);
    let endTimeInMinutes = convertStringTimeToMinutes(endTimeStr);
    let eventLength = (endTimeInMinutes - startTimeInMinutes)/60;

    return eventLength.toFixed(2);
}

function adjustLength(start, end, id) {
    let length = 100 * eventDuration(start, end);
    let startTime = convertStringTimeToMinutes(start)/60;

    // const elementToChange = document.querySelector(`#${id}`);
    const elementToChange = document.querySelector(`[data-id="${id}" ]`);
    elementToChange.style.marginTop = `${startTime * 100}px`;
    elementToChange.style.height = `${length}px`;
}

function getEventsForDay(dayParam="") {
    eventsCode = "";
    let day = dayParam;
    if(day === "") {
        day = new Date();
        day = `${day.getFullYear()}-${day.getMonth()+1}-${day.getDate()}`;
    }

    const data = {"day" :day};
    console.log(data);
    fetch("/getEventsForDay", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then(function (response) {
        // console.log(response.json());
        return response.json();
    }).then(function (events) {
        eventsContainer.innerHTML = "";
        placeEvents(events);
    });
}

function placeEvents(events) {
    events.forEach(event => {
        addEvent(event);
    });

    const eventsContainer = document.querySelector(".event-container");
    eventsContainer.innerHTML = eventsCode;

    events.forEach(event=> {
        adjustLength(event.startTime, event.endTime, event.eventID);
    });
}

function addEvent(event){
    // eventsCode += `<div class="event-tile event-tile-${event.category}" id="${event.eventID}">
    eventsCode += `<div class="event-tile event-tile-${event.category}" data-id="${event.eventID}">    
                 <div class="side-color side-color-${event.category}">
                    <div class="picture-for-event"><img src="public/avatars/${event.avatar}"/></div>   
                 </div>
                 <div class="event-desc">
                    <div class="event-name">${event.title}</div>
                    <div class="event-time">${event.startTime} - ${event.endTime}</div>
                 </div>
               </div>`;
}

nextDayBtn.addEventListener("click", () => {
    currentDay++;
    currentDate++;
    let dayToDisplay = `${currentYear}-${currentMonth+1}-${currentDate}`;

    if (monthsWith30Days.includes(months[currentMonth]) && currentDate > 30) {
        nextMonth();
    }
    else if (monthsWith31Days.includes(months[currentMonth]) && currentDate > 31) {
        checkIfNewYearAndIncrement(currentMonth);
    }
    else if (currentMonth === 1){
        if(isLeapYear(currentYear)) {
            if(currentDate > 29) {
                nextMonth();
            }
        }
        else if (currentDate > 28){
            nextMonth();
        }
    }

    if (currentDay > 6) {
        currentDay = 0;
    }
    getEventsForDay(dayToDisplay);
    renderDay();
});

prevDayBtn.addEventListener("click", () => {
    currentDay--;
    currentDate--;

    if (currentDate < 1){
        if (monthsWith30Days.includes(months[currentMonth-1])) {
            currentDate = 30;
            currentMonth--;
        }
        else if (monthsWith31Days.includes(months[currentMonth-1])){
            currentDate = 31;
            currentMonth--;
        }
        else if ((currentMonth - 1) < 0){
            currentMonth = 11;
            currentYear--;
            currentDate = 31;
        }
        else if ((currentMonth - 1) === 1){
            if(isLeapYear(currentYear)) {
                currentDate = 29;
                currentMonth--;
            }
            else {
                currentDate = 28;
                currentMonth--;
            }
        }
    }

    if (currentDay < 0) {
        currentDay = 6;
    }
    let dayToDisplay = `${currentYear}-${currentMonth+1}-${currentDate}`;
    getEventsForDay(dayToDisplay);
    renderDay();
});

renderDay();
generateDay();
generateBreakLines();
generateTimeline();
getEventsForDay();