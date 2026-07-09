# Specific-Isaac64-MP4-Video-Decryption
视频号MP4彩虹表解密（不含下载）

## 硬件要求

### 最低：
600GB以上硬盘空间（不含加密视频和解密视频）

### 推荐：
多核CPU  
32GB或以上RAM  
1TB或以上、PCIe 4.0×4或以上SSD

## 环境要求
NodeJS、Python及相关库  
充裕的时间和耐心、稳定的供电（doge）

## 测试平台
i9-13900H Laptop（14C20T，80W）  
双通道32GB DDR5 4800MHz  
1TB SSD（PCIe4.0×4、NVMe）  
1TB SSD（USB3.0）

## 使用步骤

先下载好加密视频、安装配置好环境。

以下提及的程序、`wasm_video_decode.js`、`wasm_video_decode.wasm`请放置在同一目录。  
WASM文件可以选择自行从官方CDN下载，Evil0ctal/WeChat-Channels-Video-File-Decryption项目中有官方CDN地址。  
以下提及的程序均在代码注释中有使用方法及参数，敬请自行查阅


**使用`rainbow_gen.js`生成按decode_key顺序的彩虹表**  
实测一亿条约17min  
实测20亿条约3h（65W供电+电池取电，末段转240W DC适配器，风扇全速模式）  
实测40亿条约6h20min（全程240W ADP DC适配器，风扇全速模式）  
实测20亿条约3h44min（显示器90W供电，风扇全速模式）  
实测20亿条约4h43min（200W ADP DC适配器，风扇标准模式）  

**（可选）使用`build_index_multi.py`或`build_index_single.py`生成按reserved keystream排序的彩虹表副本，便于二分查找快速解密（注意设置临时文件目录及输出目录，预留足够空间）**

**使用`decrypt.py`解密视频（可通过参数选择仅查找、输入key直接解密、单个/批量解密）**

## AI声明
大量使用AI辅助，包括豆包、Deepseek、千问、Xiaomi Claw等（均为在线版）

## 参考资料：
https://www.aynakeya.com/articles/ctf/wechat-video-encryption-reverse-engineer/  
微信视频号视频加密逆向 | Aynakeya's Blog

https://www.aynakeya.com/articles/ctf/reverse-encryption-algorithm-by-osint-wxisaac64/  
用OSINT的方法逆向加密算法 - WxIsaac64 | Aynakeya's Blog

https://zhuanlan.zhihu.com/p/1962617259756352138  
微信视频号视频文件的加密秘密:一个完整的解密方案 - 知乎

https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption  
Evil0ctal/WeChat-Channels-Video-File-Decryption: 一个可在线运行的微信视频号加密视频解密工具和 API 服务，基于逆向工程分析实现。本项目使用微信官方的 WebAssembly (WASM) 模块来生成 Isaac64 PRNG 密钥流，并通过 XOR 运算完成视频解密。

https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/issues/9  
到底怎么获取DecodeKey · Issue #9 · Evil0ctal/WeChat-Channels-Video-File-Decryption

基于参考情况，本项目使用MIT协议。
