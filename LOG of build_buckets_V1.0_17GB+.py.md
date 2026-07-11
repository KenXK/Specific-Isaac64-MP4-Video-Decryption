```text
╔═══════════════════════════════════════════════════════════╗
║      彩虹表桶化排序构建器 V1.0（三级流水线）             ║
╠═══════════════════════════════════════════════════════════╣
║  彩虹表:   E:\豆包彩虹表                                         ║
║  输入:     76 个文件 (149.0 GB)                               ║
║  输出:     D:\Ken\桶化排序彩虹表                                  ║
║  桶:       65536 (prefix[4:6])                            ║
║  排序进程: 18                                                ║
║  读缓冲:   64MB/chunk                                       ║
║  桶缓冲:   240KB/bucket                                     ║
╠═══════════════════════════════════════════════════════════╣
║  [Reader] → queue → [Distributor(numpy)] → flush_q → [Writer] ║
║    全速SSD读     向量化分桶(不做I/O)      LRU句柄池刷盘       ║
╚═══════════════════════════════════════════════════════════╝

确认开始？(y/N): y

02:54:55 [MainThread] === Phase 1: 流水线散列 ===
02:54:55 [Reader] 读取: part_000.bin (1.57 GB)
02:55:02 [Reader] 读取: part_001.bin (1.57 GB)
02:55:06 [Distributor] 分发: 17 chunks, 71M 条, numpy 352ms/ch, copy 219ms/ch, flushQ 0
02:55:11 [Reader] 读取: part_002.bin (1.57 GB)
02:55:16 [Distributor] 分发: 45 chunks, 185M 条, numpy 311ms/ch, copy 135ms/ch, flushQ 0
02:55:21 [Reader] 读取: part_003.bin (1.57 GB)
02:55:26 [Distributor] 分发: 72 chunks, 294M 条, numpy 305ms/ch, copy 117ms/ch, flushQ 0
02:55:31 [Reader] 读取: part_004.bin (1.57 GB)
02:55:36 [Distributor] 分发: 98 chunks, 400M 条, numpy 304ms/ch, copy 110ms/ch, flushQ 0
02:55:41 [Reader] 读取: part_005.bin (1.57 GB)
02:55:47 [Distributor] 分发: 125 chunks, 509M 条, numpy 302ms/ch, copy 105ms/ch, flushQ 0
02:55:51 [Reader] 读取: part_006.bin (1.57 GB)
02:55:57 [Distributor] 分发: 151 chunks, 614M 条, numpy 301ms/ch, copy 102ms/ch, flushQ 0
02:56:01 [Reader] 读取: part_007.bin (1.57 GB)
02:56:07 [Distributor] 分发: 177 chunks, 720M 条, numpy 302ms/ch, copy 100ms/ch, flushQ 0
02:56:12 [Reader] 读取: part_008.bin (1.57 GB)
02:56:17 [Distributor] 分发: 203 chunks, 825M 条, numpy 302ms/ch, copy 99ms/ch, flushQ 0
02:56:22 [Reader] 读取: part_009.bin (1.57 GB)
02:56:27 [Distributor] 分发: 228 chunks, 926M 条, numpy 303ms/ch, copy 98ms/ch, flushQ 0
02:56:33 [Writer] 写入: 1 flush, 0.0 GB, 0 MB/s, FD 1/8100, open 1 close 0
02:56:33 [Reader] 读取: part_010.bin (1.57 GB)
02:56:38 [Distributor] 分发: 246 chunks, 998M 条, numpy 306ms/ch, copy 111ms/ch, flushQ 2048
02:56:43 [Writer] 写入: 16352 flush, 3.7 GB, 36 MB/s, FD 8100/8100, open 16352 close 8252
02:56:49 [Distributor] 分发: 248 chunks, 1006M 条, numpy 306ms/ch, copy 151ms/ch, flushQ 2048
02:56:53 [Writer] 写入: 38211 flush, 8.8 GB, 76 MB/s, FD 8100/8100, open 38211 close 30111
02:57:01 [Distributor] 分发: 250 chunks, 1014M 条, numpy 306ms/ch, copy 194ms/ch, flushQ 2048
02:57:03 [Writer] 写入: 57659 flush, 13.2 GB, 106 MB/s, FD 8100/8100, open 57659 close 49559
02:57:13 [Writer] 写入: 63226 flush, 14.5 GB, 107 MB/s, FD 8100/8100, open 63226 close 55126
02:57:21 [Distributor] 分发: 254 chunks, 1031M 条, numpy 307ms/ch, copy 265ms/ch, flushQ 2048
02:57:24 [Writer] 写入: 63520 flush, 14.6 GB, 101 MB/s, FD 8100/8100, open 63520 close 55420
02:57:31 [Reader] 读取: part_011.bin (1.57 GB)
02:57:31 [Distributor] 分发: 269 chunks, 1090M 条, numpy 305ms/ch, copy 272ms/ch, flushQ 0
02:57:41 [Reader] 读取: part_012.bin (1.57 GB)
02:57:42 [Distributor] 分发: 295 chunks, 1196M 条, numpy 304ms/ch, copy 258ms/ch, flushQ 0
02:57:51 [Reader] 读取: part_013.bin (1.57 GB)
02:57:52 [Distributor] 分发: 320 chunks, 1297M 条, numpy 303ms/ch, copy 247ms/ch, flushQ 0
02:58:02 [Reader] 读取: part_014.bin (1.57 GB)
02:58:02 [Distributor] 分发: 346 chunks, 1402M 条, numpy 302ms/ch, copy 236ms/ch, flushQ 0
02:58:12 [Distributor] 分发: 371 chunks, 1503M 条, numpy 302ms/ch, copy 227ms/ch, flushQ 0
02:58:12 [Reader] 读取: part_015.bin (1.57 GB)
02:58:22 [Distributor] 分发: 395 chunks, 1600M 条, numpy 303ms/ch, copy 221ms/ch, flushQ 0
02:58:23 [Reader] 读取: part_016.bin (1.57 GB)
02:58:33 [Distributor] 分发: 418 chunks, 1693M 条, numpy 303ms/ch, copy 216ms/ch, flushQ 0
02:58:35 [Reader] 读取: part_017.bin (1.57 GB)
02:58:43 [Distributor] 分发: 441 chunks, 1789M 条, numpy 303ms/ch, copy 213ms/ch, flushQ 0
02:58:47 [Reader] 读取: part_018.bin (1.57 GB)
02:58:53 [Distributor] 分发: 463 chunks, 1878M 条, numpy 303ms/ch, copy 210ms/ch, flushQ 0
02:58:59 [Reader] 读取: part_000.bin (1.57 GB)
02:59:04 [Distributor] 分发: 484 chunks, 1962M 条, numpy 303ms/ch, copy 208ms/ch, flushQ 0
02:59:05 [Writer] 写入: 65537 flush, 15.0 GB, 62 MB/s, FD 8100/8100, open 65537 close 57437
02:59:14 [Distributor] 分发: 494 chunks, 2000M 条, numpy 304ms/ch, copy 219ms/ch, flushQ 2048
02:59:15 [Writer] 写入: 69644 flush, 16.0 GB, 63 MB/s, FD 8100/8100, open 69644 close 61544
02:59:25 [Writer] 写入: 76776 flush, 17.6 GB, 67 MB/s, FD 8100/8100, open 76776 close 68676
02:59:32 [Distributor] 分发: 496 chunks, 2008M 条, numpy 304ms/ch, copy 252ms/ch, flushQ 2048
02:59:35 [Writer] 写入: 83059 flush, 19.0 GB, 70 MB/s, FD 8100/8100, open 83059 close 74959
02:59:44 [Distributor] 分发: 497 chunks, 2013M 条, numpy 304ms/ch, copy 276ms/ch, flushQ 2048
02:59:45 [Writer] 写入: 90143 flush, 20.7 GB, 73 MB/s, FD 8100/8100, open 90143 close 82043
02:59:55 [Writer] 写入: 97280 flush, 22.3 GB, 76 MB/s, FD 8100/8100, open 97280 close 89180
02:59:58 [Distributor] 分发: 498 chunks, 2017M 条, numpy 304ms/ch, copy 302ms/ch, flushQ 2048
03:00:05 [Writer] 写入: 104469 flush, 24.0 GB, 79 MB/s, FD 8100/8100, open 104469 close 96369
03:00:10 [Distributor] 分发: 499 chunks, 2021M 条, numpy 304ms/ch, copy 325ms/ch, flushQ 2048
03:00:15 [Writer] 写入: 111772 flush, 25.6 GB, 82 MB/s, FD 8100/8100, open 111772 close 103672
03:00:20 [Distributor] 分发: 500 chunks, 2025M 条, numpy 304ms/ch, copy 345ms/ch, flushQ 2048
03:00:25 [Writer] 写入: 119043 flush, 27.3 GB, 85 MB/s, FD 8100/8100, open 119043 close 110943
03:00:29 [Reader] 读取: part_001.bin (1.57 GB)
03:00:35 [Writer] 写入: 124664 flush, 28.6 GB, 86 MB/s, FD 8100/8100, open 124664 close 116564
03:00:36 [Distributor] 分发: 502 chunks, 2034M 条, numpy 304ms/ch, copy 373ms/ch, flushQ 2048
03:00:45 [Writer] 写入: 128441 flush, 29.5 GB, 86 MB/s, FD 8100/8100, open 128441 close 120341
03:00:55 [Writer] 写入: 128723 flush, 29.5 GB, 84 MB/s, FD 8100/8100, open 128723 close 120623
03:00:56 [Distributor] 分发: 505 chunks, 2046M 条, numpy 304ms/ch, copy 410ms/ch, flushQ 2048
03:01:05 [Writer] 写入: 128851 flush, 29.6 GB, 82 MB/s, FD 8100/8100, open 128851 close 120751
03:01:15 [Writer] 写入: 128937 flush, 29.6 GB, 80 MB/s, FD 8100/8100, open 128937 close 120837
03:01:15 [Distributor] 分发: 506 chunks, 2050M 条, numpy 304ms/ch, copy 446ms/ch, flushQ 2048
03:01:25 [Writer] 写入: 129838 flush, 29.8 GB, 78 MB/s, FD 8100/8100, open 129838 close 121738
03:01:26 [Distributor] 分发: 516 chunks, 2092M 条, numpy 304ms/ch, copy 452ms/ch, flushQ 807
03:01:31 [Reader] 读取: part_002.bin (1.57 GB)
03:01:36 [Distributor] 分发: 540 chunks, 2189M 条, numpy 304ms/ch, copy 437ms/ch, flushQ 0
03:01:42 [Reader] 读取: part_003.bin (1.57 GB)
03:01:46 [Distributor] 分发: 563 chunks, 2282M 条, numpy 303ms/ch, copy 426ms/ch, flushQ 0
03:01:53 [Reader] 读取: part_004.bin (1.57 GB)
03:01:56 [Distributor] 分发: 587 chunks, 2379M 条, numpy 302ms/ch, copy 414ms/ch, flushQ 0
03:02:04 [Reader] 读取: part_005.bin (1.57 GB)
03:02:07 [Distributor] 分发: 613 chunks, 2484M 条, numpy 302ms/ch, copy 401ms/ch, flushQ 0
03:02:14 [Reader] 读取: part_006.bin (1.57 GB)
03:02:17 [Distributor] 分发: 638 chunks, 2585M 条, numpy 301ms/ch, copy 390ms/ch, flushQ 0
03:02:25 [Reader] 读取: part_007.bin (1.57 GB)
03:02:27 [Distributor] 分发: 661 chunks, 2678M 条, numpy 301ms/ch, copy 381ms/ch, flushQ 0
03:02:37 [Distributor] 分发: 682 chunks, 2762M 条, numpy 302ms/ch, copy 374ms/ch, flushQ 0
03:02:38 [Reader] 读取: part_008.bin (1.57 GB)
03:02:47 [Distributor] 分发: 704 chunks, 2850M 条, numpy 302ms/ch, copy 368ms/ch, flushQ 0
03:02:50 [Reader] 读取: part_009.bin (1.57 GB)
03:02:57 [Distributor] 分发: 725 chunks, 2939M 条, numpy 302ms/ch, copy 362ms/ch, flushQ 0
03:03:01 [Writer] 写入: 131073 flush, 30.1 GB, 63 MB/s, FD 8100/8100, open 131073 close 122973
03:03:03 [Reader] 读取: part_010.bin (1.57 GB)
03:03:09 [Distributor] 分发: 741 chunks, 3002M 条, numpy 302ms/ch, copy 364ms/ch, flushQ 2048
03:03:11 [Writer] 写入: 133664 flush, 30.7 GB, 63 MB/s, FD 8100/8100, open 133664 close 125564
03:03:21 [Writer] 写入: 139657 flush, 32.0 GB, 65 MB/s, FD 8100/8100, open 139657 close 131557
03:03:21 [Distributor] 分发: 743 chunks, 3010M 条, numpy 302ms/ch, copy 378ms/ch, flushQ 2048
03:03:31 [Writer] 写入: 144996 flush, 33.3 GB, 66 MB/s, FD 8100/8100, open 144996 close 136896
03:03:32 [Distributor] 分发: 744 chunks, 3014M 条, numpy 302ms/ch, copy 391ms/ch, flushQ 2048
03:03:41 [Writer] 写入: 150651 flush, 34.6 GB, 67 MB/s, FD 8100/8100, open 150651 close 142551
03:03:43 [Distributor] 分发: 745 chunks, 3019M 条, numpy 302ms/ch, copy 405ms/ch, flushQ 2048
03:03:51 [Writer] 写入: 156664 flush, 35.9 GB, 69 MB/s, FD 8100/8100, open 156664 close 148564
03:03:55 [Distributor] 分发: 746 chunks, 3023M 条, numpy 302ms/ch, copy 421ms/ch, flushQ 2048
03:04:01 [Writer] 写入: 162643 flush, 37.3 GB, 70 MB/s, FD 8100/8100, open 162643 close 154543
03:04:08 [Distributor] 分发: 747 chunks, 3027M 条, numpy 302ms/ch, copy 437ms/ch, flushQ 2048
03:04:11 [Writer] 写入: 168717 flush, 38.7 GB, 71 MB/s, FD 8100/8100, open 168717 close 160617
03:04:20 [Distributor] 分发: 748 chunks, 3031M 条, numpy 302ms/ch, copy 452ms/ch, flushQ 2048
03:04:21 [Writer] 写入: 174795 flush, 40.1 GB, 73 MB/s, FD 8100/8100, open 174795 close 166695
03:04:31 [Writer] 写入: 180444 flush, 41.4 GB, 74 MB/s, FD 8100/8100, open 180444 close 172344
03:04:31 [Distributor] 分发: 749 chunks, 3035M 条, numpy 302ms/ch, copy 466ms/ch, flushQ 2048
03:04:41 [Writer] 写入: 186018 flush, 42.7 GB, 75 MB/s, FD 8100/8100, open 186018 close 177918
03:04:46 [Distributor] 分发: 751 chunks, 3044M 条, numpy 303ms/ch, copy 483ms/ch, flushQ 2048
03:04:51 [Writer] 写入: 191853 flush, 44.0 GB, 76 MB/s, FD 8100/8100, open 191853 close 183753
03:04:57 [Distributor] 分发: 755 chunks, 3057M 条, numpy 303ms/ch, copy 494ms/ch, flushQ 2048
03:05:01 [Writer] 写入: 193997 flush, 44.5 GB, 75 MB/s, FD 8100/8100, open 193997 close 185897
03:05:09 [Distributor] 分发: 756 chunks, 3061M 条, numpy 303ms/ch, copy 509ms/ch, flushQ 2048
03:05:11 [Writer] 写入: 194291 flush, 44.6 GB, 74 MB/s, FD 8100/8100, open 194291 close 186191
03:05:21 [Writer] 写入: 194352 flush, 44.6 GB, 73 MB/s, FD 8100/8100, open 194352 close 186252
03:05:31 [Writer] 写入: 194441 flush, 44.6 GB, 72 MB/s, FD 8100/8100, open 194441 close 186341
03:05:31 [Distributor] 分发: 757 chunks, 3065M 条, numpy 303ms/ch, copy 536ms/ch, flushQ 2048
03:05:41 [Writer] 写入: 194567 flush, 44.6 GB, 71 MB/s, FD 8100/8100, open 194567 close 186467
03:05:44 [Distributor] 分发: 759 chunks, 3074M 条, numpy 303ms/ch, copy 551ms/ch, flushQ 1969
03:05:46 [Reader] 读取: part_011.bin (1.57 GB)
03:05:51 [Writer] 写入: 196605 flush, 45.1 GB, 70 MB/s, FD 8100/8100, open 196605 close 188505
03:05:54 [Distributor] 分发: 782 chunks, 3166M 条, numpy 302ms/ch, copy 539ms/ch, flushQ 0
03:05:56 [Reader] 读取: part_012.bin (1.57 GB)
03:06:04 [Distributor] 分发: 805 chunks, 3263M 条, numpy 302ms/ch, copy 528ms/ch, flushQ 0
03:06:08 [Reader] 读取: part_013.bin (1.57 GB)
03:06:14 [Distributor] 分发: 825 chunks, 3343M 条, numpy 302ms/ch, copy 521ms/ch, flushQ 0
03:06:22 [Reader] 读取: part_014.bin (1.57 GB)
03:06:25 [Distributor] 分发: 847 chunks, 3431M 条, numpy 301ms/ch, copy 512ms/ch, flushQ 0
03:06:32 [Reader] 读取: part_015.bin (1.57 GB)
03:06:35 [Distributor] 分发: 872 chunks, 3532M 条, numpy 301ms/ch, copy 501ms/ch, flushQ 0
03:06:43 [Reader] 读取: part_016.bin (1.57 GB)
03:06:45 [Distributor] 分发: 896 chunks, 3629M 条, numpy 301ms/ch, copy 491ms/ch, flushQ 0
03:06:55 [Reader] 读取: part_017.bin (1.57 GB)
03:06:55 [Distributor] 分发: 918 chunks, 3718M 条, numpy 301ms/ch, copy 483ms/ch, flushQ 0
03:07:05 [Distributor] 分发: 939 chunks, 3802M 条, numpy 301ms/ch, copy 476ms/ch, flushQ 0
03:07:07 [Reader] 读取: part_018.bin (1.57 GB)
03:07:16 [Distributor] 分发: 960 chunks, 3890M 条, numpy 301ms/ch, copy 469ms/ch, flushQ 0
03:07:20 [Reader] 读取: part_000.bin (3.14 GB)
03:07:25 [Writer] 写入: 196609 flush, 45.1 GB, 62 MB/s, FD 8100/8100, open 196609 close 188509
03:07:26 [Distributor] 分发: 981 chunks, 3974M 条, numpy 301ms/ch, copy 463ms/ch, flushQ 2
03:07:35 [Writer] 写入: 197744 flush, 45.4 GB, 61 MB/s, FD 8100/8100, open 197744 close 189644
03:07:38 [Distributor] 分发: 990 chunks, 4008M 条, numpy 302ms/ch, copy 468ms/ch, flushQ 2048
03:07:45 [Writer] 写入: 202265 flush, 46.4 GB, 62 MB/s, FD 8100/8100, open 202265 close 194165
03:07:51 [Distributor] 分发: 992 chunks, 4017M 条, numpy 302ms/ch, copy 480ms/ch, flushQ 2048
03:07:55 [Writer] 写入: 207064 flush, 47.5 GB, 62 MB/s, FD 8100/8100, open 207064 close 198964
03:08:05 [Writer] 写入: 211811 flush, 48.6 GB, 63 MB/s, FD 8100/8100, open 211811 close 203711
03:08:12 [Distributor] 分发: 994 chunks, 4025M 条, numpy 302ms/ch, copy 500ms/ch, flushQ 2048
03:08:15 [Writer] 写入: 216689 flush, 49.7 GB, 64 MB/s, FD 8100/8100, open 216689 close 208589
03:08:25 [Writer] 写入: 221697 flush, 50.8 GB, 64 MB/s, FD 8100/8100, open 221697 close 213597
03:08:25 [Distributor] 分发: 995 chunks, 4029M 条, numpy 302ms/ch, copy 512ms/ch, flushQ 2048
03:08:35 [Writer] 写入: 225874 flush, 51.8 GB, 65 MB/s, FD 8100/8100, open 225874 close 217774
03:08:41 [Distributor] 分发: 996 chunks, 4034M 条, numpy 302ms/ch, copy 526ms/ch, flushQ 2048
03:08:45 [Writer] 写入: 230543 flush, 52.9 GB, 65 MB/s, FD 8100/8100, open 230543 close 222443
03:08:54 [Distributor] 分发: 997 chunks, 4038M 条, numpy 302ms/ch, copy 539ms/ch, flushQ 2048
03:08:55 [Writer] 写入: 235315 flush, 54.0 GB, 66 MB/s, FD 8100/8100, open 235315 close 227215
03:09:05 [Writer] 写入: 240168 flush, 55.1 GB, 66 MB/s, FD 8100/8100, open 240168 close 232068
03:09:07 [Distributor] 分发: 998 chunks, 4042M 条, numpy 302ms/ch, copy 551ms/ch, flushQ 2048
03:09:15 [Writer] 写入: 244888 flush, 56.2 GB, 67 MB/s, FD 8100/8100, open 244888 close 236788
03:09:18 [Distributor] 分发: 999 chunks, 4046M 条, numpy 302ms/ch, copy 561ms/ch, flushQ 2048
03:09:25 [Writer] 写入: 249565 flush, 57.2 GB, 67 MB/s, FD 8100/8100, open 249565 close 241465
03:09:35 [Writer] 写入: 253626 flush, 58.2 GB, 68 MB/s, FD 8100/8100, open 253626 close 245526
03:09:36 [Distributor] 分发: 1001 chunks, 4055M 条, numpy 302ms/ch, copy 577ms/ch, flushQ 2048
03:09:45 [Writer] 写入: 257970 flush, 59.2 GB, 68 MB/s, FD 8100/8100, open 257970 close 249870
03:09:47 [Distributor] 分发: 1004 chunks, 4067M 条, numpy 302ms/ch, copy 586ms/ch, flushQ 2048
03:09:55 [Writer] 写入: 259555 flush, 59.5 GB, 68 MB/s, FD 8100/8100, open 259555 close 251455
03:10:05 [Distributor] 分发: 1006 chunks, 4075M 条, numpy 302ms/ch, copy 602ms/ch, flushQ 2048
03:10:05 [Writer] 写入: 259766 flush, 59.6 GB, 67 MB/s, FD 8100/8100, open 259766 close 251666
03:10:15 [Writer] 写入: 259858 flush, 59.6 GB, 66 MB/s, FD 8100/8100, open 259858 close 251758
03:10:25 [Distributor] 分发: 1007 chunks, 4080M 条, numpy 302ms/ch, copy 621ms/ch, flushQ 2048
03:10:25 [Writer] 写入: 259957 flush, 59.6 GB, 66 MB/s, FD 8100/8100, open 259957 close 251857
03:10:35 [Writer] 写入: 260014 flush, 59.6 GB, 65 MB/s, FD 8100/8100, open 260014 close 251914
03:10:37 [Distributor] 分发: 1008 chunks, 4084M 条, numpy 302ms/ch, copy 632ms/ch, flushQ 2048
03:10:45 [Writer] 写入: 260228 flush, 59.7 GB, 64 MB/s, FD 8100/8100, open 260228 close 252128
03:10:47 [Distributor] 分发: 1015 chunks, 4113M 条, numpy 302ms/ch, copy 635ms/ch, flushQ 1644
03:10:49 [Reader] 读取: part_001.bin (3.14 GB)
03:10:58 [Distributor] 分发: 1040 chunks, 4215M 条, numpy 302ms/ch, copy 623ms/ch, flushQ 0
03:11:08 [Distributor] 分发: 1061 chunks, 4303M 条, numpy 302ms/ch, copy 614ms/ch, flushQ 0
03:11:14 [Reader] 读取: part_002.bin (3.14 GB)
03:11:18 [Distributor] 分发: 1078 chunks, 4374M 条, numpy 302ms/ch, copy 609ms/ch, flushQ 0
03:11:29 [Distributor] 分发: 1095 chunks, 4442M 条, numpy 302ms/ch, copy 605ms/ch, flushQ 0
03:11:39 [Distributor] 分发: 1119 chunks, 4543M 条, numpy 302ms/ch, copy 595ms/ch, flushQ 0
03:11:40 [Reader] 读取: part_003.bin (3.14 GB)
03:11:50 [Distributor] 分发: 1143 chunks, 4640M 条, numpy 302ms/ch, copy 585ms/ch, flushQ 0
03:12:00 [Distributor] 分发: 1164 chunks, 4728M 条, numpy 303ms/ch, copy 577ms/ch, flushQ 0
03:12:04 [Reader] 读取: part_004.bin (3.14 GB)
03:12:10 [Distributor] 分发: 1186 chunks, 4820M 条, numpy 303ms/ch, copy 569ms/ch, flushQ 0
03:12:20 [Distributor] 分发: 1207 chunks, 4905M 条, numpy 303ms/ch, copy 562ms/ch, flushQ 0
03:12:29 [Writer] 写入: 262145 flush, 60.1 GB, 58 MB/s, FD 8100/8100, open 262145 close 254045
03:12:30 [Reader] 读取: part_005.bin (3.14 GB)
03:12:31 [Distributor] 分发: 1226 chunks, 4985M 条, numpy 303ms/ch, copy 557ms/ch, flushQ 31
03:12:39 [Writer] 写入: 263068 flush, 60.3 GB, 58 MB/s, FD 8100/8100, open 263068 close 254968
03:12:42 [Distributor] 分发: 1233 chunks, 5014M 条, numpy 303ms/ch, copy 561ms/ch, flushQ 2048
03:12:49 [Writer] 写入: 267055 flush, 61.3 GB, 58 MB/s, FD 8100/8100, open 267055 close 258955
03:12:55 [Distributor] 分发: 1235 chunks, 5022M 条, numpy 303ms/ch, copy 570ms/ch, flushQ 2048
03:12:59 [Writer] 写入: 271267 flush, 62.2 GB, 59 MB/s, FD 8100/8100, open 271267 close 263167
03:13:09 [Writer] 写入: 275435 flush, 63.2 GB, 59 MB/s, FD 8100/8100, open 275435 close 267335
03:13:15 [Distributor] 分发: 1237 chunks, 5031M 条, numpy 303ms/ch, copy 585ms/ch, flushQ 2048
03:13:19 [Writer] 写入: 279729 flush, 64.2 GB, 60 MB/s, FD 8100/8100, open 279729 close 271629
03:13:28 [Distributor] 分发: 1238 chunks, 5035M 条, numpy 304ms/ch, copy 595ms/ch, flushQ 2048
03:13:29 [Writer] 写入: 283886 flush, 65.1 GB, 60 MB/s, FD 8100/8100, open 283886 close 275786
03:13:39 [Writer] 写入: 287849 flush, 66.0 GB, 60 MB/s, FD 8100/8100, open 287849 close 279749
03:13:43 [Distributor] 分发: 1239 chunks, 5039M 条, numpy 304ms/ch, copy 606ms/ch, flushQ 2048
03:13:49 [Writer] 写入: 292159 flush, 67.0 GB, 61 MB/s, FD 8100/8100, open 292159 close 284059
03:13:57 [Distributor] 分发: 1240 chunks, 5043M 条, numpy 304ms/ch, copy 616ms/ch, flushQ 2048
03:13:59 [Writer] 写入: 296435 flush, 68.0 GB, 61 MB/s, FD 8100/8100, open 296435 close 288335
03:14:09 [Writer] 写入: 300826 flush, 69.0 GB, 61 MB/s, FD 8100/8100, open 300826 close 292726
03:14:10 [Distributor] 分发: 1241 chunks, 5048M 条, numpy 304ms/ch, copy 627ms/ch, flushQ 2048
03:14:19 [Writer] 写入: 305125 flush, 70.0 GB, 62 MB/s, FD 8100/8100, open 305125 close 297025
03:14:23 [Distributor] 分发: 1242 chunks, 5052M 条, numpy 304ms/ch, copy 636ms/ch, flushQ 2048
03:14:29 [Writer] 写入: 309071 flush, 70.9 GB, 62 MB/s, FD 8100/8100, open 309071 close 300971
03:14:37 [Distributor] 分发: 1244 chunks, 5057M 条, numpy 304ms/ch, copy 646ms/ch, flushQ 2048
03:14:39 [Writer] 写入: 312922 flush, 71.8 GB, 62 MB/s, FD 8100/8100, open 312922 close 304822
03:14:49 [Writer] 写入: 317188 flush, 72.7 GB, 62 MB/s, FD 8100/8100, open 317188 close 309088
03:14:53 [Distributor] 分发: 1246 chunks, 5065M 条, numpy 304ms/ch, copy 657ms/ch, flushQ 2048
03:14:59 [Writer] 写入: 321339 flush, 73.7 GB, 63 MB/s, FD 8100/8100, open 321339 close 313239
03:15:05 [Distributor] 分发: 1249 chunks, 5078M 条, numpy 304ms/ch, copy 664ms/ch, flushQ 2048
03:15:09 [Writer] 写入: 324695 flush, 74.5 GB, 63 MB/s, FD 8100/8100, open 324695 close 316595
03:15:17 [Distributor] 分发: 1251 chunks, 5086M 条, numpy 304ms/ch, copy 672ms/ch, flushQ 2048
03:15:19 [Writer] 写入: 325209 flush, 74.6 GB, 62 MB/s, FD 8100/8100, open 325209 close 317109
03:15:29 [Writer] 写入: 325304 flush, 74.6 GB, 62 MB/s, FD 8100/8100, open 325304 close 317204
03:15:36 [Distributor] 分发: 1252 chunks, 5090M 条, numpy 304ms/ch, copy 687ms/ch, flushQ 2048
03:15:39 [Writer] 写入: 325458 flush, 74.6 GB, 61 MB/s, FD 8100/8100, open 325458 close 317358
03:15:49 [Writer] 写入: 325477 flush, 74.7 GB, 61 MB/s, FD 8100/8100, open 325477 close 317377
03:15:54 [Distributor] 分发: 1253 chunks, 5095M 条, numpy 304ms/ch, copy 700ms/ch, flushQ 2048
03:16:00 [Writer] 写入: 325583 flush, 74.7 GB, 60 MB/s, FD 8100/8100, open 325583 close 317483
03:16:07 [Distributor] 分发: 1255 chunks, 5103M 条, numpy 304ms/ch, copy 709ms/ch, flushQ 1990
03:16:10 [Writer] 写入: 325816 flush, 74.7 GB, 60 MB/s, FD 8100/8100, open 325816 close 317716
03:16:17 [Distributor] 分发: 1273 chunks, 5178M 条, numpy 304ms/ch, copy 703ms/ch, flushQ 106
03:16:18 [Reader] 读取: part_006.bin (3.14 GB)
03:16:28 [Distributor] 分发: 1296 chunks, 5272M 条, numpy 304ms/ch, copy 693ms/ch, flushQ 0
03:16:38 [Distributor] 分发: 1313 chunks, 5343M 条, numpy 304ms/ch, copy 688ms/ch, flushQ 0
03:16:47 [Reader] 读取: part_007.bin (3.14 GB)
03:16:49 [Distributor] 分发: 1329 chunks, 5410M 条, numpy 304ms/ch, copy 684ms/ch, flushQ 0
03:16:59 [Distributor] 分发: 1344 chunks, 5473M 条, numpy 304ms/ch, copy 681ms/ch, flushQ 0
03:17:09 [Distributor] 分发: 1365 chunks, 5558M 条, numpy 304ms/ch, copy 673ms/ch, flushQ 0
03:17:15 [Reader] 读取: part_008.bin (3.14 GB)
03:17:20 [Distributor] 分发: 1389 chunks, 5658M 条, numpy 304ms/ch, copy 664ms/ch, flushQ 0
03:17:30 [Distributor] 分发: 1409 chunks, 5739M 条, numpy 304ms/ch, copy 657ms/ch, flushQ 0
03:17:40 [Reader] 读取: part_009.bin (3.14 GB)
03:17:40 [Distributor] 分发: 1430 chunks, 5827M 条, numpy 304ms/ch, copy 650ms/ch, flushQ 0
03:17:51 [Distributor] 分发: 1450 chunks, 5907M 条, numpy 304ms/ch, copy 644ms/ch, flushQ 0
03:17:59 [Writer] 写入: 327681 flush, 75.2 GB, 56 MB/s, FD 8100/8100, open 327681 close 319581
03:18:01 [Distributor] 分发: 1469 chunks, 5987M 条, numpy 305ms/ch, copy 638ms/ch, flushQ 21
03:18:09 [Writer] 写入: 328338 flush, 75.3 GB, 55 MB/s, FD 8100/8100, open 328338 close 320238
03:18:14 [Distributor] 分发: 1477 chunks, 6021M 条, numpy 305ms/ch, copy 642ms/ch, flushQ 2048
03:18:19 [Writer] 写入: 331693 flush, 76.1 GB, 56 MB/s, FD 8100/8100, open 331693 close 323593
03:18:28 [Distributor] 分发: 1479 chunks, 6029M 条, numpy 305ms/ch, copy 650ms/ch, flushQ 2048
03:18:29 [Writer] 写入: 335148 flush, 76.9 GB, 56 MB/s, FD 8100/8100, open 335148 close 327048
03:18:29 [Reader] 读取: part_010.bin (3.14 GB)
03:18:39 [Writer] 写入: 338449 flush, 77.6 GB, 56 MB/s, FD 8100/8100, open 338449 close 330349
03:18:39 [Distributor] 分发: 1480 chunks, 6033M 条, numpy 305ms/ch, copy 657ms/ch, flushQ 2048
03:18:49 [Writer] 写入: 342055 flush, 78.5 GB, 56 MB/s, FD 8100/8100, open 342055 close 333955
03:18:50 [Distributor] 分发: 1481 chunks, 6037M 条, numpy 305ms/ch, copy 664ms/ch, flushQ 2048
03:18:59 [Writer] 写入: 345704 flush, 79.3 GB, 56 MB/s, FD 8100/8100, open 345704 close 337604
03:19:03 [Distributor] 分发: 1482 chunks, 6042M 条, numpy 305ms/ch, copy 672ms/ch, flushQ 2048
03:19:09 [Writer] 写入: 349393 flush, 80.1 GB, 56 MB/s, FD 8100/8100, open 349393 close 341293
03:19:17 [Distributor] 分发: 1483 chunks, 6046M 条, numpy 305ms/ch, copy 680ms/ch, flushQ 2048
03:19:19 [Writer] 写入: 353143 flush, 81.0 GB, 57 MB/s, FD 8100/8100, open 353143 close 345043
03:19:29 [Writer] 写入: 356739 flush, 81.8 GB, 57 MB/s, FD 8100/8100, open 356739 close 348639
03:19:33 [Distributor] 分发: 1484 chunks, 6050M 条, numpy 305ms/ch, copy 690ms/ch, flushQ 2048
03:19:39 [Writer] 写入: 360065 flush, 82.6 GB, 57 MB/s, FD 8100/8100, open 360065 close 351965
03:19:48 [Distributor] 分发: 1485 chunks, 6054M 条, numpy 305ms/ch, copy 700ms/ch, flushQ 2048
03:19:49 [Writer] 写入: 363787 flush, 83.4 GB, 57 MB/s, FD 8100/8100, open 363787 close 355687
03:19:59 [Writer] 写入: 367571 flush, 84.3 GB, 57 MB/s, FD 8100/8100, open 367571 close 359471
03:20:02 [Distributor] 分发: 1486 chunks, 6058M 条, numpy 305ms/ch, copy 708ms/ch, flushQ 2048
03:20:09 [Writer] 写入: 371244 flush, 85.1 GB, 58 MB/s, FD 8100/8100, open 371244 close 363144
03:20:15 [Distributor] 分发: 1487 chunks, 6063M 条, numpy 305ms/ch, copy 716ms/ch, flushQ 2048
03:20:19 [Writer] 写入: 374886 flush, 86.0 GB, 58 MB/s, FD 8100/8100, open 374886 close 366786
03:20:26 [Distributor] 分发: 1488 chunks, 6067M 条, numpy 305ms/ch, copy 723ms/ch, flushQ 2048
03:20:29 [Writer] 写入: 378327 flush, 86.8 GB, 58 MB/s, FD 8100/8100, open 378327 close 370227
03:20:37 [Distributor] 分发: 1489 chunks, 6071M 条, numpy 305ms/ch, copy 730ms/ch, flushQ 2048
03:20:39 [Writer] 写入: 381649 flush, 87.5 GB, 58 MB/s, FD 8100/8100, open 381649 close 373549
03:20:49 [Writer] 写入: 385348 flush, 88.4 GB, 58 MB/s, FD 8100/8100, open 385348 close 377248
03:20:51 [Distributor] 分发: 1491 chunks, 6079M 条, numpy 305ms/ch, copy 738ms/ch, flushQ 2048
03:20:59 [Writer] 写入: 388961 flush, 89.2 GB, 58 MB/s, FD 8100/8100, open 388961 close 380861
03:21:02 [Distributor] 分发: 1494 chunks, 6092M 条, numpy 305ms/ch, copy 743ms/ch, flushQ 2048
03:21:09 [Writer] 写入: 390483 flush, 89.6 GB, 58 MB/s, FD 8100/8100, open 390483 close 382383
03:21:16 [Distributor] 分发: 1496 chunks, 6100M 条, numpy 305ms/ch, copy 751ms/ch, flushQ 2048
03:21:19 [Writer] 写入: 390801 flush, 89.6 GB, 58 MB/s, FD 8100/8100, open 390801 close 382701
03:21:29 [Writer] 写入: 390875 flush, 89.7 GB, 58 MB/s, FD 8100/8100, open 390875 close 382775
03:21:32 [Distributor] 分发: 1497 chunks, 6104M 条, numpy 305ms/ch, copy 761ms/ch, flushQ 2048
03:21:39 [Writer] 写入: 390961 flush, 89.7 GB, 57 MB/s, FD 8100/8100, open 390961 close 382861
03:21:49 [Writer] 写入: 391029 flush, 89.7 GB, 57 MB/s, FD 8100/8100, open 391029 close 382929
03:21:52 [Distributor] 分发: 1499 chunks, 6109M 条, numpy 305ms/ch, copy 773ms/ch, flushQ 2048
03:21:59 [Writer] 写入: 391123 flush, 89.7 GB, 57 MB/s, FD 8100/8100, open 391123 close 383023
03:22:06 [Distributor] 分发: 1501 chunks, 6118M 条, numpy 305ms/ch, copy 781ms/ch, flushQ 1996
03:22:09 [Writer] 写入: 391324 flush, 89.8 GB, 56 MB/s, FD 8100/8100, open 391324 close 383224
03:22:17 [Distributor] 分发: 1518 chunks, 6189M 条, numpy 306ms/ch, copy 775ms/ch, flushQ 329
03:22:22 [Reader] 读取: part_011.bin (3.14 GB)
03:22:27 [Distributor] 分发: 1540 chunks, 6281M 条, numpy 306ms/ch, copy 766ms/ch, flushQ 0
03:22:37 [Distributor] 分发: 1556 chunks, 6345M 条, numpy 306ms/ch, copy 762ms/ch, flushQ 0
03:22:47 [Distributor] 分发: 1571 chunks, 6408M 条, numpy 306ms/ch, copy 758ms/ch, flushQ 0
03:22:55 [Reader] 读取: part_012.bin (3.14 GB)
03:22:58 [Distributor] 分发: 1586 chunks, 6471M 条, numpy 306ms/ch, copy 755ms/ch, flushQ 0
03:23:08 [Distributor] 分发: 1599 chunks, 6526M 条, numpy 306ms/ch, copy 753ms/ch, flushQ 0
03:23:18 [Distributor] 分发: 1621 chunks, 6614M 条, numpy 306ms/ch, copy 745ms/ch, flushQ 0
03:23:23 [Reader] 读取: part_013.bin (3.14 GB)
03:23:29 [Distributor] 分发: 1643 chunks, 6707M 条, numpy 306ms/ch, copy 736ms/ch, flushQ 0
03:23:39 [Distributor] 分发: 1662 chunks, 6783M 条, numpy 306ms/ch, copy 730ms/ch, flushQ 0
03:23:49 [Distributor] 分发: 1682 chunks, 6867M 条, numpy 307ms/ch, copy 724ms/ch, flushQ 0
03:23:50 [Reader] 读取: part_014.bin (3.14 GB)
03:24:00 [Distributor] 分发: 1702 chunks, 6947M 条, numpy 307ms/ch, copy 718ms/ch, flushQ 0
03:24:03 [Writer] 写入: 393217 flush, 90.2 GB, 53 MB/s, FD 8100/8100, open 393217 close 385117
03:24:11 [Distributor] 分发: 1718 chunks, 7014M 条, numpy 307ms/ch, copy 714ms/ch, flushQ 927
03:24:13 [Writer] 写入: 393785 flush, 90.3 GB, 53 MB/s, FD 8100/8100, open 393785 close 385685
03:24:23 [Writer] 写入: 396556 flush, 91.0 GB, 53 MB/s, FD 8100/8100, open 396556 close 388456
03:24:26 [Distributor] 分发: 1722 chunks, 7031M 条, numpy 307ms/ch, copy 721ms/ch, flushQ 2048
03:24:33 [Writer] 写入: 399388 flush, 91.6 GB, 53 MB/s, FD 8100/8100, open 399388 close 391288
03:24:43 [Writer] 写入: 402592 flush, 92.3 GB, 53 MB/s, FD 8100/8100, open 402592 close 394492
03:24:45 [Distributor] 分发: 1724 chunks, 7040M 条, numpy 307ms/ch, copy 731ms/ch, flushQ 2048
03:24:53 [Writer] 写入: 405925 flush, 93.1 GB, 53 MB/s, FD 8100/8100, open 405925 close 397825
03:24:56 [Distributor] 分发: 1725 chunks, 7044M 条, numpy 307ms/ch, copy 736ms/ch, flushQ 2048
03:25:03 [Writer] 写入: 409152 flush, 93.8 GB, 53 MB/s, FD 8100/8100, open 409152 close 401052
03:25:09 [Distributor] 分发: 1726 chunks, 7048M 条, numpy 307ms/ch, copy 743ms/ch, flushQ 2048
03:25:13 [Writer] 写入: 412533 flush, 94.6 GB, 53 MB/s, FD 8100/8100, open 412533 close 404433
03:25:23 [Distributor] 分发: 1727 chunks, 7052M 条, numpy 307ms/ch, copy 751ms/ch, flushQ 2048
03:25:23 [Writer] 写入: 416059 flush, 95.4 GB, 53 MB/s, FD 8100/8100, open 416059 close 407959
03:25:33 [Writer] 写入: 419083 flush, 96.1 GB, 54 MB/s, FD 8100/8100, open 419083 close 410983
03:25:38 [Distributor] 分发: 1728 chunks, 7056M 条, numpy 307ms/ch, copy 759ms/ch, flushQ 2048
03:25:43 [Writer] 写入: 422348 flush, 96.9 GB, 54 MB/s, FD 8100/8100, open 422348 close 414248
03:25:53 [Writer] 写入: 425829 flush, 97.7 GB, 54 MB/s, FD 8100/8100, open 425829 close 417729
03:25:53 [Distributor] 分发: 1729 chunks, 7061M 条, numpy 307ms/ch, copy 767ms/ch, flushQ 2048
03:26:03 [Writer] 写入: 429082 flush, 98.4 GB, 54 MB/s, FD 8100/8100, open 429082 close 420982
03:26:08 [Distributor] 分发: 1730 chunks, 7065M 条, numpy 307ms/ch, copy 775ms/ch, flushQ 2048
03:26:13 [Writer] 写入: 432587 flush, 99.2 GB, 54 MB/s, FD 8100/8100, open 432587 close 424487
03:26:22 [Distributor] 分发: 1731 chunks, 7069M 条, numpy 307ms/ch, copy 782ms/ch, flushQ 2048
03:26:23 [Writer] 写入: 436052 flush, 100.0 GB, 54 MB/s, FD 8100/8100, open 436052 close 427952
03:26:33 [Writer] 写入: 439558 flush, 100.8 GB, 54 MB/s, FD 8100/8100, open 439558 close 431458
03:26:34 [Distributor] 分发: 1732 chunks, 7073M 条, numpy 307ms/ch, copy 789ms/ch, flushQ 2048
03:26:43 [Writer] 写入: 442945 flush, 101.6 GB, 55 MB/s, FD 8100/8100, open 442945 close 434845
03:26:46 [Distributor] 分发: 1733 chunks, 7077M 条, numpy 307ms/ch, copy 795ms/ch, flushQ 2048
03:26:53 [Writer] 写入: 445858 flush, 102.3 GB, 55 MB/s, FD 8100/8100, open 445858 close 437758
03:26:56 [Reader] 读取: part_015.bin (3.14 GB)
03:27:03 [Writer] 写入: 449235 flush, 103.0 GB, 55 MB/s, FD 8100/8100, open 449235 close 441135
03:27:04 [Distributor] 分发: 1735 chunks, 7086M 条, numpy 307ms/ch, copy 804ms/ch, flushQ 2048
03:27:13 [Writer] 写入: 452530 flush, 103.8 GB, 55 MB/s, FD 8100/8100, open 452530 close 444430
03:27:15 [Distributor] 分发: 1737 chunks, 7094M 条, numpy 307ms/ch, copy 809ms/ch, flushQ 2048
03:27:23 [Writer] 写入: 455363 flush, 104.4 GB, 55 MB/s, FD 8100/8100, open 455363 close 447263
03:27:25 [Distributor] 分发: 1740 chunks, 7107M 条, numpy 307ms/ch, copy 813ms/ch, flushQ 2048
03:27:33 [Writer] 写入: 456063 flush, 104.6 GB, 55 MB/s, FD 8100/8100, open 456063 close 447963
03:27:43 [Writer] 写入: 456279 flush, 104.7 GB, 54 MB/s, FD 8100/8100, open 456279 close 448179
03:27:49 [Distributor] 分发: 1742 chunks, 7115M 条, numpy 307ms/ch, copy 825ms/ch, flushQ 2048
03:27:53 [Writer] 写入: 456455 flush, 104.7 GB, 54 MB/s, FD 8100/8100, open 456455 close 448355
03:28:03 [Writer] 写入: 456502 flush, 104.7 GB, 54 MB/s, FD 8100/8100, open 456502 close 448402
03:28:05 [Distributor] 分发: 1743 chunks, 7119M 条, numpy 307ms/ch, copy 834ms/ch, flushQ 2048
03:28:13 [Writer] 写入: 456590 flush, 104.7 GB, 54 MB/s, FD 8100/8100, open 456590 close 448490
03:28:20 [Distributor] 分发: 1744 chunks, 7124M 条, numpy 307ms/ch, copy 842ms/ch, flushQ 2048
03:28:24 [Writer] 写入: 456671 flush, 104.7 GB, 53 MB/s, FD 8100/8100, open 456671 close 448571
03:28:31 [Distributor] 分发: 1746 chunks, 7132M 条, numpy 307ms/ch, copy 846ms/ch, flushQ 1990
03:28:35 [Writer] 写入: 456843 flush, 104.8 GB, 53 MB/s, FD 8100/8100, open 456843 close 448743
03:28:41 [Distributor] 分发: 1759 chunks, 7183M 条, numpy 307ms/ch, copy 844ms/ch, flushQ 972
03:28:45 [Writer] 写入: 458626 flush, 105.2 GB, 53 MB/s, FD 8100/8100, open 458626 close 450526
03:28:51 [Distributor] 分发: 1782 chunks, 7280M 条, numpy 308ms/ch, copy 835ms/ch, flushQ 0
03:28:53 [Reader] 读取: part_016.bin (3.14 GB)
03:29:01 [Distributor] 分发: 1800 chunks, 7355M 条, numpy 307ms/ch, copy 829ms/ch, flushQ 0
03:29:12 [Distributor] 分发: 1815 chunks, 7415M 条, numpy 307ms/ch, copy 825ms/ch, flushQ 0
03:29:22 [Distributor] 分发: 1828 chunks, 7469M 条, numpy 307ms/ch, copy 823ms/ch, flushQ 0
03:29:29 [Reader] 读取: part_017.bin (3.14 GB)
03:29:32 [Distributor] 分发: 1840 chunks, 7519M 条, numpy 307ms/ch, copy 821ms/ch, flushQ 0
03:29:43 [Distributor] 分发: 1852 chunks, 7570M 条, numpy 307ms/ch, copy 820ms/ch, flushQ 0
03:29:53 [Distributor] 分发: 1874 chunks, 7659M 条, numpy 307ms/ch, copy 812ms/ch, flushQ 0
03:29:59 [Reader] 读取: part_018.bin (3.14 GB)
03:30:03 [Distributor] 分发: 1895 chunks, 7747M 条, numpy 308ms/ch, copy 805ms/ch, flushQ 0
03:30:14 [Distributor] 分发: 1915 chunks, 7827M 条, numpy 308ms/ch, copy 798ms/ch, flushQ 0
03:30:24 [Distributor] 分发: 1934 chunks, 7907M 条, numpy 308ms/ch, copy 792ms/ch, flushQ 0
03:30:26 [Reader] 读取: part_000.bin (1.57 GB)
03:30:34 [Writer] 写入: 458753 flush, 105.2 GB, 50 MB/s, FD 8100/8100, open 458753 close 450653
03:30:34 [Distributor] 分发: 1951 chunks, 7978M 条, numpy 308ms/ch, copy 788ms/ch, flushQ 0
03:30:44 [Writer] 写入: 459316 flush, 105.3 GB, 50 MB/s, FD 8100/8100, open 459316 close 451216
03:30:44 [Distributor] 分发: 1963 chunks, 8025M 条, numpy 308ms/ch, copy 786ms/ch, flushQ 1608
03:30:47 [Reader] 读取: part_001.bin (1.57 GB)
03:30:54 [Writer] 写入: 461908 flush, 105.9 GB, 50 MB/s, FD 8100/8100, open 461908 close 453808
03:30:58 [Distributor] 分发: 1966 chunks, 8038M 条, numpy 308ms/ch, copy 791ms/ch, flushQ 2048
03:31:04 [Writer] 写入: 464931 flush, 106.6 GB, 50 MB/s, FD 8100/8100, open 464931 close 456831
03:31:14 [Writer] 写入: 468107 flush, 107.4 GB, 50 MB/s, FD 8100/8100, open 468107 close 460007
03:31:14 [Distributor] 分发: 1968 chunks, 8046M 条, numpy 308ms/ch, copy 799ms/ch, flushQ 2048
03:31:24 [Writer] 写入: 471328 flush, 108.1 GB, 51 MB/s, FD 8100/8100, open 471328 close 463228
03:31:25 [Distributor] 分发: 1969 chunks, 8050M 条, numpy 308ms/ch, copy 803ms/ch, flushQ 2048
03:31:34 [Writer] 写入: 474129 flush, 108.7 GB, 51 MB/s, FD 8100/8100, open 474129 close 466029
03:31:38 [Distributor] 分发: 1970 chunks, 8055M 条, numpy 308ms/ch, copy 809ms/ch, flushQ 2048
03:31:44 [Writer] 写入: 477353 flush, 109.5 GB, 51 MB/s, FD 8100/8100, open 477353 close 469253
03:31:51 [Distributor] 分发: 1971 chunks, 8059M 条, numpy 308ms/ch, copy 815ms/ch, flushQ 2048
03:31:54 [Writer] 写入: 480681 flush, 110.2 GB, 51 MB/s, FD 8100/8100, open 480681 close 472581
03:32:04 [Writer] 写入: 483995 flush, 111.0 GB, 51 MB/s, FD 8100/8100, open 483995 close 475895
03:32:05 [Distributor] 分发: 1972 chunks, 8063M 条, numpy 308ms/ch, copy 822ms/ch, flushQ 2048
03:32:14 [Writer] 写入: 487237 flush, 111.8 GB, 51 MB/s, FD 8100/8100, open 487237 close 479137
03:32:19 [Distributor] 分发: 1973 chunks, 8067M 条, numpy 308ms/ch, copy 828ms/ch, flushQ 2048
03:32:24 [Writer] 写入: 490467 flush, 112.5 GB, 51 MB/s, FD 8100/8100, open 490467 close 482367
03:32:34 [Writer] 写入: 493341 flush, 113.2 GB, 51 MB/s, FD 8100/8100, open 493341 close 485241
03:32:35 [Distributor] 分发: 1974 chunks, 8071M 条, numpy 308ms/ch, copy 836ms/ch, flushQ 2048
03:32:44 [Writer] 写入: 496567 flush, 113.9 GB, 51 MB/s, FD 8100/8100, open 496567 close 488467
03:32:49 [Distributor] 分发: 1975 chunks, 8075M 条, numpy 308ms/ch, copy 842ms/ch, flushQ 2048
03:32:54 [Writer] 写入: 499844 flush, 114.6 GB, 52 MB/s, FD 8100/8100, open 499844 close 491744
03:33:02 [Distributor] 分发: 1976 chunks, 8080M 条, numpy 308ms/ch, copy 849ms/ch, flushQ 2048
03:33:04 [Writer] 写入: 502931 flush, 115.4 GB, 52 MB/s, FD 8100/8100, open 502931 close 494831
03:33:14 [Writer] 写入: 506203 flush, 116.1 GB, 52 MB/s, FD 8100/8100, open 506203 close 498103
03:33:14 [Distributor] 分发: 1977 chunks, 8084M 条, numpy 309ms/ch, copy 854ms/ch, flushQ 2048
03:33:24 [Writer] 写入: 509483 flush, 116.9 GB, 52 MB/s, FD 8100/8100, open 509483 close 501383
03:33:25 [Distributor] 分发: 1978 chunks, 8088M 条, numpy 309ms/ch, copy 859ms/ch, flushQ 2048
03:33:34 [Writer] 写入: 512196 flush, 117.5 GB, 52 MB/s, FD 8100/8100, open 512196 close 504096
03:33:36 [Distributor] 分发: 1979 chunks, 8092M 条, numpy 309ms/ch, copy 864ms/ch, flushQ 2048
03:33:44 [Writer] 写入: 515176 flush, 118.2 GB, 52 MB/s, FD 8100/8100, open 515176 close 507076
03:33:50 [Distributor] 分发: 1981 chunks, 8101M 条, numpy 309ms/ch, copy 870ms/ch, flushQ 2048
03:33:54 [Writer] 写入: 518265 flush, 118.9 GB, 52 MB/s, FD 8100/8100, open 518265 close 510165
03:34:03 [Distributor] 分发: 1985 chunks, 8114M 条, numpy 309ms/ch, copy 873ms/ch, flushQ 2048
03:34:04 [Writer] 写入: 520844 flush, 119.5 GB, 52 MB/s, FD 8100/8100, open 520844 close 512744
03:34:13 [Distributor] 分发: 1987 chunks, 8122M 条, numpy 309ms/ch, copy 877ms/ch, flushQ 2048
03:34:14 [Writer] 写入: 521650 flush, 119.6 GB, 52 MB/s, FD 8100/8100, open 521650 close 513550
03:34:23 [Distributor] 分发: 1988 chunks, 8126M 条, numpy 309ms/ch, copy 882ms/ch, flushQ 2048
03:34:24 [Writer] 写入: 521899 flush, 119.7 GB, 52 MB/s, FD 8100/8100, open 521899 close 513799
03:34:35 [Writer] 写入: 521946 flush, 119.7 GB, 52 MB/s, FD 8100/8100, open 521946 close 513846
03:34:42 [Distributor] 分发: 1989 chunks, 8130M 条, numpy 309ms/ch, copy 891ms/ch, flushQ 2048
03:34:45 [Writer] 写入: 522066 flush, 119.7 GB, 51 MB/s, FD 8100/8100, open 522066 close 513966
03:34:55 [Writer] 写入: 522101 flush, 119.7 GB, 51 MB/s, FD 8100/8100, open 522101 close 514001
03:34:56 [Distributor] 分发: 1990 chunks, 8135M 条, numpy 309ms/ch, copy 898ms/ch, flushQ 2048
03:34:57 [Reader] 读取: part_002.bin (1.57 GB)
03:35:06 [Writer] 写入: 522189 flush, 119.8 GB, 51 MB/s, FD 8100/8100, open 522189 close 514089
03:35:09 [Distributor] 分发: 1991 chunks, 8139M 条, numpy 309ms/ch, copy 904ms/ch, flushQ 2036
03:35:16 [Writer] 写入: 522306 flush, 119.8 GB, 51 MB/s, FD 8100/8100, open 522306 close 514206
03:35:20 [Distributor] 分发: 1996 chunks, 8160M 条, numpy 309ms/ch, copy 906ms/ch, flushQ 1808
03:35:26 [Writer] 写入: 523601 flush, 120.1 GB, 51 MB/s, FD 8100/8100, open 523601 close 515501
03:35:29 [Reader] 读取: part_003.bin (1.57 GB)
03:35:30 [Distributor] 分发: 2019 chunks, 8252M 条, numpy 309ms/ch, copy 897ms/ch, flushQ 43
03:35:40 [Distributor] 分发: 2038 chunks, 8328M 条, numpy 309ms/ch, copy 891ms/ch, flushQ 0
03:35:43 [Reader] 读取: part_004.bin (1.57 GB)
03:35:50 [Distributor] 分发: 2054 chunks, 8395M 条, numpy 308ms/ch, copy 886ms/ch, flushQ 0
03:36:01 [Distributor] 分发: 2068 chunks, 8450M 条, numpy 308ms/ch, copy 884ms/ch, flushQ 0
03:36:01 [Reader] 读取: part_005.bin (1.57 GB)
03:36:11 [Distributor] 分发: 2080 chunks, 8501M 条, numpy 308ms/ch, copy 882ms/ch, flushQ 0
03:36:21 [Distributor] 分发: 2092 chunks, 8547M 条, numpy 308ms/ch, copy 880ms/ch, flushQ 0
03:36:23 [Reader] 读取: part_006.bin (1.57 GB)
03:36:32 [Distributor] 分发: 2102 chunks, 8589M 条, numpy 308ms/ch, copy 879ms/ch, flushQ 0
03:36:42 [Distributor] 分发: 2120 chunks, 8661M 条, numpy 308ms/ch, copy 874ms/ch, flushQ 0
03:36:42 [Reader] 读取: part_007.bin (1.57 GB)
03:36:52 [Distributor] 分发: 2142 chunks, 8749M 条, numpy 309ms/ch, copy 866ms/ch, flushQ 0
03:36:55 [Reader] 读取: part_008.bin (1.57 GB)
03:37:02 [Distributor] 分发: 2161 chunks, 8829M 条, numpy 309ms/ch, copy 861ms/ch, flushQ 0
03:37:08 [Reader] 读取: part_009.bin (1.57 GB)
03:37:13 [Distributor] 分发: 2181 chunks, 8909M 条, numpy 309ms/ch, copy 854ms/ch, flushQ 0
03:37:21 [Writer] 写入: 524289 flush, 120.2 GB, 48 MB/s, FD 8100/8100, open 524289 close 516189
03:37:22 [Reader] 读取: part_010.bin (1.57 GB)
03:37:23 [Distributor] 分发: 2200 chunks, 8985M 条, numpy 309ms/ch, copy 849ms/ch, flushQ 0
03:37:31 [Writer] 写入: 524733 flush, 120.4 GB, 48 MB/s, FD 8100/8100, open 524733 close 516633
03:37:34 [Distributor] 分发: 2211 chunks, 9031M 条, numpy 309ms/ch, copy 848ms/ch, flushQ 1546
03:37:41 [Writer] 写入: 526514 flush, 120.8 GB, 48 MB/s, FD 8100/8100, open 526514 close 518414
03:37:47 [Distributor] 分发: 2214 chunks, 9044M 条, numpy 309ms/ch, copy 853ms/ch, flushQ 2048
03:37:51 [Writer] 写入: 529395 flush, 121.4 GB, 48 MB/s, FD 8100/8100, open 529395 close 521295
03:38:01 [Writer] 写入: 532323 flush, 122.1 GB, 48 MB/s, FD 8100/8100, open 532323 close 524223
03:38:03 [Distributor] 分发: 2216 chunks, 9052M 条, numpy 309ms/ch, copy 859ms/ch, flushQ 2048
03:38:11 [Writer] 写入: 535219 flush, 122.8 GB, 48 MB/s, FD 8100/8100, open 535219 close 527119
03:38:15 [Distributor] 分发: 2218 chunks, 9057M 条, numpy 309ms/ch, copy 863ms/ch, flushQ 2048
03:38:21 [Writer] 写入: 538246 flush, 123.5 GB, 49 MB/s, FD 8100/8100, open 538246 close 530146
03:38:26 [Distributor] 分发: 2219 chunks, 9061M 条, numpy 309ms/ch, copy 867ms/ch, flushQ 2048
03:38:31 [Writer] 写入: 541264 flush, 124.1 GB, 49 MB/s, FD 8100/8100, open 541264 close 533164
03:38:38 [Distributor] 分发: 2220 chunks, 9065M 条, numpy 309ms/ch, copy 872ms/ch, flushQ 2048
03:38:41 [Writer] 写入: 544311 flush, 124.8 GB, 49 MB/s, FD 8100/8100, open 544311 close 536211
03:38:51 [Writer] 写入: 546952 flush, 125.4 GB, 49 MB/s, FD 8100/8100, open 546952 close 538852
03:38:54 [Distributor] 分发: 2221 chunks, 9069M 条, numpy 309ms/ch, copy 879ms/ch, flushQ 2048
03:39:01 [Writer] 写入: 550010 flush, 126.1 GB, 49 MB/s, FD 8100/8100, open 550010 close 541910
03:39:08 [Distributor] 分发: 2222 chunks, 9074M 条, numpy 309ms/ch, copy 885ms/ch, flushQ 2048
03:39:11 [Writer] 写入: 553052 flush, 126.8 GB, 49 MB/s, FD 8100/8100, open 553052 close 544952
03:39:21 [Writer] 写入: 556158 flush, 127.6 GB, 49 MB/s, FD 8100/8100, open 556158 close 548058
03:39:22 [Distributor] 分发: 2223 chunks, 9078M 条, numpy 309ms/ch, copy 891ms/ch, flushQ 2048
03:39:31 [Writer] 写入: 558922 flush, 128.2 GB, 49 MB/s, FD 8100/8100, open 558922 close 550822
03:39:38 [Distributor] 分发: 2224 chunks, 9082M 条, numpy 309ms/ch, copy 897ms/ch, flushQ 2048
03:39:38 [Reader] 读取: part_011.bin (1.57 GB)
03:39:41 [Writer] 写入: 561820 flush, 128.9 GB, 49 MB/s, FD 8100/8100, open 561820 close 553720
03:39:51 [Writer] 写入: 564937 flush, 129.6 GB, 49 MB/s, FD 8100/8100, open 564937 close 556837
03:39:52 [Distributor] 分发: 2225 chunks, 9086M 条, numpy 309ms/ch, copy 903ms/ch, flushQ 2048
03:40:01 [Writer] 写入: 567873 flush, 130.2 GB, 49 MB/s, FD 8100/8100, open 567873 close 559773
03:40:05 [Distributor] 分发: 2226 chunks, 9090M 条, numpy 309ms/ch, copy 908ms/ch, flushQ 2048
03:40:11 [Writer] 写入: 571036 flush, 131.0 GB, 49 MB/s, FD 8100/8100, open 571036 close 562936
03:40:17 [Distributor] 分发: 2227 chunks, 9095M 条, numpy 309ms/ch, copy 913ms/ch, flushQ 2048
03:40:21 [Writer] 写入: 574127 flush, 131.7 GB, 49 MB/s, FD 8100/8100, open 574127 close 566027
03:40:27 [Distributor] 分发: 2228 chunks, 9099M 条, numpy 309ms/ch, copy 917ms/ch, flushQ 2048
03:40:31 [Writer] 写入: 576897 flush, 132.3 GB, 50 MB/s, FD 8100/8100, open 576897 close 568797
03:40:38 [Distributor] 分发: 2229 chunks, 9103M 条, numpy 309ms/ch, copy 921ms/ch, flushQ 2048
03:40:41 [Writer] 写入: 579708 flush, 133.0 GB, 50 MB/s, FD 8100/8100, open 579708 close 571608
03:40:51 [Distributor] 分发: 2231 chunks, 9111M 条, numpy 309ms/ch, copy 926ms/ch, flushQ 2048
03:40:51 [Writer] 写入: 582668 flush, 133.6 GB, 50 MB/s, FD 8100/8100, open 582668 close 574568
03:41:01 [Writer] 写入: 585474 flush, 134.3 GB, 50 MB/s, FD 8100/8100, open 585474 close 577374
03:41:03 [Distributor] 分发: 2234 chunks, 9124M 条, numpy 309ms/ch, copy 930ms/ch, flushQ 2048
03:41:11 [Writer] 写入: 586998 flush, 134.6 GB, 50 MB/s, FD 8100/8100, open 586998 close 578898
03:41:21 [Distributor] 分发: 2237 chunks, 9137M 条, numpy 309ms/ch, copy 936ms/ch, flushQ 2048
03:41:21 [Writer] 写入: 587308 flush, 134.7 GB, 50 MB/s, FD 8100/8100, open 587308 close 579208
03:41:31 [Writer] 写入: 587416 flush, 134.7 GB, 49 MB/s, FD 8100/8100, open 587416 close 579316
03:41:37 [Distributor] 分发: 2238 chunks, 9141M 条, numpy 309ms/ch, copy 943ms/ch, flushQ 2048
03:41:42 [Writer] 写入: 587538 flush, 134.8 GB, 49 MB/s, FD 8100/8100, open 587538 close 579438
03:41:52 [Writer] 写入: 587587 flush, 134.8 GB, 49 MB/s, FD 8100/8100, open 587587 close 579487
03:41:54 [Distributor] 分发: 2239 chunks, 9145M 条, numpy 309ms/ch, copy 950ms/ch, flushQ 2048
03:42:02 [Writer] 写入: 587698 flush, 134.8 GB, 49 MB/s, FD 8100/8100, open 587698 close 579598
03:42:07 [Distributor] 分发: 2240 chunks, 9149M 条, numpy 309ms/ch, copy 955ms/ch, flushQ 2022
03:42:12 [Writer] 写入: 587775 flush, 134.8 GB, 49 MB/s, FD 8100/8100, open 587775 close 579675
03:42:19 [Distributor] 分发: 2242 chunks, 9157M 条, numpy 309ms/ch, copy 959ms/ch, flushQ 1953
03:42:22 [Writer] 写入: 587911 flush, 134.8 GB, 48 MB/s, FD 8100/8100, open 587911 close 579811
03:42:27 [Reader] 读取: part_012.bin (1.57 GB)
03:42:29 [Distributor] 分发: 2255 chunks, 9208M 条, numpy 309ms/ch, copy 956ms/ch, flushQ 1050
03:42:32 [Writer] 写入: 589429 flush, 135.2 GB, 48 MB/s, FD 8100/8100, open 589429 close 581329
03:42:39 [Reader] 读取: part_013.bin (1.57 GB)
03:42:39 [Distributor] 分发: 2277 chunks, 9297M 条, numpy 309ms/ch, copy 948ms/ch, flushQ 0
03:42:50 [Distributor] 分发: 2294 chunks, 9368M 条, numpy 309ms/ch, copy 944ms/ch, flushQ 0
03:42:55 [Reader] 读取: part_014.bin (1.57 GB)
03:43:00 [Distributor] 分发: 2310 chunks, 9431M 条, numpy 309ms/ch, copy 940ms/ch, flushQ 0
03:43:11 [Distributor] 分发: 2323 chunks, 9482M 条, numpy 309ms/ch, copy 937ms/ch, flushQ 0
03:43:15 [Reader] 读取: part_015.bin (1.57 GB)
03:43:21 [Distributor] 分发: 2335 chunks, 9532M 条, numpy 309ms/ch, copy 936ms/ch, flushQ 0
03:43:32 [Distributor] 分发: 2346 chunks, 9579M 条, numpy 309ms/ch, copy 934ms/ch, flushQ 0
03:43:40 [Reader] 读取: part_016.bin (1.57 GB)
03:43:43 [Distributor] 分发: 2357 chunks, 9621M 条, numpy 309ms/ch, copy 933ms/ch, flushQ 0
03:43:53 [Distributor] 分发: 2376 chunks, 9697M 条, numpy 309ms/ch, copy 928ms/ch, flushQ 0
03:43:55 [Reader] 读取: part_017.bin (1.57 GB)
03:44:04 [Distributor] 分发: 2398 chunks, 9789M 条, numpy 309ms/ch, copy 920ms/ch, flushQ 0
03:44:08 [Reader] 读取: part_018.bin (1.57 GB)
03:44:14 [Distributor] 分发: 2417 chunks, 9865M 条, numpy 309ms/ch, copy 915ms/ch, flushQ 0
03:44:22 [Reader] 读线程完成: 149.0 GB, 2967s, 51 MB/s
03:44:24 [Distributor] 分发: 2439 chunks, 9953M 条, numpy 308ms/ch, copy 909ms/ch, flushQ 0
03:44:27 [Writer] 写入: 589825 flush, 135.3 GB, 47 MB/s, FD 8100/8100, open 589825 close 581725
03:45:30 [Writer] 写入: 589866 flush, 135.3 GB, 46 MB/s, FD 8100/8100, open 589866 close 581766
03:45:40 [Writer] 写入: 595273 flush, 136.4 GB, 46 MB/s, FD 8100/8100, open 594875 close 586775
03:45:50 [Writer] 写入: 599995 flush, 137.4 GB, 46 MB/s, FD 8100/8100, open 599539 close 591439
03:46:00 [Writer] 写入: 605563 flush, 138.6 GB, 46 MB/s, FD 8100/8100, open 605107 close 597007
03:46:10 [Writer] 写入: 611885 flush, 139.9 GB, 47 MB/s, FD 8100/8100, open 611429 close 603329
03:46:20 [Writer] 写入: 621688 flush, 142.0 GB, 47 MB/s, FD 8100/8100, open 621232 close 613132
03:46:30 [Writer] 写入: 634990 flush, 144.7 GB, 48 MB/s, FD 8100/8100, open 634534 close 626434
03:46:40 [Writer] 写入: 649930 flush, 147.9 GB, 49 MB/s, FD 8100/8100, open 649474 close 641374
03:46:42 [Distributor] 分发完成: 2451 chunks, 10000M 条, 3107s
03:46:42 [Distributor]   numpy均值: 307ms/chunk
03:46:42 [Distributor]   copy均值: 906ms/chunk
03:50:23 [Writer] 写入: 653354 flush, 148.6 GB, 46 MB/s, FD 8100/8100, open 652898 close 644798
03:50:26 [Writer] 写入完成: 655400 flush, 149.0 GB, 3331s, 46 MB/s, open 654944 close 646844
03:50:26 [MainThread] 散列完成: 655,400 次flush, 149.0 GB, 3331s
03:50:28 [MainThread] 非空桶: 65536/65536
03:50:28 [MainThread] === Phase 2: 排序 ===
03:50:30 [MainThread] 排序: 18 进程, 65536 个桶
03:50:43 [MainThread] 排序: [5000/65536] 13s, ETA 161s
03:50:58 [MainThread] 排序: [10000/65536] 29s, ETA 158s
03:51:18 [MainThread] 排序: [15000/65536] 48s, ETA 163s
03:51:38 [MainThread] 排序: [20000/65536] 69s, ETA 157s
03:52:00 [MainThread] 排序: [25000/65536] 91s, ETA 147s
03:52:22 [MainThread] 排序: [30000/65536] 112s, ETA 133s
03:52:54 [MainThread] 排序: [35000/65536] 145s, ETA 126s
03:53:26 [MainThread] 排序: [40000/65536] 176s, ETA 113s
03:53:56 [MainThread] 排序: [45000/65536] 206s, ETA 94s
03:54:20 [MainThread] 排序: [50000/65536] 230s, ETA 71s
03:54:46 [MainThread] 排序: [55000/65536] 257s, ETA 49s
03:55:08 [MainThread] 排序: [60000/65536] 278s, ETA 26s
03:55:29 [MainThread] 排序: [65000/65536] 299s, ETA 2s
03:55:31 [MainThread] 排序: [65536/65536] 301s, ETA 0s
03:55:31 [MainThread] 排序完成: 10,000,000,000 条, 301s
03:55:31 [MainThread] === 完成 ===
03:55:31 [MainThread] 记录: 10,000,000,000
03:55:31 [MainThread] 桶:   65536
03:55:31 [MainThread] Phase 1: 3333s
03:55:31 [MainThread] Phase 2: 302s
03:55:31 [MainThread] 总计:    3635s (60.6分钟)
```
