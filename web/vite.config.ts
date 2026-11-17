import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    target: "es2022",
    // 数据产物(ht build 输出)在 public/data,vite 原样拷贝
    assetsInlineLimit: 0,
    rollupOptions: {
      output: {
        // OT-004:maplibre 独立 vendor chunk,业务代码更新时不重下大依赖
        manualChunks: {
          maplibre: ["maplibre-gl"],
        },
      },
    },
  },
});
