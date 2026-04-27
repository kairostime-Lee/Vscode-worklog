/**
 * 画网格定位灯头精确坐标
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\_debug_grid.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

const PS_SCRIPT = `
try {
    var doc = app.activeDocument;
    var w = doc.width.as("px");
    var h = doc.height.as("px");

    var layer = doc.artLayers.add();
    layer.name = "Grid";
    layer.opacity = 70;

    var red = new SolidColor();
    red.rgb.red = 255; red.rgb.green = 0; red.rgb.blue = 0;

    // 每 200px 画水平线（只在左半部分，y标注）
    for (var y = 200; y < h; y += 200) {
        doc.selection.select([
            [0, y], [w/2, y], [w/2, y+3], [0, y+3]
        ], SelectionType.REPLACE, 0, false);
        doc.selection.fill(red, ColorBlendMode.NORMAL, 100);
    }

    var green = new SolidColor();
    green.rgb.red = 0; green.rgb.green = 200; green.rgb.blue = 0;

    // 每 200px 画垂直线（只在上半部分，x标注）
    for (var x = 200; x < w; x += 200) {
        doc.selection.select([
            [x, 0], [x+3, 0], [x+3, h/2], [x, h/2]
        ], SelectionType.REPLACE, 0, false);
        doc.selection.fill(green, ColorBlendMode.NORMAL, 100);
    }

    doc.selection.deselect();
    doc.flatten();
    app.echoToOE("SCRIPT_DONE");
} catch(e) {
    app.echoToOE("ERR:" + e.message);
}
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
    await page.goto('file:///' + HOST_HTML.replace(/\\/g, '/'), { waitUntil: 'domcontentloaded', timeout: 15000 });
    await waitForTitle(page, 'PP_READY', 60000);

    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((a) => window.sendFile(new Uint8Array(a).buffer), [...imageBuffer]);
    await waitForTitle(page, 'PP_CMD_DONE', 30000);

    await page.evaluate((s) => window.runScript(s), PS_SCRIPT);
    await new Promise(r => setTimeout(r, 8000));

    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) { fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData)); console.log('OK'); }
    await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
