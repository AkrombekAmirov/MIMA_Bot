document.addEventListener("DOMContentLoaded", async () => {
  const summaryDiv = document.getElementById("test-summary");
  const userId = USER_ID;

  try {
    const res = await fetch("/api/finish-block", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        subject_id: SUBJECT_ID,
      }),
    });

    const result = await res.json();

    if (res.ok) {
      const passed = result.status;
      summaryDiv.innerHTML = `
        <h2 class="text-2xl font-bold mb-4">${result.message}</h2>
        <p><strong>Jami savollar:</strong> ${result.total_questions}</p>
        <p><strong>To'g'ri javoblar:</strong> ${result.correct_answers}</p>
        <p><strong>Natija:</strong> ${result.accuracy}%</p>
        <p class="mt-4 text-lg ${passed ? 'text-green-600' : 'text-red-500'}">
          ${passed ? "Tabriklaymiz! Siz ushbu blokni muvaffaqiyatli yakunladingiz." : "Afsuski, bu blokda o‘tish uchun yetarli natija to‘plangani yo‘q."}
        </p>
      `;

      // Auto redirect for next block
      setTimeout(() => {
        window.location.href = `/start-real-test/${userId}`;
      }, 5000); // 5s delay

    } else {
      Swal.fire("Xatolik", result.detail || "Natijani olishda xatolik", "error");
    }
  } catch (err) {
    console.error(err);
    Swal.fire("Server xatolik", "Aloqa uzildi", "error");
  }
});