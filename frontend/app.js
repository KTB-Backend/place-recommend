const API_BASE = "";
const SAMPLE_STATIONS = ["서울역", "강남역"];

const state = {
  stations: [...SAMPLE_STATIONS],
  query: "조용한 카페",
  topK: 3,
  lastRequest: null,
  selectionDecision: null,
  placeDetails: {},
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
const workspace = document.querySelector(".workspace");
const resultPanel = document.querySelector(".result-panel");
const mapContainer = document.querySelector("#kakao-map");
const mapFallback = document.querySelector("#map-fallback");
const mapOpenLink = document.querySelector("#map-open-link");
const mapTitle = document.querySelector("#map-title");

let kakaoMap = null;
let activeMarker = null;
let selectedPlaceMarker = null;
let selectedPlaceInfoOverlay = null;
let selectedPlaceInfoElement = null;
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

function formatRating(rating) {
  return rating > 0 ? `${rating.toFixed(1)} / 5.0` : "평점 정보 없음";
}

function reviewStorageKey(placeId) {
  return `mid-meet:place-reviews:${placeId}`;
}

function placeReviews(placeId) {
  try {
    return JSON.parse(localStorage.getItem(reviewStorageKey(placeId)) || "[]");
  } catch {
    return [];
  }
}

function savePlaceReviews(placeId, reviews) {
  localStorage.setItem(reviewStorageKey(placeId), JSON.stringify(reviews));
}

function randomNickname() {
  const adjectives = ["느긋한", "든든한", "상냥한", "차분한", "활기찬", "꼼꼼한", "따뜻한", "솔직한"];
  const nouns = ["모임러", "카페러", "맛잘알", "길잡이", "탐방러", "동네친구", "리뷰어", "약속러"];
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  const noun = nouns[Math.floor(Math.random() * nouns.length)];
  const suffix = Math.floor(100 + Math.random() * 900);
  return `${adjective} ${noun}${suffix}`;
}

function renderPlaceReviews(placeId) {
  const reviews = placeReviews(placeId);
  if (reviews.length === 0) {
    return `<p class="review-empty">아직 등록된 후기가 없습니다.</p>`;
  }
  return `
    <ul class="review-list">
      ${reviews
        .map(
          (review) => `
            <li>
              <div class="review-meta">
                <strong>${escapeHtml(review.nickname || "익명 리뷰어")}</strong>
                <time datetime="${escapeHtml(review.createdAt)}">${escapeHtml(review.label)}</time>
              </div>
              <p>${escapeHtml(review.text)}</p>
            </li>
          `,
        )
        .join("")}
    </ul>
  `;
}

function addPlaceReview(placeId, text) {
  const reviewText = text.trim();
  if (!reviewText) return;

  const now = new Date();
  const reviews = placeReviews(placeId);
  reviews.unshift({
    text: reviewText.slice(0, 240),
    nickname: randomNickname(),
    createdAt: now.toISOString(),
    label: now.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }),
  });
  savePlaceReviews(placeId, reviews.slice(0, 20));
}

const PLACE_TYPE_RULES = [
  { label: "햄버거", glyph: "버거", keywords: ["햄버거", "버거", "버거킹", "롯데리아", "맥도날드", "맘스터치", "쉐이크쉑"] },
  { label: "카페", glyph: "카페", keywords: ["카페", "커피", "로스터리", "스타벅스", "투썸", "이디야"] },
  { label: "베이커리", glyph: "빵", keywords: ["베이커리", "제과", "빵", "파리크라상", "파리바게뜨", "뚜레쥬르"] },
  { label: "술집", glyph: "술집", keywords: ["술집", "호프", "맥주", "와인", "이자카야", "포차", "바"] },
  { label: "한식", glyph: "한식", keywords: ["한식", "국밥", "찌개", "삼겹살", "고기", "백반"] },
  { label: "일식", glyph: "일식", keywords: ["일식", "초밥", "스시", "라멘", "돈카츠", "우동"] },
  { label: "중식", glyph: "중식", keywords: ["중식", "중국집", "짜장", "짬뽕", "마라"] },
  { label: "양식", glyph: "양식", keywords: ["양식", "파스타", "피자", "스테이크"] },
  { label: "분식", glyph: "분식", keywords: ["분식", "김밥", "떡볶이", "튀김"] },
  { label: "샐러드", glyph: "샐러드", keywords: ["샐러드", "포케", "샌드위치"] },
];

function placeType(place) {
  const source = [
    place.subcategory,
    place.category,
    ...(place.tags || []),
    place.name,
  ]
    .filter(Boolean)
    .join(" ");

  const rule = PLACE_TYPE_RULES.find((item) =>
    item.keywords.some((keyword) => source.includes(keyword)),
  );
  if (rule) return { label: rule.label, glyph: rule.glyph };

  if (place.category?.includes("레스토랑")) {
    return { label: "음식점", glyph: "음식" };
  }
  if (place.subcategory) {
    const label = place.subcategory.split(",")[0].trim();
    return { label, glyph: label.slice(0, 3) };
  }
  return { label: place.category || "장소", glyph: "장소" };
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
  selectedPlaceMarker = null;
  selectedPlaceInfoOverlay = null;
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
      yAnchor: 2.85,
      content: `<div class="map-marker-label ${labelClass || ""}">${escapeHtml(label)}</div>`,
    });
    routeOverlays.push(overlay);
  }
  return marker;
}

function markerImage({ fill, stroke, halo, glyph, fontSize = 9.5 }) {
  if (!window.kakao?.maps) return null;
  const safeGlyph = escapeHtml(glyph);
  const svg = encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="44" height="56" viewBox="0 0 44 56">
      <defs>
        <filter id="shadow" x="-30%" y="-20%" width="160%" height="170%">
          <feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#1b1611" flood-opacity="0.34"/>
        </filter>
        <linearGradient id="pin" x1="12" y1="5" x2="32" y2="45" gradientUnits="userSpaceOnUse">
          <stop stop-color="${halo}"/>
          <stop offset="0.52" stop-color="${fill}"/>
          <stop offset="1" stop-color="${stroke}"/>
        </linearGradient>
      </defs>
      <ellipse cx="22" cy="51" rx="11" ry="3.2" fill="#1b1611" opacity="0.28"/>
      <path filter="url(#shadow)" fill="url(#pin)" stroke="#fff7eb" stroke-width="2.6"
        d="M22 3.5c-9.4 0-17 7.3-17 16.3C5 32.1 22 52 22 52s17-19.9 17-32.2c0-9-7.6-16.3-17-16.3Z"/>
      <circle cx="22" cy="20" r="10.8" fill="#fffaf0" opacity="0.96"/>
      <circle cx="22" cy="20" r="8.1" fill="${fill}" opacity="0.14"/>
      <text x="22" y="23.7" text-anchor="middle"
        font-family="Pretendard, Inter, Arial, sans-serif" font-size="${fontSize}" font-weight="900"
        fill="${stroke}">${safeGlyph}</text>
    </svg>
  `);
  return new window.kakao.maps.MarkerImage(
    `data:image/svg+xml;charset=UTF-8,${svg}`,
    new window.kakao.maps.Size(44, 56),
    { offset: new window.kakao.maps.Point(22, 52) },
  );
}

function placeMarkerImage(place) {
  const type = placeType(place);
  return markerImage({
    fill: "#28a88f",
    stroke: "#145c54",
    halo: "#91ead6",
    glyph: type.glyph,
    fontSize: type.glyph.length > 2 ? 7.4 : 9.5,
  });
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
  const originImage = markerImage({
    fill: "#4ea3c7",
    stroke: "#1f5b78",
    halo: "#9bd9ef",
    glyph: "GO",
  });
  const meetingImage = markerImage({
    fill: "#f29a38",
    stroke: "#9f4f18",
    halo: "#ffd39c",
    glyph: "MID",
  });

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
    const selectedPlaceType = placeType(selectedPlace);
    selectedPlaceMarker = createMarker({
      title: selectedPlace.name,
      lat: selectedPlace.lat,
      lng: selectedPlace.lng,
      image: placeMarkerImage(selectedPlace),
      label: `${selectedPlaceType.label} · ${selectedPlace.name}`,
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

function mapVisibleCenterOffset() {
  if (!mapContainer) return { x: 0, y: 0 };
  const mapRect = mapContainer.getBoundingClientRect();
  let left = mapRect.left;
  let right = mapRect.right;

  [workspace, resultPanel].forEach((panel) => {
    if (!panel) return;
    const style = window.getComputedStyle(panel);
    if (style.position !== "fixed" || style.display === "none" || style.visibility === "hidden") {
      return;
    }
    const rect = panel.getBoundingClientRect();
    const overlapsVertically = rect.bottom > mapRect.top && rect.top < mapRect.bottom;
    if (!overlapsVertically) return;

    const overlapsHorizontally = rect.right > mapRect.left && rect.left < mapRect.right;
    if (!overlapsHorizontally) return;

    const panelCenterX = rect.left + rect.width / 2;
    const mapCenterX = mapRect.left + mapRect.width / 2;
    if (panelCenterX < mapCenterX) {
      left = Math.max(left, rect.right);
    } else {
      right = Math.min(right, rect.left);
    }
  });

  const visibleCenterX = (left + right) / 2 - mapRect.left;
  const visibleCenterY = mapRect.height / 2;
  return {
    x: visibleCenterX - mapRect.width / 2,
    y: visibleCenterY - mapRect.height / 2,
  };
}

function centerMapOnMarker(position, { level = 3, accountForPanels = true } = {}) {
  if (!kakaoMap || !window.kakao?.maps) return;
  kakaoMap.setLevel(level);
  kakaoMap.setCenter(position);

  if (!accountForPanels || window.innerWidth <= 1180) return;
  const offset = mapVisibleCenterOffset();
  if (Math.abs(offset.x) < 1 && Math.abs(offset.y) < 1) return;
  kakaoMap.panBy(-Math.round(offset.x), -Math.round(offset.y));
}

function focusStationOnMap(station) {
  if (!station || !kakaoMap || !window.kakao?.maps) return;
  const position = new window.kakao.maps.LatLng(station.lat, station.lng);
  centerMapOnMarker(position, { level: 4 });
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
  centerMapOnMarker(position, { level: 3 });

  if (selectedPlaceMarker) {
    selectedPlaceMarker.setPosition(position);
    selectedPlaceMarker.setImage(placeMarkerImage(place));
  } else {
    const selectedPlaceType = placeType(place);
    selectedPlaceMarker = createMarker({
      title: place.name,
      lat: place.lat,
      lng: place.lng,
      image: placeMarkerImage(place),
      label: `${selectedPlaceType.label} · ${place.name}`,
      labelClass: "place",
    });
  }

  if (!activeMarker) {
    activeMarker = new window.kakao.maps.Marker({ map: kakaoMap, position });
  } else {
    activeMarker.setPosition(position);
  }
}

function closePlaceInfo() {
  if (selectedPlaceInfoOverlay) {
    selectedPlaceInfoOverlay.setMap(null);
    selectedPlaceInfoOverlay = null;
  }
  if (selectedPlaceInfoElement) {
    selectedPlaceInfoElement.remove();
    selectedPlaceInfoElement = null;
  }
  workspace?.classList.remove("showing-place-info");
}

function placeInfoContent(place, similarityScore, reviewsOpen = false) {
  const mapUrl = kakaoPlaceUrl(place.name, place.lat, place.lng);
  const reviewsMarkup = renderPlaceReviews(place.id);
  const tags = place.tags
    .slice(0, 4)
    .map((tag) => `<span class="pill">${escapeHtml(tag)}</span>`)
    .join("");

  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <article class="map-place-info">
      <button class="map-place-close" type="button" data-close-place-info
        aria-label="장소 정보 닫기" title="장소 정보 닫기">×</button>
      <div class="map-place-header">
        <p class="eyebrow">Place Detail</p>
        <h3>${escapeHtml(place.name)}</h3>
      </div>
      <div class="place-meta">
        <span>${escapeHtml(place.category)}</span>
        <span>${escapeHtml(place.subcategory)}</span>
        <span>${formatScore(similarityScore)}</span>
      </div>
      <dl class="map-place-facts">
        <div class="map-place-address">
          <dt>주소</dt>
          <dd>${escapeHtml(place.address || "주소 정보 없음")}</dd>
        </div>
        <div>
          <dt>평점</dt>
          <dd>${formatRating(place.rating)}</dd>
        </div>
      </dl>
      <p>${escapeHtml(place.description)}</p>
      <div class="map-place-tags">${tags}</div>
      <section class="place-review-section" data-review-section="${escapeHtml(place.id)}">
        <div class="review-heading">
          <h4>후기</h4>
          <span>${placeReviews(place.id).length}개</span>
        </div>
        <button class="review-toggle" type="button" data-review-toggle
          aria-expanded="${reviewsOpen ? "true" : "false"}">
          ${reviewsOpen ? "후기 숨기기" : "후기 보기"}
        </button>
        <div class="review-body" data-review-body ${reviewsOpen ? "" : "hidden"}>
          <div class="review-items" data-review-list="${escapeHtml(place.id)}">
            ${reviewsMarkup}
          </div>
          <form class="review-form" data-review-form="${escapeHtml(place.id)}">
            <textarea name="review" rows="3" maxlength="240"
              placeholder="이 장소에 대한 후기를 남겨주세요"></textarea>
            <button type="submit">후기 등록</button>
          </form>
        </div>
      </section>
      <a class="map-place-link" href="${escapeHtml(mapUrl)}" target="_blank" rel="noreferrer">
        Kakao Map에서 열기
      </a>
    </article>
  `;
  return wrapper.firstElementChild;
}

function showPlaceInfo(placeId, reviewsOpen = false) {
  const detail = state.placeDetails[placeId];
  if (!detail) return;

  const { place, similarityScore } = detail;
  closePlaceInfo();
  selectedPlaceInfoElement = placeInfoContent(place, similarityScore, reviewsOpen);
  selectedPlaceInfoElement.classList.add("workspace-place-info");
  workspace?.classList.add("showing-place-info");
  workspace?.appendChild(selectedPlaceInfoElement);
  focusPlaceOnMap(place);
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
  closePlaceInfo();
  state.placeDetails = {};
  state.selectionDecision = null;
  resultTitle.textContent = "아직 결과가 없습니다";
  resultContent.className = "result-content empty-state";
  resultContent.innerHTML = "<p>출발역과 원하는 장소를 입력하면 추천 결과가 표시됩니다.</p>";
  updateKakaoSearch("서울역", "조용한 카페");
  setStatus("요청 대기 중");
}

function renderError(error) {
  closePlaceInfo();
  state.placeDetails = {};
  state.selectionDecision = null;
  resultTitle.textContent = "요청 실패";
  resultContent.className = "result-content";
  resultContent.innerHTML = `<div class="error-box">${escapeHtml(error.message)}</div>`;
  setStatus("오류가 발생했습니다");
}

function renderRefreshControls(stationId) {
  return `
    <div class="refresh-controls">
      <label>
        이 중간역에서 다시 찾을 장소
        <input type="text" data-refresh-query
          value="${escapeHtml(state.query)}" placeholder="예: 맛있는 안주 술집" />
      </label>
      <button class="choice-button refresh-button" type="button"
        data-station-id="${escapeHtml(stationId)}">
        현재 중간역에서 추천 다시 찾기
      </button>
    </div>
  `;
}

function renderRecommendations(decision, options = {}) {
  closePlaceInfo();
  state.placeDetails = {};
  renderRouteOnMap({
    origins: decision.origin_locations,
    meetingStation: decision.meeting_station,
  });
  focusStationOnMap(decision.meeting_station || decision.station);
  setMapLink(`${decision.station.name} 추천`, kakaoSearchUrl(`${decision.station.name} ${state.query}`));
  resultTitle.textContent = `${decision.station.name} 추천`;
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    ${
      options.showBackToOptions
        ? `<button class="choice-button back-button" type="button" data-back-to-options>
            다른 역 다시 보기
          </button>`
        : ""
    }
    <div class="summary-band success">
      <strong>${escapeHtml(stationLabel(decision.station))}</strong>
      <p>파란 마커는 출발역, 주황 마커는 중간역입니다. 장소의 지도 버튼을 누르면 초록 마커가 추가되고 지도가 자동으로 맞춰집니다.</p>
      ${renderRefreshControls(decision.station.id)}
    </div>
    ${decision.recommendations.map(renderPlace).join("")}
  `;
  setStatus(`${decision.station.name} 주변 ${decision.recommendations.length}개 추천`);
}

function renderSelection(decision) {
  closePlaceInfo();
  state.placeDetails = {};
  renderRouteOnMap({
    origins: decision.origin_locations,
    meetingStation: decision.meeting_station,
  });
  focusStationOnMap(decision.meeting_station);
  setMapLink(
    `${decision.meeting_station.name} ${state.query}`,
    decision.map_search.url,
  );
  resultTitle.textContent = "중간역 주변 데이터 없음";
  resultContent.className = "result-content";
  resultContent.innerHTML = `
    <div class="summary-band warning">
      <strong>${escapeHtml(stationLabel(decision.meeting_station))}</strong>
      <p>아직 추천받은 위치가 없어요! 여러분의 방문을 공유해주세요!</p>
      <a class="map-link" href="${escapeHtml(decision.map_search.url)}"
        target="_blank" rel="noreferrer">
        ${escapeHtml(decision.map_search.label)}
      </a>
      ${renderRefreshControls(decision.meeting_station.id)}
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
  state.placeDetails[place.id] = {
    place,
    similarityScore: recommendation.similarity_score,
  };
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
        data-place-id="${escapeHtml(place.id)}"
        data-place-name="${escapeHtml(place.name)}"
        data-place-category="${escapeHtml(place.category)}"
        data-place-subcategory="${escapeHtml(place.subcategory)}"
        data-place-lat="${place.lat}"
        data-place-lng="${place.lng}">
        장소 정보 보기
      </button>
    </article>
  `;
}

async function submitRecommendation(selectedStationId = null, options = {}) {
  const queryOverride = options.query?.trim();
  const baseRequest = selectedStationId
    ? { ...(state.lastRequest || readForm()) }
    : readForm();

  if (queryOverride) {
    baseRequest.query = queryOverride;
    state.query = queryOverride;
    queryInput.value = queryOverride;
    state.lastRequest = { ...baseRequest };
  }

  const payload = selectedStationId
    ? { ...baseRequest, selected_station_id: selectedStationId }
    : baseRequest;

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
      state.selectionDecision = null;
    }
    state.lastDecision = data;

    if (data.status === "station_selection_required") {
      state.selectionDecision = data;
      renderSelection(data);
      return;
    }
    renderRecommendations(data, {
      showBackToOptions: Boolean(selectedStationId && state.selectionDecision),
    });
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
  if (event.target.closest("[data-back-to-options]")) {
    if (state.selectionDecision) {
      state.lastDecision = state.selectionDecision;
      renderSelection(state.selectionDecision);
    }
    return;
  }

  const placeButton = event.target.closest("[data-place-lat]");
  if (placeButton) {
    const selectedPlace = state.placeDetails[placeButton.dataset.placeId]?.place || {
      name: placeButton.dataset.placeName,
      category: placeButton.dataset.placeCategory,
      subcategory: placeButton.dataset.placeSubcategory,
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
    showPlaceInfo(placeButton.dataset.placeId);
    setStatus(`${selectedPlace.name} 위치로 이동`);
    return;
  }

  const button = event.target.closest("[data-station-id]");
  if (!button) return;
  const refreshInput = button
    .closest(".refresh-controls")
    ?.querySelector("[data-refresh-query]");
  const query = refreshInput instanceof HTMLInputElement ? refreshInput.value : "";
  submitRecommendation(button.dataset.stationId, { query });
});

document.addEventListener("submit", (event) => {
  const formElement = event.target;
  if (!(formElement instanceof HTMLFormElement)) return;
  const placeId = formElement.dataset.reviewForm;
  if (!placeId) return;

  event.preventDefault();
  const textarea = formElement.querySelector("textarea[name='review']");
  if (!(textarea instanceof HTMLTextAreaElement)) return;
  addPlaceReview(placeId, textarea.value);
  showPlaceInfo(placeId, true);
});

document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const reviewToggle = event.target.closest("[data-review-toggle]");
  if (reviewToggle instanceof HTMLButtonElement) {
    const section = reviewToggle.closest("[data-review-section]");
    const body = section?.querySelector("[data-review-body]");
    if (body instanceof HTMLElement) {
      const shouldOpen = body.hidden;
      body.hidden = !shouldOpen;
      reviewToggle.setAttribute("aria-expanded", String(shouldOpen));
      reviewToggle.textContent = shouldOpen ? "후기 숨기기" : "후기 보기";
    }
    return;
  }
  if (event.target.closest("[data-close-place-info]")) {
    closePlaceInfo();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closePlaceInfo();
  }
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
