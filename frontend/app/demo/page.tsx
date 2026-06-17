import Link from "next/link";

const accounts = [
  {
    role: "고객",
    email: "customer@breadgo.test",
    password: "12345678",
    description: "지역 상품 조회, 예약, Mock 결제, 픽업코드 확인 흐름을 시연합니다.",
  },
  {
    role: "가맹점",
    email: "merchant@breadgo.test",
    password: "12345678",
    description: "매장, 상품, 이미지 업로드, 픽업 확인 흐름을 시연합니다.",
  },
  {
    role: "관리자",
    email: "admin@breadgo.test",
    password: "12345678",
    description: "사용자, 가맹점, 매장, 상품, 예약, 결제 현황을 확인합니다.",
  },
];

const quickLinks = [
  { label: "고객으로 시작", href: "/login" },
  { label: "가맹점으로 시작", href: "/login" },
  { label: "관리자로 시작", href: "/login" },
  { label: "상품 보기", href: "/products" },
  { label: "픽업 확인", href: "/merchant/pickup" },
];

const recommendedFlows = [
  {
    role: "Customer",
    title: "고객 시연",
    flow: "login → products → reserve → mock payment → pickup code → my reservations/payments",
    body: "고객이 지역 상품을 찾고 예약, Mock 결제, 픽업코드 확인까지 완료하는 흐름입니다.",
  },
  {
    role: "Merchant",
    title: "가맹점 시연",
    flow: "login → dashboard → stores → products → image upload → pickup confirmation",
    body: "가맹점이 매장과 상품을 관리하고 대표 이미지를 업로드한 뒤 픽업코드로 수령을 확정합니다.",
  },
  {
    role: "Admin",
    title: "관리자 시연",
    flow: "login → admin dashboard → users/merchants/stores/products/reservations/payments",
    body: "운영자가 전체 지표와 핵심 운영 데이터를 한 화면에서 모니터링합니다.",
  },
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
    body: "내 예약과 내 결제에서 예약 상태, 결제 상태, 픽업코드를 확인합니다.",
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
    title: "매장과 상품 관리",
    body: "가맹점 대시보드, 매장 관리, 상품 관리 화면에서 매장/상품 목록과 이미지 업로드를 확인합니다.",
    href: "/merchant/products",
    action: "상품 관리",
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
            상품 이미지 업로드, 관리자 모니터링 흐름을 순서대로 보여주기 위한 발표용 페이지입니다.
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
        <div className="account-grid">
          {recommendedFlows.map((flow) => (
            <article className="account-card" key={flow.role}>
              <div className="card-title-row">
                <h3>{flow.title}</h3>
                <span className="badge success">{flow.role}</span>
              </div>
              <p>{flow.body}</p>
              <code>{flow.flow}</code>
            </article>
          ))}
        </div>
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
