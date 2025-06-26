document.addEventListener("DOMContentLoaded", async () => {
    const summaryBox = document.getElementById("summary-results");
    const totalScoreText = document.getElementById("total-score");
    const userNameBox = document.getElementById("user-name");

    const colorMap = {
        green: {
            border: "border-green-400",
            text: "text-green-600",
            bg: "bg-green-100",
            circle: "text-green-500"
        },
        yellow: {
            border: "border-yellow-400",
            text: "text-yellow-600",
            bg: "bg-yellow-100",
            circle: "text-yellow-500"
        },
        red: {
            border: "border-red-400",
            text: "text-red-600",
            bg: "bg-red-100",
            circle: "text-red-500"
        }
    };

    try {
        const res = await fetch(`/user/api/final-summary?user_id=${USER_ID}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Ma'lumotlar olinmadi");

        const { blocks, total_score, full_name } = data;

        // Super dizayndagi ism-familiya
        userNameBox.textContent = full_name;
        totalScoreText.textContent = `${total_score} / 100`;

        blocks.forEach(block => {
            const percentage = Math.round((block.score / block.max_score) * 100);
            const rating = percentage >= 80 ? "🌟 Ajoyib"
                        : percentage >= 50 ? "⚠️ O‘rtacha"
                        : "❌ Yomon";
            const colorKey = percentage >= 80 ? "green"
                            : percentage >= 50 ? "yellow"
                            : "red";
            const colorClass = colorMap[colorKey];

            const card = document.createElement("div");
            card.className = `bg-white rounded-xl p-6 shadow-md hover:shadow-2xl transition duration-300 border-l-4 ${colorClass.border} relative`;

            card.innerHTML = `
              <div class="absolute top-2 right-2 text-xs ${colorClass.bg} ${colorClass.text} px-2 py-1 rounded-full">${rating}</div>
              <h3 class="text-lg font-bold text-indigo-800 mb-2">🧩 ${block.block_number}-blok: ${block.subject_name}</h3>
              <ul class="text-sm mb-3 text-gray-700 space-y-1">
                <li><strong>✅ To'g'ri:</strong> ${block.correct_answers} ta</li>
                <li><strong>❌ Xato:</strong> ${block.wrong_answers} ta</li>
                <li><strong>📚 Jami:</strong> ${block.total_questions} ta</li>
                <li><strong>⏱️ Vaqt:</strong> ${block.time_spent} daqiqa</li>
              </ul>
              <div class="flex items-center justify-center mb-2">
                <div class="relative w-20 h-20">
                  <svg class="w-full h-full">
                    <circle class="text-gray-200" stroke-width="6" stroke="currentColor" fill="transparent" r="30" cx="40" cy="40"/>
                    <circle class="${colorClass.circle}" stroke-width="6" stroke-dasharray="188.5"
                      stroke-dashoffset="${188.5 - (188.5 * percentage) / 100}"
                      stroke-linecap="round" stroke="currentColor" fill="transparent" r="30" cx="40" cy="40"/>
                  </svg>
                  <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center">
                    <span class="text-md font-bold text-indigo-700">${percentage}%</span>
                  </div>
                </div>
              </div>
              <p class="text-sm text-center text-gray-600 mt-1">Ball: <span class="font-bold">${block.score}</span> / ${block.max_score}</p>
            `;

            summaryBox.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        Swal.fire("Xatolik", err.message, "error");
    }
});
