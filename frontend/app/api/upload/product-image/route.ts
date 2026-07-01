import { put } from "@vercel/blob";
import { createHash, createHmac } from "crypto";
import { NextResponse } from "next/server";

export const runtime = "nodejs";

const MAX_IMAGE_SIZE_BYTES = 3 * 1024 * 1024;
const IMAGE_UPLOAD_DISABLED_MESSAGE =
  "이미지 파일 업로드 storage가 설정되지 않았습니다. 이미지 URL 직접 입력은 계속 사용할 수 있습니다.";

type StorageStatus = {
  enabled: boolean;
  backend: string;
  message: string;
  missing_env: string[];
};

function sanitizeFileName(fileName: string): string {
  return fileName
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 120) || "product-image";
}

function normalizeBackend() {
  const configuredBackend = process.env.STORAGE_BACKEND?.trim().toLowerCase();
  if (configuredBackend) {
    return configuredBackend;
  }
  if (process.env.BLOB_READ_WRITE_TOKEN) {
    return "vercel_blob";
  }
  if (process.env.S3_BUCKET || process.env.S3_ENDPOINT_URL) {
    return "s3";
  }
  return "none";
}

function missingEnv(names: string[]) {
  return names.filter((name) => !process.env[name]?.trim());
}

function getStorageStatus(): StorageStatus {
  if (process.env.IMAGE_UPLOAD_ENABLED?.trim().toLowerCase() === "false") {
    return {
      enabled: false,
      backend: normalizeBackend(),
      message: "이미지 파일 업로드가 환경변수 IMAGE_UPLOAD_ENABLED=false로 비활성화되어 있습니다.",
      missing_env: [],
    };
  }

  const backend = normalizeBackend();
  if (backend === "vercel_blob") {
    const missing = missingEnv(["BLOB_READ_WRITE_TOKEN"]);
    return {
      enabled: missing.length === 0,
      backend,
      message:
        missing.length === 0
          ? "Vercel Blob 이미지 업로드를 사용할 수 있습니다."
          : IMAGE_UPLOAD_DISABLED_MESSAGE,
      missing_env: missing,
    };
  }

  if (backend === "s3" || backend === "cloudflare_r2" || backend === "r2") {
    const missing = missingEnv([
      "S3_BUCKET",
      "S3_REGION",
      "S3_ACCESS_KEY_ID",
      "S3_SECRET_ACCESS_KEY",
    ]);
    if (process.env.S3_ENDPOINT_URL && !process.env.PUBLIC_ASSET_BASE_URL) {
      missing.push("PUBLIC_ASSET_BASE_URL");
    }
    return {
      enabled: missing.length === 0,
      backend,
      message:
        missing.length === 0
          ? "S3-compatible 이미지 업로드를 사용할 수 있습니다."
          : IMAGE_UPLOAD_DISABLED_MESSAGE,
      missing_env: missing,
    };
  }

  return {
    enabled: false,
    backend,
    message: IMAGE_UPLOAD_DISABLED_MESSAGE,
    missing_env: ["BLOB_READ_WRITE_TOKEN"],
  };
}

function encodeObjectKey(key: string) {
  return key.split("/").map(encodeURIComponent).join("/");
}

function hashHex(data: Buffer | string) {
  return createHash("sha256").update(data).digest("hex");
}

function hmac(key: Buffer | string, data: string) {
  return createHmac("sha256", key).update(data).digest();
}

function hmacHex(key: Buffer | string, data: string) {
  return createHmac("sha256", key).update(data).digest("hex");
}

function amzDate(date: Date) {
  return date.toISOString().replace(/[:-]|\.\d{3}/g, "");
}

function s3ObjectUrl(key: string) {
  const bucket = process.env.S3_BUCKET?.trim();
  const region = process.env.S3_REGION?.trim();
  const endpoint = process.env.S3_ENDPOINT_URL?.trim().replace(/\/+$/, "");
  if (!bucket || !region) {
    throw new Error("S3 storage is not configured.");
  }
  const encodedKey = encodeObjectKey(key);
  if (endpoint) {
    return `${endpoint}/${bucket}/${encodedKey}`;
  }
  return `https://${bucket}.s3.${region}.amazonaws.com/${encodedKey}`;
}

function publicAssetUrl(key: string) {
  const publicBaseUrl = process.env.PUBLIC_ASSET_BASE_URL?.trim().replace(/\/+$/, "");
  if (publicBaseUrl) {
    return `${publicBaseUrl}/${encodeObjectKey(key)}`;
  }
  if (!process.env.S3_ENDPOINT_URL) {
    return s3ObjectUrl(key);
  }
  throw new Error("PUBLIC_ASSET_BASE_URL is required for S3-compatible custom endpoints.");
}

async function putS3CompatibleObject(key: string, file: File) {
  const accessKeyId = process.env.S3_ACCESS_KEY_ID?.trim();
  const secretAccessKey = process.env.S3_SECRET_ACCESS_KEY?.trim();
  const region = process.env.S3_REGION?.trim();
  if (!accessKeyId || !secretAccessKey || !region) {
    throw new Error("S3 storage is not configured.");
  }

  const body = Buffer.from(await file.arrayBuffer());
  const payloadHash = hashHex(body);
  const now = new Date();
  const dateStamp = now.toISOString().slice(0, 10).replace(/-/g, "");
  const requestDate = amzDate(now);
  const objectUrl = new URL(s3ObjectUrl(key));
  const contentType = file.type || "application/octet-stream";
  const canonicalUri = objectUrl.pathname;
  const canonicalHeaders = [
    `content-type:${contentType}`,
    `host:${objectUrl.host}`,
    `x-amz-content-sha256:${payloadHash}`,
    `x-amz-date:${requestDate}`,
    "",
  ].join("\n");
  const signedHeaders = "content-type;host;x-amz-content-sha256;x-amz-date";
  const canonicalRequest = [
    "PUT",
    canonicalUri,
    "",
    canonicalHeaders,
    signedHeaders,
    payloadHash,
  ].join("\n");
  const credentialScope = `${dateStamp}/${region}/s3/aws4_request`;
  const stringToSign = [
    "AWS4-HMAC-SHA256",
    requestDate,
    credentialScope,
    hashHex(canonicalRequest),
  ].join("\n");
  const signingKey = hmac(
    hmac(hmac(hmac(`AWS4${secretAccessKey}`, dateStamp), region), "s3"),
    "aws4_request",
  );
  const signature = hmacHex(signingKey, stringToSign);

  const response = await fetch(objectUrl, {
    method: "PUT",
    headers: {
      Authorization: `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`,
      "Content-Type": contentType,
      "x-amz-content-sha256": payloadHash,
      "x-amz-date": requestDate,
    },
    body,
  });

  if (!response.ok) {
    throw new Error("S3-compatible image upload failed.");
  }

  return publicAssetUrl(key);
}

export async function GET() {
  return NextResponse.json(getStorageStatus());
}

export async function POST(request: Request) {
  const storageStatus = getStorageStatus();
  if (!storageStatus.enabled) {
    return NextResponse.json(
      { detail: storageStatus.message, storage: storageStatus },
      { status: 503 },
    );
  }

  const formData = await request.formData();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ detail: "file field is required." }, { status: 400 });
  }

  if (!file.type.startsWith("image/")) {
    return NextResponse.json({ detail: "이미지 파일만 업로드할 수 있습니다." }, { status: 400 });
  }

  if (file.size > MAX_IMAGE_SIZE_BYTES) {
    return NextResponse.json({ detail: "이미지 용량은 3MB 이하만 가능합니다." }, { status: 400 });
  }

  try {
    const safeName = sanitizeFileName(file.name);
    const objectKey = `product-images/${Date.now()}-${safeName}`;
    if (storageStatus.backend === "s3" || storageStatus.backend === "cloudflare_r2" || storageStatus.backend === "r2") {
      const url = await putS3CompatibleObject(objectKey, file);
      return NextResponse.json({ url });
    }

    const blob = await put(objectKey, file, { access: "public" });
    return NextResponse.json({ url: blob.url });
  } catch {
    return NextResponse.json(
      { detail: "이미지 업로드에 실패했습니다. storage 설정과 파일 형식을 확인해 주세요." },
      { status: 500 },
    );
  }
}
