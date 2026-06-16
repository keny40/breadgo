import Link from "next/link";

const features = [
  {
    title: "고객",
    flow: "지역 선택 -> 상품 예약 -> 픽업",
    body: "우리 동네에서 오늘 픽업 가능한 마감 할인 빵을 빠르게 찾고 예약합니다.",
  },
  {
    title: "가맹점",
    flow: "남은 빵 등록 -> 예약 확인 -> 픽업 확정",
    body: "폐기될 수 있는 상품을 등록하고 고객 픽업을 간단히 확인합니다.",
  },
  {
    title: "관리자",
    flow: "전체 운영 현황 확인",
    body: "사용자, 매장, 상품, 예약, 결제 상태를 한 화면에서 모니터링합니다.",
  },
];

export default function HomePage() {
  return (
    <section className="hero">
      <div className="hero-panel">
        <div>
          <p className="eyebrow">Food rescue marketplace</p>
          <h1>우리 동네 마감 할인 빵을 예약하고 픽업하세요.</h1>
        </div>
        <p>
          BreadGo는 동네 베이커리의 남는 빵을 고객에게 연결해 폐기를 줄이고,
          고객은 합리적인 가격으로 오늘 픽업 가능한 상품을 예약할 수 있는 MVP입니다.
        </p>
        <div className="actions">
          <Link href="/demo">
            <button>데모 가이드 보기</button>
          </Link>
          <Link href="/products">
            <button className="secondary">상품 보러 가기</button>
          </Link>
          <Link href="/merchant">
            <button className="secondary">가맹점 시작하기</button>
          </Link>
        </div>
      </div>

      <div className="feature-grid">
        {features.map((feature) => (
          <article className="item" key={feature.title}>
            <div className="card-title-row">
              <h3>{feature.title}</h3>
              <span className="badge success">{feature.flow}</span>
            </div>
            <p>{feature.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
