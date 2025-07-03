// answer_test.js
const USER_ID = parseInt(document.getElementById('user-id').value, 10);
const container = document.getElementById("questions-container");
const navButtons = document.getElementById("nav-buttons");
const finishBtn = document.getElementById("finish-test-btn");
const progressBar = document.getElementById("progress-bar");
const timeRemaining = document.getElementById("time-remaining");

let subjectId, blockNumber, countdownInterval, totalSeconds, isMathSubject;

document.addEventListener("DOMContentLoaded", fetchQuestions);

async function fetchQuestions() {
  clearInterval(countdownInterval);
  container.innerHTML = "";
  navButtons.innerHTML = "";

  try {
    const res = await fetch(`/user/api/start-real-test/${USER_ID}`);
    if (!res.ok) {
      const err = await res.json();
      await Swal.fire("Yakun", err.detail || "Test topilmadi.", "info");
      return window.location.href = "/";
    }

    const data = await res.json();
    ({ block_number: blockNumber, subject_id: subjectId } = data);
    isMathSubject = data.subject_name.trim().toLowerCase().includes("matematika");

    const title = document.createElement("h2");
    title.className = "text-2xl font-bold mb-6 text-center text-indigo-700";
    title.textContent = `${blockNumber}-blok: ${data.subject_name}`;
    container.appendChild(title);

    const seen = new Set();
    const uniqueQs = data.questions.filter(q => {
      if (seen.has(q.id)) return false;
      seen.add(q.id);
      return true;
    });

    uniqueQs.forEach((q, idx) => {
      const qDiv = document.createElement("div");
      qDiv.id = `question-${q.id}`;
      qDiv.className = "space-y-4 border-b pb-6";

      const qText = document.createElement("h3");
      qText.className = "text-lg font-semibold";
      qText.textContent = `${idx + 1}. ${q.text}`;
      qDiv.appendChild(qText);

      if (isMathSubject && q.formula) {
        const fDiv = document.createElement("div");
        fDiv.className = "prose";
        fDiv.innerHTML = `\\[${q.formula}\\]`;
        qDiv.appendChild(fDiv);
      }

      q.options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "option-btn w-full text-left border px-4 py-2 rounded hover:bg-blue-100";
        btn.textContent = isMathSubject ? "" : opt;
        if (isMathSubject) btn.innerHTML = `\\(${opt}\\)`;

        // ❗ Tanlangan variantni oldindan faollashtiramiz
        if (opt === q.selected_option) {
          btn.classList.add("bg-blue-100", "font-semibold");
          setTimeout(() => {
            document.getElementById(`nav-btn-${q.id}`)?.classList.add("active-btn");
          }, 50);
        }

        btn.onclick = async () => {
          qDiv.querySelectorAll(".option-btn").forEach(b => b.classList.remove("bg-blue-100", "font-semibold"));
          btn.classList.add("bg-blue-100", "font-semibold");

          const resp = await fetch("/user/api/submit-answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: USER_ID,
              question_id: q.id,
              selected_option: opt
            })
          });

          const result = await resp.json();
          if (resp.ok) {
            document.getElementById(`nav-btn-${q.id}`)?.classList.add("active-btn");
          } else {
            Swal.fire("Xatolik", result.detail || "Javob yuborilmadi", "error");
          }
        };

        qDiv.appendChild(btn);
      });

      container.appendChild(qDiv);

      const navBtn = document.createElement("button");
      navBtn.id = `nav-btn-${q.id}`;
      navBtn.className = "border w-10 h-10 rounded hover:bg-gray-200";
      navBtn.textContent = idx + 1;
      navBtn.onclick = () => {
        document.getElementById(`question-${q.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
      };
      navButtons.appendChild(navBtn);
    });

    if (isMathSubject && window.MathJax?.typesetPromise) {
      await MathJax.typesetPromise();
    }

    initTimer(data.start_time);
  } catch (error) {
    console.error("❌ Fetch Questions Error:", error);
    Swal.fire("Xatolik", "Tizimda kutilmagan xatolik", "error");
  }
}

function initTimer(startIso) {
  const initial = blockNumber === 1 ? 3600 : 1800;
  const elapsed = Math.floor((Date.now() - new Date(startIso)) / 1000);
  totalSeconds = initial - elapsed;

  if (totalSeconds <= 0) {
    return Swal.fire("⏳ Taymer tugadi!", "Blok yakunlanmoqda...", "info").then(() => finishBtn.click());
  }

  updateProgress(initial);
  countdownInterval = setInterval(() => {
    totalSeconds--;
    updateProgress(initial);
    if (totalSeconds <= 0) {
      clearInterval(countdownInterval);
      Swal.fire("⏳ Taymer tugadi!", "Blok yakunlanmoqda...", "info").then(() => finishBtn.click());
    }
  }, 1000);
}

function updateProgress(initial) {
  const m = Math.floor(totalSeconds / 60), s = totalSeconds % 60;
  timeRemaining.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  const pct = ((initial - totalSeconds) / initial) * 100;
  progressBar.style.width = `${100 - pct}%`;
}

finishBtn.addEventListener("click", async () => {
  if (!subjectId) return Swal.fire("Xatolik", "Fan aniqlanmadi", "error");
  const resp = await fetch('/user/api/finish-block', {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify({ user_id: USER_ID, subject_id: subjectId })
  });

  const data = await resp.json();
  if (resp.ok) {
    if (blockNumber === 3) {
      window.location.href = `/final-summary?user_id=${USER_ID}`;
    } else {
      fetchQuestions();
    }
  } else {
    Swal.fire("Xatolik", data.detail || "Blokni yakunlashda muammo", "error");
  }
});
