let currentHeartRate, currentHeartRateCategory, currentHeartRateAdvice;

function calculateHeartRate(event) {
  event.preventDefault();
  const heartRate = parseFloat(
    document.querySelector('[name="heartRate"]').value
  );

  if (!isNaN(heartRate)) {
    displayHeartRateResult(heartRate.toFixed(2));
  } else {
    displayHeartRateResult(
      null,
      `<h1 class="error-message">Invalid input. Please enter a valid number for heart rate.</h1>`
    );
  }
}

function displayHeartRateResult(heartRate, error = null) {
  let message;
  if (error) {
    message = error;
  } else {
    let category, advice;
    if (heartRate < 60) {
      category = "Low";
      advice =
        "A heart rate below 60 bpm is considered low. It's important to consult a healthcare provider to understand the cause.";
    } else if (heartRate <= 100) {
      category = "Normal";
      advice =
        "A heart rate between 60 and 100 bpm is considered normal. Continue maintaining a healthy lifestyle to keep your heart rate in this range.";
    } else {
      category = "High";
      advice =
        "A heart rate above 100 bpm is considered high. It's important to consult a healthcare provider to understand the cause and manage your heart health.";
    }

    // Store current data for saving
    currentHeartRate = heartRate;
    currentHeartRateCategory = category;
    currentHeartRateAdvice = advice;

    message = `
      <p class="heart-rate-result-detail" style="font-weight:bold;">Your Heart Rate: ${heartRate} bpm</p>
      <p class="heart-rate-category">Heart Rate Category: ${category}</p>
      <p class="${category.toLowerCase()}-rate-message">${advice}</p>
    `;
  }

  document.getElementById("heart-rate-result").innerHTML = message;
  document.getElementById("modal").style.display = "flex";
}

function saveHeartRateResult() {
  // Implement the save functionality here
  console.log(`Saving Heart Rate result:
    Heart Rate: ${currentHeartRate} bpm,
    Category: ${currentHeartRateCategory},
    Advice: ${currentHeartRateAdvice}`);
  alert("Your heart rate data has been saved!");
  closeModal();
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("modal").style.display = "none";
});
