import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import prettier from "eslint-config-prettier";
import boundariesPlugin from "eslint-plugin-boundaries";
import importPlugin from "eslint-plugin-import";
import prettierPlugin from "eslint-plugin-prettier";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

const eslintConfig = defineConfig([
  // JS / config ファイルはプロジェクト参照なしで解析
  {
    files: ["**/*.{js,cjs,mjs}"],
    languageOptions: {
      parserOptions: {
        project: null,
      },
    },
  },
  ...nextVitals,
  ...nextTs,
  // TypeScript + 追加ルール
  ...tseslint.config(
    ...tseslint.configs.recommendedTypeChecked,
    {
      files: ["**/*.{ts,tsx}"],
      plugins: {
        import: importPlugin,
        prettier: prettierPlugin,
        boundaries: boundariesPlugin,
      },
      settings: {
        "import/resolver": {
          typescript: true,
          node: true,
        },
        "boundaries/elements": [
          { type: "shared", pattern: "src/shared/**/*" },
          { type: "features", pattern: "src/features/**/*" },
          { type: "app", pattern: "src/app/**/*" },
        ],
        "boundaries/ignore": ["**/*.test.*", "**/*.spec.*"],
      },
      languageOptions: {
        parserOptions: {
          project: "./tsconfig.json",
          tsconfigRootDir: import.meta.dirname,
        },
      },
      rules: {
        "@typescript-eslint/no-misused-promises": [
          "error",
          { checksVoidReturn: false },
        ],
        // フォーマット
        "prettier/prettier": "error",
        "react/react-in-jsx-scope": "off",
        // import順序
        "import/order": [
          "error",
          {
            groups: ["builtin", "external", "internal", "parent", "sibling", "index"],
            "newlines-between": "always",
            alphabetize: { order: "asc", caseInsensitive: true },
            pathGroups: [
              { pattern: "react**", group: "builtin", position: "before" },
              { pattern: "@/shared/**", group: "internal", position: "before" },
              { pattern: "@/features/**", group: "internal", position: "after" },
            ],
            pathGroupsExcludedImportTypes: ["react"],
          },
        ],
        // Features-based アーキテクチャの依存制約
        "boundaries/element-types": [
          "error",
          {
            default: "disallow",
            rules: [
              {
                from: "features",
                allow: ["shared", "features"],
                message: "Features can import from shared or other features.",
              },
              {
                from: "app",
                allow: ["features", "shared"],
                message: "App can import from features and shared.",
              },
              {
                from: "shared",
                allow: ["shared"],
                message: "Shared can only import from shared. No features imports allowed.",
              },
            ],
          },
        ],
      },
    }
  ),
  prettier,
  globalIgnores([
    "node_modules/**",
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "eslint.config.mjs",
    "postcss.config.mjs",
  ]),
]);

export default eslintConfig;
