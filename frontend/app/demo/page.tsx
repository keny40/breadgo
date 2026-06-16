import Link from "next/link";

const accounts = [
  {
    role: "관리자",
    email: "admin@breadgo.test",
    password: "12345678",
    description: "전체 현황과 가맹점 승인 상태를 확인합니다.",
  },
  {
    role: "가맹점",
    email: "merchant@breadgo.test",
    password: "12345678",
    description: "매장, 상품, 픽업 확인 흐름을 시연합니다.",
  },
  {
    role: "고객",
    email: "customer@breadgo.test",
    password: "12345678",
    description: "지역 상품 조회, 예약, 결제 흐름을 시연합니다.",
  },
];

const quickLinks = [
  { label: "고객으로 시작", href: "/login" },
  { label: "가맹점 화면", href: "/merchant" },
  { label: "관리자 화면", href: "/admin" },
  { label: "상품 보기", href: "/products" },
  { label: "픽업 확인", href: "/merchant/pickup" },
];

const recommendedFlow = [
  "고객 계정으로 로그인",
  "서울특별시 강남구 역삼동 선택",
  "마감할인 상품 예약",
  "Mock 결제 진행",
  "내 예약에서 픽업코드 확인",
  "가맹점 계정으로 로그인",
  "픽업코드 조회 및 픽업 확정",
  "관리자 계정으로 로그인",
  "관리자 대시보드 확인",
];

const steps = [
  {
    title: "고객 로그인",
    body: "customer@breadgo.test 계정으로 로그인합니다.",
    href: "/login",
    action: "로그인으로 이동",
  },
  {
    title: "지역 선택",
    body: "상품 보기 화면에서 서울특별시 강남구 역삼동을 선택합니다.",
    href: "/products",
    action: "상품 보기",
  },
  {
    title: "상품 예약",
    body: "마감할인 상품을 선택하고 수량을 입력해 예약합니다.",
    href: "/products",
    action: "예약 화면으로 이동",
  },
  {
    title: "Mock 결제",
    body: "카드, 카카오페이, 네이버페이 중 하나로 모의결제를 완료합니다.",
    href: "/products",
    action: "결제 흐름 보기",
  },
  {
    title: "픽업코드 확인",
    body: "내 예약에서 고객에게 발급된 픽업코드를 확인합니다.",
    href: "/my-reservations",
    action: "내 예약으로 이동",
  },
  {
    title: "가맹점 로그인",
    body: "merchant@breadgo.test 계정으로 로그인합니다.",
    href: "/login",
    action: "로그인으로 이동",
  },
  {
    title: "픽업 확정",
    body: "픽업코드를 조회하고 예약 상태를 PICKED_UP으로 변경합니다.",
    href: "/merchant/pickup",
    action: "픽업 확인",
  },
  {
    title: "관리자 로그인",
    body: "admin@breadgo.test 계정으로 로그인합니다.",
    href: "/login",
    action: "로그인으로 이동",
  },
  {
    title: "관리자 대시보드 확인",
    body: "사용자, 매장, 상품, 예약, 결제 현황을 한 화면에서 확인합니다.",
    href: "/admin",
    action: "관리자 화면",
  },
];

export default function DemoPage() {
  return (
    <section className="section demo-page">
      <div className="demo-hero">
        <div>
          <p className="eyebrow">Live demo script</p>
          <h1>브레드고 데모 가이드</h1>
          <p>
            비기술 이해관계자에게 BreadGo MVP의 고객 예약, Mock 결제, 가맹점 픽업,
            관리자 모니터링 흐름을 순서대로 보여주기 위한 발표용 페이지입니다.
          </p>
        </div>
        <div className="actions">
          {quickLinks.map((link) => (
            <Link href={link.href} key={link.href}>
              <button type="button">{link.label}</button>
            </Link>
          ))}
        </div>
      </div>

      <section className="section">
        <h2>데모 계정</h2>
        <div className="account-grid">
          {accounts.map((account) => (
            <article className="account-card" key={account.email}>
              <div>
                <div className="card-title-row">
                  <h3>{account.role}</h3>
                  <span className="badge success">Demo</span>
                </div>
                <p>{account.description}</p>
              </div>
              <dl>
                <div>
                  <dt>Email</dt>
                  <dd>{account.email}</dd>
                </div>
                <div>
                  <dt>Password</dt>
                  <dd>{account.password}</dd>
                </div>
              </dl>
              <Link href="/login">
                <button type="button">로그인 페이지로 이동</button>
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>추천 시연 흐름</h2>
        <ol className="flow-list">
          {recommendedFlow.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      </section>

      <section className="section">
        <h2>상세 진행 단계</h2>
        <ol className="demo-steps">
          {steps.map((step, index) => (
            <li key={`${step.title}-${index}`}>
              <div className="step-heading">
                <span>Step {index + 1}</span>
                <h3>{step.title}</h3>
              </div>
              <p>{step.body}</p>
              <div className="actions">
                <Link href={step.href}>
                  <button type="button">{step.action}</button>
                </Link>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </section>
  );
}
