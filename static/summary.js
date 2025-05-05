// summary.js
document.addEventListener("DOMContentLoaded", async () => {
  const summaryBox = document.getElementById("summary-results");

  try {
    const response = await fetch(`/user/api/final-result?user_id=${USER_ID}`);
    const data = await response.json();

    if (!response.ok) {
      Swal.fire("Xatolik", data.detail || "Natijalarni olishda xatolik", "error");
      return;
    }

    const totalPoints = data.total_score;
    const blockSummaries = data.blocks;

    blockSummaries.forEach((block, idx) => {
      const blockDiv = document.createElement("div");
      blockDiv.className = "bg-gray-50 border border-gray-200 p-4 rounded";

      blockDiv.innerHTML = `
        <h2 class="text-xl font-semibold mb-2">🧩 ${block.block_number}-blok: ${block.subject_name}</h2>
        <p><strong>Savollar soni:</strong> ${block.total_questions} ta</p>
        <p><strong>To'g'ri javoblar:</strong> ${block.correct_answers} ta</p>
        <p><strong>Ushbu blokdan olgan ball:</strong> <span class="text-blue-600 font-bold">${block.score}</span> / ${block.max_score}</p>
      `;

      summaryBox.appendChild(blockDiv);
    });

    const finalDiv = document.createElement("div");
    finalDiv.className = "text-center mt-6 text-xl font-bold text-green-700";
    finalDiv.textContent = `Umumiy ball: ${totalPoints} / 100`;

    summaryBox.appendChild(finalDiv);

  } catch (err) {
    console.error(err);
    Swal.fire("Xatolik", "Server bilan aloqa uzildi", "error");
  }
});
