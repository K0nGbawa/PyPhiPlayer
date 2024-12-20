# PyPhiReader
## 简介
这是一个使用Python编写的Phigros模拟器



## 依赖库
- altgraph==0.17.4
- colorama==0.4.6
- numpy==2.2.0
- packaging==24.2
- pillow==11.0.0
- pydub==0.25.1
- pygame==2.6.1
- PyOpenGL==3.1.7
- pywin32==308
- pywin32-ctypes==0.2.3
- setuptools==75.6.0
- tqdm==4.67.1
<br/><br/>
可在源代码根目录下使用 `pip install -r requirements.txt` 命令安装

## 功能

<details>
<summary>展开</summary>

- [x] 为已实现
- [ ] 为未实现
<br/><br/>
- [x] Phigros官谱
  - [x] formatVersion
    - [ ] 1
    - [x] 3
    - [ ] 其它
  - [ ] offset
  - [x] 谱面读取
  - [x] 判定线
    - [x] 生成
    - [x] 事件读取及处理
  - [x] Notes
    - [x] Tap
    - [x] Drag
    - [x] Hold
    - [x] Flick
- [ ] RPE
  - [x] 谱面读取
  - [ ] 判定线
    - [ ] 生成
    - [ ] 事件读取及处理
  - [ ] Notes
    - [ ] Tap
    - [ ] Drag
    - [ ] Hold
    - [ ] Flick
- [x] 渲染视频
  - [x] 背景音乐
  - [x] 视频画面
  - [ ] 打击音效
</details>

- 部分代码参考了 [qaqFei](https://github.com/qaqFei) 的 [PhigrosPlayer](https://github.com/qaqFei/PhigrosPlayer)
- 此项目仅供学习交流，请勿用于商业用途