import Link from "next/link";

export default function HomePage() {
  return (
    <section className="hero">
      <h1>BreadGo</h1>
      <p>
        동네 베이커리의 남는 빵을 합리적인 가격으로 예약하고, 매장은 폐기될
        수 있는 식품을 더 많은 고객에게 연결하는 푸드 레스큐 마켓플레이스입니다.
      </p>
      <div className="actions">
        <Link href="/products">
          <button>Customer flow</button>
        </Link>
        <Link href="/merchant">
          <button className="secondary">Merchant flow</button>
        </Link>
      </div>
    </section>
  );
}
