/**
 * 调试4：用最简单的方式测试 Photopea 脚本是否在执行
 * 并用 UnitValue 指定坐标
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const IMAGE_PATH = 'D:\\ClaudeWork\\海报输出\\Gemini_Generated_Image_o3j4xno3j4xno3j4.png';
const OUTPUT_PATH = 'D:\\ClaudeWork\\海报输出\\_debug4.png';
const HOST_HTML = 'D:\\ClaudeWork\\scripts\\photopea_host.html';

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
    console.log('Image loaded');

    // 分步执行脚本，每步检查结果
    // Step 1: 获取文档信息
    await page.evaluate(() => {
        window.runScript('app.echoToOE("DOC:" + app.activeDocument.width.as("px") + "x" + app.activeDocument.height.as("px") + " layers:" + app.activeDocument.layers.length);');
    });
    await new Promise(r => setTimeout(r, 3000));
    let status = await page.evaluate(() => document.getElementById("status").textContent);
    console.log('Step1:', status);

    // Step 2: 简单操作 - 反转图像颜色（明显的变化来确认脚本在执行）
    await page.evaluate(() => {
        window.runScript('app.activeDocument.activeLayer.invert(); app.echoToOE("INVERTED");');
    });
    await new Promise(r => setTimeout(r, 3000));
    status = await page.evaluate(() => document.getElementById("status").textContent);
    console.log('Step2:', status);

    // Step 3: 撤销反转
    await page.evaluate(() => {
        window.runScript('app.activeDocument.activeLayer.invert(); app.echoToOE("RESTORED");');
    });
    await new Promise(r => setTimeout(r, 3000));
    status = await page.evaluate(() => document.getElementById("status").textContent);
    console.log('Step3:', status);

    // Step 4: 尝试画一个选区并填充
    await page.evaluate(() => {
        window.runScript(`
            try {
                var doc = app.activeDocument;
                // 全选然后缩小选区来测试
                doc.selection.selectAll();
                doc.selection.contract(new UnitValue(500, "px"));
                var c = new SolidColor();
                c.rgb.red = 255; c.rgb.green = 0; c.rgb.blue = 0;
                doc.selection.fill(c);
                doc.selection.deselect();
                app.echoToOE("FILLED_RED");
            } catch(e) {
                app.echoToOE("ERROR:" + e.message);
            }
        `);
    });
    await new Promise(r => setTimeout(r, 5000));
    status = await page.evaluate(() => document.getElementById("status").textContent);
    console.log('Step4:', status);

    // 导出
    await page.evaluate(() => window.runScript('app.activeDocument.saveToOE("png");'));
    try { await waitForTitle(page, 'PP_FILE', 20000); } catch(e) { await new Promise(r => setTimeout(r, 5000)); }

    const fileData = await page.evaluate(() => window.getLastFile());
    if (fileData) { fs.writeFileSync(OUTPUT_PATH, Buffer.from(fileData)); console.log('Saved'); }
    else { console.log('No file'); }
    await browser.close();
}
main().catch(e => { console.error(e.message); process.exit(1); });
