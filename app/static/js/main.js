// Submit image uploads without navigating away from the portfolio interface.
const form = document.querySelector("#prediction-form");
const result = document.querySelector("#result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const task = document.querySelector("#task").value;
  const image = document.querySelector("#image").files[0];

  result.textContent = "Running inference...";
  const body = new FormData();
  body.append("file", image);

  try {
    const response = await fetch(`/api/v1/${task}/predict`, {
      method: "POST",
      body,
    });
    const payload = await response.json();
    result.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    result.textContent = JSON.stringify({ error: error.message }, null, 2);
  }
});
