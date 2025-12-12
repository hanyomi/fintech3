// 백엔드 API 기본 URL
const BASE_URL = "http://localhost:8000/api/v1"; 

// 1. 탭 전환 로직
function showTab(tabId, title) {
    // 모든 탭 컨텐츠 숨기기
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    // 모든 네비게이션 버튼 비활성화
    document.querySelectorAll('.bottom-nav button').forEach(el => el.classList.remove('active'));

    // 해당 탭 컨텐츠 보이기
    document.getElementById(tabId).style.display = 'block';
    // 해당 네비게이션 버튼 활성화
    document.getElementById(`nav-${tabId}`).classList.add('active');
    // 헤더 타이틀 업데이트
    document.getElementById('page-title').textContent = title;

    // 탭별 데이터 로드 함수 호출
    if (tabId === 'home') loadHomeData();
    else if (tabId === 'market') loadMarketData('all');
    else if (tabId === 'live') loadLiveContent(' 진행중');
    else if (tabId === 'community') loadCommunityData();
    // 'my' 탭은 정적 데이터로 처리
}

// 2. 홈 화면 데이터 로드 (FR-010, FR-011, FR-012, FR-A01, FR-013)
async function loadHomeData() {
    try {
        const assetResponse = await fetch(`${BASE_URL}/home/assets`);
        const assetData = await assetResponse.json();
        
        const liveResponse = await fetch(`${BASE_URL}/live/list`);
        const liveData = await liveResponse.json();

        // FR-010: 총 자산 표시
        document.getElementById('total-asset').textContent = `${assetData.total_asset.toLocaleString('ko-KR')} KRW`;
        
        // FR-A01: AI 브리핑 카드
        document.getElementById('ai-briefing-card').innerHTML = `
            <strong>AI 자산 브리핑:</strong><br>
            <p style="margin-top: 5px; font-size: 0.9rem; line-height: 1.4;">${assetData.ai_briefing}</p>
        `;

        // FR-011: 자산 비중 표시
        const breakdownList = document.getElementById('asset-breakdown');
        breakdownList.innerHTML = assetData.asset_breakdown.map(item => `
            <li class="simple-list__item" style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>${item.type}</span>
                <span style="font-weight: 600;">${item.amount.toLocaleString('ko-KR')} KRW (${item.percentage.toFixed(1)}%)</span>
            </li>
        `).join('');

        // FR-012: 계좌 요약 표시
        const accountSummary = document.getElementById('account-summary');
        accountSummary.innerHTML = assetData.accounts.map(item => `
            <div class="card" style="padding: 12px; margin-bottom: 8px; cursor: pointer;" onclick="alert('계좌 상세 페이지로 이동 (향후)')">
                <strong style="font-size: 0.9rem;">${item.financial_company}</strong> - ${item.account_name}<br>
                <span style="font-size: 1.1rem; font-weight: 700;">${item.balance.toLocaleString('ko-KR')} KRW</span>
            </div>
        `).join('');
        
        // FR-013: 추천 라이브 섹션
        const recommendedLive = document.getElementById('recommended-live');
        const liveItem = liveData.recommended_live[0];
        recommendedLive.innerHTML = `
            <h3 style="font-size: 1.1rem; margin-bottom: 10px;">추천 라이브</h3>
            <div class="card" style="background-color: #e0f2fe; border: 1px solid #90cdf4; cursor: pointer; padding: 12px;" onclick="showTab('live', '라이브')">
                <p style="margin: 0; font-weight: 600; color: #1e40af;">${liveItem.title}</p>
                <small style="color: #3b82f6;">전문가: ${liveItem.expert} | 지금 시청하기 ▶️</small>
            </div>
        `;

    } catch (error) {
        console.error("홈 데이터 로드 오류:", error);
        document.getElementById('total-asset').textContent = '데이터 로드 실패';
    }
}

// 3. 마켓 화면 데이터 로드 (FR-020, FR-021, FR-022)
async function loadMarketData(category = 'all') {
    // 탭 활성화 상태 변경
    document.querySelectorAll('#market-category-tabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });

    const url = category === 'all' ? `${BASE_URL}/market/products` : `${BASE_URL}/market/products?category=${category}`;

    try {
        const response = await fetch(url);
        const products = await response.json();

        const productListBody = document.getElementById('product-list-body');
        productListBody.innerHTML = products.map(product => `
            <tr onclick="showProductDetail(${product.id}, '${product.name}', '${product.code}', '${product.category}', '${product.risk_level}', ${product.expected_return}, '${product.schedule}')" style="cursor: pointer;">
                <td style="font-weight: 600;">${product.name}</td>
                <td>${product.risk_level}</td>
                <td style="color: ${product.expected_return > 0 ? '#10b981' : '#ef4444'};">${product.expected_return ? product.expected_return.toFixed(1) + '%' : 'N/A'}</td>
                <td>${product.schedule.substring(0, 10)}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error("마켓 데이터 로드 오류:", error);
        document.getElementById('product-list-body').innerHTML = '<tr><td colspan="4" style="text-align: center;">데이터 로드 실패</td></tr>';
    }
}

// 4. 상품 상세 모달 표시 (FR-022)
function showProductDetail(id, name, code, category, risk, expectedReturn, schedule) {
    document.getElementById('modal-product-name').textContent = name;
    document.getElementById('modal-product-code').textContent = code;
    document.getElementById('modal-product-category').textContent = category;
    document.getElementById('modal-product-risk').textContent = risk;
    document.getElementById('modal-product-return').textContent = expectedReturn ? expectedReturn.toFixed(1) + '%' : 'N/A';
    document.getElementById('modal-product-schedule').textContent = schedule;
    
    // 모달 표시
    document.getElementById('product-modal').style.display = 'flex';
}

// 5. 커뮤니티 데이터 로드 (FR-040, FR-042)
async function loadCommunityData() {
    try {
        const response = await fetch(`${BASE_URL}/community/posts`);
        const posts = await response.json();

        const listContainer = document.getElementById('post-list-body');
        listContainer.innerHTML = posts.map(post => `
            <div class="market-list__item" style="padding: 10px 16px; border-bottom: 1px solid #f3f4f6; cursor: pointer;" 
                 onclick="alert('제목: ${post.title}\\n작성자: ${post.author}\\n내용: ${post.content.substring(0, 50)}... (FR-042 간단 상세 펼침)')">
                <div style="font-weight: 600; font-size: 0.95rem;">${post.title}</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">
                    <span>${post.author}</span> · <span>${post.created_at.substring(5, 16)}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error("커뮤니티 데이터 로드 오류:", error);
        document.getElementById('post-list-body').innerHTML = '<p style="padding: 16px; text-align: center;">데이터 로드 실패</p>';
    }
}

// 6. 라이브 화면 데이터 로드 (FR-030)
async function loadLiveContent(status) {
    // 탭 활성화 상태 변경
    document.querySelectorAll('#live-tabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.liveTab === status) {
            btn.classList.add('active');
        }
    });

    try {
        const response = await fetch(`${BASE_URL}/live/list`);
        const data = await response.json();
        const liveList = data[status.trim()]; 

        const listContainer = document.getElementById('live-list-content');
        if (liveList && liveList.length > 0) {
            listContainer.innerHTML = liveList.map(live => `
                <div class="card" onclick="alert('라이브 상세 시청 (FR-031)은 향후 고도화 예정입니다.')" style="cursor: pointer; padding: 12px; margin-bottom: 8px;">
                    <p style="margin: 0 0 5px 0;">
                        ${live.status === 'LIVE' ? '<span style="color: red; font-weight: bold;">🔴 LIVE</span>' : live.status}
                        - <strong style="font-size: 1rem;">${live.title}</strong>
                    </p>
                    <small style="color: #6b7280;">전문가: ${live.expert} | 시청자: ${live.viewer.toLocaleString()}명</small>
                </div>
            `).join('');
        } else {
            listContainer.innerHTML = '<p style="padding: 16px; text-align: center;">현재 해당 카테고리에 라이브가 없습니다.</p>';
        }

    } catch (error) {
        console.error("라이브 데이터 로드 오류:", error);
        document.getElementById('live-list-content').innerHTML = '<p style="padding: 16px; text-align: center;">라이브 데이터 로드 실패</p>';
    }
}


// 초기화: 첫 화면 로드 및 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', () => {
    // 첫 탭을 Home으로 설정
    showTab('home', 'EasyFin V2.0'); 

    // 마켓 탭 클릭 이벤트 리스너 (FR-020)
    document.querySelectorAll('#market-category-tabs .tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            loadMarketData(e.target.dataset.category);
        });
    });

    // 라이브 탭 클릭 이벤트 리스너 (FR-030)
    document.querySelectorAll('#live-tabs .tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            loadLiveContent(e.target.dataset.liveTab);
        });
    });

    // 모달 닫기 이벤트 리스너
    window.onclick = function(event) {
        const modal = document.getElementById('product-modal');
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
});