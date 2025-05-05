document.addEventListener("DOMContentLoaded", async () => {
  const summaryBox = document.getElementById("summary-results");
  const totalScoreText = document.getElementById("total-score");

  try {
    const res = await fetch(`/user/api/final-summary?user_id=${USER_ID}`);
    const data = await res.json();

    if (!res.ok) {
      Swal.fire("Xatolik", data.detail || "Ma'lumotlar olinmadi", "error");
      return;
    }

    const { blocks, total_score } = data;
    totalScoreText.textContent = `${total_score} / 100`;

    blocks.forEach(block => {
      const percentage = Math.round((block.score / block.max_score) * 100);

      // Rangga asoslangan badge
      let rating = "";
      if (percentage >= 80) rating = "🌟 Ajoyib";
      else if (percentage >= 50) rating = "⚠️ O‘rtacha";
      else rating = "❌ Yomon";

      const card = document.createElement("div");
      card.className = "bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition relative";

      card.innerHTML = `
        <div class="absolute top-2 right-2 text-xs bg-indigo-100 text-indigo-600 px-2 py-1 rounded-full">${rating}</div>

        <h3 class="text-lg font-bold text-indigo-800 mb-2">🧩 ${block.block_number}-blok: ${block.subject_name}</h3>
        <ul class="text-sm mb-3 text-gray-700 space-y-1">
          <li><strong>To'g'ri javoblar:</strong> ${block.correct_answers} ta</li>
          <li><strong>Xato javoblar:</strong> ${block.wrong_answers} ta</li>
          <li><strong>Jami savollar:</strong> ${block.total_questions} ta</li>
        </ul>

        <div class="flex items-center justify-center mb-2">
          <div class="relative w-20 h-20">
            <svg class="w-full h-full">
              <circle class="text-gray-200" stroke-width="6" stroke="currentColor" fill="transparent" r="30" cx="40" cy="40"/>
              <circle class="text-green-500" stroke-width="6" stroke-dasharray="188.5"
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
    Swal.fire("Server bilan xatolik", "Iltimos keyinroq urinib ko‘ring", "error");
  }
});
