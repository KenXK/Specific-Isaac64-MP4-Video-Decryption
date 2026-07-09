#!/usr/bin/env node
/**
 * keystream_gen.js - 从 decode_key 生成 Isaac64 密钥流
 *
 * 用法: node keystream_gen.js <decode_key>
 * 输出: 131072 字节的 reversed keystream 到 stdout (binary)
 *
 * 依赖: wasm_video_decode.wasm 和 wasm_video_decode.js 在同目录
 */

const fs = require('fs');
const path = require('path');

const dir = __dirname;
const KEYSTREAM_SIZE = 131072;

// 读取 WASM 二进制
const wasmBin = fs.readFileSync(path.join(dir, 'wasm_video_decode.wasm'));

// 读取并修补 JS
let jsSrc = fs.readFileSync(path.join(dir, 'wasm_video_decode.js'), 'utf8');
jsSrc = jsSrc.replace(
    "var Module = typeof Module !== 'undefined' ? Module : {};",
    `var Module = typeof Module !== 'undefined' ? Module : {};\n` +
    `Module.wasmBinary = new Uint8Array(${JSON.stringify(Array.from(wasmBin))});\n` +
    `Module.locateFile = function(p){ return ${JSON.stringify(dir)}+'/'+p; };`
);

// emscripten 全局变量
const header = [
    `var VTS_WASM_URL=${JSON.stringify(path.join(dir, 'wasm_video_decode.wasm'))};`,
    'var MAX_HEAP_SIZE=33554432;',
    'var wasm_ffmpeg_error_report=function(){};',
    'var wasm_ffmpeg_fwrite=function(){return 0;};',
    'var wasm_ffmpeg_fsize=function(){};',
    'var wasm_ffmpeg_fseek=function(){return 0;};',
    'var wasm_ffmpeg_fclose=function(){};',
    'var wasm_ffmpeg_fopen=async function(){return 0;};',
    'var wasm_ffmpeg_fread=async function(){return 0;};',
].join('\n');

const tmp = path.join(dir, `_keystream_tmp.js`);
fs.writeFileSync(tmp, header + '\n' + jsSrc + '\nmodule.exports=Module;\n');

// 模拟浏览器全局对象
global.self = global;
global.location = { href: 'file://' + dir + '/' };
if (!global.document) global.document = { addEventListener(){}, createElement(){ return {} } };

// 密钥流回调
let done = false;
global.wasm_isaac_generate = function(ptr, size) {
    if (done) return;
    done = true;
    const H = global._mod.HEAPU8;
    const ks = Buffer.alloc(size);
    // 读取原始密钥流并反转
    for (let i = 0; i < size; i++) {
        ks[i] = H[ptr + size - 1 - i];
    }
    // Use writeSync to ensure all data is flushed before exit
    fs.writeSync(1, ks);
    try { fs.unlinkSync(tmp); } catch(e) {}
    process.exit(0);
};

// 加载模块
const M = require(tmp);
global._mod = M;

const decodeKey = process.argv[2];
if (!decodeKey) {
    console.error('Usage: node keystream_gen.js <decode_key>');
    process.exit(1);
}

function waitReady() {
    if (M.WxIsaac64) {
        const d = new M.WxIsaac64(decodeKey);
        d.generate(KEYSTREAM_SIZE);
        d.delete();
        // 如果回调没触发，等待一下
        setTimeout(() => {
            if (!done) {
                console.error('Error: keystream generation failed');
                try { fs.unlinkSync(tmp); } catch(e) {}
                process.exit(1);
            }
        }, 5000);
    } else {
        setTimeout(waitReady, 100);
    }
}

setTimeout(waitReady, 500);
setTimeout(() => {
    if (!done) {
        console.error('Error: WASM module load timeout');
        try { fs.unlinkSync(tmp); } catch(e) {}
        process.exit(1);
    }
}, 15000);
