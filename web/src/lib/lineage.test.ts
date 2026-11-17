import { describe, expect, it } from "vitest";
import { confidenceMeta, dynastyForYear, entryForYear, isCapitalRole, type LineageEntry } from "./lineage";

const entries: LineageEntry[] = [
  { claimId: "c1", earliest: -202, latest: 8, precision: "year", name: "长安", role: "京兆尹治所", note: "", confidence: "G3", status: "machine-checked", attestations: [] },
  { claimId: "c2", earliest: 618, latest: 907, precision: "year", name: "长安", role: "京兆府·京师", note: "", confidence: "G3", status: "machine-checked", attestations: [] },
  { claimId: "c3", earliest: 960, latest: 1127, precision: "year", name: "京兆府", role: "永兴军路治", note: "", confidence: "G2", status: "machine-checked", attestations: [] },
];

const dynasties = [
  { key: "han", label: "汉", earliest: -202, latest: 8 },
  { key: "tang", label: "唐", earliest: 618, latest: 907 },
  { key: "song", label: "宋", earliest: 960, latest: 1127 },
];

describe("entryForYear", () => {
  it("返回覆盖年份的条目", () => {
    expect(entryForYear(entries, 0)?.name).toBe("长安");
    expect(entryForYear(entries, 700)?.role).toBe("京兆府·京师");
    expect(entryForYear(entries, 1000)?.name).toBe("京兆府");
  });

  it("端点含边界", () => {
    expect(entryForYear(entries, -202)?.claimId).toBe("c1");
    expect(entryForYear(entries, 8)?.claimId).toBe("c1");
    expect(entryForYear(entries, 907)?.claimId).toBe("c2");
  });

  it("间隙返回 undefined", () => {
    expect(entryForYear(entries, 500)).toBeUndefined();
  });
});

describe("dynastyForYear", () => {
  it("按年份选朝代", () => {
    expect(dynastyForYear(dynasties, 700)?.label).toBe("唐");
    expect(dynastyForYear(dynasties, 500)).toBeUndefined();
  });
});

describe("confidenceMeta", () => {
  it("四级映射印章", () => {
    expect(confidenceMeta("G4").label).toBe("考");
    expect(confidenceMeta("G3").label).toBe("源");
    expect(confidenceMeta("G2").cls).toBe("seal-g2");
    expect(confidenceMeta("G1").label).toBe("疑");
  });
});

describe("isCapitalRole", () => {
  it("识别京师类角色", () => {
    expect(isCapitalRole("京兆府·京师")).toBe(true);
    expect(isCapitalRole("东京开封府·京师")).toBe(true);
    expect(isCapitalRole("蜀郡治")).toBe(false);
  });
});
