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

            document.getElementById("faculty-info").innerHTML = `
              <span class="block text-lg text-gray-700 font-semibold leading-snug">
                🎓 Siz tanlagan yo‘nalish:
                <span class="text-indigo-700 font-bold tracking-wide">${data.faculty}</span>
              </span>
              <span class="block mt-2 text-base text-gray-600 leading-relaxed">
                Quyidagi <strong class="text-green-600">fanlardan test topshirasiz</strong>.
                Har bir blok sizning bilim, tahlil va xulosa chiqarish qobiliyatingizni sinovdan o‘tkazadi.
              </span>`;

            const list = document.getElementById("subject-list");
            list.innerHTML = "";

            data.subjects.forEach((sub) => {
                let testCount = 10;
                let time = "30 daqiqa";

                if (sub.block_number === 1) {
                    testCount = 20;
                    time = "1 soat";
                } else if (sub.block_number === 2) {
                    testCount = 15;
                    time = "45 daqiqa";
                }

                const li = document.createElement("li");
                li.innerHTML = `
                    <strong class="text-indigo-700">${sub.block_number}-blok:</strong>
                    <span class="font-medium">${sub.subject_name}</span> —
                    <span class="text-green-600 font-semibold">${testCount} ta test</span>,
                    vaqt: <span class="text-blue-600">${time}</span>
                `;
                list.appendChild(li);
            });

            // ✅ Imtihonni boshlash tugmasi ishlaydi
            const startBtn = document.getElementById("start-test-btn");
            if (startBtn) {
                startBtn.addEventListener("click", () => {
                    window.location.href = `/start-real-test/${userId}`;
                });
            } else {
                console.warn("❗ 'start-test-btn' tugmasi DOMda topilmadi.");
            }

        } else {
            Swal.fire("Xatolik", data.detail || "Ma'lumotlarni yuklab bo'lmadi", "error");
        }
    } catch (error) {
        spinner.classList.add("hidden");
        console.error(error);
        Swal.fire("Server Xatolik", "Server bilan aloqa uzildi!", "error");
    }
});
