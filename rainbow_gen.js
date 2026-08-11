/**
 * 微信视频号 彩虹表生成工具
 * 输出格式：二进制，每条16字节 = [8字节反转密钥流头][8字节key(大端64位无符号)]
 * 命令: node rainbow_gen.js [起始key] [结束key] [输出目录]
 */
const fs = require('fs');
const path = require('path');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const os = require('os');

// ==================== 配置 ====================
const WORKER_COUNT = os.cpus().length-1;
const BATCH_SIZE = 10000;       // 每批次写入的key数量，控制内存占用
const PROGRESS_INTERVAL = 10000;// 进度打印间隔(ms)
// ==============================================

if (isMainThread) {
    // ========== 主线程：任务分配 + 进度汇总 ==========
    const argStart = process.argv[2] || '0';
    const argEnd   = process.argv[3] || '10000000000';
    const outDir   = process.argv[4] || path.join(__dirname, 'rainbow_output');

    const rangeStart = BigInt(argStart);
    const rangeEnd   = BigInt(argEnd);
    const totalKeys  = rangeEnd - rangeStart;

    // 创建输出目录
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

    const perWorker = totalKeys / BigInt(WORKER_COUNT);

    // 打印启动信息
    console.log('╔═══════════════════════════════════════════════════════╗');
    console.log('║          微信视频号 彩虹表生成工具                    ║');
    console.log('╠═══════════════════════════════════════════════════════╣');
    const cpuModel = (os.cpus()[0]?.model || 'unknown').trim().slice(0, 39);
    console.log(`║  CPU:        ${cpuModel}`.padEnd(56) + '║');
    console.log(`║  线程数:     ${WORKER_COUNT}`.padEnd(56) + '║');
    console.log(`║  范围（左闭右开）:${rangeStart.toString()} ~ ${rangeEnd.toString()}`.padEnd(56) + '║');
    console.log(`║  总量:       ${totalKeys.toString()} 个 key`.padEnd(56) + '║');
    console.log(`║  单条大小:   16 字节 (8字节哈希 + 8字节Key)`.padEnd(56) + '║');
    const totalGB = (Number(totalKeys) * 16 / 1024 / 1024 / 1024).toFixed(2);
    console.log(`║  预计体积:   ${totalGB} GB`.padEnd(56) + '║');
    console.log(`║  输出目录:   ${outDir}`.padEnd(56) + '║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');

    const t0 = Date.now();
    let totalGenerated = 0n;
    const workers = [];

    // 启动Worker
    for (let i = 0; i < WORKER_COUNT; i++) {
        const s = rangeStart + BigInt(i) * perWorker;
        const e = (i === WORKER_COUNT - 1) ? rangeEnd : s + perWorker;
        const outputFile = path.join(outDir, `part_${i.toString().padStart(3, '0')}.bin`);

        const w = new Worker(__filename, {
            workerData: {
                startKey: s.toString(),
                endKey: e.toString(),
                wid: i,
                outputFile: outputFile,
                batchSize: BATCH_SIZE
            }
        });

        w.on('message', msg => {
            if (msg.type === 'progress') {
                totalGenerated += BigInt(msg.delta);
            } else if (msg.type === 'done') {
                console.log(`[Worker ${i}] 完成，共生成 ${msg.count} 条 → ${path.basename(msg.file)}`);
            }
        });
        w.on('error', err => console.error(`Worker ${i} 异常:`, err.message));
        workers.push(w);
    }

    // 定时打印进度
    const timer = setInterval(() => {
        const sec = (Date.now() - t0) / 1000;
        const kps = Math.round(Number(totalGenerated) / sec);
        const remain = Number(totalKeys - totalGenerated);
        const eta = kps > 0 ? remain / kps : 0;
        const percent = (Number(totalGenerated) / Number(totalKeys) * 100).toFixed(2);

        console.log(
            `[${new Date().toLocaleTimeString()}] ` +
            `${totalGenerated.toString().padStart(12, ' ')} / ${totalKeys.toString()} ` +
            `(${percent}%) | ` +
            `${kps.toLocaleString()} keys/sec | ` +
            `剩余 ${Math.floor(eta/3600)}h${Math.floor(eta%3600/60)}m`
        );
    }, PROGRESS_INTERVAL);

    // 等待全部完成
    Promise.all(workers.map(w => new Promise(r => w.on('exit', r)))).then(() => {
        clearInterval(timer);
        const sec = ((Date.now() - t0) / 1000).toFixed(1);
        console.log(`\n═══════════════════════════════════════════════════════`);
        console.log(`全部生成完成！总耗时 ${sec} 秒，输出目录: ${outDir}`);
        console.log(`═══════════════════════════════════════════════════════`);
    });

} else {
    // ========== Worker 线程：生成密钥流 + 写入文件 ==========
    const { startKey, endKey, wid, outputFile, batchSize } = workerData;
    const start = BigInt(startKey);
    const end = BigInt(endKey);
    const dir = __dirname;

    // 读取 WASM 二进制和胶水代码
    const wasmBin = fs.readFileSync(path.join(dir, 'wasm_video_decode.wasm'));
    let jsSrc = fs.readFileSync(path.join(dir, 'wasm_video_decode.js'), 'utf8');

    // 注入 wasmBinary 和路径回调，避免重复加载
    jsSrc = jsSrc.replace(
        "var Module = typeof Module !== 'undefined' ? Module : {};",
        `var Module = typeof Module !== 'undefined' ? Module : {};\n` +
        `Module.wasmBinary = new Uint8Array(${JSON.stringify(Array.from(wasmBin))});\n` +
        `Module.locateFile = function(p){ return ${JSON.stringify(dir)}+'/'+p; };`
    );

    // 环境模拟 + 无关函数占位（与原bruteforce保持一致）
    const header = [
        `var VTS_WASM_URL=${JSON.stringify(path.join(dir,'wasm_video_decode.wasm'))};`,
        'var MAX_HEAP_SIZE=33554432;',
        'var wasm_ffmpeg_error_report=function(){};',
        'var wasm_ffmpeg_fwrite=function(){return 0;};',
        'var wasm_ffmpeg_fsize=function(){};',
        'var wasm_ffmpeg_fseek=function(){return 0;};',
        'var wasm_ffmpeg_fclose=function(){};',
        'var wasm_ffmpeg_fopen=async function(){return 0;};',
        'var wasm_ffmpeg_fread=async function(){return 0;};',
    ].join('\n');

    // 写入临时加载文件
    const tmpFile = path.join(dir, `_rainbow_w${wid}.js`);
    fs.writeFileSync(tmpFile, header + '\n' + jsSrc + '\nmodule.exports=Module;\n');

    // 模拟浏览器全局环境
    global.self = global;
    global.location = { href: 'file://' + dir + '/' };
    if (!global.document) global.document = { addEventListener(){}, createElement(){ return {} } };

    // 缓冲区与文件句柄
    const RECORD_SIZE = 16;
    const buf = Buffer.alloc(batchSize * RECORD_SIZE);
    let bufOffset = 0;
    let totalCount = 0;
    const fd = fs.openSync(outputFile, 'w');

    // 密钥流生成回调：提取反转后的前8字节
    global.wasm_isaac_generate = function(ptr, size) {
        const HEAP = global._mod.HEAPU8;
        const lastByte = ptr + size - 1; // 原密钥流最后一个字节 = 反转后第0字节

        // 写入8字节反转密钥流头
        for (let i = 0; i < 8; i++) {
            buf[bufOffset + i] = HEAP[lastByte - i];
        }
        // 写入8字节key（大端64位无符号整数）
        buf.writeBigUInt64BE(BigInt(global._currKeyNum), bufOffset + 8);

        bufOffset += RECORD_SIZE;
        totalCount++;

        // 缓冲区满，写入文件
        if (bufOffset >= buf.length) {
            fs.writeSync(fd, buf, 0, bufOffset);
            bufOffset = 0;
            parentPort.postMessage({ type: 'progress', delta: batchSize });
        }
    };

    // 加载WASM模块
    const Module = require(tmpFile);
    global._mod = Module;

    function runLoop() {
        if (!Module.WxIsaac64) {
            setTimeout(runLoop, 100);
            return;
        }

        for (let k = start; k < end; k++) {
            const keyStr = k.toString().padStart(10, '0');
            global._currKeyNum = k.toString();

            const isaac = new Module.WxIsaac64(keyStr);
            isaac.generate(131072);
            isaac.delete();
        }

        // 写入缓冲区剩余数据
        if (bufOffset > 0) {
            fs.writeSync(fd, buf, 0, bufOffset);
        }
        fs.closeSync(fd);

        // 清理临时文件
        try { fs.unlinkSync(tmpFile); } catch(e) {}

        parentPort.postMessage({
            type: 'done',
            count: totalCount,
            file: outputFile
        });
        process.exit(0);
    }

    setTimeout(runLoop, 500);
    setTimeout(() => { console.error(`Worker ${wid}: 初始化超时`); process.exit(1); }, 30000);
}