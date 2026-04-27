/**
 * 调试：在图上画出选区，确认灯头区域
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\_debug_selection.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

// 画选区轮廓 + 标记旋转锚点
const PS_SCRIPT = `
var doc = app.activeDocument;

// 在新图层上画选区轮廓
var layer = doc.artLayers.add();
layer.name = "SelectionDebug";

// 左灯灯头选区（需要调整的区域）
// 灯头水平条 + 顶部折臂连接处
doc.selection.select([
    [100, 260],     // 灯头左端顶部
    [640, 240],     // 灯头右端顶部（靠近折臂）
    [700, 340],     // 折臂连接处
    [640, 440],     // 灯头右端底部
    [100, 400]      // 灯头左端底部
], SelectionType.REPLACE, 0, false);

// 描边选区（红色，3px）
var strokeColor = new SolidColor();
strokeColor.rgb.red = 255;
strokeColor.rgb.green = 0;
strokeColor.rgb.blue = 0;
doc.selection.stroke(strokeColor, 3, StrokeLocation.CENTER, ColorBlendMode.NORMAL, 100);

// 标记旋转锚点（绿色圆点）
// 锚点在折臂连接处约 (680, 370)
doc.selection.select([
    [670, 360], [690, 360], [690, 380], [670, 380]
], SelectionType.REPLACE, 0, false);
var greenColor = new SolidColor();
greenColor.rgb.red = 0;
greenColor.rgb.green = 255;
greenColor.rgb.blue = 0;
doc.selection.fill(greenColor, ColorBlendMode.NORMAL, 100);

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
        executablePath: CHROME_PATH,
        headless: 'new',
        protocolTimeout: 120000,
        args: ['--no-sandbox', '--proxy-server=http://192.168.10.1:7893'],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.authenticate({ username: 'Clash', password: '5EpPEQ3n' });

    await page.goto(`file:///${HOST_HTML.replace(/\\/g, '/')}`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    console.log('Waiting for Photopea...');
    await waitForTitle(page, 'PP_READY', 60000);
    console.log('Ready!');

    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((imgArr) => {
        window.sendFile(new Uint8Array(imgArr).buffer);
    }, [...imageBuffer]);
    await waitForTitle(page, 'PP_CMD_DONE', 30000);
    console.log('Image loaded');

    await page.evaluate((s) => window.runScript(s), PS_SCRIPT);
    try { await waitForTitle(page, 'PP_SCRIPT_DONE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }
    console.log('Script done');

    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) {
        fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData));
        console.log('Saved debug image');
    } else {
        console.log('No file received');
    }
    await browser.close();
}

main().catch(e => { console.error(e.message); process.exit(1); });
