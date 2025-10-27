
document.addEventListener('DOMContentLoaded', function () {
    const uploadBtn = document.getElementById('submitBtn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', uploadFile);
    }
});
document.getElementById("uploadForm").addEventListener("submit", function(event) {
    event.preventDefault();
    uploadFile();
  });


async function uploadFile() {
    const form = document.getElementById("uploadForm");
    const resultDiv = document.getElementById("result");
    const formData = new FormData(form);
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;

     try {
        const response = await fetch("/upload_form/upload", {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData,
        });

        let data;
        try {
            data = await response.json();
            console.log(data.message);
        } catch (err) {
            data = { status: "error", message: "Некорректный ответ от сервера " + err  };
        }

        if (!response.ok) {
            resultDiv.innerHTML = `<div class="alert alert-danger">${data.message || "Ошибка загрузки файла"}</div>`;
            return;
        }

        if (data.status === "success") {
            resultDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        } else {
            resultDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
        }

    } catch (error) {
        console.error("Upload error:", error);
        resultDiv.innerHTML = `<div class="alert alert-danger">Ошибка соединения с сервером</div>`;
    }
}

