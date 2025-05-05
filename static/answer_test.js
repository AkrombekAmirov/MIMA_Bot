const USER_ID = parseInt(document.getElementById('user-id').value);

const container = document.getElementById("questions-container");
const navButtons = document.getElementById("nav-buttons");
const finishBtn = document.getElementById("finish-test-btn");

let subjectId = null;
let blockNumber = null;
let selectedAnswers = {};

async function fetchQuestions() {
  try {
    container.innerHTML = "";
    navButtons.innerHTML = "";

    const res = await fetch(`/user/api/start-real-test/${USER_ID}`);
    if (!res.ok) {
      Swal.fire("Yakun", "Barcha testlar yakunlangan yoki test topilmadi.", "info")
        .then(() => window.location.href = "/");
      return;
    }

    const data = await res.json();
    const { block_number, subject_name, subject_id, questions } = data;
    subjectId = subject_id;
    blockNumber = block_number;

    const title = document.createElement("h2");
    title.className = "text-2xl font-bold mb-6 text-center text-indigo-700";
    title.textContent = `${block_number}-blok: ${subject_name}`;
    container.prepend(title);

    questions.forEach((q, index) => {
      const qDiv = document.createElement("div");
      qDiv.classList.add("space-y-4", "border-b", "pb-6");
      qDiv.id = `question-${q.id}`;

      const qText = document.createElement("h3");
      qText.classList.add("text-lg", "font-semibold");
      qText.textContent = `${index + 1}. ${q.text}`;
      qDiv.appendChild(qText);

      q.options.forEach((opt) => {
        const btn = document.createElement("button");
        btn.textContent = opt;
        btn.className = "option-btn w-full text-left border border-gray-300 px-4 py-2 rounded hover:bg-blue-100";
        btn.onclick = async () => {
          qDiv.querySelectorAll(".option-btn").forEach(b => {
            b.classList.remove("bg-blue-100", "font-semibold");
          });
          btn.classList.add("bg-blue-100", "font-semibold");

          selectedAnswers[q.id] = opt;

          const response = await fetch('/user/api/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: USER_ID,
              question_id: q.id,
              selected_option: opt
            })
          });

          const result = await response.json();
          if (response.ok) {
            document.getElementById(`nav-btn-${q.id}`).classList.add('active-btn');
          } else {
            Swal.fire("Xatolik", result.detail || "Javob yuborishda muammo", "error");
          }
        };
        qDiv.appendChild(btn);
      });

      container.appendChild(qDiv);

      const navBtn = document.createElement("button");
      navBtn.textContent = index + 1;
      navBtn.id = `nav-btn-${q.id}`;
      navBtn.className = "border border-gray-300 w-10 h-10 rounded hover:bg-gray-200";
      navBtn.onclick = () => {
        document.getElementById(`question-${q.id}`).scrollIntoView({ behavior: 'smooth', block: 'center' });
      };
      navButtons.appendChild(navBtn);
    });
  } catch (err) {
    console.error("Xatolik:", err);
    Swal.fire("Xatolik", "Savollarni yuklashda muammo yuz berdi", "error");
  }
}

finishBtn.addEventListener("click", async () => {
  if (!subjectId) {
    Swal.fire("Xatolik", "Fan identifikatori topilmadi", "error");
    return;
  }

  const res = await fetch(`/user/api/finish-block`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: USER_ID, subject_id: subjectId })
  });

  const data = await res.json();

  if (res.ok) {
    if (blockNumber === 3) {
      const summaryUrl = `/user/api/final-summary?user_id=${USER_ID}&summary=${data.total_questions}|${data.correct_answers}|${data.accuracy}|${data.status}`;
      window.location.href = summaryUrl;
    } else {
      await fetchQuestions(); // keyingi blokka o'tish
    }
  } else {
    Swal.fire("Xatolik", data.detail || "Yakunlashda xatolik", "error");
  }
});

// Boshlanishda birinchi blokni chaqirish
fetchQuestions();
