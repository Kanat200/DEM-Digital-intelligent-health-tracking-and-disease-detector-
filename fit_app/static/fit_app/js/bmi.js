let currentHeight, currentWeight, currentBMI, currentCategory, currentAdvice;

function calculateBMI(event) {
  event.preventDefault();
  const height = parseFloat(document.querySelector('[name="height"]').value);
  const weight = parseFloat(document.querySelector('[name="weight"]').value);

  if (!isNaN(height) && !isNaN(weight)) {
    const heightInMeters = height / 100;
    const bmi = weight / (heightInMeters * heightInMeters);
    displayResult(height, weight, bmi.toFixed(2));
  } else {
    displayResult(
      null,
      null,
      null,
      `<h1 class="error-message">Invalid input. Please enter valid numbers for height and weight.</h1>`
    );
  }
}

function displayResult(height, weight, bmi, error = null) {
  let message;
  if (error) {
    message = error;
  } else {
    let category, advice;
    if (bmi < 18.5) {
      category = "Short";
      advice =
        "It's important to maintain a healthy diet to reach a normal weight. Consider consulting a healthcare provider for personalized advice.";
    } else if (bmi < 24.9) {
      category = "Healthy";
      advice =
        "Continue maintaining a balanced diet and regular physical activity to stay healthy.";
    } else if (bmi < 29.9) {
      category = "Excess";
      advice =
        "Consider adopting healthier eating habits and increasing your physical activity to achieve a healthier weight.";
    } else {
      category = "Obese";
      advice =
        "It's crucial to seek advice from a healthcare provider to create a plan for achieving a healthier weight. Focus on a balanced diet and regular physical activity.";
    }

    currentHeight = height;
    currentWeight = weight;
    currentBMI = bmi;
    currentCategory = category;
    currentAdvice = advice;

    message = `
      <p class="bmi-result-detail">Height: ${height} cm</p>
      <p class="bmi-result-detail">Weight: ${weight} kg</p>
      <p class="bmi-result">Your BMI is: ${bmi}</p>
      <p class="bmi-category">Weight Category: ${category}</p>
      <p class="${category
        .toLowerCase()
        .replace(" ", "-")}-message">${advice}</p>
    `;
  }

  document.getElementById("bmi-result").innerHTML = message;
  document.getElementById("modal").style.display = "flex";
}

function saveBMIResult() {
  console.log(`Saving BMI result:
    Height: ${currentHeight} cm,
    Weight: ${currentWeight} kg,
    BMI: ${currentBMI},
    Category: ${currentCategory},
    Advice: ${currentAdvice}`);
  alert("Your BMI data has been saved!");
  closeModal();
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("modal").style.display = "none";
});
