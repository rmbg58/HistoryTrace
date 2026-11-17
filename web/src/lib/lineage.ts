/** 沿革领域逻辑(纯函数,vitest 覆盖)。 */

export interface Dynasty {
  key: string;
  label: string;
  earliest: number;
  latest: number;
  note?: string;
}

export interface LineageEntry {
  claimId: string;
  earliest: number;
  latest: number;
  precision: string;
  name: string;
  role: string;
  note: string;
  confidence: "G1" | "G2" | "G3" | "G4";
  status: string;
  attestations: Attestation[];
}

export interface Attestation {
  source: string;
  sourceId: string;
  edition: string;
  locus: string;
  quote: string | null;
  certainty: number | null;
  tier: string;
}

/** 返回覆盖 year 的条目(区间含端点)。 */
export function entryForYear(entries: LineageEntry[], year: number): LineageEntry | undefined {
  return entries.find((e) => year >= e.earliest && year <= e.latest);
}

/** 返回覆盖 year 的朝代;无匹配返回 undefined。 */
export function dynastyForYear(dynasties: Dynasty[], year: number): Dynasty | undefined {
  return dynasties.find((d) => year >= d.earliest && year <= d.latest);
}

/** 置信等级 → 印章样式与悬停说明(G 视觉见 05-DESIGN)。 */
export function confidenceMeta(conf: LineageEntry["confidence"]): { label: string; cls: string; title: string } {
  switch (conf) {
    case "G4":
      return { label: "考", cls: "seal-g4", title: "G4 已验证:多源一致并经人工裁决" };
    case "G3":
      return { label: "源", cls: "seal-g3", title: "G3 多源一致:≥2 独立来源,未对影印本" };
    case "G2":
      return { label: "单", cls: "seal-g2", title: "G2 单源或存在未决异文" };
    case "G1":
      return { label: "疑", cls: "seal-g1", title: "G1 存疑:仅机器/理校来源,默认不渲染" };
  }
}

/** 是否含"京师/都/行在"类角色(影响标记渲染)。 */
export function isCapitalRole(role: string): boolean {
  return /京师|东都|行在|都城/.test(role);
}
