// Start with an initial value of 20 seconds
// TODO find how to set the timer
let TIME_LIMIT = 20;

const COLOR_CODES = {
  info: {
    color: "green"
  }
};

let remainingPathColor = COLOR_CODES.info.color;

// Initially, no time has passed, but this will count up
// and subtract from the TIME_LIMIT
let timePassed = 0;
let timeLeft = TIME_LIMIT;

let timerInterval = null;

//html for the timer
function setHtmlCircle() {
  document.getElementById("TimerPosition").innerHTML = `
<div class="base-timer">
  <svg class="base-timer__svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g class="base-timer__circle">
      <circle class="base-timer__path-elapsed" cx="50" cy="50" r="45"></circle>
      <path
        id="base-timer-path-remaining"
        stroke-dasharray="283"
        class="base-timer__path-remaining ${remainingPathColor}"
        d="
          M 50, 50
          m -45, 0
          a 45,45 0 1,0 90,0
          a 45,45 0 1,0 -90,0
        "
      ></path>
    </g>
  </svg>
  <span id="base-timer-label" class="base-timer__label">
    ${formatTimeLeft(timeLeft)}
  </span>
</div>
`;
}

// Divides time left by the defined time limit.
function calculateTimeFraction() {
   const rawTimeFraction = timeLeft / TIME_LIMIT;

   //it could be return just rawTimeFraction but this remove the lag of the one
    // second at the end of the animation
  return rawTimeFraction - (1 / TIME_LIMIT) * (1 - rawTimeFraction);
}

// Update the dasharray value as time passes, starting with 283
function setCircleDasharray() {
  const circleDasharray = `${(
    calculateTimeFraction() * 283
  ).toFixed(0)} 283`;
  document
    .getElementById("base-timer-path-remaining")
    .setAttribute("stroke-dasharray", circleDasharray);
}


//update the timer label
function formatTimeLeft(time) {
  // The largest round integer less than or equal to the result of time divided being by 60.
  const minutes = Math.floor(time / 60);

  // Seconds are the remainder of the time divided by 60 (modulus operator)
  let seconds = time % 60;

  // If the value of seconds is less than 10, then display seconds with a leading zero
  if (seconds < 10) {
    seconds = `0${seconds}`;
  }

  // The output in MM:SS format
  return `${minutes}:${seconds}`;
}

//when call start the timer
//TODO when time finish send a signal to server
//TODO for now it will just restart
function startTimer(timerInitialValue) {

  console.log("start time enter")
  TIME_LIMIT = timerInitialValue;

  timerInterval = setInterval(() => {

    // The amount of time passed increments by one
    timePassed = timePassed += 1;
    timeLeft = TIME_LIMIT - timePassed;

    // The time left label is updated
    document.getElementById("base-timer-label").innerHTML = formatTimeLeft(timeLeft);

    setCircleDasharray();
  }, 1000);
}


