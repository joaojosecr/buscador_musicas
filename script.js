const API_URL = "http://127.0.0.1:5000/process";

document
  .getElementById("searchForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const query = document.getElementById("searchInput").value.trim();
    if (!query) return;

    const resultsList = document.getElementById("resultsList");
    resultsList.innerHTML = "<li>Buscando...</li>";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: query }),
      });

      if (!response.ok) throw new Error("Erro na busca");

      const data = await response.json();

      resultsList.innerHTML = "";
      if (data.resultados.length === 0) {
        resultsList.innerHTML = "<li>Nenhum resultado encontrado.</li>";
      } else {
        data.resultados.forEach((result) => {
          const li = document.createElement("li");
          li.textContent = result;
          resultsList.appendChild(li);
        });
      }
    } catch (error) {
      resultsList.innerHTML =
        "<li>Erro ao buscar os resultados. Tente novamente.</li>";
      console.error(error);
    }
  });
