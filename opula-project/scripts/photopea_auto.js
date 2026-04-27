/**
 * Photopea 自动化 v2 - 用 iframe 方式通信
 * 先用小图测试流程是否通畅
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
// 先用原图（小一点的）测试
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\o3j4xn_photopea_fixed.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

// Photoshop 脚本（坐标基于原图 2752x1536）
const PS_SCRIPT = `
var doc = app.activeDocument;

// 1. 多边形选中左灯灯头区域
doc.selection.select([
    [130, 240],
    [700, 240],
    [730, 350],
    [700, 460],
    [130, 390]
], SelectionType.REPLACE, 10, false);

// 2. 羽化选区
doc.selection.feather(12);

// 3. 复制到新图层
doc.selection.copy();
doc.paste();
var headLayer = doc.activeLayer;
headLayer.name = "LampHead";

// 4. 旋转 -15 度（顺时针），以右中为锚点
headLayer.rotate(-15, AnchorPosition.MIDDLERIGHT);

// 5. 向右平移让灯头更收拢
headLayer.translate(25, 8);

// 6. 合并所有图层
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
    throw new Error(`Timeout waiting for title: ${prefix}`);
}

async function main() {
    console.log('Starting Chrome...');
    const browser = await puppeteer.launch({
        executablePath: CHROME_PATH,
        headless: 'new',
        protocolTimeout: 120000,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1920,1080',
            '--proxy-server=http://192.168.10.1:7893',
        ],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.authenticate({ username: 'Clash', password: '5EpPEQ3n' });

    // 加载本地 HTML（包含 Photopea iframe）
    console.log('Loading host page with Photopea iframe...');
    await page.goto(`file:///${HOST_HTML.replace(/\\/g, '/')}`, {
        waitUntil: 'domcontentloaded',
        timeout: 15000
    });

    // 等待 Photopea 初始化（通过 title 变化检测）
    console.log('Waiting for Photopea to initialize...');
    try {
        await waitForTitle(page, 'PP_READY', 60000);
        console.log('Photopea ready!');
    } catch (e) {
        console.log('Timeout waiting for Photopea. Taking debug screenshot...');
        await page.screenshot({ path: 'D:\\ClaudeWork\\海报输出\\_debug_pp2.png' });
        const title = await page.title();
        console.log('Current title:', title);
        await browser.close();
        return;
    }

    // 发送图片文件
    console.log('Sending image to Photopea...');
    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    console.log(`Image size: ${(imageBuffer.length / 1024 / 1024).toFixed(1)} MB`);

    await page.evaluate((imgArr) => {
        const uint8 = new Uint8Array(imgArr);
        window.sendFile(uint8.buffer);
    }, [...imageBuffer]);

    // 等待文件加载
    console.log('Waiting for image to load in Photopea...');
    try {
        await waitForTitle(page, 'PP_CMD_DONE', 30000);
        console.log('Image loaded!');
    } catch (e) {
        console.log('Waiting extra time for large image...');
        await new Promise(r => setTimeout(r, 10000));
    }

    // 执行 Photoshop 脚本
    console.log('Running Photoshop script...');
    await page.evaluate((script) => {
        window.runScript(script);
    }, PS_SCRIPT);

    // 等待脚本完成
    try {
        await waitForTitle(page, 'PP_SCRIPT_DONE', 30000);
        console.log('Script done!');
    } catch (e) {
        console.log('Script may still be running, waiting more...');
        await new Promise(r => setTimeout(r, 10000));
    }

    // 导出 PNG
    console.log('Exporting PNG...');
    await page.evaluate(() => {
        window.runScript('app.activeDocument.saveToOE("png");');
    });

    // 等待文件返回
    try {
        await waitForTitle(page, 'PP_FILE', 30000);
        console.log('File received!');
    } catch (e) {
        console.log('Waiting for export...');
        await new Promise(r => setTimeout(r, 10000));
    }

    // 获取文件数据
    const fileData = await page.evaluate(() => {
        return window.getLastFile();
    });

    if (fileData) {
        const buffer = Buffer.from(fileData);
        fs.writeFileSync(OUTPUT_PATH, buffer);
        console.log(`Saved: ${OUTPUT_PATH} (${(buffer.length / 1024 / 1024).toFixed(1)} MB)`);
    } else {
        console.log('ERROR: No file received');
        await page.screenshot({ path: 'D:\\ClaudeWork\\海报输出\\_debug_pp_final.png' });
        console.log('Debug screenshot saved');
    }

    await browser.close();
    console.log('All done!');
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
