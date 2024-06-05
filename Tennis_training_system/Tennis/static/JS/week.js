const week = document.querySelector(".week"),
    prevWeekBtn = document.querySelector(".prev-week-btn"),
    nextWeekBtn = document.querySelector(".next-week-btn"),
    daysForTheWeekContainerMonday = document.querySelector(".monday-grid-tiles"),
    daysForTheWeekContainerTuesday = document.querySelector(".tuesday-grid-tiles"),
    daysForTheWeekContainerWednesday = document.querySelector(".wednesday-grid-tiles"),
    daysForTheWeekContainerThursday =  document.querySelector(".thursday-grid-tiles"),
    daysForTheWeekContainerFriday =  document.querySelector(".friday-grid-tiles"),
    daysForTheWeekContainerSaturday =  document.querySelector(".saturday-grid-tiles"),
    daysForTheWeekContainerSunday =  document.querySelector(".sunday-grid-tiles"),
    timelineContainer = document.querySelector(".timeline");


const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
];

const monthsWith30Days = ["Apr", "Jun", "Sept", "Nov"];
const monthsWith31Days = ["Jan", "Mar", "May", "Jul", "Aug", "Oct", "Dec"];

const date = new Date();

let currentDate = date.getDate();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();
let lastDayMonth = currentMonth;
let firstDay = currentDate - date.getDay();
let lastDay = firstDay + 6;


function renderWeek() {
    week.innerHTML = `${firstDay}  ${months[currentMonth]}  ${currentYear} - ${lastDay}  ${months[lastDayMonth]}  ${currentYear}`;
}
renderWeek();

function isLeapYear(year) {
    return (year % 100 === 0) ? (year % 400 === 0) : (year % 4 === 0);
}

function checkIfNewYearAndIncrement(month){
    if((month+1) > 11){
        firstDay -= 31;
        lastDay = firstDay + 6;
        currentMonth = 0;
        currentYear++;
        lastDayMonth = currentMonth;
    }
    else {
        currentMonth++;
        firstDay -= 31;
        lastDay = firstDay + 6;
    }
}

function nextWeek() {
    firstDay+=7;
    lastDay = firstDay + 6;
    checkIfLastDayForNextMonthIsMoreThan30or31();

    if(monthsWith30Days.includes(months[currentMonth]) && firstDay > 30){
        currentMonth++;
        firstDay -= 30;
    }
    else if(monthsWith31Days.includes(months[currentMonth]) && firstDay > 31){
        checkIfNewYearAndIncrement(currentMonth);
    }
    else if ((currentMonth) === 1){
        if(isLeapYear(currentYear) && firstDay > 29) {
            currentMonth++;
            firstDay -=29;
        }
        else if(firstDay > 28) {
            currentMonth++;
            firstDay -=28;
        }
    }
    renderWeek();
}

function checkIfLastDayForNextMonthIsMoreThan30or31(){
    lastDay = firstDay + 6;

    if(monthsWith30Days.includes(months[currentMonth]) && lastDay > 30){
        lastDayMonth = currentMonth+1;
        lastDay -= 30;
    }
    else if(monthsWith31Days.includes(months[currentMonth]) && lastDay > 31){
        lastDayMonth = currentMonth+1;
        lastDay -= 31;
        if(lastDayMonth > 11){
            lastDayMonth = 0;
        }
    }
    else if ((currentMonth) === 1){
        if(isLeapYear(currentYear) && lastDay > 29) {
            lastDayMonth = currentMonth+1;
            lastDay -= 29;
        }
        else if (lastDay > 28) {
            lastDayMonth = currentMonth+1;
            lastDay -= 28;
        }
    }
    else if(lastDay <= 31){
        lastDayMonth = currentMonth;
    }
}

function checkIfLastDayForPrevMonthIsMoreThan30or31(){
    lastDay = firstDay + 6;
    if(monthsWith30Days.includes(months[currentMonth-1]) && lastDay > 30){
        lastDayMonth = currentMonth+1;
        lastDay -= 30;
    }
    else if(monthsWith31Days.includes(months[currentMonth-1]) && lastDay > 31){
        lastDayMonth = currentMonth+1;
        lastDay -= 31;
    }
    else if ((currentMonth-1) === 1){
        if(isLeapYear(currentYear) && lastDay > 29) {
            lastDayMonth = currentMonth+1;
            lastDay -= 29;
        }
        else if (lastDay > 28) {
            lastDayMonth = currentMonth+1;
            lastDay -= 28;
        }
        else{
            lastDayMonth = currentMonth;
        }
    }
    else if(lastDay <= 31){
        lastDayMonth = currentMonth;
    }
}

function checkIfLastDayIsLessThan1() {
    if (lastDay < 1){
        if (monthsWith30Days.includes(months[currentMonth-1])) {
            lastDay = 30;
        }
        else if (monthsWith31Days.includes(months[currentMonth - 1])) {
            lastDay = 31;
        }
        else if (currentMonth - 1 === 1){
            if(isLeapYear(currentYear)) {
                lastDay = 29;
            }
            else{
                lastDay = 28;
            }
        }
    }
}
function prevWeek(){
    firstDay-=7;
    lastDay = firstDay + 6;
    checkIfLastDayForPrevMonthIsMoreThan30or31();
    checkIfLastDayIsLessThan1();
    if (firstDay < 1) {
        if (monthsWith30Days.includes(months[currentMonth - 1])) {
            firstDay += 30;
            currentMonth--;
        }
        else if(monthsWith31Days.includes(months[currentMonth-1])){
            firstDay += 31;
            currentMonth--;
        }
        else if ((currentMonth - 1) < 0){
            currentMonth = 11;
            currentYear--;
            firstDay += 31;
        }
        else if ((currentMonth -1) === 1){
            if(isLeapYear(currentYear)) {
                currentMonth--;
                firstDay +=29;
            }
            else {
                currentMonth--;
                firstDay +=28;
            }
        }
    }
    renderWeek();
}

prevWeekBtn.addEventListener ("click", () => {
    prevWeek();
    renderWeek();
});

nextWeekBtn.addEventListener ("click", () => {
    nextWeek(currentDate, 1);
    renderWeek();
});

function generateTimeline() {
    let hours = "";

    for (let i = 1; i <= 23; i++) {
        hours += `<div class="hour">${i}:00</div>`;
    }
    timelineContainer.innerHTML = hours;
}

generateTimeline();

function generateDaysForWeek() {
    let days = "";

    for (let i = 0; i <= 22; i++) {
        days += `<div class="week-grid-tile"></div>`;
    }
    days += `<div class="week-grid-tile last-tile"></div>`;

    daysForTheWeekContainerMonday.innerHTML = days;
    daysForTheWeekContainerTuesday.innerHTML = days;
    daysForTheWeekContainerWednesday.innerHTML = days;
    daysForTheWeekContainerThursday.innerHTML = days;
    daysForTheWeekContainerFriday.innerHTML = days;
    daysForTheWeekContainerSaturday.innerHTML = days;
    daysForTheWeekContainerSunday.innerHTML = days;

}

generateDaysForWeek();