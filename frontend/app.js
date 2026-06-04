const API_BASE = "";
const SAMPLE_STATIONS = ["서울역", "강남역"];

const state = {
  stations: [...SAMPLE_STATIONS],
  query: "조용한 카페",
  topK: 3,
  lastRequest: null,
};

const form = document.querySelector("#recommend-form");
const locationsEl = document.querySelector("#locations");
const queryInput = document.querySelector("#query");
const topKInput = document.querySelector("#top-k");
const addLocationButton = document.querySelector("#add-location");
const sampleButton = document.querySelector("#sample-button");
const submitButton = document.querySelector("#submit-button");
const clearButton = document.querySelector("#clear-button");
const resultTitle = document.querySelector("#result-title");
const resultContent = document.querySelector("#result-content");
const statusStrip = document.querySelector("#status-strip");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function stationLabel(station) {
  if (!station) return "알 수 없음";
  return `${station.name} · ${station.line}`;
}

function formatScore(score) {
  return `${Math.round(score * 100)}%`;
}

function setStatus(text) {
  statusStrip.textContent = text;
}

function setLoading(isLoading) {
  form.classList.toggle("loading", isLoading);
  submitButton.disabled = isLoading;
  submitButton.innerHTML = isLoading
    ? "요청 중"
    : `<svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="m16 16 4 4" />
      </svg>
      추천 받기`;
}

function renderLocations() {
  locationsEl.innerHTML = "";
  state.stations.forEach((station, index) => {
    const row = document.createElement("div");
    row.className = "location-row";
    row.innerHTML = `
      <div class="field-row">
        <label for="station-${index}">역 이름</label>
        <input id="station-${index}" data-index="${index}" type="text"
          value="${escapeHtml(station)}" placeholder="예: 강남역" required />
      </div>
      <button class="icon-button" type="button" data-remove="${index}"
        aria-label="출발 위치 삭제" title="출발 위치 삭제">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 12h14" />
        </svg>
      </button>
    `;
    locationsEl.appendChild(row);
  });
}

function readForm() {
  const stations = [...locationsEl.querySelectorAll("input[data-index]")]
    .map((input) => input.value.trim())
    .filter(Boolean);

  state.stations = stations;
  state.query = queryInput.value.trim();
  state.topK = Number(topKInput.value);

  return {
    stations,
    query: state.query,
    top_k: state.topK,
  };
}

async function postRecommend(payload) {
  const response = await fetch(`${API_BASE}/api/v1/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "추천 요청에 실패했습니다.");
  }
  return data;
}

function renderEmpty() {
  resultTitle.textContent = "아직 결과가 없습니다";
  resultContent.className = "result-content empty-state";
  resultContent.innerHTML = "<p>출발 역과 장소를 입력하면 추천 결과가 표시됩니다.</p>";
  setStatus("요청 대기 중");
}

function renderError(error) {
  resultTitle.textContent = "요청 실패";
  resultContent.className = "result-content";
  resultContent.innerHTML = `<div class="error-box">${escapeHtml(error.message)}</div>`;
  setStatus("오류가 발생했습니다");
}

function renderRecommendations(decision) {
  resultTitle.textContent = `${decision.station.name} 추천`;
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    <div class="summary-band">
      <strong>${escapeHtml(stationLabel(decision.station))}</strong>
      <p>중간역 ${escapeHtml(stationLabel(decision.meeting_station))} 기준</p>
    </div>
    ${decision.recommendations.map(renderPlace).join("")}
  `;
  setStatus(`${decision.station.name} 주변 ${decision.recommendations.length}개 추천`);
}

function renderSelection(decision) {
  resultTitle.textContent = "주변 역을 선택하세요";
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    <div class="summary-band">
      <strong>${escapeHtml(stationLabel(decision.meeting_station))}</strong>
      <p>현재 DB 추천이 없어 가까운 역 후보를 준비했습니다.</p>
      <a class="map-link" href="${escapeHtml(decision.map_search.url)}"
        target="_blank" rel="noreferrer">
        ${escapeHtml(decision.map_search.label)}
      </a>
    </div>
    ${decision.options.map(renderOption).join("")}
  `;
  setStatus(`${decision.meeting_station.name} 대신 선택 가능한 역 ${decision.options.length}개`);
}

function renderOption(option) {
  const previewItems = option.recommendations
    .slice(0, 3)
    .map(
      (recommendation) => `
        <li>
          <span>${escapeHtml(recommendation.place.name)}</span>
          <span>${formatScore(recommendation.similarity_score)}</span>
        </li>
      `,
    )
    .join("");

  return `
    <article class="option-card">
      <div>
        <h3>${escapeHtml(option.station.name)}</h3>
        <div class="station-meta">
          <span>${escapeHtml(option.station.line)}</span>
          <span class="pill">${option.recommendations.length}개 미리보기</span>
        </div>
      </div>
      <ul class="preview-list">${previewItems}</ul>
      <button class="choice-button" type="button"
        data-station-id="${escapeHtml(option.station.id)}">
        이 역으로 보기
      </button>
    </article>
  `;
}

function renderPlace(recommendation) {
  const place = recommendation.place;
  const tags = place.tags
    .slice(0, 4)
    .map((tag) => `<span class="pill">${escapeHtml(tag)}</span>`)
    .join("");

  return `
    <article class="place-card">
      <div>
        <h3>${escapeHtml(place.name)}</h3>
        <div class="place-meta">
          <span>${escapeHtml(place.category)}</span>
          <span>${place.distance_from_station_m}m</span>
          <span>${formatScore(recommendation.similarity_score)}</span>
        </div>
      </div>
      <p>${escapeHtml(place.address)}</p>
      <div class="place-meta">${tags}</div>
    </article>
  `;
}

async function submitRecommendation(selectedStationId = null) {
  const payload = selectedStationId
    ? { ...state.lastRequest, selected_station_id: selectedStationId }
    : readForm();

  if (!payload.query) {
    renderError(new Error("찾는 장소를 입력하세요."));
    return;
  }
  if (!payload.stations || payload.stations.length < 2) {
    renderError(new Error("출발 역은 최소 2개가 필요합니다."));
    return;
  }

  try {
    setLoading(true);
    setStatus("추천 계산 중");
    const data = await postRecommend(payload);
    if (!selectedStationId) {
      state.lastRequest = payload;
    }

    if (data.status === "station_selection_required") {
      renderSelection(data);
      return;
    }
    renderRecommendations(data);
  } catch (error) {
    renderError(error);
  } finally {
    setLoading(false);
  }
}

locationsEl.addEventListener("input", (event) => {
  const input = event.target;
  if (!(input instanceof HTMLInputElement)) return;
  const index = Number(input.dataset.index);
  if (!Number.isNaN(index)) {
    state.stations[index] = input.value;
  }
});

locationsEl.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest("[data-remove]");
  if (!button) return;
  const index = Number(button.dataset.remove);
  if (state.stations.length <= 2) return;
  state.stations.splice(index, 1);
  renderLocations();
});

resultContent.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest("[data-station-id]");
  if (!button) return;
  submitRecommendation(button.dataset.stationId);
});

addLocationButton.addEventListener("click", () => {
  if (state.stations.length >= 10) return;
  state.stations.push("");
  renderLocations();
});

sampleButton.addEventListener("click", () => {
  state.stations = [...SAMPLE_STATIONS];
  queryInput.value = "조용한 카페";
  topKInput.value = "3";
  renderLocations();
  renderEmpty();
});

clearButton.addEventListener("click", renderEmpty);

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitRecommendation();
});

renderLocations();
renderEmpty();
