const day = document.querySelector(".day"),
    prevDayBtn = document.querySelector(".prev-day-btn"),
    nextDayBtn = document.querySelector(".next-day-btn"),

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
