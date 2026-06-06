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
const mapContainer = document.querySelector("#kakao-map");
const mapFallback = document.querySelector("#map-fallback");
const mapOpenLink = document.querySelector("#map-open-link");
const mapTitle = document.querySelector("#map-title");

let kakaoMap = null;
let activeMarker = null;
let routeMarkers = [];
let routeOverlays = [];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function stationLabel(station) {
  if (!station) return "역 정보 없음";
  return `${station.name} · ${station.line}`;
}

function formatScore(score) {
  return `${Math.round(score * 100)}%`;
}

function kakaoSearchUrl(query) {
  return `https://map.kakao.com/link/search/${encodeURIComponent(query)}`;
}

function kakaoPlaceUrl(name, lat, lng) {
  return `https://map.kakao.com/link/map/${encodeURIComponent(name)},${lat},${lng}`;
}

function setMapLink(title, url) {
  mapTitle.textContent = title;
  mapOpenLink.href = url;
}

function showMapFallback(message = null) {
  mapFallback.hidden = false;
  if (message) {
    mapFallback.querySelector("p").textContent = message;
  }
}

function clearRouteMarkers() {
  routeMarkers.forEach((marker) => marker.setMap(null));
  routeOverlays.forEach((overlay) => overlay.setMap(null));
  routeMarkers = [];
  routeOverlays = [];
}

function createMarker({ title, lat, lng, image, label, labelClass }) {
  if (!kakaoMap || !window.kakao?.maps) return null;
  const position = new window.kakao.maps.LatLng(lat, lng);
  const marker = new window.kakao.maps.Marker({
    map: kakaoMap,
    position,
    title,
    image,
  });
  routeMarkers.push(marker);
  if (label) {
    const overlay = new window.kakao.maps.CustomOverlay({
      map: kakaoMap,
      position,
      yAnchor: 2.25,
      content: `<div class="map-marker-label ${labelClass || ""}">${escapeHtml(label)}</div>`,
    });
    routeOverlays.push(overlay);
  }
  return marker;
}

function markerImage(color) {
  if (!window.kakao?.maps) return null;
  const svg = encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="34" height="44" viewBox="0 0 34 44">
      <path fill="${color}" stroke="white" stroke-width="3" d="M17 2C9.2 2 3 8.2 3 16c0 10.5 14 26 14 26s14-15.5 14-26C31 8.2 24.8 2 17 2Z"/>
      <circle cx="17" cy="16" r="5" fill="white"/>
    </svg>
  `);
  return new window.kakao.maps.MarkerImage(
    `data:image/svg+xml;charset=UTF-8,${svg}`,
    new window.kakao.maps.Size(34, 44),
    { offset: new window.kakao.maps.Point(17, 42) },
  );
}

function fitMapToPoints(points) {
  if (!kakaoMap || !window.kakao?.maps || points.length === 0) return;
  const bounds = new window.kakao.maps.LatLngBounds();
  points.forEach((point) => {
    bounds.extend(new window.kakao.maps.LatLng(point.lat, point.lng));
  });
  kakaoMap.setBounds(bounds, 48, 48, 48, 48);
}

function renderRouteOnMap({ origins = [], meetingStation = null, selectedPlace = null }) {
  clearRouteMarkers();
  const points = [];
  const originImage = markerImage("#2b6d91");
  const meetingImage = markerImage("#b86f1d");
  const placeImage = markerImage("#1d6f5f");

  origins.forEach((origin, index) => {
    createMarker({
      title: `출발지 ${index + 1}`,
      lat: origin.lat,
      lng: origin.lng,
      image: originImage,
      label: `출발지 ${index + 1}`,
      labelClass: "origin",
    });
    points.push(origin);
  });

  if (meetingStation) {
    createMarker({
      title: `${meetingStation.name}역`,
      lat: meetingStation.lat,
      lng: meetingStation.lng,
      image: meetingImage,
      label: "중간역",
      labelClass: "meeting",
    });
    points.push(meetingStation);
  }

  if (selectedPlace) {
    createMarker({
      title: selectedPlace.name,
      lat: selectedPlace.lat,
      lng: selectedPlace.lng,
      image: placeImage,
      label: "선택 장소",
      labelClass: "place",
    });
    points.push(selectedPlace);
  }

  fitMapToPoints(points);
}

function setMapPosition({ title, lat, lng }) {
  const url = kakaoPlaceUrl(title, lat, lng);
  setMapLink(title, url);

  if (!kakaoMap || !window.kakao?.maps) return;

  const position = new window.kakao.maps.LatLng(lat, lng);
  kakaoMap.setCenter(position);
  kakaoMap.setLevel(3);

  if (!activeMarker) {
    activeMarker = new window.kakao.maps.Marker({ map: kakaoMap, position });
  } else {
    activeMarker.setPosition(position);
  }
}

function focusPlaceOnMap(place) {
  if (!kakaoMap || !window.kakao?.maps) {
    setMapPosition({
      title: place.name,
      lat: place.lat,
      lng: place.lng,
    });
    return;
  }

  const position = new window.kakao.maps.LatLng(place.lat, place.lng);
  setMapLink(place.name, kakaoPlaceUrl(place.name, place.lat, place.lng));
  kakaoMap.setCenter(position);
  kakaoMap.setLevel(3);

  if (!activeMarker) {
    activeMarker = new window.kakao.maps.Marker({ map: kakaoMap, position });
  } else {
    activeMarker.setPosition(position);
  }
}

function updateKakaoSearch(stationName, query) {
  const keyword = `${stationName} ${query || "추천 카페"}`.trim();
  setMapLink(keyword, kakaoSearchUrl(keyword));
}

async function loadClientConfig() {
  const response = await fetch(`${API_BASE}/api/v1/client-config`);
  if (!response.ok) return { kakao_javascript_key: "" };
  return response.json();
}

function loadKakaoSdk(appKey) {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      window.kakao.maps.load(resolve);
      return;
    }

    const script = document.createElement("script");
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${encodeURIComponent(appKey)}&autoload=false`;
    script.async = true;
    script.onload = () => {
      if (!window.kakao?.maps) {
        reject(new Error("Kakao Maps SDK가 차단되었습니다."));
        return;
      }
      window.kakao.maps.load(resolve);
    };
    script.onerror = () => reject(new Error("Kakao Maps SDK를 불러오지 못했습니다."));
    document.head.appendChild(script);
  });
}

async function initMap() {
  updateKakaoSearch("서울역", "조용한 카페");
  setStatus("Kakao 지도 로딩 중");

  try {
    const config = await loadClientConfig();
    if (!config.kakao_javascript_key) {
      showMapFallback(".env에 KAKAO_JAVASCRIPT_KEY를 설정하면 지도가 표시됩니다.");
      return;
    }

    await loadKakaoSdk(config.kakao_javascript_key);
    const center = new window.kakao.maps.LatLng(37.5547, 126.9706);
    kakaoMap = new window.kakao.maps.Map(mapContainer, {
      center,
      level: 4,
    });
    activeMarker = new window.kakao.maps.Marker({
      map: kakaoMap,
      position: center,
    });
    window.kakao.maps.event.addListener(kakaoMap, "tilesloaded", () => {
      setStatus("Kakao 지도 준비 완료");
    });
    mapFallback.hidden = true;
  } catch (error) {
    showMapFallback(
      "Kakao Developers의 Web 플랫폼에 http://localhost:8000 과 http://127.0.0.1:8000 을 등록해야 합니다.",
    );
    setStatus("Kakao 지도 로딩 실패");
    console.warn(error);
  }
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
        aria-label="출발역 제거" title="출발역 제거">
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
  resultContent.innerHTML = "<p>출발역과 원하는 장소를 입력하면 추천 결과가 표시됩니다.</p>";
  updateKakaoSearch("서울역", "조용한 카페");
  setStatus("요청 대기 중");
}

function renderError(error) {
  resultTitle.textContent = "요청 실패";
  resultContent.className = "result-content";
  resultContent.innerHTML = `<div class="error-box">${escapeHtml(error.message)}</div>`;
  setStatus("오류가 발생했습니다");
}

function renderRecommendations(decision) {
  renderRouteOnMap({
    origins: decision.origin_locations,
    meetingStation: decision.meeting_station,
  });
  setMapLink(`${decision.station.name} 추천`, kakaoSearchUrl(`${decision.station.name} ${state.query}`));
  resultTitle.textContent = `${decision.station.name} 추천`;
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    <div class="summary-band success">
      <strong>${escapeHtml(stationLabel(decision.station))}</strong>
      <p>파란 마커는 출발역, 주황 마커는 중간역입니다. 장소의 지도 버튼을 누르면 초록 마커가 추가되고 지도가 자동으로 맞춰집니다.</p>
    </div>
    ${decision.recommendations.map(renderPlace).join("")}
  `;
  setStatus(`${decision.station.name} 주변 ${decision.recommendations.length}개 추천`);
}

function renderSelection(decision) {
  renderRouteOnMap({
    origins: decision.origin_locations,
    meetingStation: decision.meeting_station,
  });
  setMapLink(
    `${decision.meeting_station.name} ${state.query}`,
    decision.map_search.url,
  );
  resultTitle.textContent = "중간역 주변 데이터 없음";
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    <div class="summary-band warning">
      <strong>${escapeHtml(stationLabel(decision.meeting_station))}</strong>
      <p>현재 DB에는 이 중간역 주변 추천 데이터가 없습니다. 추천 데이터가 있는 가까운 역을 선택하거나, 기존 중간역을 Kakao Map에서 바로 검색할 수 있습니다.</p>
      <a class="map-link" href="${escapeHtml(decision.map_search.url)}"
        target="_blank" rel="noreferrer">
        ${escapeHtml(decision.map_search.label)}
      </a>
    </div>
    <div class="section-note">추천 가능한 주변역</div>
    ${decision.options.map(renderOption).join("")}
  `;
  setStatus(`${decision.meeting_station.name} 데이터 없음 · 주변역 ${decision.options.length}개 선택 가능`);
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
        이 역으로 추천 보기
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
      <button class="choice-button" type="button"
        data-place-name="${escapeHtml(place.name)}"
        data-place-lat="${place.lat}"
        data-place-lng="${place.lng}">
        지도에서 보기
      </button>
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
    renderError(new Error("출발역은 최소 2개가 필요합니다."));
    return;
  }

  try {
    setLoading(true);
    setStatus("추천 계산 중");
    const data = await postRecommend(payload);
    if (!selectedStationId) {
      state.lastRequest = payload;
    }
    state.lastDecision = data;

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
  const placeButton = event.target.closest("[data-place-lat]");
  if (placeButton) {
    const selectedPlace = {
      name: placeButton.dataset.placeName,
      lat: Number(placeButton.dataset.placeLat),
      lng: Number(placeButton.dataset.placeLng),
    };
    const originLocations = state.lastDecision?.origin_locations || [];
    const meetingStation = state.lastDecision?.meeting_station || null;
    renderRouteOnMap({
      origins: originLocations,
      meetingStation,
      selectedPlace,
    });
    focusPlaceOnMap(selectedPlace);
    setStatus(`${selectedPlace.name} 위치로 이동`);
    return;
  }

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
initMap();
