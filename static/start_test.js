// ✅ start_test.js (Frontend JS) yangilangan versiyasi

document.addEventListener("DOMContentLoaded", async () => {
  const spinner = document.getElementById("spinner");
  spinner.classList.remove("hidden");

  const userId = USER_ID;

  try {
    const response = await fetch(`/user/api/start-test/${userId}`);
    const data = await response.json();
    spinner.classList.add("hidden");

    if (response.ok) {
      const fullName = data.welcome_message.split(", ")[1];
      document.getElementById("user-name").textContent = fullName;

      document.getElementById("faculty-info").textContent =
        `Siz ${data.faculty} yo'nalishini tanlagansiz. Quyidagi fanlardan test topshirasiz:`;

      const list = document.getElementById("subject-list");
      list.innerHTML = "";

      data.subjects.forEach((sub, idx) => {
        const testCount = idx === 0 ? 30 : 10;
        const time = idx === 0 ? "1 soat" : "30 daqiqa";
        const li = document.createElement("li");

        li.innerHTML = `
          <strong class="text-indigo-700">${sub.block_number}-blok:</strong>
          <span class="font-medium">${sub.subject_name}</span> —
          <span class="text-green-600 font-semibold">${testCount} ta test</span>,
          vaqt: <span class="text-blue-600">${time}</span>
        `;
        list.appendChild(li);
      });

      document.getElementById("start-test-btn").addEventListener("click", () => {
        window.location.href = `/start-real-test/${userId}`;
      });

    } else {
      Swal.fire("Xatolik", data.detail || "Ma'lumotlarni yuklab bo'lmadi", "error");
    }
  } catch (error) {
    spinner.classList.add("hidden");
    console.error(error);
    Swal.fire("Server Xatolik", "Server bilan aloqa uzildi!", "error");
  }
});
