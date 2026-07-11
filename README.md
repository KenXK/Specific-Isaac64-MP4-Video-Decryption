# Specific-Isaac64-MP4-Video-Decryption
视频号MP4彩虹表解密（不含下载）

## 硬件要求

### 最低：
不重新排序彩虹表（遍历全表查找）：150GB以上硬盘空间  
重新排序彩虹表（二分查找彩虹表）：600GB以上硬盘空间  
（均不含加密视频和解密视频）

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
内置1TB SSD（主板插槽PCIe4.0×4、NVMe）  
外置1TB SSD（USB3.0）

## 使用步骤

先下载好加密视频、安装配置好环境。

以下提及的程序、`wasm_video_decode.js`、`wasm_video_decode.wasm`请放置在同一目录。  
WASM文件可以选择自行从官方CDN下载，Evil0ctal/WeChat-Channels-Video-File-Decryption项目中有官方CDN地址。  
以下提及的程序均在代码注释中有使用方法及参数，敬请自行查阅


**使用`rainbow_gen.js`生成按decode_key顺序的彩虹表**  
实测一亿条约17min  
实测20亿条约3h（65W供电+电池取电，末段转240W DC适配器，风扇全速模式）  
实测40亿条约6h20min（全程240W ADP DC适配器，风扇全速模式）  
实测20亿条约3h44min（全程显示器90W供电，风扇全速模式）  
实测20亿条约4h43min（全程200W ADP DC适配器，风扇标准模式）  

**（可选）使用`build_index_multi.py`或`build_index_single.py`生成按reserved keystream排序的彩虹表副本，便于二分查找快速解密（注意设置临时文件目录及输出目录，预留足够空间）**
实测`build_index_single.py`，输入输出路径均为上述外置SSD，临时文件路径为上述内置SSD，全程200W DC适配器，风扇全速模式，约4.5h  
<img width="1100" height="1572" alt="4fb4f4b76d9d11b554a1797520484ae1" src="https://github.com/user-attachments/assets/173daadb-6162-4c98-ae03-498e1e680e25" />


**使用`decrypt.py`解密视频（可通过参数选择仅查找、输入key直接解密、单个/批量解密）**
以下均将彩虹表放在内置SSD上测试  
实测未排序（遍历全表）查表耗时272s，总耗时277s  
<img width="944" height="1805" alt="PixPin_2026-07-12_02-20-19" src="https://github.com/user-attachments/assets/cb9b6cca-89da-48fa-a521-99470cd7c198" />  
实测排序后（二分查找）查表耗时7.5ms和9.7ms（注意单位哟），总耗时约2s  
<img width="978" height="1049" alt="PixPin_2026-07-12_02-29-38" src="https://github.com/user-attachments/assets/7c4909a4-970a-4c58-9c0a-2a64133a866a" />  
未来优化为先尝试某个box_size（首次解密成功后就能知道，短期内应该不变），失败后尝试其他，相信速度还能提高一丢丢

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

基于参考情况，本项目使用MIT协议。项目不包括对既有软件或算法文件的逆向或破解，不包括对任何系统或服务的入侵或破坏。如果侵犯您的权益，请联系我删除。
