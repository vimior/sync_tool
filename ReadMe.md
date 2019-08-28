## 文件夹同步工具

此工具用于把一个文件夹（原文件夹）拷贝到另一个文件夹（目标文件夹）

- 通过配置来指定忽略某些文件夹或文件

- 通过配置来指定不忽略某些文件或文件夹

### 开发初衷

​一直以来，我都是使用同步盘来同步我的资料，从最初的Dropbox到现在的坚果云，真的很方便。

真正让我放弃这种便利的是因为前段时间的坚果云的自动升级，把我的坚果云的配置都清空了（这里主要指的是忽略规则），本来坚果云的规则就不太方便（文件可以使用通配符，文件夹不可以，要忽略某个文件夹必须使用全路径），这一升级，就是要我把要忽略的文件和文件夹的全路径找出来配置一遍（还不止一台电脑），鉴于要忽略的太多（__ps: 太多node_modules、build、dist__），而且使用全路径的配置不通用，果断放弃了。

放弃了同步盘这一类工具，本着通过U盘来拷贝就好，但单纯的拷贝无法忽略某些文件夹，而且拷贝的文件数比较多太耗时，于是打算写一个工具用来拷贝的（主要是__可以配置忽略的内容__和__只拷贝改动过的__）

### 拷贝规则

- 判断文件是否在忽略规则里面，如果是则直接忽略不拷贝，否则往下判断
- 如果目标文件不存在，直接拷贝，否则往下判断
- 通过比较md5，如果md5一样，不拷贝，否则拷贝

### 忽略规则（.syncignore文件）

- 每一行代表一条规则

- #开头的为注释，不生效

- 每行开头和结尾都可以使用*号通配符，代表以xxx开头或以xxx结尾或包含xxx的

- 以/开头的代表表示把原文件夹当做根目录来解析规则

- 可以使用绝对路径

- 以!开头的表示不忽略的内容（只能使用!{绝对路径}或!{/xxx}的形式）

  ```shell
  # 忽略所有名字为__pycache__的文件或文件夹
  __pycache__
  # 忽略所有名字为node_modules的文件或文件夹
  node_modules
  # 忽略所有名字以.pyc结尾的文件或文件夹
  *.pyc
  # 忽略名字包含ntvs的文件或文件夹
  *.ntvs*
  
  # 忽略{原文件夹}/Project/github/sync_tool/spec/build文件或文件夹
  /Project/github/sync_tool/spec/build
  # 忽略所有dist文件或文件夹
  dist/
  # 不忽略{原文件夹}/Project/github/sync_tool/spec/dist文件或文件夹
  !/Project/github/sync_tool/spec/dist/
  
  # 忽略绝对路径
  E:\Vinman\Project\github\sync_tool\spec\dist\SyncTool.exe
  ```

  

### 配置（config.ini文件）

- ```ini
  [Genernal]
  debug = True
  thread_size = 10
  source = E:\\Vinman
  target = H:\\Vinman
  
  # 说明：
  debug: 为True时表示日志级别为DEBUG，否则为INFO，默认为False
  thread_size: 拷贝线程数，默认为10
  source: 要拷贝的原文件夹
  target: 拷贝的目标文件夹
  ```

  



