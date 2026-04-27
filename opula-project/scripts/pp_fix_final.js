/**
 * 最终修改：用精确坐标旋转左灯灯头
 * 灯头区域：x=180~820, y=380~580
 * 旋转锚点（折臂连接处）：约 (800, 500)
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\o3j4xn_photopea_fixed.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

// Photoshop脚本：选中灯头 → 复制到新层 → 旋转 → 融合
const PS_SCRIPT = `
try {
    var doc = app.activeDocument;

    // 1. 多边形选区覆盖左灯灯头（精确坐标）
    doc.selection.select([
        [160, 390],    // 灯头左端顶部
        [820, 340],    // 灯头右端顶部（折臂连接处上方）
        [840, 520],    // 折臂连接处下方
        [800, 590],    // 灯头右端底部
        [160, 570]     // 灯头左端底部
    ], SelectionType.REPLACE, 0, false);

    // 2. 羽化边缘
    doc.selection.feather(new UnitValue(15, "px"));

    // 3. 复制选区到新图层
    doc.selection.copy();
    doc.paste();
    var headLayer = doc.activeLayer;
    headLayer.name = "LampHead";

    // 4. 旋转 -18 度（顺时针），让灯头更水平
    // 以右中为锚点（折臂连接处）
    headLayer.rotate(-18, AnchorPosition.MIDDLERIGHT);

    // 5. 向右上平移，让灯头更靠近灯臂（更收拢）
    headLayer.translate(new UnitValue(35, "px"), new UnitValue(-10, "px"));

    // 6. 合并图层
    doc.flatten();

    app.echoToOE("SCRIPT_DONE");
} catch(e) {
    app.echoToOE("ERROR:" + e.message);
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
    console.log('Photopea ready');

    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((a) => window.sendFile(new Uint8Array(a).buffer), [...imageBuffer]);
    await waitForTitle(page, 'PP_CMD_DONE', 30000);
    console.log('Image loaded');

    await page.evaluate((s) => window.runScript(s), PS_SCRIPT);
    await new Promise(r => setTimeout(r, 10000));
    console.log('Script executed');

    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 8000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) {
        fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData));
        console.log('Saved: ' + OUTPUT_PATH);
    } else { console.log('No file'); }
    await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
