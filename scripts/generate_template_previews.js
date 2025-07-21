const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const puppeteer = require('puppeteer');

const THEMES = [
  { id: 'professional', npm: 'jsonresume-theme-classy' },
  { id: 'modern', npm: 'jsonresume-theme-elegant' },
  { id: 'creative', npm: 'jsonresume-theme-kendall' },
  { id: 'minimalist', npm: 'jsonresume-theme-cora' },
  { id: 'executive', npm: 'jsonresume-theme-elegant' }
];

const SAMPLE_JSON = path.resolve(__dirname, 'sample_resume_data.json');
const OUTPUT_DIR = path.resolve(__dirname, 'static/templates');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function renderAndScreenshot(theme) {
  const htmlFile = path.resolve(__dirname, `${theme.id}_preview.html`);
  const pngFile = path.resolve(OUTPUT_DIR, `${theme.id}_preview.png`);

  // 1. Render HTML using resume-cli
  try {
    execSync(`resume export ${htmlFile} --theme ${theme.npm} --resume ${SAMPLE_JSON} --format html`, { stdio: 'inherit' });
  } catch (err) {
    console.error(`Failed to render HTML for theme ${theme.id}`);
    return;
  }

  // 2. Screenshot with Puppeteer
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('file://' + htmlFile, { waitUntil: 'networkidle0' });
  await page.setViewport({ width: 1200, height: 1600 });
  await page.screenshot({ path: pngFile, fullPage: true });
  await browser.close();

  // 3. Clean up HTML file
  fs.unlinkSync(htmlFile);
  console.log(`✅ Saved preview: ${pngFile}`);
}

(async () => {
  for (const theme of THEMES) {
    await renderAndScreenshot(theme);
  }
  console.log('All previews generated!');
})(); 