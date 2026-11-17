import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    target: "es2022",
    // 数据产物(ht build 输出)在 public/data,vite 原样拷贝
    assetsInlineLimit: 0,
  },
});
