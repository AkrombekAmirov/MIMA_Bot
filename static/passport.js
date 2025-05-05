document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById('passport-form');
  const spinner = document.getElementById('spinner');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const passport = document.getElementById('passport').value.trim().toUpperCase();
    const passportRegex = /^[A-Z]{2}[0-9]{7}$/;

    if (!passportRegex.test(passport)) {
      showAlert("Passport formati xato", "Iltimos, AA1234567 shaklida kiriting!", "error");
      return;
    }

    spinner.classList.remove('hidden');

    try {
      const response = await fetch(`/user/api/check-passport/?passport=${passport}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      const result = await response.json();
      spinner.classList.add('hidden');

      if (response.ok && Array.isArray(result) && result.length > 0 && result[0].id) {
        const user = result[0];
        console.log("✅ Foydalanuvchi topildi:", user);

        showAlert("Muvaffaqiyatli!", `Xush kelibsiz, ${user.name}!`, "success");
        setTimeout(() => {
          window.location.href = `/start-test/${user.id}`;
        }, 1500);
      } else {
        showAlert("Xatolik", result.detail || "Foydalanuvchi topilmadi yoki ID aniqlanmadi", "error");
        console.warn("⚠️ No valid user:", result);
      }
    } catch (error) {
      spinner.classList.add('hidden');
      console.error("❌ Server xatoligi:", error);
      showAlert("Server Xatolik", "Aloqa uzildi", "error");
    }
  });

  function showAlert(title, text, icon) {
    Swal.fire({
      title: title,
      text: text,
      icon: icon,
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'OK'
    });
  }
});
