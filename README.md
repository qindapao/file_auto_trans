# file_auto_trans
Files are automatically sent and received for scenarios requiring a transfer server

用于自动向调测服务器里面的环境部署脚本。

## 自动构建exe

直接运行`auto_pack.py`即可打包完成。生成的文件在`exe`目录中。目前发现一个问题，就是生成的`file_auto_put.exe`可能会被杀毒软件当成病毒给干掉。唯一的办法是把当前这个目录加入到杀毒软件的白名单中，不要让它处理。


## 运行说明

运行的时候我们先运行`file_auto_put.exe`，先把文件传送过去，然后再在远程端执行`file_auto_get.exe`，以便于那边生成一个粗略的`get_file.json`，远端的代码如果发现`json`文件中有`DEST_DIR`键，并且这个键的值不是空，那么会根据第一次从绿传中获取到的文件列表生成一份`DEST_DIR`字典，并且清空`DEST_DIR`键，然后退出程序。

如果默认生成的`get_file.json`中的内容不是你想要的，比如你想改变某些文件发送到远端服务器后的名字，那么你可以手动编辑调整。调整完毕后再执行下面的操作。

这个时候，我们再先重新打开`file_auto_put.exe`，然后把文件再重新传递一次过来，然后，再在远端运行一下`file_auto_get`即可。

## 待办

