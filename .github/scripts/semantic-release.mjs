import fs from "node:fs";
import semanticRelease from "semantic-release";

const result = await semanticRelease();
const outputPath = process.env.GITHUB_OUTPUT;

const outputs = result
  ? {
      new_release: "true",
      version: result.nextRelease.version,
      git_tag: result.nextRelease.gitTag
    }
  : {
      new_release: "false",
      version: "",
      git_tag: ""
    };

if (outputPath) {
  const lines = Object.entries(outputs)
    .map(([key, value]) => `${key}=${value}`)
    .join("\n");
  fs.appendFileSync(outputPath, `${lines}\n`);
}

console.log(JSON.stringify(outputs, null, 2));
