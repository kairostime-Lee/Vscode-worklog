/**
 * 用 Puppeteer + Photopea 修改 o3j4xn 左灯灯头
 *
 * 流程：
 * 1. 启动 Chrome，打开 Photopea
 * 2. 加载增强后的图片
 * 3. 用 Photoshop 脚本选中左灯灯头 → 旋转 → 融合
 * 4. 导出保存
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\o3j4xn_enhanced_2x.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\o3j4xn_photopea_fixed.png';

// 将本地图片转为 data URI
function imageToDataURI(filePath) {
    const data = fs.readFileSync(filePath);
    const base64 = data.toString('base64');
    const ext = path.extname(filePath).slice(1).toLowerCase();
    const mime = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
    return `data:${mime};base64,${base64}`;
}

// Photoshop 脚本：选中左灯灯头区域 → 复制到新图层 → 旋转 → 融合
// 坐标基于 2x 增强图 (5504x3072)，原图坐标 x2
const PS_SCRIPT = `
// ======= 修改左灯灯头 =======
var doc = app.activeDocument;
var w = doc.width.as("px");
var h = doc.height.as("px");

// 1. 选中左灯灯头区域（多边形选区）
// 原图坐标 x2: 灯头水平条区域
doc.selection.select([
    [260, 480],    // 灯头左端上边
    [1400, 480],   // 灯头右端上边（靠近折臂连接处）
    [1460, 700],   // 折臂连接处下方
    [1400, 920],   // 灯头右端下边
    [260, 780],    // 灯头左端下边
], SelectionType.REPLACE, 20, false);

// 2. 羽化选区
doc.selection.feather(15);

// 3. 复制到新图层
doc.selection.copy();
doc.paste();
var headLayer = doc.activeLayer;
headLayer.name = "LampHead_Left";

// 4. 以折臂连接点为中心旋转（顺时针12度）
// 连接点大约在 (1350, 750)
headLayer.rotate(-12, AnchorPosition.MIDDLERIGHT);

// 5. 微调位置（向右推一点，让灯头看起来更收拢）
headLayer.translate(40, 10);

// 6. 合并图层
doc.flatten();

// 7. 通知完成
app.echoToOE("DONE");
`;

async function main() {
    console.log('Starting Chrome...');

    const browser = await puppeteer.launch({
        executablePath: CHROME_PATH,
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1920,1080',
            // 代理设置
            '--proxy-server=http://192.168.10.1:7893',
        ],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    // 代理认证
    await page.authenticate({
        username: 'Clash',
        password: '5EpPEQ3n'
    });

    console.log('Loading Photopea...');

    // 构建 Photopea URL（带图片和脚本）
    const dataURI = imageToDataURI(IMAGE_PATH);
    console.log(`Image data URI length: ${dataURI.length}`);

    // 由于 data URI 太大，先加载 Photopea，再通过 postMessage 发送图片
    await page.goto('https://www.photopea.com', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    console.log('Photopea loaded, waiting for initialization...');

    // 等待 Photopea 发送 "done" 消息
    await page.evaluate(() => {
        return new Promise((resolve) => {
            window.addEventListener("message", function handler(e) {
                if (e.data === "done") {
                    window.removeEventListener("message", handler);
                    resolve();
                }
            });
        });
    });

    console.log('Photopea ready, sending image...');

    // 通过 postMessage 发送图片文件（ArrayBuffer）
    const imageBuffer = fs.readFileSync(IMAGE_PATH);
    await page.evaluate((imgData) => {
        const uint8 = new Uint8Array(imgData);
        const pp = document.querySelector('iframe');
        if (pp) {
            pp.contentWindow.postMessage(uint8.buffer, "*");
        } else {
            // Photopea 可能不在 iframe 中（直接访问时）
            // 直接用全局 app 对象
            window.postMessage(uint8.buffer, "*");
        }
    }, [...imageBuffer]);

    console.log('Image sent, waiting for load...');

    // 等待图片加载完成
    await new Promise(r => setTimeout(r, 5000));

    console.log('Running Photoshop script...');

    // 发送 Photoshop 脚本
    let scriptDone = false;

    // 监听 echoToOE 返回
    page.on('console', msg => {
        console.log('Console:', msg.text());
    });

    // 通过 postMessage 发送脚本
    await page.evaluate((script) => {
        window._ppResult = null;
        window._ppFiles = [];

        window.addEventListener("message", function(e) {
            if (e.data === "done") {
                console.log("PP: done signal received");
            } else if (e.data instanceof ArrayBuffer) {
                window._ppFiles.push(e.data);
                console.log("PP: received file, size=" + e.data.byteLength);
            } else if (typeof e.data === "string") {
                console.log("PP: " + e.data);
                if (e.data === "DONE") {
                    window._ppResult = "DONE";
                }
            }
        });

        // Photopea 直接访问时，脚本通过 postMessage 发送到自身
        window.postMessage(script, "*");
    }, PS_SCRIPT);

    // 等待脚本执行
    console.log('Waiting for script execution...');
    await new Promise(r => setTimeout(r, 8000));

    // 导出为 PNG
    console.log('Exporting PNG...');
    await page.evaluate(() => {
        window.postMessage('app.activeDocument.saveToOE("png");', "*");
    });

    // 等待导出
    await new Promise(r => setTimeout(r, 5000));

    // 获取导出的文件
    const fileData = await page.evaluate(() => {
        if (window._ppFiles.length > 0) {
            const buf = window._ppFiles[window._ppFiles.length - 1];
            return Array.from(new Uint8Array(buf));
        }
        return null;
    });

    if (fileData) {
        const buffer = Buffer.from(fileData);
        fs.writeFileSync(OUTPUT_PATH, buffer);
        console.log(`Saved: ${OUTPUT_PATH} (${(buffer.length / 1024 / 1024).toFixed(1)} MB)`);
    } else {
        console.log('ERROR: No output file received from Photopea');

        // 调试：截图看当前状态
        await page.screenshot({ path: path.join('D:\\ClaudeWork\\海报输出', '_debug_photopea.png') });
        console.log('Debug screenshot saved');
    }

    await browser.close();
    console.log('Done!');
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
