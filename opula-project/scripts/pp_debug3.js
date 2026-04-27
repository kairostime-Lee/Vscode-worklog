/**
 * 调试3：用百分比定位，画十字线找坐标系
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\_debug_selection3.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

// 简单脚本：获取文档尺寸，在中心和四角画标记
const PS_SCRIPT = `
var doc = app.activeDocument;
var w = doc.width.as("px");
var h = doc.height.as("px");

// 报告尺寸
app.echoToOE("SIZE:" + w + "x" + h);

var layer = doc.artLayers.add();
layer.name = "Debug";

var red = new SolidColor();
red.rgb.red = 255; red.rgb.green = 50; red.rgb.blue = 50;

// 画中心十字
var cx = Math.round(w/2);
var cy = Math.round(h/2);

// 水平线穿过中心
doc.selection.select([
    [0, cy-2], [w, cy-2], [w, cy+2], [0, cy+2]
], SelectionType.REPLACE, 0, false);
doc.selection.fill(red, ColorBlendMode.NORMAL, 100);

// 垂直线穿过中心
doc.selection.select([
    [cx-2, 0], [cx+2, 0], [cx+2, h], [cx-2, h]
], SelectionType.REPLACE, 0, false);
doc.selection.fill(red, ColorBlendMode.NORMAL, 100);

// 25% 位置画额外的线
var qx = Math.round(w/4);
var qy = Math.round(h/4);

var green = new SolidColor();
green.rgb.red = 50; green.rgb.green = 255; green.rgb.blue = 50;

// 25% 水平
doc.selection.select([
    [0, qy-1], [w, qy-1], [w, qy+1], [0, qy+1]
], SelectionType.REPLACE, 0, false);
doc.selection.fill(green, ColorBlendMode.NORMAL, 100);

// 25% 垂直
doc.selection.select([
    [qx-1, 0], [qx+1, 0], [qx+1, h], [qx-1, h]
], SelectionType.REPLACE, 0, false);
doc.selection.fill(green, ColorBlendMode.NORMAL, 100);

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
    await page.goto('file:///' + HOST_HTML.replace(/\\/g, '/'), { waitUntil: 'domcontentloaded', timeout: 15000 });
    await waitForTitle(page, 'PP_READY', 60000);

    // 捕获 echo 消息
    const echoMessages = [];
    // 修改 host 页面来捕获 echo
    await page.evaluate(() => {
        window._echoMsgs = [];
        const origHandler = window.onmessage;
        window.addEventListener("message", function(e) {
            if (typeof e.data === "string" && e.data.startsWith("SIZE:")) {
                window._echoMsgs.push(e.data);
                document.title = "PP_ECHO_" + e.data;
            }
        });
    });

    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((a) => window.sendFile(new Uint8Array(a).buffer), [...imageBuffer]);
    await waitForTitle(page, 'PP_CMD_DONE', 30000);
    console.log('Image loaded');

    await page.evaluate((s) => window.runScript(s), PS_SCRIPT);
    await new Promise(r => setTimeout(r, 8000));

    // 获取 echo 消息
    const msgs = await page.evaluate(() => window._echoMsgs);
    console.log('Echo messages:', msgs);

    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) { fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData)); console.log('Saved'); }
    await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
