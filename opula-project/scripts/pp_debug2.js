/**
 * 调试2：画多个候选区域，找到正确的灯头位置
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\_debug_selection2.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

// 画多个矩形区域来定位
const PS_SCRIPT = `
var doc = app.activeDocument;
var w = doc.width.as("px");
var h = doc.height.as("px");

var layer = doc.artLayers.add();
layer.name = "Debug";

var red = new SolidColor();
red.rgb.red = 255; red.rgb.green = 0; red.rgb.blue = 0;

var green = new SolidColor();
green.rgb.red = 0; green.rgb.green = 255; green.rgb.blue = 0;

var blue = new SolidColor();
blue.rgb.red = 0; blue.rgb.green = 0; blue.rgb.blue = 255;

// 画网格参考线（每200px）
// 水平线
for (var y = 200; y < h; y += 200) {
    doc.selection.select([[0, y], [50, y], [50, y+2], [0, y+2]]);
    doc.selection.fill(red);
}
// 垂直线
for (var x = 200; x < w; x += 200) {
    doc.selection.select([[x, 0], [x+2, 0], [x+2, 50], [x, 50]]);
    doc.selection.fill(red);
}

// 候选区域 A（灯头可能的位置）: 更靠右下
doc.selection.select([[250, 350], [850, 350], [850, 550], [250, 550]]);
doc.selection.stroke(red, 4, StrokeLocation.CENTER);

// 候选区域 B: 再往下
doc.selection.select([[300, 450], [900, 450], [900, 650], [300, 650]]);
doc.selection.stroke(green, 4, StrokeLocation.CENTER);

// 候选区域 C: 更大范围
doc.selection.select([[200, 300], [950, 300], [950, 700], [200, 700]]);
doc.selection.stroke(blue, 4, StrokeLocation.CENTER);

doc.selection.deselect();
doc.flatten();
app.echoToOE("SCRIPT_DONE");
`;

async function waitForTitle(page, prefix, timeout = 30000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        const title = await page.title();
        if (title.startsWith(prefix)) return title;
        await new Promise(r => setTimeout(r, 500));
    }
    throw new Error(`Timeout: ${prefix}`);
}

async function main() {
    const browser = await puppeteer.launch({
        executablePath: CHROME_PATH, headless: 'new', protocolTimeout: 120000,
        args: ['--no-sandbox', '--proxy-server=http://192.168.10.1:7893'],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.authenticate({ username: 'Clash', password: '5EpPEQ3n' });
    await page.goto('file:///' + HOST_HTML.replace(/\\\\/g, '/'), { waitUntil: 'domcontentloaded', timeout: 15000 });
    await waitForTitle(page, 'PP_READY', 60000);

    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((a) => window.sendFile(new Uint8Array(a).buffer), [...imageBuffer]);
    await waitForTitle(page, 'PP_CMD_DONE', 30000);

    await page.evaluate((s) => window.runScript(s), PS_SCRIPT);
    try { await waitForTitle(page, 'PP_SCRIPT_DONE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) { fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData)); console.log('OK'); }
    await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
