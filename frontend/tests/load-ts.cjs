const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");
const ts = require("typescript");

// Run the shipped TypeScript directly without adding a test-only dependency.
function loadTs(relativePath, mocks = {}) {
  const frontend = path.resolve(__dirname, "..");
  const cache = new Map();

  function load(filename) {
    if (cache.has(filename)) return cache.get(filename).exports;
    const loadedModule = { exports: {} };
    cache.set(filename, loadedModule);
    const requireFromFile = createRequire(filename);
    const localRequire = (specifier) => {
      if (Object.hasOwn(mocks, specifier)) return mocks[specifier];
      if (specifier.startsWith("@/") || specifier.startsWith(".")) {
        const base = specifier.startsWith("@/")
          ? path.join(frontend, "src", specifier.slice(2))
          : path.resolve(path.dirname(filename), specifier);
        const source = [base, `${base}.ts`, `${base}.tsx`].find(
          (candidate) => fs.existsSync(candidate) && fs.statSync(candidate).isFile(),
        );
        if (source) return load(source);
      }
      return requireFromFile(specifier);
    };
    const { outputText } = ts.transpileModule(fs.readFileSync(filename, "utf8"), {
      fileName: filename,
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2022,
        jsx: ts.JsxEmit.ReactJSX,
      },
    });
    new Function("require", "module", "exports", outputText)(localRequire, loadedModule, loadedModule.exports);
    return loadedModule.exports;
  }

  return load(path.resolve(frontend, relativePath));
}

module.exports = { loadTs };
