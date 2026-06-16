"use client";

import { FormEvent, useEffect, useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Store } from "@/lib/types";

export default function MerchantStoresPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [addressDetail, setAddressDetail] = useState("");
  const [sido, setSido] = useState("서울특별시");
  const [sigungu, setSigungu] = useState("강남구");
  const [dong, setDong] = useState("역삼동");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [description, setDescription] = useState("");
  const [openingTime, setOpeningTime] = useState("09:00");
  const [closingTime, setClosingTime] = useState("21:00");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    void loadStores();
  }, []);

  async function loadStores() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Store[]>("/api/v1/stores/me", {}, true);
      setStores(data);
      setMessage(`${data.length}개 매장을 불러왔습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function createStore(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Store>(
        "/api/v1/stores",
        {
          method: "POST",
          body: JSON.stringify({
            name,
            address,
            address_detail: addressDetail || null,
            sido: sido || null,
            sigungu: sigungu || null,
            dong: dong || null,
            latitude: latitude || null,
            longitude: longitude || null,
            phone_number: phoneNumber,
            description: description || null,
            opening_time: openingTime,
            closing_time: closingTime,
          }),
        },
        true,
      );
      setMessage("매장이 등록되었습니다.");
      await loadStores();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="매장 관리"
        description="지역 기반 상품 노출을 위해 매장 주소와 지역 정보를 함께 등록합니다."
        actions={
          <button type="button" onClick={loadStores}>
            매장 불러오기
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <form className="panel form-grid" onSubmit={createStore}>
        <h2>매장 등록</h2>
        <div className="two-column">
          <label>
            매장명
            <input value={name} onChange={(event) => setName(event.target.value)} required />
          </label>
          <label>
            전화번호
            <input value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} required />
          </label>
        </div>
        <label>
          주소
          <input value={address} onChange={(event) => setAddress(event.target.value)} required />
        </label>
        <label>
          상세 주소
          <input value={addressDetail} onChange={(event) => setAddressDetail(event.target.value)} />
        </label>
        <div className="three-column">
          <label>
            시/도
            <input value={sido} onChange={(event) => setSido(event.target.value)} placeholder="서울특별시" />
          </label>
          <label>
            시/군/구
            <input value={sigungu} onChange={(event) => setSigungu(event.target.value)} placeholder="강남구" />
          </label>
          <label>
            동/읍/면
            <input value={dong} onChange={(event) => setDong(event.target.value)} placeholder="역삼동" />
          </label>
        </div>
        <div className="two-column">
          <label>
            Latitude
            <input value={latitude} onChange={(event) => setLatitude(event.target.value)} placeholder="37.500000" />
          </label>
          <label>
            Longitude
            <input value={longitude} onChange={(event) => setLongitude(event.target.value)} placeholder="127.030000" />
          </label>
        </div>
        <label>
          매장 설명
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
        </label>
        <div className="two-column">
          <label>
            Opening time
            <input type="time" value={openingTime} onChange={(event) => setOpeningTime(event.target.value)} required />
          </label>
          <label>
            Closing time
            <input type="time" value={closingTime} onChange={(event) => setClosingTime(event.target.value)} required />
          </label>
        </div>
        <button type="submit">매장 등록</button>
      </form>

      <div className="list">
        {stores.length === 0 && !isError && (
          <EmptyState title="매장이 없습니다. 먼저 매장을 등록하세요." description="상품 등록은 매장 생성 후 가능합니다." />
        )}
        {stores.map((store) => (
          <article className="item" key={store.id}>
            <div className="card-title-row">
              <h3>{store.name}</h3>
              <StatusBadge status={store.is_active ? "ACTIVE" : "HIDDEN"} />
            </div>
            <div className="meta">
              <span>ID {store.id}</span>
              <span>{[store.sido, store.sigungu, store.dong].filter(Boolean).join(" ") || "지역 미입력"}</span>
              <span>{store.address}</span>
              <span>{store.opening_time} - {store.closing_time}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
