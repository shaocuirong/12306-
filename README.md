基于fiddler抓包分析python为主体的12306抢票脚本
  源码都有格式，去ui运行就好，需要tk，requests等库，换了一个版本，更新了一下ui，修复了一些bug

对于fiddler（具体怎么用详细见：https://blog.csdn.net/Mubei1314/article/details/122389950）抓包分析.
主要流程就是：
  1抓包，
  2分析协议头，
  3用python模拟伪装浏览器发送请求
首先得对12306网页的分析和相关请求的分析（这里有一篇21年的帖子https://blog.csdn.net/qq_46092061/article/details/119967871虽然很多接口的参数已经修改不能用了，但也能作为一个参考）
先开着fiddler在自己用网页端走一遍购票流程，然后保存相印的包信息

第一步肯定是获取网页的协议头，这样才能正常的发送请求，然后剖析

看21年的帖子可以知道可以访问
  1.https://www.12306.cn/index/
  2.https://kyfw.12306.cn/otn/login/conf
  3.https://kyfw.12306.cn/otn/index12306/getLoginBanner
这几个网站去初步获取cookies，但实际测试下来，主要是得获取JSESSIONID这个参数（只能通过第三个请求获取）其他的都一样

然后就是登陆，有两种登陆方式扫码和账号密码（这边选择扫码，更加方便）通过对抓到的包分析，
首先得要访问
https://kyfw.12306.cn/passport/web/create-qr64
获取二维码和其uuid（后面检查二维码状态用）
再是每隔一秒访问https://kyfw.12306.cn/passport/web/checkqr 
检查二维码状态
检测到二维码被扫描后，就开始登陆操作（太困了，暂时先写到这里。。。


